import cv2
import numpy as np
import pickle

cap = cv2.VideoCapture("carpark.mp4")

try:
    with open("polygon_points.pkl", 'rb') as f:
        polygons = pickle.load(f)
except:
    polygons = []

points = []
drawing_polygon = False

def draw_polygons(frame, polygons):
    for polygon in polygons:
        points_array = np.array(polygon, np.int32).reshape((-1, 1, 2))
        frame = cv2.polylines(frame, [points_array], isClosed=True, color=(0, 255, 0), thickness=2)
    return frame

def save_polygons(polygons):
    with open("polygon_points.pkl", 'wb') as f:
        pickle.dump(polygons, f)

def complete_polygon():
    global points, drawing_polygon
    if drawing_polygon and len(points) >= 3:
        polygons.append(points)
        points = []
        drawing_polygon = False

def mouse_callback(event, x, y, flags, param):
    global points, drawing_polygon

    if event == cv2.EVENT_LBUTTONDOWN:
        if not drawing_polygon:
            points = []
            drawing_polygon = True
        points.append((x, y))
    elif event == cv2.EVENT_RBUTTONDOWN:
        if drawing_polygon:
            points = []
            drawing_polygon = False
        else:
            for i, polygon in enumerate(polygons):
                if cv2.pointPolygonTest(np.array(polygon), (x, y), False) >= 0:
                    polygons.pop(i)
                    break

while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.resize(frame, (720, 480))

    frame = draw_polygons(frame, polygons)

    if drawing_polygon and len(points) > 0:
        cv2.polylines(frame, [np.array(points)], isClosed=False, color=(0, 255, 0), thickness=2)

    cv2.imshow("Frame", frame)

    cv2.setMouseCallback("Frame", mouse_callback)

    key = cv2.waitKey(1) & 0xFF

    if key == 27:  # Press 'Escape' to quit
        break
    elif key == ord("s"):
        save_polygons(polygons)
        print("Polygon points saved to 'polygon_points.pkl'")
    elif key == ord("c"):
        complete_polygon()

cap.release()
cv2.destroyAllWindows()