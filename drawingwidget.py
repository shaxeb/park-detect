from PySide6.QtGui import QPainter, QPen, QColor, QPolygon, QPolygonF, QBrush
from PySide6.QtCore import Qt, QPoint
from PySide6.QtWidgets import QWidget


class DrawingWidget(QWidget):
    def __init__(self, parent=None):
        super(DrawingWidget, self).__init__(parent)
        self.current_polygon = []
        self.polygons = []

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.current_polygon.append(event.pos())
            self.update()

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
            painter.drawPolyline(QPolygon(self.current_polygon))