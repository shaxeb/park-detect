import pickle
import cv2
import numpy as np
import torch

points = []  # A list to store points

with open("assets/data.pkl", 'rb') as f:
    data = pickle.load(f)  # Load camera IP, polygons, and labels from file

camera_ip = data["camera_ip"]
polygons = data["polygons"]
labels = data["labels"]


def POINTS(event, x, y, flags, param):
    """Callback function for mouse events"""
    if event == cv2.EVENT_MOUSEMOVE:
        colorsBGR = [x, y]  # Get the coordinates of the mouse cursor
        print(colorsBGR)


cv2.namedWindow('FRAME')
cv2.setMouseCallback('FRAME', POINTS)  # Set the mouse callback function for the frame

model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)  # Load the YOLOv5 model

cap = cv2.VideoCapture(camera_ip)  # Open the video stream for capturing frames
count = 0

while True:
    ret, frame = cap.read()  # Read a frame from the video
    if not ret:
        break

    frame = cv2.resize(frame, (720, 480))  # Resize the frame for better display

    results = model(frame)  # Perform object detection on the frame using YOLOv5

    list = []  # A list to store objects detected within the defined areas
    for index, row in results.pandas().xyxy[0].iterrows():
        x1 = int(row['xmin'])
        y1 = int(row['ymin'])
        x2 = int(row['xmax'])
        y2 = int(row['ymax'])
        d = (row['name'])
        cx = int(x1 + x2) // 2
        cy = int(y1 + y2) // 2
        if 'car' in d:
            for area in polygons:
                results = cv2.pointPolygonTest(np.array(area, np.int32), (cx, cy), False)
                if results >= 0:
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)  # Draw bounding box around the car
                    # cv2.putText(frame, str(d), (x1, y1), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)  # Add label
                    list.append([cx])

    for i, area in enumerate(polygons):
        cv2.polylines(frame, [np.array(area, np.int32)], True, (0, 255, 0), 2)  # Draw the defined areas
        if i in labels:
            label = labels[i]
            label_position = (area[0][0], area[0][1] - 10)
            cv2.putText(frame, label, label_position, cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)                                           

    a = len(list)  # Count the number of cars detected within the defined areas
    cv2.putText(frame, str(a), (82, 69), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)  # Add car count to the frame

    cv2.imshow("FRAME", frame)  # Display the frame
    # cv2.setMouseCallback("FRAME", POINTS)  # Set the mouse callback function for the frame

    if cv2.waitKey(1) & 0xFF == 27:  # Press 'Escape' to quit the program
        break

cap.release()  # Release the video capture
cv2.destroyAllWindows()  # Close all windows
