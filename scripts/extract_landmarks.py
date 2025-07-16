import os
import numpy as np
import cv2
import mediapipe as mp

VIDEOS_DIR = os.path.join(os.path.dirname(__file__), '..', 'videos')
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=False)

X, y = [], []

for label in os.listdir(VIDEOS_DIR):
    label_dir = os.path.join(VIDEOS_DIR, label)
    if not os.path.isdir(label_dir):
        continue
    print(f"📂 กำลังประมวลผล label: {label}")
    for video_file in os.listdir(label_dir):
        if not video_file.lower().endswith(('.mp4', '.avi', '.mov')):
            continue
        print(f"  🎞️ วิดีโอ: {video_file}")
        cap = cv2.VideoCapture(os.path.join(label_dir, video_file))
        frame_count = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(frame_rgb)
            if results.pose_landmarks:
                landmarks = np.array([[lm.x, lm.y, lm.z, lm.visibility] for lm in results.pose_landmarks.landmark]).flatten()
                X.append(landmarks)
                y.append(label)
                frame_count += 1
        print(f"     ✅ เก็บได้ {frame_count} frame")
        cap.release()


X = np.array(X)
y = np.array(y)
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
np.save(os.path.join(DATA_DIR, 'X.npy'), X)
np.save(os.path.join(DATA_DIR, 'y.npy'), y)
print(f"Saved {X.shape[0]} samples to data/") 