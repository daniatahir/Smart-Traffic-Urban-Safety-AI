import cv2
import math
import tempfile
import numpy as np
from ultralytics import YOLO

# Load YOLOv8 - 'n' is fast, 's' is more accurate
model = YOLO("yolov8n.pt")

def center(box):
    return (int((box[0] + box[2]) / 2), int((box[1] + box[3]) / 2))

def calculate_speed(p1, p2, fps):
    # Euclidean distance in pixels
    dist = math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)
    return dist * fps

def analyze_video(video_file):
    temp_video = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    temp_video.write(video_file.read())
    temp_video.close()

    cap = cv2.VideoCapture(temp_video.name)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    
    track_history = {} # Stores previous centers: {id: (x, y)}
    total_vehicles_detected = set()
    min_distance = float('inf')
    final_risk = "LOW"
    reasons_set = set()
    speed_history = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break

        # Using .track() maintains ID across frames
        results = model.track(frame, persist=True, conf=0.3, classes=[2,3,5,7], verbose=False)
        
        if results[0].boxes.id is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy()
            ids = results[0].boxes.id.int().cpu().numpy()
            
            frame_speeds = []
            current_centers = {}

            for box, obj_id in zip(boxes, ids):
                c = center(box)
                current_centers[obj_id] = c
                total_vehicles_detected.add(obj_id)

                # 1. SPEED CALCULATION (Temporal)
                if obj_id in track_history:
                    speed = calculate_speed(c, track_history[obj_id], fps)
                    frame_speeds.append(speed)
                    if speed > 500: # Threshold for 'reckless' pixel speed
                        final_risk = "HIGH"
                        reasons_set.add("High speed / Reckless driving")

                # 2. PROXIMITY DETECTION (Inter-object)
                for other_id, other_center in current_centers.items():
                    if obj_id != other_id:
                        d = math.sqrt((c[0]-other_center[0])**2 + (c[1]-other_center[1])**2)
                        if d < min_distance: min_distance = d
                        
                        # Risk Logic
                        if d < 100: 
                            final_risk = "HIGH"
                            reasons_set.add("Extreme tailgating / Near collision")
                        elif d < 180 and final_risk != "HIGH":
                            final_risk = "MEDIUM"
                            reasons_set.add("Congested traffic flow")

            track_history = current_centers
            if frame_speeds:
                speed_history.append(sum(frame_speeds)/len(frame_speeds))

    cap.release()
    return {
        "Average Vehicles": len(total_vehicles_detected),
        "Minimum Distance (pixels)": int(min_distance) if min_distance != float('inf') else 0,
        "Accident Risk Level": final_risk,
        "Reasons": list(reasons_set),
        "Speed History": speed_history
    }