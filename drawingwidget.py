from PySide6.QtGui import QPainter, QPen, QColor, QPolygon, QPolygonF, QBrush
from PySide6.QtCore import Qt, QPoint
from PySide6.QtWidgets import QWidget


class DrawingWidget(QWidget):
    def __init__(self, parent=None):
        super(DrawingWidget, self).__init__(parent)
        self.current_polygon = None
        self.polygons = []

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if not self.current_polygon:
                self.current_polygon = QPolygonF()
            self.current_polygon.append(event.pos())
            self.update()

    def add_polygon(self, polygon):
        self.polygons.append(polygon)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw the completed polygons
        for polygon in self.polygons:
            painter.setPen(QPen(Qt.green, 2))
            painter.setBrush(QBrush(Qt.green, Qt.BDiagPattern))
            painter.drawPolygon(polygon)

        # Draw the currently drawn polygon
        if self.current_polygon:
            painter.setPen(QPen(Qt.red, 2))
            painter.drawPolyline(self.current_polygon)

    def complete_polygon(self):
        if self.current_polygon:
            self.polygons.append(self.current_polygon)
            self.current_polygon = None
            self.update()
