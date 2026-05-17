import cv2
import numpy as np
import joblib

# Load the model
dt_model = joblib.load("models/car_condition_dt.pkl")

def analyze_car_image(image_bytes):
    img = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
    img = cv2.resize(img, (400, 300))

    # Enhance contrast to highlight scratches/dents
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    cl = clahe.apply(l)
    enhanced_img = cv2.merge((cl,a,b))
    enhanced_img = cv2.cvtColor(enhanced_img, cv2.COLOR_LAB2BGR)

    gray = cv2.cvtColor(enhanced_img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150) # Adjusted thresholds

    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    large_contours = [cv2.contourArea(c) for c in contours if cv2.contourArea(c) > 500]

    total_damage_area = sum(large_contours)
    damage_ratio = total_damage_area / (400 * 300)

    # Threshold Logic
    if damage_ratio < 0.01:
        return {"damage_detected": "No", "damage_type": [], "damage_location": [], "condition": "Good", "estimated_cost": 0}

    if damage_ratio < 0.04:
        damage_type, loc, cost = ["Scratch"], ["Surface"], 15000
    elif damage_ratio < 0.08:
        damage_type, loc, cost = ["Dent"], ["Bumper/Door"], 35000
    else:
        damage_type, loc, cost = ["Severe"], ["Multiple Panels"], 85000

    # MATCHING THE TRAINING DATA: [num_parts, cost, severity_ratio]
    features = np.array([[len(large_contours), cost, damage_ratio]])
    predicted_condition = dt_model.predict(features)[0]

    return {
        "damage_detected": "Yes",
        "damage_type": damage_type,
        "damage_location": loc,
        "condition": predicted_condition,
        "estimated_cost": cost
    }