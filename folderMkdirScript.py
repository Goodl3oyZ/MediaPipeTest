import os

# กำหนด path หลักที่ต้องการสร้างโฟลเดอร์ (แก้ไข path ตามโปรเจกต์ของคุณ)
base_path = "virtual_trainer_ai/videos/"

# ลิสต์ท่าออกกำลังกาย (ชื่อโฟลเดอร์)
exercise_labels = [
    "Bench Press",
    "Incline Bench Press",
    "Decline Bench Press",
    "Dumbbell Fly",
    "Chest Dip",
    "Push-up",
    "Pull-up",
    "Chin-up",
    "Lat Pulldown",
    "Seated Row",
    "Bent Over Row",
    "Deadlift",
    "T-bar Row",
    "Face Pull",
    "Overhead Press",
    "Lateral Raise",
    "Front Raise",
    "Rear Delt Fly",
    "Arnold Press",
    "Shrug",
    "Barbell Curl",
    "Dumbbell Curl",
    "Hammer Curl",
    "Triceps Pushdown",
    "Skullcrusher",
    "Triceps Overhead Extension",
    "Preacher Curl",
    "Concentration Curl",
    "Squat",
    "Front Squat",
    "Leg Press",
    "Lunge",
    "Leg Extension",
    "Leg Curl",
    "Romanian Deadlift",
    "Calf Raise",
    "Plank",
    "Hanging Leg Raise",
    "Cable Crunch",
    "Russian Twist",
    "Ab Wheel Rollout",
    "Hip Thrust",
    "Farmer’s Walk",
    "Sled Push",
    "Sled Pull",
    "Battle Rope",
    "Box Jump"
]

for label in exercise_labels:
    # แทนที่อักขระที่ไม่เหมาะสมกับชื่อโฟลเดอร์
    safe_label = label.replace("/", "-").replace("’", "'")
    folder_path = os.path.join(base_path, safe_label)
    os.makedirs(folder_path, exist_ok=True)
    print(f"สร้างโฟลเดอร์: {folder_path}")

print("สร้างโฟลเดอร์ทั้งหมดเรียบร้อยแล้ว")