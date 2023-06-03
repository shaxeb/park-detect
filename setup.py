import cv2
import numpy as np
import pickle

cap = cv2.VideoCapture("carpark.mp4")  # Open the video file for capturing frames

try:
    with open("polygon_points.pkl", 'rb') as f:
        polygons = pickle.load(f)  # Load previously saved polygons from file
except:
    polygons = []  # If file doesn't exist or failed to load, start with an empty list of polygons

points = []  # Stores the points of the current polygon being drawn
drawing_polygon = False  # Flag to indicate if a polygon is being drawn or not

def draw_polygons(frame, polygons):
    """Draws the stored polygons on the frame"""
    for polygon in polygons:
        points_array = np.array(polygon, np.int32).reshape((-1, 1, 2))
        frame = cv2.polylines(frame, [points_array], isClosed=True, color=(0, 255, 0), thickness=2)
    return frame

def save_polygons(polygons):
    """Saves the polygons to a file"""
    with open("polygon_points.pkl", 'wb') as f:
        pickle.dump(polygons, f)

def complete_polygon():
    """Completes the current polygon being drawn and adds it to the list of polygons"""
    global points, drawing_polygon
    if drawing_polygon and len(points) >= 3:  # Minimum 3 points required to form a polygon
        polygons.append(points)
        points = []
        drawing_polygon = False

def delete_last_polygon():
    """Deletes the last drawn polygon from the list of polygons"""
    if len(polygons) > 0:
        polygons.pop()

def delete_all_polygons():
    """Deletes all polygons from the list"""
    polygons.clear()

def mouse_callback(event, x, y, flags, param):
    """Callback function for mouse events"""
    global points, drawing_polygon

    if event == cv2.EVENT_LBUTTONDOWN:
        if not drawing_polygon:
            points = []  # Start a new polygon
            drawing_polygon = True
        points.append((x, y))  # Add the clicked point to the current polygon
    elif event == cv2.EVENT_RBUTTONDOWN:
        if drawing_polygon:
            points = []  # Cancel the current polygon if right-clicked
            drawing_polygon = False
        else:
            # Check if right-clicked point is inside any existing polygon, and remove that polygon
            for i, polygon in enumerate(polygons):
                if cv2.pointPolygonTest(np.array(polygon), (x, y), False) >= 0:
                    polygons.pop(i)
                    break

while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.resize(frame, (720, 480))  # Resize the frame for better display

    frame = draw_polygons(frame, polygons)  # Draw the stored polygons on the frame

    if drawing_polygon and len(points) > 0:
        cv2.polylines(frame, [np.array(points)], isClosed=False, color=(0, 255, 0), thickness=2)
        # Draw the current polygon being drawn on the frame

    cv2.imshow("Frame", frame)  # Display the frame

    cv2.setMouseCallback("Frame", mouse_callback)  # Set the mouse callback function for the frame

    key = cv2.waitKey(1) & 0xFF

    if key == 27:  # Press 'Escape' to quit the program
        break
    elif key == ord("s"):
        save_polygons(polygons)
        print("Polygon points saved to 'polygon_points.pkl'")  # Save the polygons to a file
    elif key == ord("c"):
        complete_polygon()  # Complete the current polygon being drawn
    elif key == ord("d"):
        delete_last_polygon()  # Delete the last drawn polygon
    elif key == ord("a"):
        delete_all_polygons()  # Delete all polygons

cap.release()
cv2.destroyAllWindows()
