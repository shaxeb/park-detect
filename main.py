import cv2
import pickle
import torch
import numpy as np

points = []  # A list to store points

def POINTS(event, x, y, flags, param):
    """Callback function for mouse events"""
    if event == cv2.EVENT_MOUSEMOVE:
        colorsBGR = [x, y]  # Get the coordinates of the mouse cursor
        print(colorsBGR)

cv2.namedWindow('FRAME')
cv2.setMouseCallback('FRAME', POINTS)  # Set the mouse callback function for the frame

model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)  # Load the YOLOv5 model

cap = cv2.VideoCapture('carpark.mp4')  # Open the video file for capturing frames
count = 0

with open("polygon_points.pkl", 'rb') as f:
    areas = pickle.load(f)  # Load the stored areas from file

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
            for area in areas:
                results = cv2.pointPolygonTest(np.array(area, np.int32), ((cx, cy)), False)
                if results >= 0:
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)  # Draw bounding box around the car
                    #cv2.putText(frame, str(d), (x1, y1), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)  # Add label
                    list.append([cx])

    for area in areas:
        cv2.polylines(frame, [np.array(area, np.int32)], True, (0, 255, 0), 2)  # Draw the defined areas

    a = len(list)  # Count the number of cars detected within the defined areas
    cv2.putText(frame, str(a), (82, 69), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)  # Add car count to the frame

    cv2.imshow("FRAME", frame)  # Display the frame
    # cv2.setMouseCallback("FRAME", POINTS)  # Set the mouse callback function for the frame

    if cv2.waitKey(1) & 0xFF == 27:  # Press 'Escape' to quit the program
        break

cap.release()  # Release the video capture
cv2.destroyAllWindows()  # Close all windows
