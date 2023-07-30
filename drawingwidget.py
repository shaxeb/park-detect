import json
import sqlite3

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QBrush, QFont, QPainter, QPen, QPolygonF
from PySide6.QtWidgets import QApplication, QInputDialog, QMessageBox, QWidget
from shapely.geometry import Polygon, LineString
from shapely.validation import explain_validity


class DrawingWidget(QWidget):
    def __init__(self, parent=None):
        super(DrawingWidget, self).__init__(parent)
        self.current_polygon = None
        self.polygons = []
        self.labels = {}
        self.camera_id = None
        self.conn = sqlite3.connect("camera_database.db")
        self.cursor = self.conn.cursor()

    def resizeEvent(self, event):
        # Resize the drawing widget to match the size of its parent
        self.setGeometry(self.parent().rect())
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if not self.current_polygon:
                self.current_polygon = QPolygonF()
            self.current_polygon.append(event.pos())
            self.update()
        elif event.button() == Qt.RightButton:
            if not self.polygons:
                return

            # Check if the right-click position is inside any polygon
            for i, polygon in enumerate(self.polygons):
                if polygon.containsPoint(event.pos(), Qt.OddEvenFill):
                    self.remove_polygon(i)
                    self.update()
                    break

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

    def save_polygon_data(self):
        polygon_data = []
        for i, polygon in enumerate(self.polygons):
            coordinates = [(point.x(), point.y()) for point in polygon]
            label = self.labels.get(i, "")
            polygon_data.append({"coordinates": coordinates, "label": label})

        polygon_data_json = json.dumps(polygon_data)

        self.cursor.execute(
            "UPDATE Cameras SET polygon_data = ? WHERE id = ?", (polygon_data_json, self.camera_id)
        )
        self.conn.commit()

    def complete_polygon(self):
        if not self.current_polygon.isEmpty():
            if self.has_self_intersection():
                QMessageBox.warning(
                    self, "Invalid Polygon", "Please redraw the polygon with non-intersecting lines."
                )
                self.current_polygon = QPolygonF()  # Clear the current polygon
            else:
                self.polygons.append(QPolygonF(self.current_polygon))
                self.current_polygon = QPolygonF()
                self.update()

                # Prompt the user for a label
                label, ok = QInputDialog.getText(
                    QApplication.activeWindow(), "Polygon Label", "Enter label for the polygon:"
                )
                if ok and label:
                    polygon_index = len(self.polygons) - 1
                    self.labels[polygon_index] = label

                    # Save the polygon data to the database
                    self.save_polygon_data()

    def remove_polygon(self, index):
        if index in self.labels:
            del self.labels[index]
        if index < len(self.polygons):
            del self.polygons[index]

            # Save the updated polygon data to the database
            self.save_polygon_data()

    def remove_all_polygons(self):
        self.polygons = []
        self.labels = {}
        self.update()

        # Remove the polygon data from the database
        self.cursor.execute(
            "UPDATE Cameras SET polygon_data = NULL WHERE id = ?", (self.camera_id,)
        )
        self.conn.commit()

    def set_camera_id(self, camera_id):
        self.camera_id = camera_id
        self.load_polygon_data()

    def has_self_intersection(self):
        if not self.current_polygon:
            return False

        # Convert the current polygon to Shapely's Polygon object
        points = [(point.x(), point.y()) for point in self.current_polygon]
        polygon = Polygon(points)

        # Check if the polygon is valid and simple (non-self-intersecting)
        if not polygon.is_valid or not polygon.is_simple:
            explanation = explain_validity(polygon)
            print(f"Warning: Invalid Polygon - {explanation}")
            return True

        # Check for self-intersections by comparing each pair of edges
        edges = polygon.exterior.coords[:-1]
        num_edges = len(edges)
        for i in range(num_edges - 1):
            edge1 = LineString([edges[i], edges[i + 1]])
            for j in range(i + 2, num_edges - 1):
                edge2 = LineString([edges[j], edges[j + 1]])
                if edge1.intersects(edge2):
                    return True

        return False


    def load_polygon_data(self):
        self.polygons = []
        self.labels = {}

        if not self.camera_id:
            return

        # Fetch the polygon data from the database for the current camera
        self.cursor.execute(
            "SELECT polygon_data FROM Cameras WHERE id = ?", (self.camera_id,)
        )
        result = self.cursor.fetchone()
        if result is not None and result[0]:
            polygon_data_json = result[0]
            polygon_data = json.loads(polygon_data_json)

            # Process the fetched polygons
            for polygon in polygon_data:
                label = polygon["label"]
                coordinates = polygon["coordinates"]

                # Convert the list of coordinates to QPointF objects
                points = [QPointF(x, y) for x, y in coordinates]

                # Create a QPolygonF object and add it to the polygons list
                self.polygons.append(QPolygonF(points))
                self.labels[len(self.polygons) - 1] = label

        self.update()
