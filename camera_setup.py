import pickle
import cv2
import numpy as np

# Prompt the user to select an option
print('Select your option:')
print('Enter 1 for loading previously used camera IP, polygons, and labels')
print('Enter 2 for entering a new camera IP \n')
ip_select = int(input())

if ip_select == 1:
    try:
        with open("assets/data.pkl", 'rb') as f:
            data = pickle.load(f)  # Load previously saved data from file
    except:
        data = {"camera_ip": "", "polygons": [], "labels": {}}  # If file doesn't exist or failed to load, start with empty data
        print("There's no saved camera IP, Enter a new IP: ")
        data["camera_ip"] = str(input())
        with open("assets/data.pkl", 'wb') as f:
            pickle.dump(data, f)
elif ip_select == 2:
    print("Enter a new IP: ")
    camera_ip = str(input())
    data = {"camera_ip": camera_ip, "polygons": [], "labels": {}}
    with open("assets/data.pkl", 'wb') as f:
        pickle.dump(data, f)

print('Draw a polygon using your mouse and then label it')
cap = cv2.VideoCapture(data["camera_ip"])  # Open the video stream for capturing frames

polygons = data["polygons"]  # Stores the drawn polygons
labels = data["labels"]  # Stores the labels for each polygon

points = []  # Stores the points of the current polygon being drawn
drawing_polygon = False  # Flag to indicate if a polygon is being drawn or not


def draw_polygons(frame, polygons, labels):
    """Draws the stored polygons and labels on the frame"""
    for i, polygon in enumerate(polygons):
        points_array = np.array(polygon, np.int32).reshape((-1, 1, 2))
        frame = cv2.polylines(frame, [points_array], isClosed=True, color=(0, 255, 0), thickness=2)
        if i in labels:
            label = labels[i]
            label_position = (polygon[0][0], polygon[0][1] - 10)
            cv2.putText(frame, label, label_position, cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)
    return frame


def save_data(data):
    """Saves the data to a file"""
    with open("assets/data.pkl", 'wb') as f:
        pickle.dump(data, f)


def complete_polygon(label):
    """Completes the current polygon being drawn, adds it to the list of polygons, and saves the label"""
    global points, drawing_polygon
    if drawing_polygon and len(points) >= 3:  # Minimum 3 points required to form a polygon
        polygons.append(points)
        labels[len(polygons) - 1] = label
        points = []
        drawing_polygon = False


def delete_last_polygon():
    """Deletes the last drawn polygon from the list of polygons"""
    if len(polygons) > 0:
        polygons.pop()
        labels.pop(len(polygons), None)


def delete_all_polygons():
    """Deletes all polygons from the list"""
    polygons.clear()
    labels.clear()


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
                    labels.pop(i, None)
                    break


while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.resize(frame, (720, 480))  # Resize the frame for better display

    frame = draw_polygons(frame, polygons, labels)  # Draw the stored polygons and labels on the frame

    if drawing_polygon and len(points) > 0:
        cv2.polylines(frame, [np.array(points)], isClosed=False, color=(0, 255, 0), thickness=2)
        # Draw the current polygon being drawn on the frame

    cv2.imshow("Frame", frame)  # Display the frame

    cv2.setMouseCallback("Frame", mouse_callback)  # Set the mouse callback function for the frame

    key = cv2.waitKey(1) & 0xFF

    if key == 27:  # Press 'Escape' to quit the program
        break
    elif key == ord("s"):
        label = input("Enter a label for the polygon: ")  # Prompt the user to enter a label
        complete_polygon(label)  # Complete the current polygon being drawn and save the label
        save_data({"camera_ip": data["camera_ip"], "polygons": polygons, "labels": labels})
    elif key == ord("d"):
        delete_last_polygon()  # Delete the last drawn polygon
        save_data({"camera_ip": data["camera_ip"], "polygons": polygons, "labels": labels})
    elif key == ord("x"):
        delete_all_polygons()  # Delete all polygons
        save_data({"camera_ip": data["camera_ip"], "polygons": polygons, "labels": labels})

cap.release()
cv2.destroyAllWindows()
