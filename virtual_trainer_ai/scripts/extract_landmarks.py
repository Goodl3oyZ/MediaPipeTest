import os
import numpy as np
import cv2
import mediapipe as mp

# กำหนด path สำหรับโฟลเดอร์วิดีโอ input และโฟลเดอร์ข้อมูล output
VIDEOS_DIR = os.path.join(os.path.dirname(__file__), '..', 'videos')
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

# สร้าง MediaPipe Pose สำหรับตรวจจับจุด landmark ในวิดีโอ (โหมดวิดีโอ ไม่ใช่ภาพนิ่ง)
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=False)

# เตรียม list สำหรับเก็บข้อมูล landmark (X) และ label (y)
X, y = [], []

# วนลูปแต่ละ label (ชื่อท่าออกกำลังกาย = ชื่อโฟลเดอร์ย่อยใน videos/)
for label in os.listdir(VIDEOS_DIR):
    label_dir = os.path.join(VIDEOS_DIR, label)
    if not os.path.isdir(label_dir):
        continue  # ข้ามถ้าไม่ใช่โฟลเดอร์
    print(f"📂 กำลังประมวลผล label: {label}")
    # วนลูปแต่ละไฟล์วิดีโอในโฟลเดอร์ label
    for video_file in os.listdir(label_dir):
        if not video_file.lower().endswith(('.mp4', '.avi', '.mov')):
            continue  # ข้ามไฟล์ที่ไม่ใช่วิดีโอ
        print(f"  🎞️ วิดีโอ: {video_file}")
        cap = cv2.VideoCapture(os.path.join(label_dir, video_file))
        frame_count = 0
        # วนลูปอ่านทีละเฟรมจากวิดีโอ
        while True:
            ret, frame = cap.read()
            if not ret:
                break  # จบวิดีโอ
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # แปลงเป็น RGB สำหรับ MediaPipe
            results = pose.process(frame_rgb)  # ตรวจจับ landmark
            # เก็บเฉพาะเฟรมที่ตรวจจับ landmark ได้
            if results.pose_landmarks:
                # ดึงค่าจุด landmark (x, y, z, visibility) ทุกจุด แล้ว flatten เป็นเวกเตอร์เดียว
                landmarks = np.array([[lm.x, lm.y, lm.z, lm.visibility] for lm in results.pose_landmarks.landmark]).flatten()
                X.append(landmarks)
                y.append(label)
                frame_count += 1
        print(f"     ✅ เก็บได้ {frame_count} frame")
        cap.release()  # ปิดไฟล์วิดีโอหลังประมวลผลเสร็จ

# แปลง list เป็น numpy array เพื่อประสิทธิภาพและความเข้ากันกับ ML
X = np.array(X)
y = np.array(y)

# ตรวจสอบว่ามีโฟลเดอร์ data หรือยัง ถ้ายังไม่มีให้สร้างใหม่
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
# บันทึกข้อมูล feature (X) และ label (y) เป็นไฟล์ .npy สำหรับใช้กับ ML ต่อไป
np.save(os.path.join(DATA_DIR, 'X.npy'), X)
np.save(os.path.join(DATA_DIR, 'y.npy'), y)
print(f"Saved {X.shape[0]} samples to data/") 