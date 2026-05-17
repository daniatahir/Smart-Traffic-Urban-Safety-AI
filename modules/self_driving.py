import cv2
import time
from ultralytics import YOLO
from modules.voice_engine import play_warning

# Purani line: def run_self_driving_ai(video_path, st_frame):
# Nayi line (In sab ko accept karne ke liye):

def run_self_driving_ai(video_path, st_frame, alert_st, line_pos, dash_ignore, f_skip):
    import cv2
    import time
    from ultralytics import YOLO
    from modules.voice_engine import play_warning # ya trigger_voice jo bhi aapne rakha hai

    model = YOLO('yolov8n.pt')
    cap = cv2.VideoCapture(video_path)
    last_alert = 0
    frame_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break

        frame_count += 1
        # Frame skipping logic
        if frame_count % f_skip != 0:
            st_frame.image(frame, channels="BGR", use_container_width=True)
            continue

        h, w, _ = frame.shape
        # YOLO detection on resized frame for speed
        results = model.track(frame, persist=True, classes=[0, 2, 3, 7], conf=0.3, verbose=False)
        annotated_frame = results[0].plot()

        # Dynamic zones based on sliders
        d_start = int(h * line_pos)
        d_end = int(h * dash_ignore)

        # Draw Zone on screen
        #cv2.rectangle(annotated_frame, (0, d_start), (w, d_end), (0, 255, 255), 2)

        danger_detected = False
        if results[0].boxes:
            for box in results[0].boxes.xyxy.cpu().numpy():
                y_bottom = box[3]
                
                # Proximity Logic
                if d_start < y_bottom < d_end:
                    danger_detected = True
                    if time.time() - last_alert > 5:
                        alert_st.error("⚠️ OBJECT TOO CLOSE!")
                        # Voice engine call
                        from modules.voice_engine import play_warning
                        play_warning("Warning! Object detected.")
                        last_alert = time.time()

        if not danger_detected:
            alert_st.empty()

        st_frame.image(annotated_frame, channels="BGR", use_container_width=True)

    cap.release()