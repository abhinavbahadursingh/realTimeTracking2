import cv2
import numpy as np
import threading
import time
from ultralytics import YOLO
import vehicleData
import speedData

# Load YOLO model on GPU
model = YOLO("yolo11n.pt")

# Open video file
cap = cv2.VideoCapture(r'E:\Projects\Hacknovate6\realtimne\real-time\realTimeTracking\Data\Video\yadav_chai.mp4')

# Reduce video resolution for faster processing
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) * 0.5)
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) * 0.5)
fps = cap.get(cv2.CAP_PROP_FPS) or 30

# Frame skipping
frame_skip = 3
frame_count = 0

# Main loop for video processing
# Main loop for video processing
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1
    if frame_count % frame_skip != 0:
        continue

    # Resize frame for performance
    frame = cv2.resize(frame, (frame_width, frame_height), interpolation=cv2.INTER_AREA)

    # Run YOLO model on GPU
    results = model.track(frame, persist=True)

    # Process detections
    if results and results[0].boxes is not None:
        for i, box in enumerate(results[0].boxes.xyxy.cpu().numpy()):
            x1, y1, x2, y2 = map(int, box)
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2  # Object center

            # Ensure we get all track IDs correctly
            if results[0].boxes.id is not None and i < len(results[0].boxes.id):
                track_id = int(results[0].boxes.id[i].item())
            else:
                track_id = None  # If no ID is assigned

            if track_id is not None:
                # Example: Assuming detected objects are vehicles
                vehicleData.track_vehicle(track_id, cx, cy, "Car", x1, y1, x2, y2)

            # Draw bounding box on the frame
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

    cv2.imshow("YOLO Object Tracking", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
