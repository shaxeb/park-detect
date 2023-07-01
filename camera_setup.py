import json
import sqlite3
import sys

import cv2
import numpy as np


polygons = []
labels = {}


# Create a SQLite3 database and a table to store camera data
conn = sqlite3.connect("assets/database.db")
cursor = conn.cursor()
cursor.execute(
    "CREATE TABLE IF NOT EXISTS cameras (name TEXT, ip TEXT PRIMARY KEY, polygons TEXT, labels TEXT)")


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


def draw_polygon_temp(frame, points):
    """Draws the temporary polygon while the user is drawing it"""
    if len(points) > 0:
        cv2.polylines(frame, [np.array(points)],
                      isClosed=False, color=(0, 255, 0), thickness=2)


def display_status(frame, is_playing):
    """Displays the play/pause status on the frame"""
    status_text = "Playing" if is_playing else "Paused"
    status_position = (20, 40)
    cv2.putText(frame, f"Status: {status_text}", status_position,
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2, cv2.LINE_AA)


def save_data(data):
    """Saves the data to the SQLite3 database"""
    for camera_name, database in data["cameras"].items():
        polygons = json.dumps(database["polygons"])
        labels = json.dumps(database["labels"])
        cursor.execute("INSERT OR REPLACE INTO cameras (name, ip, polygons, labels) VALUES (?, ?, ?, ?)",
                       (camera_name, database["camera_ip"], polygons, labels))
    conn.commit()


def complete_polygon(label):
    """Completes the current polygon being drawn, adds it to the list of polygons, and saves the label"""
    global points, drawing_polygon
    # Minimum 3 points required to form a polygon
    if drawing_polygon and len(points) >= 3:
        polygons.append(points)
        labels[len(polygons) - 1] = label
        points = []
        drawing_polygon = False

        # Get the current frame
        _, frame = cap.read()

        # Draw the stored polygons and labels on the frame
        frame = draw_polygons(frame, polygons, labels)

        # Get the label position of the completed polygon
        if len(polygons) > 0:
            label_position = (polygons[-1][0][0], polygons[-1][0][1] - 10)

            # Update the label of the last drawn polygon on the frame
            if str(len(polygons) - 1) in labels and labels[str(len(polygons) - 1)]:
                label = labels[str(len(polygons) - 1)]
                cv2.putText(frame, label, label_position,
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)

        cv2.imshow("Frame", frame)  # Display the updated frame

        # Save the data for the selected camera
        selected_camera["polygons"] = polygons
        selected_camera["labels"] = labels



def delete_last_polygon():
    if len(polygons) > 0:
        polygons.pop()
        last_polygon_label = str(len(polygons))
        if last_polygon_label in labels:
            labels.pop(last_polygon_label)
            # Remove the corresponding entry from the database using the camera IP as the key
            if selected_camera["camera_ip"] in data["cameras"]:
                camera_data = data["cameras"][selected_camera["camera_ip"]]
                if last_polygon_label in camera_data["polygons"]:
                    del camera_data["polygons"][last_polygon_label]
                if last_polygon_label in camera_data["labels"]:
                    del camera_data["labels"][last_polygon_label]

def delete_all_polygons():
    polygons.clear()
    labels.clear()
    # Check if the selected_camera variable is properly initialized
    if "camera_ip" in selected_camera:
        camera_ip = selected_camera["camera_ip"]
        # Remove all entries from the database using the camera IP as the key
        if camera_ip in data["cameras"]:
            camera_data = data["cameras"][camera_ip]
            camera_data["polygons"].clear()
            camera_data["labels"].clear()


def mouse_callback(event, x, y, flags, param):
    """Callback function for mouse events"""
    global points, drawing_polygon, is_playing

    if is_playing:
        return

    if event == cv2.EVENT_LBUTTONDOWN:
        if not drawing_polygon:
            points = []  # Start a new polygon
            drawing_polygon = True
        points.append((x, y))  # Add the clicked point to the current polygon


def play_pause_video():
    """Toggles the play/pause state of the video"""
    global is_playing
    is_playing = not is_playing


# Variable to track the play/pause state of the video
is_playing = True


try:
    cursor.execute("SELECT * FROM cameras")
    rows = cursor.fetchall()
    data = {"cameras": {}}
    for row in rows:
        camera_name, camera_ip, polygons, labels = row
        data["cameras"][camera_name] = {
            "camera_ip": camera_ip,
            "polygons": json.loads(polygons),
            "labels": json.loads(labels)
        }
except sqlite3.Error:
    # If the table doesn't exist or failed to load, start with empty data
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

    # Check if a camera with the same IP address already exists in the database
    if any(camera_data["camera_ip"] == camera_ip for camera_data in data["cameras"].values()):
        print("A camera with the same IP address already exists.")
        print("Enter 1 to select the existing camera or enter 2 to add a different one:")
        selection_option = int(input())

        if selection_option == 1:
            # Find the existing camera with the same IP address
            selected_camera = next((camera_data for camera_data in data["cameras"].values() if camera_data["camera_ip"] == camera_ip), None)
            print("Existing camera selected.")
        else:
            # Add a different camera with a different IP address
            data["cameras"][camera_name] = {
                "camera_ip": camera_ip,
                "polygons": [],
                "labels": {}
            }
            selected_camera = data["cameras"][camera_name]
            print("New camera added successfully!")
    else:
        # Add the new camera to the data
        data["cameras"][camera_name] = {
            "camera_ip": camera_ip,
            "polygons": [],
            "labels": {}
        }
        selected_camera = data["cameras"][camera_name]
        print("New camera added successfully!")


    print("Select an option:")
    print("Enter 1 to annotate the newly added camera")
    print("Enter 2 to exit")

    annotation_option = int(input())

    if annotation_option == 1:
        # Check if a camera with the same IP address already exists in the database
        existing_camera = next((camera_data for camera_data in data["cameras"].values() if camera_data["camera_ip"] == camera_ip), None)

        if existing_camera:
            # Use the existing camera data
            selected_camera = existing_camera
            selected_camera_name = next((camera_name for camera_name, camera_data in data["cameras"].items() if camera_data == existing_camera), None)
            print("Existing camera selected.")
        else:
            # Load the newly added camera for annotation
            print("Annotating camera:", camera_name)
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
            if is_playing:
                success, frame = cap.read()
                if not success:
                    break

            # Resize the frame for better display
            frame = cv2.resize(frame, (720, 480))

            # Draw the stored polygons and labels on the frame
            frame = draw_polygons(frame, polygons, labels)

            if drawing_polygon and len(points) > 0:
                draw_polygon_temp(frame, points)
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
                # Update the labels on the frame
                frame = draw_polygons(frame, polygons, labels)
                cv2.imshow("Frame", frame)  # Display the updated frame
                # Save the data for the selected camera
                selected_camera["polygons"] = polygons
                selected_camera["labels"] = labels
                save_data(data)
            elif key == ord("d"):
                delete_last_polygon()  # Delete the last drawn polygon
                # Update the labels on the frame
                frame = draw_polygons(frame, polygons, labels)
                cv2.imshow("Frame", frame)  # Display the updated frame
                # Save the data for the selected camera
                selected_camera["polygons"] = polygons
                selected_camera["labels"] = labels
                save_data(data)
            elif key == ord("x"):
                delete_all_polygons()  # Delete all polygons
                # Update the labels on the frame
                frame = draw_polygons(frame, polygons, labels)
                cv2.imshow("Frame", frame)  # Display the updated frame
                # Save the data for the selected camera
                selected_camera["polygons"] = polygons
                selected_camera["labels"] = labels
                save_data(data)
            elif key == ord(" "):
                is_playing = not is_playing  # Toggle play/pause state

        cap.release()
        cv2.destroyAllWindows()
        # Close the SQLite3 connection
        conn.close()
        sys.exit(0)

    elif annotation_option == 2:
        print("Exiting the program.")
        # Close the SQLite3 connection
        conn.close()
        sys.exit(0)


if option == 1:
    print("Select a camera to annotate:")
    camera_names = list(data["cameras"].keys())
    for i, name in enumerate(camera_names):
        print(f"Enter {i+1} for {name}")

    camera_select = int(input())
    selected_camera_name = camera_names[camera_select - 1]
    selected_camera = data["cameras"][selected_camera_name]

    # Save the camera IP in the selected camera dictionary
    selected_camera["camera_ip"] = camera_ip

    # Load polygons and labels for annotation
    polygons = selected_camera["polygons"]
    labels = selected_camera["labels"]

    print('Draw a polygon using your mouse and then label it')
    cap = cv2.VideoCapture(camera_ip)

    points = []  # Stores the points of the current polygon being drawn
    drawing_polygon = False  # Flag to indicate if a polygon is being drawn or not

    while True:
        if is_playing:
            success, frame = cap.read()
            if not success:
                break

        # Resize the frame for better display
        frame = cv2.resize(frame, (720, 480))

        # Draw the stored polygons and labels on the frame
        frame = draw_polygons(frame, polygons, labels)

        if drawing_polygon and len(points) > 0:
            draw_polygon_temp(frame, points)
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
            # Update the labels on the frame
            frame = draw_polygons(frame, polygons, labels)
            cv2.imshow("Frame", frame)  # Display the updated frame
            # Update the data for the selected camera
            selected_camera["polygons"] = polygons
            selected_camera["labels"] = labels
            save_data(data)
        elif key == ord("d"):
            delete_last_polygon()  # Delete the last drawn polygon
            # Update the labels on the frame
            frame = draw_polygons(frame, polygons, labels)
            cv2.imshow("Frame", frame)  # Display the updated frame
            # Save the data for the selected camera
            selected_camera["polygons"] = polygons
            selected_camera["labels"] = labels
            save_data(data)
        elif key == ord("x"):
            delete_all_polygons()  # Delete all polygons
            # Update the labels on the frame
            frame = draw_polygons(frame, polygons, labels)
            cv2.imshow("Frame", frame)  # Display the updated frame
            # Save the data for the selected camera
            selected_camera["polygons"] = polygons
            selected_camera["labels"] = labels
            save_data(data)
        elif key == ord(" "):
            is_playing = not is_playing  # Toggle play/pause state

    cap.release()
    cv2.destroyAllWindows()
    # Close the SQLite3 connection
    conn.close()
