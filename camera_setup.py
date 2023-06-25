import json
import cv2
import sys
import numpy as np

def draw_polygons(frame, polygons, labels):
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
    return frame

def save_data(data):
    """Saves the data to a file"""
    with open("assets/data.json", 'w') as f:
        json.dump(data, f)

def complete_polygon(label):
    """Completes the current polygon being drawn, adds it to the list of polygons, and saves the label"""
    global points, drawing_polygon
    # Minimum 3 points required to form a polygon
    if drawing_polygon and len(points) >= 3:
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

try:
    with open("assets/data.json", 'r') as f:
        data = json.load(f)
        # Remove unused "polygons" and "labels"
        data.pop("polygons", None)
        data.pop("labels", None)
        # Convert label keys to integers
        data["cameras"] = {
            camera_name: {
                "camera_ip": camera_data["camera_ip"],
                "polygons": camera_data.get("polygons", []),
                "labels": {str(key): value for key, value in camera_data.get("labels", {}).items()}
            }
            for camera_name, camera_data in data["cameras"].items()
        }

except (FileNotFoundError, json.JSONDecodeError):
    # If file doesn't exist or failed to load, start with empty data
    data = {"cameras": {}}

# Prompt the user to select an option
print('Select your option:')
print('Enter 1 to load previously used cameras, polygons, and labels')
print('Enter 2 to add a new camera and annotate polygons')
option = int(input())

if option == 1:
    if not data["cameras"]:
        print("No cameras available. Add a new camera to annotate.")
        option = 2

if option == 2:
    print("Enter a name for the new camera:")
    camera_name = str(input())
    print("Enter the IP address of the new camera:")
    camera_ip = str(input())

    # Add the new camera to the data
    data["cameras"][camera_name] = {
        "camera_ip": camera_ip,
        "polygons": [],
        "labels": {}
    }

    # Save the updated data to the file
    with open("assets/data.json", 'w') as f:
        json.dump(data, f)

    print("New camera added successfully!")

    print("Select an option:")
    print("Enter 1 to annotate the newly added camera")
    print("Enter 2 to exit")

    annotation_option = int(input())

    if annotation_option == 1:
        # Load the newly added camera for annotation
        selected_camera_name = camera_name
        selected_camera = data["cameras"][selected_camera_name]

        # Load camera IP and polygons for annotation
        camera_ip = selected_camera["camera_ip"]
        polygons = selected_camera["polygons"]
        labels = selected_camera["labels"]

        print('Draw a polygon using your mouse and then label it')
        cap = cv2.VideoCapture(camera_ip)

        points = []  # Stores the points of the current polygon being drawn
        drawing_polygon = False  # Flag to indicate if a polygon is being drawn or not

        while True:
            success, frame = cap.read()
            if not success:
                break

            # Resize the frame for better display
            frame = cv2.resize(frame, (720, 480))

            # Draw the stored polygons and labels on the frame
            frame = draw_polygons(frame, polygons)

            # Draw the labels on the frame
            for label, points in labels.items():
                for point in points:
                    cv2.putText(frame, label, tuple(point), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)


            if drawing_polygon and len(points) > 0:
                cv2.polylines(frame, [np.array(points)],
                              isClosed=False, color=(0, 255, 0), thickness=2)
                # Draw the current polygon being drawn on the frame

            cv2.imshow("Frame", frame)  # Display the frame

            # Set the mouse callback function for the frame
            cv2.setMouseCallback("Frame", mouse_callback)

            key = cv2.waitKey(1) & 0xFF

            if key == 27:  # Press 'Escape' to quit the program
                break
            elif key == ord("s"):
                # Prompt the user to enter a label
                label = input("Enter a label for the polygon: ")
                # Complete the current polygon being drawn and save the label
                complete_polygon(label)
                # Save the data for the selected camera
                selected_camera["polygons"] = polygons
                selected_camera["labels"] = labels
                save_data(data)
            elif key == ord("d"):
                delete_last_polygon()  # Delete the last drawn polygon
                # Save the data for the selected camera
                selected_camera["polygons"] = polygons
                selected_camera["labels"] = labels
                save_data(data)
            elif key == ord("x"):
                delete_all_polygons()  # Delete all polygons
                # Save the data for the selected camera
                selected_camera["polygons"] = polygons
                selected_camera["labels"] = labels
                save_data(data)

        cap.release()
        cv2.destroyAllWindows()

    elif annotation_option == 2:
        print("Exiting the program.")
        sys.exit(0)


if option == 1:
    print("Select a camera to annotate:")
    camera_names = list(data["cameras"].keys())
    for i, name in enumerate(camera_names):
        print(f"Enter {i+1} for {name}")

    camera_select = int(input())
    selected_camera_name = camera_names[camera_select - 1]
    selected_camera = data["cameras"][selected_camera_name]

    # Load camera IP and polygons for annotation
    camera_ip = selected_camera["camera_ip"]
    polygons = selected_camera["polygons"]
    labels = selected_camera["labels"]

    print('Draw a polygon using your mouse and then label it')
    cap = cv2.VideoCapture(camera_ip)

    points = []  # Stores the points of the current polygon being drawn
    drawing_polygon = False  # Flag to indicate if a polygon is being drawn or not

    while True:
        success, frame = cap.read()
        if not success:
            break

        # Resize the frame for better display
        frame = cv2.resize(frame, (720, 480))

        # Draw the stored polygons and labels on the frame
        frame = draw_polygons(frame, polygons, labels)

        if drawing_polygon and len(points) > 0:
            cv2.polylines(frame, [np.array(points)],
                          isClosed=False, color=(0, 255, 0), thickness=2)
            # Draw the current polygon being drawn on the frame

        cv2.imshow("Frame", frame)  # Display the frame

        # Set the mouse callback function for the frame
        cv2.setMouseCallback("Frame", mouse_callback)

        key = cv2.waitKey(1) & 0xFF

        if key == 27:  # Press 'Escape' to quit the program
            break
        elif key == ord("s"):
            # Prompt the user to enter a label
            label = input("Enter a label for the polygon: ")
            # Complete the current polygon being drawn and save the label
            complete_polygon(label)
            # Save the data for the selected camera
            selected_camera["polygons"] = polygons
            selected_camera["labels"] = labels
            save_data(data)
        elif key == ord("d"):
            delete_last_polygon()  # Delete the last drawn polygon
            # Save the data for the selected camera
            selected_camera["polygons"] = polygons
            selected_camera["labels"] = labels
            save_data(data)
        elif key == ord("x"):
            delete_all_polygons()  # Delete all polygons
            # Save the data for the selected camera
            selected_camera["polygons"] = polygons
            selected_camera["labels"] = labels
            save_data(data)

    cap.release()
    cv2.destroyAllWindows()
