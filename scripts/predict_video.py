import cv2
import mediapipe as mp
import numpy as np
import joblib
import argparse
import os

# ฟังก์ชันช่วยเลือกไฟล์แบบ interactive (เฉพาะถ้าไม่มี argument)
def choose_file(prompt, folder, exts):
    files = [f for f in os.listdir(folder) if f.lower().endswith(exts)]
    if not files:
        print(f"ไม่พบไฟล์ใน {folder}")
        exit(1)
    print(prompt)
    for i, f in enumerate(files):
        print(f"{i+1}. {f}")
    idx = int(input("เลือกหมายเลขไฟล์: ")) - 1
    return os.path.join(folder, files[idx])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', help='Input video file')
    parser.add_argument('--output', help='Output video file')
    args = parser.parse_args()

    # path พื้นฐาน
    DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
    MODEL_PATH = os.path.join(DATA_DIR, 'exercise_classifier.joblib')
    DEFAULT_INPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'videos', 'Plank')
    DEFAULT_OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'results')

    # โหลดโมเดล
    model = joblib.load(MODEL_PATH)

    # ถ้าไม่มี input ให้ user เลือกไฟล์
    if not args.input:
        args.input = choose_file("เลือกไฟล์วิดีโอ input:", DEFAULT_INPUT_DIR, ('.mp4', '.avi', '.mov'))
    # ถ้าไม่มี output ให้ตั้งชื่ออัตโนมัติ
    if not args.output:
        basename = os.path.splitext(os.path.basename(args.input))[0]
        args.output = os.path.join(DEFAULT_OUTPUT_DIR, f"{basename}_output.mp4")

    # สร้าง output dir ถ้ายังไม่มี
    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    # สร้าง MediaPipe Pose สำหรับตรวจจับท่าทาง (landmark) ในวิดีโอ
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(static_image_mode=False)
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
            mp.solutions.drawing_utils.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        cv2.putText(frame, f'Prediction: {label}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        if out is None:
            out = cv2.VideoWriter(args.output, fourcc, cap.get(cv2.CAP_PROP_FPS), (frame.shape[1], frame.shape[0]))
        out.write(frame)

    cap.release()
    if out:
        out.release()
    print(f'Output saved to {args.output}')

if __name__ == '__main__':
    main() 