import sqlite3
import json
import cv2
import numpy as np
import sys
import time

from PySide6.QtGui import QImage, QPixmap, Qt, QPolygonF
from PySide6.QtCore import Slot, QThread, Signal, QMutex, QWaitCondition
from PySide6.QtSql import QSqlDatabase, QSqlQueryModel, QSqlQuery
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton,
                               QStackedWidget, QTableWidget, QTableWidgetItem, QWidget, QMessageBox, QLabel)

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

        self.view.selectCamButton.clicked.connect(
            self.select_cam_button_clicked)

        self.view.toggleStreamButton.clicked.connect(
            self.toggle_stream_button_clicked)  # Connect toggleStreamButton

        self.view.user_btn.clicked.connect(self.user_btn_clicked)

        # Create a DrawingWidget as a child of the camViewLabel
        self.view.drawingWidget = DrawingWidget(self.view.camViewLabel)
        self.view.drawingWidget.setGeometry(self.view.camViewLabel.rect())

        self.view.completeButton.clicked.connect(self.complete_button_clicked) 

    @Slot()
    def complete_button_clicked(self):
        if len(self.model.current_polygon_points) > 1:
            self.view.drawingWidget.add_polygon(self.model.current_polygon_points)
            self.view.drawingWidget.repaint()  # Force the widget to repaint
            self.model.polygons.append(self.model.current_polygon_points)
            self.model.current_polygon_points = []

    @Slot()
    def select_cam_button_clicked(self):
        self.view.stackedWidget.setCurrentIndex(2)
        selected_ip_item = self.view.camTableWidget.item(
            self.view.camTableWidget.currentRow(), 1)
        if selected_ip_item:
            self.model.selected_ip = selected_ip_item.text()
            self.view.selectedCamLabel.setText(
                f"Selected Camera IP: {self.model.selected_ip}")
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

        # Resize the frame to fit the camViewLabel
        width, height = 800, 600
        frame_resized = cv2.resize(frame_rgb, (width, height))

        # Convert the frame to QImage format
        image = QImage(
            frame_resized.data, frame_resized.shape[1], frame_resized.shape[0], QImage.Format_RGB888)

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
                self.frame_available.emit(frame)

            QApplication.processEvents()

            time.sleep(0.001)  # Pause the thread for a short interval

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
        self.conn = sqlite3.connect("camera_database.db")
        cursor = self.conn.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS Cameras (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, ip_address TEXT NOT NULL)"
        )

        cursor.execute(
            "CREATE TABLE IF NOT EXISTS Polygons (id INTEGER PRIMARY KEY AUTOINCREMENT, camera_id INTEGER NOT NULL, label TEXT NOT NULL, coordinates TEXT NOT NULL, FOREIGN KEY (camera_id) REFERENCES Cameras (id))"
        )


        self.model.current_polygon_points = []  # Remove this line

        self.ui.drawingWidget = DrawingWidget(self.ui.camViewLabel)
        self.ui.drawingWidget.setGeometry(self.ui.camViewLabel.geometry())
        
        self.ui.completeButton.clicked.connect(self.complete_button_clicked)

    @Slot()
    def complete_button_clicked(self):
        if self.model.current_polygon_points:
            self.model.polygons.append(self.model.current_polygon_points)
            self.model.current_polygon_points = []
            self.ui.drawingWidget.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.ui.toggleStreamButton.isChecked():
                self.model.current_polygon_points.append(
                    (event.pos().x(), event.pos().y()))
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

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.ui.toggleStreamButton.isChecked():
                self.model.current_polygon_points.append(
                    (event.pos().x(), event.pos().y()))

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
                    "SELECT COUNT(*) FROM Cameras WHERE ip_address = ? OR name = ?", (value2, value1))
                result = cursor.fetchone()[0]
                if result > 0:
                    QMessageBox.warning(
                        self, "Duplicate Entry", "The IP address or camera name already exists in the database.")
                else:
                    cursor.execute(
                        "INSERT INTO Cameras (name, ip_address) VALUES (?, ?)", (value1, value2))
                    self.conn.commit()
                    self.load_table_data()
                    self.clear_input_fields()
            except Exception as e:
                print("Error inserting data:", e)
        else:
            QMessageBox.warning(self, "Missing Values",
                                "Please enter both Name and IP.")

    @Slot()
    def delete_data(self):
        selected_row = self.ui.camTableWidget.currentRow()
        if selected_row >= 0:
            ip = self.ui.camTableWidget.item(selected_row, 1).text()
            cursor = self.conn.cursor()
            cursor.execute("SELECT id FROM Cameras WHERE ip_address = ?", (ip,))
            camera_id = cursor.fetchone()[0]

            cursor.execute("DELETE FROM Polygons WHERE camera_id = ?", (camera_id,))
            cursor.execute("DELETE FROM Cameras WHERE ip_address = ?", (ip,))
            self.conn.commit()
            self.load_table_data()
            self.clear_input_fields()
        else:
            QMessageBox.warning(self, "No Row Selected", "Please select a row to delete.")\
    
    def get_polygons(self):
        selected_row = self.ui.camTableWidget.currentRow()
        if selected_row >= 0:
            ip = self.ui.camTableWidget.item(selected_row, 1).text()
            cursor = self.conn.cursor()
            cursor.execute("SELECT id FROM Cameras WHERE ip_address = ?", (ip,))
            camera_id = cursor.fetchone()[0]

            cursor.execute("SELECT label, coordinates FROM Polygons WHERE camera_id = ?", (camera_id,))
            polygons = cursor.fetchall()

            # Process the fetched polygons as needed

            print(polygons)
        else:
            QMessageBox.warning(self, "No Row Selected", "Please select a camera.")


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
