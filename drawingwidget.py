from PySide6.QtGui import QPainter, QPen, QPolygonF, QBrush, QFont
from PySide6.QtCore import Qt, QPointF
from PySide6.QtWidgets import QWidget, QInputDialog, QApplication, QMessageBox
from shapely.geometry import Polygon, Point, LineString
from shapely.affinity import translate
from shapely import STRtree
from shapely.validation import explain_validity


class DrawingWidget(QWidget):
    def __init__(self, parent=None):
        super(DrawingWidget, self).__init__(parent)
        self.current_polygon = None
        self.polygons = []
        self.labels = {}

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if not self.current_polygon:
                self.current_polygon = QPolygonF()
            self.current_polygon.append(event.pos())
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Define the spacing between the polygon and label
        spacing = 10

        # Draw the completed polygons and their labels
        for i, polygon in enumerate(self.polygons):
            painter.setPen(QPen(Qt.green, 2))
            painter.setBrush(QBrush(Qt.green, Qt.BDiagPattern))
            painter.drawPolygon(QPolygonF(polygon))

            # Draw the label beside the polygon
            if i in self.labels:
                label = self.labels[i]
                top_left = self.calculate_polygon_top_left(polygon)
                label_position = QPointF(top_left.x(), top_left.y() - spacing)
                painter.setPen(QPen(Qt.green))
                painter.setFont(QFont("Arial", 10))
                painter.drawText(label_position, label)

        # Draw the currently drawn polygon
        if self.current_polygon:
            painter.setPen(QPen(Qt.red, 2))
            painter.drawPolyline(QPolygonF(self.current_polygon))

    def calculate_polygon_top_left(self, polygon):
        x_min = min(point.x() for point in polygon)
        y_min = min(point.y() for point in polygon)
        return QPointF(x_min, y_min)

    def complete_polygon(self):
        if self.current_polygon:
            # Convert the current polygon to Shapely's Polygon object
            points = [(point.x(), point.y()) for point in self.current_polygon]
            polygon = Polygon(points)

            # Check if the polygon is self-intersecting
            if polygon.is_valid and polygon.is_simple:
                self.polygons.append(self.current_polygon)
                self.current_polygon = None
                self.update()

                # Prompt the user for a label
                label, ok = QInputDialog.getText(
                    QApplication.activeWindow(), "Polygon Label", "Enter label for the polygon:"
                )
                if ok and label:
                    polygon_index = len(self.polygons) - 1
                    self.labels[polygon_index] = label
            else:
                QMessageBox.warning(
                    self,
                    "Invalid Polygon",
                    "Please redraw the polygon with non-intersecting lines.",
                )
                self.current_polygon = None  # Clear the current polygon
                self.update()

    def has_self_intersection(self):
        # Get the points of the current polygon
        points = [(point.x(), point.y()) for point in self.current_polygon]

        # Create the polygon object
        polygon = Polygon(points)

        # Get the polygon segments
        segments = []
        for i in range(len(points) - 1):
            segment = LineString([points[i], points[i + 1]])
            segments.append(segment)
        segment = LineString([points[-1], points[0]])
        segments.append(segment)

        # Build the STRtree index
        tree = STRtree(segments)

        # Check for intersections
        for i in range(len(segments)):
            segment = segments[i]
            intersection_candidates = tree.query(segment)

            # Check if any intersection point lies on another segment
            for candidate in intersection_candidates:
                if candidate != segment and candidate != segments[(i + 1) % len(segments)]:
                    if segment.intersects(candidate):
                        return True

        return False
