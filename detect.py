import json
import cv2
import numpy as np
import torch

def mouse_callback(event, x, y, flags, param):
    """Callback function for mouse events"""
    if event == cv2.EVENT_MOUSEMOVE:
        colorsBGR = [x, y]  # Get the coordinates of the mouse cursor
        print(colorsBGR)

# Load camera IP, polygons, and labels from file
with open("assets/data.json", 'r') as f:
    data = json.load(f)

camera_names = list(data["cameras"].keys())
if len(camera_names) == 0:
    print("No cameras available. Please add a camera to the JSON database.")
    exit()

print("Select a camera:")
for i, name in enumerate(camera_names):
    print(f"Enter {i+1} for {name}")

camera_select = int(input())
selected_camera_name = camera_names[camera_select - 1]
selected_camera = data["cameras"][selected_camera_name]
camera_ip = selected_camera["camera_ip"]
polygons = selected_camera["polygons"]
labels = selected_camera["labels"]

# Convert the label keys to integers
labels = {int(k): v for k, v in labels.items()}

cv2.namedWindow('FRAME')
cv2.setMouseCallback('FRAME', mouse_callback)

model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)  # Load the YOLOv5 model

cap = cv2.VideoCapture(camera_ip)  # Open the video stream for capturing frames

while True:
    ret, frame = cap.read()  # Read a frame from the video
    if not ret:
        break

    # Resize the frame for better display
    frame = cv2.resize(frame, (720, 480))

    # Perform object detection on the frame using YOLOv5
    results = model(frame)

    car_count = 0
    for index, row in results.pandas().xyxy[0].iterrows():
        x1 = int(row['xmin'])
        y1 = int(row['ymin'])
        x2 = int(row['xmax'])
        y2 = int(row['ymax'])
        d = row['name']
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2
        if 'car' in d:
            for area in polygons:
                if cv2.pointPolygonTest(np.array(area, np.int32), (cx, cy), False) >= 0:
                    # Draw bounding box around the car
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
                    car_count += 1

    for i, area in enumerate(polygons):
        cv2.polylines(frame, [np.array(area, np.int32)], True, (0, 255, 0), 2)  # Draw the defined areas
        if i in labels:
            label = labels[i]
            label_position = (area[0][0], area[0][1] - 10)
            cv2.putText(frame, label, label_position, cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)

    cv2.putText(frame, str(car_count), (82, 69), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)  # Add car count to the frame

    cv2.imshow("FRAME", frame)  # Display the frame

    if cv2.waitKey(1) & 0xFF == 27:  # Press 'Escape' to quit the program
        break

cap.release()  # Release the video capture
cv2.destroyAllWindows()  # Close all windows
