import sys
import cv2
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap, QPainter, QPen
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Camera Stream with Drawing")

        self.video_label = QLabel(self)
        self.video_label.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(self.video_label)

        self.play_pause_button = QPushButton("Play", self)
        self.play_pause_button.clicked.connect(self.toggle_stream)

        self.complete_button = QPushButton("Complete", self)
        self.complete_button.clicked.connect(self.complete_polygon)
        self.complete_button.setEnabled(False)

        self.play_pause_button.move(20, 20)
        self.complete_button.move(120, 20)

        self.video_capture = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)

        self.polygons = []
        self.current_polygon = []
        self.is_drawing = False
        self.dragging = False
        self.drag_point = None

        self.start_stream()

    def start_stream(self):
        self.video_capture = cv2.VideoCapture(0)
        self.timer.start(30)  # Update frame every 30ms
        self.play_pause_button.setText("Pause")

    def toggle_stream(self):
        if self.timer.isActive():
            self.timer.stop()
            self.play_pause_button.setText("Play")
            self.complete_button.setEnabled(True)
            self.is_drawing = True
        else:
            self.timer.start()
            self.play_pause_button.setText("Pause")
            self.complete_button.setEnabled(False)
            self.is_drawing = False

    def update_frame(self):
        ret, frame = self.video_capture.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, _ = frame.shape

            # Draw polygons on the frame
            for polygon in self.polygons:
                self.draw_polygon(frame, polygon)

            # Draw the current polygon being drawn
            if self.is_drawing and len(self.current_polygon) > 1:
                self.draw_current_polygon(frame)

            # Draw the temporary line while dragging
            if self.dragging and self.drag_point is not None:
                self.draw_temporary_line(frame)

            # Convert the frame to QImage and display it in the QLabel
            image = QImage(frame, width, height, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(image)
            self.video_label.setPixmap(pixmap)

    def draw_polygon(self, frame, polygon):
        for i in range(len(polygon) - 1):
            cv2.line(frame, polygon[i], polygon[i + 1], (0, 255, 0), 2)
        if len(polygon) > 1:
            cv2.line(frame, polygon[-1], polygon[0], (0, 255, 0), 2)

    def draw_current_polygon(self, frame):
        for i in range(len(self.current_polygon) - 1):
            cv2.line(frame, self.current_polygon[i], self.current_polygon[i + 1], (0, 255, 0), 2)

    def draw_temporary_line(self, frame):
        current_point = self.current_polygon[-1]
        cv2.line(frame, self.drag_point, current_point, (0, 255, 0), 2)

    def complete_polygon(self):
        if len(self.current_polygon) > 1:
            self.polygons.append(self.current_polygon)
            self.current_polygon = []
            self.is_drawing = False
            self.complete_button.setEnabled(False)
            self.update_frame()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.timer.isActive():
                return
            if not self.is_drawing:
                self.is_drawing = True
                self.complete_button.setEnabled(True)
            self.current_polygon.append((event.pos().x(), event.pos().y()))

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.is_drawing:
            if self.timer.isActive():
                return
            self.dragging = True
            self.drag_point = (event.pos().x(), event.pos().y())
            self.update_frame()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.timer.isActive():
                return
            if self.is_drawing:
                self.dragging = False
                self.drag_point = None
                self.current_polygon.append((event.pos().x(), event.pos().y()))
                self.update_frame()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
