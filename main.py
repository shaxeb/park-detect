import sqlite3
import json
import cv2
import numpy as np
import sys

from PySide6 import QtCore, QtGui
from PySide6.QtGui import QImage, QPixmap, Qt
from PySide6.QtCore import Slot, QObject, QThread, Signal, QMutex, QWaitCondition, QTimer
from PySide6.QtSql import QSqlDatabase, QSqlQueryModel, QSqlQuery
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton,
                               QStackedWidget, QTableWidget, QTableWidgetItem, QWidget, QMessageBox, QLabel)

from app_ui import Ui_MainWindow

def draw_polygons(frame, polygons, labels, current_polygon_points):
    """Draws the stored polygons and labels on the frame"""
    for i, polygon in enumerate(polygons):
        points_array = np.array(polygon, np.int32).reshape((-1, 1, 2))
        frame = cv2.polylines(
            frame, [points_array], isClosed=True, color=(0, 255, 0), thickness=2)

        # Check if i exists as a key and the value is not empty
        if str(i) in labels and labels[str(i)]:
            label = labels[str(i)]
            label_position = (polygon[0][0], polygon[0][1] - 10)
            cv2.putText(frame, label, label_position,
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)

    if len(current_polygon_points) > 0:
        current_polygon_array = np.array(current_polygon_points, np.int32).reshape((-1, 1, 2))
        frame = cv2.polylines(
            frame, [current_polygon_array], isClosed=False, color=(0, 255, 0), thickness=2)

    return frame


class Model:
    def __init__(self):
        self.current_index = 0
        self.selected_ip = ""
        self.stream_active = False
        self.current_polygon_points = []
        self.polygons = []
        self.labels = {}


class Controller:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.video_thread = None

        self.view.home_btn_1.toggled.connect(lambda: self.on_button_toggled(0))
        self.view.home_btn_2.toggled.connect(lambda: self.on_button_toggled(0))
        self.view.cam_btn_1.toggled.connect(lambda: self.on_button_toggled(1))
        self.view.cam_btn_2.toggled.connect(lambda: self.on_button_toggled(1))
        self.view.edit_btn_1.toggled.connect(lambda: self.on_button_toggled(2))
        self.view.edit_btn_2.toggled.connect(lambda: self.on_button_toggled(2))

        self.view.selectCamButton.clicked.connect(self.select_cam_button_clicked)

        self.view.completePolygonButton.clicked.connect(self.complete_polygon_button_clicked)

        self.view.toggleStreamButton.clicked.connect(self.toggle_stream_button_clicked)  # Connect toggleStreamButton

        self.view.user_btn.clicked.connect(self.user_btn_clicked)

    def complete_polygon_button_clicked(self):
        if self.model.stream_active and self.model.current_index == 1:  # Only allow completing the polygon when the stream is active and on the camPage
            ip = self.model.selected_ip
            polygons = self.fetch_polygons_from_database(ip)
            polygons.append(self.model.current_polygon_points)
            self.update_polygons_in_database(ip, polygons)

            self.model.current_polygon_points = []  # Clear the current polygon points
            self.display_frame()  # Update the frame after completing the polygon

    @Slot()
    def select_cam_button_clicked(self):
        self.view.stackedWidget.setCurrentIndex(2)  # Navigate to the editPage
        self.model.selected_ip = self.view.camTableWidget.item(
            self.view.camTableWidget.currentRow(), 1).text()  # Retrieve the selected IP address

        self.view.selectedCamLabel.setText(f"Selected Camera IP: {self.model.selected_ip}")
        self.start_video_stream()

    def start_video_stream(self):
        if self.video_thread is not None:
            self.video_thread.stop()
            self.video_thread.wait()
            self.video_thread = None

        ip = self.model.selected_ip
        self.video_thread = VideoThread(ip)
        self.video_thread.frame_available.connect(self.display_frame)
        self.video_thread.start()

    @Slot()
    def toggle_stream_button_clicked(self):
        if self.view.toggleStreamButton.isChecked():
            self.start_video_stream()  # Start or resume video playback
        else:
            self.stop_video_stream()  # Stop video playback


    def pause_video_stream(self):
        if self.video_thread is not None:
            self.video_thread.pause()  # Pause video playback

    def stop_video_stream(self):
        if self.video_thread is not None:
            self.video_thread.stop()
            self.video_thread.wait()
            self.video_thread = None

        self.view.camViewLabel.clear()
    
    @Slot(np.ndarray)
    def display_frame(self, frame):
        # Convert the frame from BGR to RGB format
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Draw polygons on the frame
        frame_with_polygons = draw_polygons(frame_rgb, self.model.polygons, self.model.labels, self.model.current_polygon_points)

        # Resize the frame to fit the camViewLabel
        width = 800
        height = 600
        frame_resized = cv2.resize(frame_with_polygons, (width, height))

        # Convert the frame to QImage format
        image = QImage(frame_resized.data, frame_resized.shape[1],
                    frame_resized.shape[0], QImage.Format_RGB888)

        # Display the frame in the camViewLabel
        pixmap = QPixmap.fromImage(image)
        self.view.camViewLabel.setPixmap(pixmap)


    @Slot()
    def user_btn_clicked(self):
        self.view.stackedWidget.setCurrentIndex(3)

    @Slot(int)
    def on_button_toggled(self, index):
        if index >= 0 and index < self.view.stackedWidget.count():
            self.view.stackedWidget.setCurrentIndex(index)
            self.model.current_index = index

from PySide6.QtCore import QTimer

class VideoThread(QThread):
    frame_available = Signal(np.ndarray)

    def __init__(self, ip):
        super(VideoThread, self).__init__()
        self.ip = ip
        self.running = False
        self.paused = False
        self.mutex = QMutex()
        self.condition = QWaitCondition()

    def run(self):
        cap = cv2.VideoCapture(self.ip)
        self.running = True

        while self.running:
            ret, frame = cap.read()
            if ret:
                self.mutex.lock()
                if self.paused:
                    self.condition.wait(self.mutex)
                self.mutex.unlock()

                self.frame_available.emit(frame)

            # Allow the event loop to process events
            QApplication.processEvents()

            # Pause the thread for a short interval
            QTimer.singleShot(1, self.dummy)  # Use a short interval to minimize delay

        cap.release()

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


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setWindowTitle("WiseLens AI")

        self.ui.icon_only_widget.hide()
        self.ui.stackedWidget.setCurrentIndex(0)
        self.ui.home_btn_2.setChecked(True)

        self.model = Model()
        self.controller = Controller(self.model, self.ui)

        self.model.current_index = 0
        self.ui.stackedWidget.setCurrentIndex(self.model.current_index)

        self.ui.stackedWidget.currentChanged.connect(
            self.on_stackedWidget_currentChanged)

        self.ui.addCamButton.clicked.connect(self.add_data)
        self.ui.removeCamButton.clicked.connect(self.delete_data)

        # Connect the camTableWidget cellClicked signal to on_table_cell_clicked slot
        self.ui.camTableWidget.cellClicked.connect(self.on_table_cell_clicked)

        # Create a SQLite3 database and a table to store camera data
        self.conn = sqlite3.connect("database.db")
        cursor = self.conn.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS cameras (name TEXT UNIQUE, ip TEXT PRIMARY KEY UNIQUE, polygons TEXT, labels TEXT)")

    def fetch_polygons_from_database(self, ip):
        polygons = []
        labels = {}

        cursor = self.conn.cursor()
        cursor.execute("SELECT polygons, labels FROM cameras WHERE ip = ?", (ip,))
        result = cursor.fetchone()

        if result:
            polygons_str, labels_str = result
            polygons = json.loads(polygons_str)
            labels = json.loads(labels_str)

        return polygons, labels

    def update_polygons_in_database(self, ip, polygons, labels):
        polygons_str = json.dumps(polygons)
        labels_str = json.dumps(labels)

        cursor = self.conn.cursor()
        cursor.execute("UPDATE cameras SET polygons = ?, labels = ? WHERE ip = ?", (polygons_str, labels_str, ip))
        self.conn.commit()

    def on_table_cell_clicked(self, row, column):
        self.ui.camnameLineEdit.setText(self.ui.camTableWidget.item(row, 0).text())
        self.ui.camipLineEdit.setText(self.ui.camTableWidget.item(row, 1).text())

    def load_table_data(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT name, ip FROM cameras")
        data = cursor.fetchall()

        self.ui.camTableWidget.setRowCount(len(data))
        self.ui.camTableWidget.setColumnCount(2)

        for row, items in enumerate(data):
            for col, item in enumerate(items[:2]):
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
                cursor.execute("SELECT COUNT(*) FROM cameras WHERE ip = ? OR name = ?", (value2, value1))
                result = cursor.fetchone()[0]
                if result > 0:
                    QMessageBox.warning(self, "Duplicate Entry",
                                        "The IP address or camera name already exists in the database.")
                else:
                    cursor.execute("INSERT INTO cameras (name, ip) VALUES (?, ?)", (value1, value2))
                    self.conn.commit()
                    self.load_table_data()
                    self.clear_input_fields()
            except Exception as e:
                print("Error inserting data:", e)
        else:
            QMessageBox.warning(self, "Missing Values", "Please enter both Name and IP.")

    @Slot()
    def delete_data(self):
        selected_row = self.ui.camTableWidget.currentRow()
        if selected_row >= 0:
            ip = self.ui.camTableWidget.item(selected_row, 1).text()
            try:
                cursor = self.conn.cursor()
                cursor.execute("DELETE FROM cameras WHERE ip = ?", (ip,))
                self.conn.commit()
                self.load_table_data()
                self.clear_input_fields()
            except Exception as e:
                print("Error deleting row:", e)
        else:
            QMessageBox.warning(self, "No Row Selected", "Please select a row to delete.")
    
    def clear_input_fields(self):
        self.ui.camnameLineEdit.clear()
        self.ui.camipLineEdit.clear()

    @Slot(int)
    def on_stackedWidget_currentChanged(self, index):
        btn_list = self.ui.icon_only_widget.findChildren(QPushButton) \
                   + self.ui.full_menu_widget.findChildren(QPushButton)

        for btn in btn_list:
            if index in [3, 4]:
                btn.setAutoExclusive(False)
                btn.setChecked(False)
            else:
                btn.setAutoExclusive(True)


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
