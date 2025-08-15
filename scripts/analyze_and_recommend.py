import json
import os
import random

# --- กำหนด mapping เป้าหมาย (goal) -> โปรแกรมฝึก (exercise plan) ---
GOAL_TO_EXERCISES = {
    'ลดพุง': ['Plank', 'Squat'],
    'เพิ่มกล้ามแขน': ['Push-up'],
    'ขาแข็งแรง': ['Squat'],
    'แก้ปวดหลัง': ['Plank'],
}

# --- ฟังก์ชันเลือกโปรแกรมถัดไปตาม goal และผลล่าสุด ---
def recommend_next_exercise(user_id, goal):
    # อ่านผลล่าสุดของ user
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'user_results.json')
    if not os.path.exists(db_path):
        return None, None, 'ยังไม่มีข้อมูลการฝึก'
    with open(db_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    user_data = [d for d in data if d['user_id'] == user_id]
    # ถ้าไม่เคยฝึกเลย แนะนำ exercise แรกของ goal
    exercises = GOAL_TO_EXERCISES.get(goal, [])
    if not exercises:
        return None, None, 'ยังไม่มีโปรแกรมสำหรับเป้าหมายนี้'
    if not user_data:
        next_ex = exercises[0]
    else:
        # ดูว่าทำ exercise ไหนล่าสุด ถ้าทำครบ loop ใหม่
        done = [d['exercise'] for d in user_data if d['exercise'] in exercises]
        for ex in exercises:
            if ex not in done:
                next_ex = ex
                break
        else:
            next_ex = exercises[0]
    # --- เลือกวิดีโอตัวอย่างจากโฟลเดอร์ ---
    video_dir = os.path.join(os.path.dirname(__file__), '..', 'videos', next_ex)
    if not os.path.exists(video_dir):
        return next_ex, None, 'ยังไม่มีวิดีโอตัวอย่าง'
    files = [f for f in os.listdir(video_dir) if f.lower().endswith(('.mp4', '.avi', '.mov'))]
    if not files:
        return next_ex, None, 'ยังไม่มีวิดีโอตัวอย่าง'
    sample_video = random.choice(files)
    return next_ex, os.path.join(video_dir, sample_video), 'แนะนำโปรแกรมถัดไปสำเร็จ'

if __name__ == '__main__':
    # --- รับ user_id และ goal ---
    user_id = input('กรุณากรอกชื่อผู้ใช้: ')
    print('เป้าหมายที่รองรับ:')
    for g in GOAL_TO_EXERCISES:
        print('-', g)
    goal = input('กรุณากรอกเป้าหมาย: ')
    next_ex, video_path, msg = recommend_next_exercise(user_id, goal)
    print('\n--- ผลลัพธ์ ---')
    print('โปรแกรมถัดไป:', next_ex)
    print('วิดีโอตัวอย่าง:', video_path)
    print('สถานะ:', msg) 