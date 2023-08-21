import json
import sqlite3
import subprocess
import sys
import threading
import time

import cv2
import numpy as np
import psutil
import torch
from PySide6.QtCore import QMutex, QObject, QThread, QWaitCondition, Signal, Slot
from PySide6.QtGui import QIcon, QImage, QPixmap, Qt
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidgetItem,
)

from app_ui import Ui_MainWindow
from drawingwidget import DrawingWidget


class Model:
    def __init__(self):
        self.current_index = 0
        self.selected_ip = ""
        self.stream_active = False
        self.current_polygon_points = []
        self.polygons = []
        self.labels = {}
        self.selected_camera_id = ""
        self.prev_width = 0
        self.prev_height = 0
        self.parking_status = {}


class Controller:
    def __init__(self, model, view, main_window):
        self.model = model
        self.view = view
        self.main_window = main_window
        self.video_thread = None
        self.video_processing_thread = None
        self.ai_processing_thread = None

        self.view.home_btn_1.toggled.connect(lambda: self.on_button_toggled(0))
        self.view.home_btn_2.toggled.connect(lambda: self.on_button_toggled(0))
        self.view.cam_btn_1.toggled.connect(lambda: self.on_button_toggled(1))
        self.view.cam_btn_2.toggled.connect(lambda: self.on_button_toggled(1))
        self.view.edit_btn_1.toggled.connect(lambda: self.on_button_toggled(2))
        self.view.edit_btn_2.toggled.connect(lambda: self.on_button_toggled(2))
        self.view.ai_btn_1.toggled.connect(lambda: self.on_button_toggled(3))
        self.view.ai_btn_2.toggled.connect(lambda: self.on_button_toggled(3))

        self.view.selectCamButton.clicked.connect(self.select_cam_button_clicked)

        self.view.toggleStreamButton.clicked.connect(
            self.toggle_stream_button_clicked
        )  # Connect toggleStreamButton

        self.view.user_btn.clicked.connect(self.user_btn_clicked)

        # Create a DrawingWidget as a child of the camViewLabel
        self.view.drawingWidget = DrawingWidget(self.view.camViewLabel)
        self.view.drawingWidget.setGeometry(self.view.camViewLabel.rect())

        self.conn = sqlite3.connect("camera_database.db")

        # Check if CUDA is available and set device
        if torch.cuda.is_available():
            self.device = torch.device("cuda")
        else:
            self.device = torch.device("cpu")

        # Load YOLOv5 model
        self.model.yolov5_model = torch.hub.load("ultralytics/yolov5", "yolov5s")

        # Move model to the selected device
        self.model.yolov5_model.to(self.device)

        print("YOLOv5 model loaded successfully.")

        self.view.runAIButton.clicked.connect(self.run_ai_button_clicked)
        self.view.aspectRatioComboBox.addItem("16:9", (960, 540))
        self.view.aspectRatioComboBox.addItem("4:3", (800, 600))
        self.view.aspectRatioComboBox.currentIndexChanged.connect(
            self.change_aspect_ratio
        )
        self.view.aspectRatioComboBox.setCurrentIndex(0)

        self.parking_status_labels = {}

        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self.monitor_usage)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

    def monitor_usage(self):
        while True:
            # Get CPU usage
            cpu_usage = psutil.cpu_percent()
            print(f"CPU Usage: {cpu_usage}%")

            # Get RAM usage
            ram = psutil.virtual_memory()
            print(f"RAM Usage: {ram.percent}%")

            # Get GPU usage (NVIDIA GPUs only)
            try:
                gpu_info = subprocess.check_output(
                    [
                        "nvidia-smi",
                        "--query-gpu=utilization.gpu",
                        "--format=csv,noheader,nounits",
                    ]
                )
                gpu_usage = float(gpu_info.decode("utf-8").strip())
                print(f"GPU Usage: {gpu_usage}%")
            except subprocess.CalledProcessError:
                print("GPU Usage: N/A (No NVIDIA GPU detected)")

            time.sleep(5)  # Adjust the interval as needed

    def change_aspect_ratio(self, index):
        aspect_ratio = self.view.aspectRatioComboBox.currentData()
        width, height = aspect_ratio

        # Resize the frame and drawing area in the UI
        self.view.camViewLabel.setFixedSize(width, height)
        self.view.drawingWidget.setGeometry(0, 0, width, height)
        self.view.aiViewLabel.setFixedSize(width, height)  # Set aiViewLabel size

        # Start the video thread with the new aspect ratio
        if self.video_thread is not None:
            self.video_thread.change_aspect_ratio(aspect_ratio)

        # Notify the AI processing thread about the new aspect ratio
        if self.ai_processing_thread is not None:
            self.ai_processing_thread.change_aspect_ratio(aspect_ratio)

    @Slot()
    def run_ai_button_clicked(self):
        if torch.cuda.is_available():
            selected_row = self.view.camTableWidget.currentRow()
            if selected_row >= 0:
                ip_item = self.view.camTableWidget.item(selected_row, 1)
                if ip_item:
                    camera_ip = ip_item.text()
                    self.start_ai_stream(camera_ip)
        else:
            QMessageBox.warning(
                self.view.centralwidget,
                "CUDA Unavailable",
                "This program requires CUDA support for GPU acceleration, which is not available on this system.",
            )

    def start_ai_stream(self, camera_ip):
        self.model.selected_ip = camera_ip
        self.model.polygons, self.model.labels = self.get_polygons(camera_ip)

        self.view.stackedWidget.setCurrentIndex(3)

        if self.video_processing_thread is not None:
            self.video_processing_thread.stop()
            self.video_processing_thread.wait()
            self.video_processing_thread = None

        self.view.aiViewLabel.clear()

        # Get the selected aspect ratio from the aspectRatioComboBox
        aspect_ratio_data = self.view.aspectRatioComboBox.currentData()
        width, height = aspect_ratio_data

        # Initialize the AI processing thread (ai_processing_thread)
        self.ai_processing_worker = AIProcessingWorker(
            camera_ip, self.model, self.model.polygons, self.model.labels, width, height
        )
        self.ai_processing_worker.frame_available.connect(
            self.display_ai_frame
        )  # Connect frame_available signal to display_ai_frame

        # Start the AI processing worker in a separate thread
        self.ai_processing_thread = QThread()
        self.ai_processing_worker.moveToThread(self.ai_processing_thread)

        self.ai_processing_thread.started.connect(
            self.ai_processing_worker.process_frame
        )
        self.ai_processing_thread.finished.connect(
            self.ai_processing_worker.deleteLater
        )

        self.ai_processing_thread.start()

    @Slot(np.ndarray, dict, dict, float)
    def display_ai_frame(self, frame, parking_status, parking_duration, occupancy_rate):
        try:
            # Convert the frame to QImage format
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            q_image = QImage(
                frame_rgb.data,
                frame_rgb.shape[1],
                frame_rgb.shape[0],
                QImage.Format_RGB888,
            )

            # Get the selected aspect ratio from the aspectRatioComboBox
            aspect_ratio_data = self.view.aspectRatioComboBox.currentData()
            width, height = aspect_ratio_data

            # Scale the QImage to fit the aiViewLabel size while maintaining the aspect ratio
            scaled_image = q_image.scaled(
                self.view.aiViewLabel.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.SmoothTransformation,
            )

            # Create a QPixmap from the scaled QImage
            pixmap = QPixmap.fromImage(scaled_image)

            # Display the frame in the aiViewLabel
            self.view.aiViewLabel.setPixmap(pixmap)

            # Update parking space status labels
            label_offset_x = self.view.aiViewLabel.width() + 10
            label_offset_y = 10
            for i, area in enumerate(self.model.polygons):
                label = self.model.labels.get(i, f"p{i}")
                status_label = self.parking_status_labels.get(i)
                if not status_label:
                    status_label = QLabel(self.view.aiPage)
                    status_label.setObjectName(f"parkingStatusLabel{i}")
                    # Increased height to accommodate duration
                    status_label.setGeometry(
                        label_offset_x, label_offset_y + i * 25, 200, 40
                    )
                    self.parking_status_labels[i] = status_label

                label = self.model.labels.get(i, f"p{i}")
                status = parking_status.get(label, "unknown")
                duration = parking_duration.get(label, 0)
                status_label.setText(
                    f"{label}: {status.capitalize()} | Duration: {duration} sec"
                )

                # Change the color of the polygon and label
                color = (0, 255, 0)  # Green
                if not status.startswith("empty"):
                    color = (0, 0, 255)  # Red

                # Draw the polygon with the updated color
                cv2.polylines(frame, [np.array(area, np.int32)], True, color, 2)
                if i in self.model.labels:
                    label_position = (int(area[0][0]), int(area[0][1] - 10))
                    cv2.putText(
                        frame,
                        label,
                        label_position,
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        color,
                        2,
                        cv2.LINE_AA,
                    )

            # Convert the frame back to RGB format for displaying in the UI
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Convert the updated frame to QImage format
            q_image = QImage(
                frame_rgb.data,
                frame_rgb.shape[1],
                frame_rgb.shape[0],
                QImage.Format_RGB888,
            )

            # Scale the QImage to fit the aiViewLabel size while maintaining the aspect ratio
            scaled_image = q_image.scaled(
                self.view.aiViewLabel.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.SmoothTransformation,
            )

            # Create a QPixmap from the scaled QImage
            pixmap = QPixmap.fromImage(scaled_image)

            # Display the updated frame in the aiViewLabel
            self.view.aiViewLabel.setPixmap(pixmap)

            # Display the occupancy rate in a QLabel on the GUI
            occupancy_label = self.view.parkingOccupancyLabel
            occupancy_label.setText(f"Occupancy Rate: {occupancy_rate:.2f}%")

        except Exception as e:
            print("Error in display_ai_frame:", e)

    def get_polygons(self, camera_ip):
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT polygon_data FROM Cameras WHERE ip_address = ?", (camera_ip,)
            )
            data = cursor.fetchone()

            if data and data[0]:
                polygon_data = json.loads(data[0])
                polygons = []
                labels = {}

                for polygon_entry in polygon_data:
                    coordinates = polygon_entry.get("coordinates")
                    if coordinates:
                        polygon = [(x, y) for x, y in coordinates]
                        polygons.append(polygon)

                    label = polygon_entry.get("label")
                    if label:
                        labels[len(polygons) - 1] = label

                labels = {int(k): v for k, v in labels.items()}
                return polygons, labels
            else:
                QMessageBox.warning(
                    self.view,
                    "No Polygons",
                    "There are no polygons for the selected camera.",
                )
        except Exception as e:
            print("Error retrieving polygons:", e)
            QMessageBox.warning(
                self.view, "Error", "An error occurred while retrieving polygons."
            )

    @Slot()
    def select_cam_button_clicked(self):
        self.view.stackedWidget.setCurrentIndex(2)
        selected_row = self.view.camTableWidget.currentRow()
        if selected_row >= 0:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id, ip_address FROM Cameras")
            data = cursor.fetchall()
            if selected_row < len(data):
                # Get the camera ID from the selected row
                camera_id = data[selected_row][0]
                ip_item = self.view.camTableWidget.item(selected_row, 1)
                camera_ip = ip_item.text()
                if ip_item:
                    self.model.selected_ip = camera_ip
                    self.model.selected_camera_id = camera_id
                    self.view.selectedCamLabel.setText(
                        f"Selected Camera IP: {self.model.selected_ip}"
                    )
                    self.view.drawingWidget.set_camera_id(
                        self.model.selected_camera_id
                    )  # Pass the camera ID
                    # Load the polygons from the database
                    self.view.drawingWidget.load_polygon_data()
                    self.start_video_stream()
            else:
                QMessageBox.warning(
                    self, "Invalid Row Selected", "Please select a valid row."
                )
        else:
            QMessageBox.warning(self, "No Row Selected", "Please select a row.")

    def start_video_stream(self):
        if self.video_thread is not None:
            self.video_thread.stop()
            self.video_thread.wait()
            self.video_thread = None

        ip = self.model.selected_ip
        self.video_thread = VideoThread(ip)
        self.video_thread.frame_available.connect(self.display_frame)
        self.video_thread.start()

        # Pass the camera ID to the DrawingWidget
        self.view.drawingWidget.set_camera_id(self.model.selected_camera_id)

    @Slot()
    def toggle_stream_button_clicked(self):
        if self.view.toggleStreamButton.isChecked():
            self.start_video_stream()  # Start or resume video playback
        else:
            self.stop_video_stream()  # Stop video playback
            self.display_frame(np.zeros((1, 1, 3), dtype=np.uint8))

    def pause_video_stream(self):
        if self.video_thread is not None:
            self.video_thread.pause()  # Pause video playback

    def stop_video_stream(self):
        if self.video_thread is not None:
            self.video_thread.stop()
            self.video_thread.wait()
            self.video_thread = None

        if self.ai_processing_thread is not None:
            self.ai_processing_worker.stop()
            self.ai_processing_thread.quit()
            self.ai_processing_thread.wait()
            self.ai_processing_thread = None

        self.view.camViewLabel.clear()

    @Slot(np.ndarray)
    def display_frame(self, frame):
        # Convert the frame from BGR to RGB format
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Resize the frame to fit the camViewLabel
        width, height = 960, 540
        frame_resized = cv2.resize(frame_rgb, (width, height))

        # Convert the frame to QImage format
        image = QImage(
            frame_resized.data,
            frame_resized.shape[1],
            frame_resized.shape[0],
            QImage.Format_RGB888,
        )

        # Display the frame in the camViewLabel
        pixmap = QPixmap.fromImage(image)
        self.view.camViewLabel.setPixmap(pixmap)

    @Slot()
    def user_btn_clicked(self):
        self.view.stackedWidget.setCurrentIndex(4)

    @Slot(int)
    def on_button_toggled(self, index):
        if index >= 0 and index < self.view.stackedWidget.count():
            self.view.stackedWidget.setCurrentIndex(index)
            self.model.current_index = index


class VideoThread(QThread):
    frame_available = Signal(np.ndarray)

    def __init__(self, ip):
        super(VideoThread, self).__init__()
        self.ip = ip
        self.running = False
        self.paused = False
        self.mutex = QMutex()
        self.condition = QWaitCondition()
        self.aspect_ratio = (960, 540)

    def run(self):
        cap = cv2.VideoCapture(self.ip)
        self.running = True

        while self.running:
            ret, frame = cap.read()
            if ret:
                frame = cv2.resize(frame, self.aspect_ratio)
                self.frame_available.emit(frame)

            QApplication.processEvents()

        cap.release()

    def change_aspect_ratio(self, aspect_ratio):
        self.aspect_ratio = aspect_ratio
        self.mutex.lock()
        self.condition.wakeAll()
        self.mutex.unlock()

    def dummy(self):
        pass

    def stop(self):
        self.running = False
        self.mutex.lock()
        self.condition.wakeAll()
        self.mutex.unlock()

    def pause(self):
        self.mutex.lock()
        self.paused = True
        self.mutex.unlock()

    def resume(self):
        self.mutex.lock()
        self.paused = False
        self.condition.wakeAll()
        self.mutex.unlock()


class VideoProcessingWorker(QObject):
    frame_available = Signal(np.ndarray)

    def __init__(self, camera_ip, model, polygons, labels):
        super().__init__()
        self.camera_ip = camera_ip
        self.model = model
        self.polygons = polygons
        self.labels = labels
        self.running = False

    def process_frame(self):
        cap = cv2.VideoCapture(self.camera_ip)
        self.running = True

        while self.running:
            ret, frame = cap.read()
            if ret:
                print("Received frame:", frame.shape)
                self.frame_available.emit(frame)

        cap.release()

    def stop(self):
        self.running = False


class VideoProcessingThread(QThread):
    frame_available = Signal(np.ndarray)

    def __init__(self, camera_ip, model, polygons, labels):
        super(VideoProcessingThread, self).__init__()
        self.camera_ip = camera_ip
        self.model = model
        self.polygons = polygons
        self.labels = labels
        self.running = False

    def run(self):
        cap = cv2.VideoCapture(self.camera_ip)
        self.running = True

        while self.running:
            ret, frame = cap.read()
            if ret:
                self.frame_available.emit(frame)

        cap.release()

    def stop(self):
        self.running = False


class AIProcessingWorker(QObject):
    frame_available = Signal(np.ndarray, dict, dict, float)

    def __init__(self, camera_ip, model, polygons, labels, width, height):
        super().__init__()
        self.camera_ip = camera_ip
        self.model = model
        self.polygons = polygons
        self.labels = labels
        self.aspect_ratio = (width, height)
        self.running = False
        self.parking_status = {}
        self.parking_duration = {}

    def process_frame(self):
        cap = cv2.VideoCapture(self.camera_ip)
        self.running = True

        while self.running:
            ret, frame = cap.read()
            if ret:
                # Resize the frame to the selected aspect ratio
                width, height = self.aspect_ratio
                frame_resized = cv2.resize(frame, (width, height))

                results = self.model.yolov5_model(frame_resized)

                car_count = 0
                for index, row in results.pandas().xyxy[0].iterrows():
                    x1 = int(row["xmin"])
                    y1 = int(row["ymin"])
                    x2 = int(row["xmax"])
                    y2 = int(row["ymax"])
                    d = row["name"]
                    cx = (x1 + x2) // 2
                    cy = (y1 + y2) // 2
                    if "car" in d:
                        for i, area in enumerate(self.polygons):
                            if (
                                cv2.pointPolygonTest(
                                    np.array(area, np.int32), (cx, cy), False
                                )
                                >= 0
                            ):
                                # Draw bounding box around the car
                                cv2.rectangle(
                                    frame_resized, (x1, y1), (x2, y2), (0, 0, 255), 3
                                )
                                car_count += 1

                for i, area in enumerate(self.polygons):
                    color = (0, 255, 0)  # Default color: Green
                    # Draw the defined areas
                    cv2.polylines(
                        frame_resized, [np.array(area, np.int32)], True, color, 2
                    )
                    if i in self.labels:
                        label = self.labels[i]
                        label_position = (int(area[0][0]), int(area[0][1] - 10))
                        cv2.putText(
                            frame_resized,
                            label,
                            label_position,
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7,
                            color,
                            2,
                            cv2.LINE_AA,
                        )

                        # Check parking space occupancy and update the parking_status dictionary
                        is_empty = True
                        for index, row in results.pandas().xyxy[0].iterrows():
                            x1 = int(row["xmin"])
                            y1 = int(row["ymin"])
                            x2 = int(row["xmax"])
                            y2 = int(row["ymax"])
                            cx = (x1 + x2) // 2
                            cy = (y1 + y2) // 2
                            if "car" in row["name"]:
                                if (
                                    cv2.pointPolygonTest(
                                        np.array(area, np.int32), (cx, cy), False
                                    )
                                    >= 0
                                ):
                                    is_empty = False
                                    break

                        label = self.labels.get(i, f"p{i}")
                        self.parking_status[label] = "empty" if is_empty else "occupied"
                        # Change color to red if the polygon is not empty
                        if not is_empty:
                            color = (0, 0, 255)

                            # Check if the parking spot already exists in the parking_duration dictionary
                            label = self.labels.get(i, f"p{i}")
                            if label in self.parking_duration:
                                # Update the parking duration for the occupied spot
                                self.parking_duration[label] += 1
                            else:
                                # Initialize the parking duration for a new occupied spot
                                self.parking_duration[label] = 1
                        else:
                            # Clear the parking duration for empty spots
                            self.parking_duration[label] = 0

                    # Draw the defined areas
                    cv2.polylines(
                        frame_resized, [np.array(area, np.int32)], True, color, 2
                    )
                    if i in self.labels:
                        label = self.labels[i]
                        label_position = (int(area[0][0]), int(area[0][1] - 10))
                        cv2.putText(
                            frame_resized,
                            label,
                            label_position,
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7,
                            color,
                            2,
                            cv2.LINE_AA,
                        )

                total_spaces = len(self.parking_status)
                occupied_spaces = list(self.parking_status.values()).count("occupied")
                occupancy_rate = (occupied_spaces / total_spaces) * 100

                self.frame_available.emit(
                    frame_resized,
                    self.parking_status,
                    self.parking_duration,
                    occupancy_rate,
                )

        cap.release()

    def stop(self):
        self.running = False


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setWindowTitle("WiseLens AI - WisePark")
        self.setWindowIcon(QIcon("favicon.ico"))

        self.ui.icon_only_widget.hide()
        self.ui.stackedWidget.setCurrentIndex(0)
        self.ui.home_btn_2.setChecked(True)

        self.model = Model()
        self.controller = Controller(self.model, self.ui, self)

        self.model.current_index = 0
        self.ui.stackedWidget.setCurrentIndex(self.model.current_index)

        self.ui.stackedWidget.currentChanged.connect(
            self.on_stackedWidget_currentChanged
        )

        self.ui.addCamButton.clicked.connect(self.add_data)
        self.ui.removeCamButton.clicked.connect(self.delete_data)

        # Connect the camTableWidget cellClicked signal to on_table_cell_clicked slot
        self.ui.camTableWidget.cellClicked.connect(self.on_table_cell_clicked)

        # Create a SQLite3 database and a table to store camera data
        self.conn = sqlite3.connect("camera_database.db")
        cursor = self.conn.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS Cameras (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, ip_address TEXT NOT NULL, polygon_data TEXT)"
        )

        self.model.current_polygon_points = []

        self.ui.drawingWidget = DrawingWidget(self.ui.camViewLabel)
        self.ui.drawingWidget.setGeometry(self.ui.camViewLabel.geometry())
        self.ui.completeButton.clicked.connect(self.ui.drawingWidget.complete_polygon)
        self.ui.deleteLastButton.clicked.connect(self.delete_last_polygon)
        self.ui.removeAllButton.clicked.connect(
            self.ui.drawingWidget.remove_all_polygons
        )

        self.ui.aiViewLabel.clear()

    def closeEvent(self, event):
        self.conn.close()

        # Stop the monitor thread
        if hasattr(self, "controller") and hasattr(self.controller, "monitor_thread"):
            self.controller.monitor_thread.join()  # Wait for the thread to finish

    @Slot()
    def delete_last_polygon(self):
        if self.ui.drawingWidget.polygons:
            self.ui.drawingWidget.remove_polygon(-1)
            self.ui.drawingWidget.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.ui.toggleStreamButton.isChecked():
                self.model.current_polygon_points.append(
                    (event.pos().x(), event.pos().y())
                )
                self.ui.drawingWidget.update()

    def clear_input_fields(self):
        self.ui.camnameLineEdit.clear()
        self.ui.camipLineEdit.clear()

    @Slot(int)
    def on_stackedWidget_currentChanged(self, index):
        btn_list = self.ui.icon_only_widget.findChildren(QPushButton)
        btn_list += self.ui.full_menu_widget.findChildren(QPushButton)

        for btn in btn_list:
            if index in [3, 4]:
                btn.setAutoExclusive(False)
                btn.setChecked(False)
            else:
                btn.setAutoExclusive(True)

    def closeEvent(self, event):
        self.conn.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

    def on_table_cell_clicked(self, row, column):
        table_widget = self.ui.camTableWidget
        cam_name = table_widget.item(row, 0).text()
        cam_ip = table_widget.item(row, 1).text()
        self.ui.camnameLineEdit.setText(cam_name)
        self.ui.camipLineEdit.setText(cam_ip)

    def load_table_data(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT name, ip_address FROM cameras")
        data = cursor.fetchall()

        num_rows = len(data)
        num_cols = 2

        self.ui.camTableWidget.setRowCount(num_rows)
        self.ui.camTableWidget.setColumnCount(num_cols)

        for row, items in enumerate(data):
            for col, item in enumerate(items[:num_cols]):
                table_item = QTableWidgetItem(str(item))
                self.ui.camTableWidget.setItem(row, col, table_item)

    @Slot()
    def add_data(self):
        value1 = self.ui.camnameLineEdit.text()
        value2 = self.ui.camipLineEdit.text()

        if value1 and value2:
            try:
                cursor = self.conn.cursor()
                # Check if the IP or camera name already exists in the database
                cursor.execute(
                    "SELECT COUNT(*) FROM Cameras WHERE ip_address = ? OR name = ?",
                    (value2, value1),
                )
                result = cursor.fetchone()[0]
                if result > 0:
                    QMessageBox.warning(
                        self,
                        "Duplicate Entry",
                        "The IP address or camera name already exists in the database.",
                    )
                else:
                    cursor.execute(
                        "INSERT INTO Cameras (name, ip_address) VALUES (?, ?)",
                        (value1, value2),
                    )
                    self.conn.commit()
                    self.load_table_data()
                    self.clear_input_fields()
            except Exception as e:
                print("Error inserting data:", e)
        else:
            QMessageBox.warning(
                self, "Missing Values", "Please enter both Name and IP."
            )

    @Slot()
    def delete_data(self):
        selected_row = self.ui.camTableWidget.currentRow()
        if selected_row >= 0:
            ip = self.ui.camTableWidget.item(selected_row, 1).text()
            cursor = self.conn.cursor()
            cursor.execute("SELECT id FROM Cameras WHERE ip_address = ?", (ip,))
            camera_id = cursor.fetchone()[0]

            cursor.execute("DELETE FROM Cameras WHERE ip_address = ?", (ip,))
            self.conn.commit()
            self.load_table_data()
            self.clear_input_fields()
        else:
            QMessageBox.warning(
                self, "No Row Selected", "Please select a row to delete."
            )


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # loading stylesheet
    with open("style.qss", "r") as stylesheet:
        stylesheet = stylesheet.read()

    app.setStyleSheet(stylesheet)

    window = MainWindow()
    window.load_table_data()
    window.show()

    sys.exit(app.exec())
