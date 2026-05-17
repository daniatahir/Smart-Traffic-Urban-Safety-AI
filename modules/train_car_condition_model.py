from sklearn.tree import DecisionTreeClassifier
import joblib
import numpy as np

# X = [Number of Contours, Estimated Cost, Damage Ratio]
X = [
    [2, 5000, 0.005],   # Good
    [5, 15000, 0.02],   # Good
    [10, 30000, 0.05],  # Average
    [15, 50000, 0.07],  # Average
    [25, 80000, 0.12],  # Poor
    [40, 150000, 0.25]  # Poor
]

y = ["Good", "Good", "Average", "Average", "Poor", "Poor"]

model = DecisionTreeClassifier(max_depth=5)
model.fit(X, y)

joblib.dump(model, "models/car_condition_dt.pkl")
print("✅ Model trained with synchronized features!")