import cv2
import mediapipe as mp
import numpy as np
import joblib
import argparse
import os

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=False)

parser = argparse.ArgumentParser()
parser.add_argument('--input', required=True, help='Input video file')
parser.add_argument('--output', required=True, help='Output video file')
args = parser.parse_args()

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
model = joblib.load(os.path.join(DATA_DIR, 'exercise_classifier.joblib'))

cap = cv2.VideoCapture(args.input)
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = None

while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(frame_rgb)
    label = 'Unknown'
    if results.pose_landmarks:
        landmarks = np.array([[lm.x, lm.y, lm.z, lm.visibility] for lm in results.pose_landmarks.landmark]).flatten().reshape(1, -1)
        label = model.predict(landmarks)[0]
        # Draw landmarks
        mp.solutions.drawing_utils.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
    cv2.putText(frame, f'Prediction: {label}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    if out is None:
        out = cv2.VideoWriter(args.output, fourcc, cap.get(cv2.CAP_PROP_FPS), (frame.shape[1], frame.shape[0]))
    out.write(frame)

cap.release()
if out:
    out.release()
print(f'Output saved to {args.output}') 