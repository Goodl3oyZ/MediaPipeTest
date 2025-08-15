import cv2
import mediapipe as mp
import numpy as np
import argparse
import os
import math
import json
from datetime import datetime
# --- import core ML/feedback logic ---
from ml_core import calculate_angle, check_squat_form, score_squat_form, predict_exercise_from_video, evaluate_exercise

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

def save_result(user_id, input_file, output_file, label, feedback, reps, summary_path=None):
    # --- ฟังก์ชันบันทึกผลลงไฟล์ user_results.json และ export summary ---
    result = {
        'user_id': user_id,
        'input_file': input_file,
        'output_file': output_file,
        'exercise': label,
        'feedback': feedback,
        'reps': reps,
        'datetime': datetime.now().isoformat(timespec='seconds')
    }
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'user_results.json')
    # โหลดข้อมูลเดิม ถ้ามี
    if os.path.exists(db_path):
        with open(db_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = []
    data.append(result)
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    # export summary เป็นไฟล์แยก (option)
    if summary_path:
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', help='Input video file')
    parser.add_argument('--output', help='Output video file')
    parser.add_argument('--user', help='User ID', default='guest')
    args = parser.parse_args()

    # path พื้นฐาน
    DEFAULT_INPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'videos', 'Squat')
    DEFAULT_OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'results')

    # ถ้าไม่มี input ให้ user เลือกไฟล์
    if not args.input:
        args.input = choose_file("เลือกไฟล์วิดีโอ input:", DEFAULT_INPUT_DIR, ('.mp4', '.avi', '.mov'))
    # ถ้าไม่มี output ให้ตั้งชื่ออัตโนมัติ
    if not args.output:
        basename = os.path.splitext(os.path.basename(args.input))[0]
        args.output = os.path.join(DEFAULT_OUTPUT_DIR, f"{basename}_output.mp4")

    # สร้าง output dir ถ้ายังไม่มี
    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    # --- ใช้ core ML function ---
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(static_image_mode=False)
    cap = cv2.VideoCapture(args.input)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = None
    label = 'Unknown'
    feedback = ''
    total_score = None
    knee_score = None
    back_score = None
    landmarks_sequence = []  # เก็บ landmark ทุกเฟรม

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(frame_rgb)
        if results.pose_landmarks:
            landmarks = np.array([[lm.x, lm.y, lm.z, lm.visibility] for lm in results.pose_landmarks.landmark])
            landmarks_sequence.append(landmarks)
            mp.solutions.drawing_utils.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        if out is None:
            out = cv2.VideoWriter(args.output, fourcc, cap.get(cv2.CAP_PROP_FPS), (frame.shape[1], frame.shape[0]))
        out.write(frame)
    cap.release()
    if out:
        out.release()

    # --- ทำนาย label จาก landmark (ใช้เฟรมแรกที่เจอ pose) ---
    if landmarks_sequence:
        flat_landmarks = landmarks_sequence[0].flatten().reshape(1, -1)
        from ml_core import model
        label = model.predict(flat_landmarks)[0]
        # ประเมินฟอร์ม + นับ rep ด้วย evaluate_exercise (รองรับทุก label)
        result = evaluate_exercise(landmarks_sequence, label)
        feedback = result['form_feedback']
        reps = result['reps']
    else:
        feedback = 'ไม่พบท่าทางในวิดีโอ'
        reps = 0

    # --- export summary เป็น JSON ---
    summary_path = os.path.splitext(args.output)[0] + '_summary.json'
    save_result(args.user, args.input, args.output, label, feedback, reps, summary_path=summary_path)
    print(f'Output saved to {args.output}')
    print(f'Summary saved to {summary_path}')

if __name__ == '__main__':
    main() 