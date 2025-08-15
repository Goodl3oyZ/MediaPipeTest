# Virtual Trainer AI (Backend)

## 1. ภาพรวมระบบ

Virtual Trainer AI เป็นระบบ backend สำหรับแอปวิเคราะห์ท่าออกกำลังกายจากวิดีโอ โดยใช้ FastAPI + GraphQL + PostgreSQL + Machine Learning (MediaPipe + scikit-learn)

- รองรับผู้ใช้หลายคน (User Management)
- วิเคราะห์วิดีโอด้วย ML และบันทึกผลลงฐานข้อมูล
- Query/Mutation ผ่าน GraphQL API
- ขยายต่อยอดได้ทั้ง Web/Mobile

---

## 2. โครงสร้างโปรเจกต์ (Project Structure)

```
virtual_trainer_ai/
│
├── backend/
│   ├── main.py                # Entry point ของ FastAPI app
│   ├── db.py                  # ตั้งค่า SQLAlchemy, เชื่อมต่อ PostgreSQL
│   ├── models.py              # ORM models (User, ExerciseResult, SampleVideo)
│   ├── auth.py                # ฟังก์ชัน hash password, JWT encode/decode
│   ├── graphql_schema.py      # GraphQL schema, query, mutation, resolver
│   ├── init_db.py             # สร้างตารางในฐานข้อมูล
│   ├── requirements.txt       # Dependencies สำหรับ backend
│   └── .gitignore             # ไฟล์ที่ไม่ควรขึ้น git (เช่น .env)
│
├── scripts/
│   ├── extract_landmarks.py   # ดึง landmark จากวิดีโอ สร้าง dataset ML
│   ├── train_model.py         # เทรน ML model (RandomForest) จาก landmark
│   ├── predict_video.py       # CLI ทำนายท่า/feedback จากวิดีโอ (เรียกใช้ ml_core.py)
│   ├── ml_core.py             # Core ML logic (predict, feedback, scoring, etc.)
│   └── analyze_and_recommend.py # แนะนำโปรแกรมฝึกถัดไป (demo logic)
│
├── data/
│   ├── X.npy                  # Landmark features (numpy array)
│   ├── y.npy                  # Labels (numpy array)
│   └── exercise_classifier.joblib # ไฟล์โมเดล ML ที่เทรนแล้ว
│
├── results/                   # วิดีโอ output ที่ประมวลผลแล้ว
│
├── videos/                    # วิดีโอตัวอย่าง (แบ่งตามท่า)
│   ├── Squat/
│   ├── Push-up/
│   └── Plank/
│
├── .gitignore                 # ไฟล์/โฟลเดอร์ที่ไม่ควรขึ้น git
└── README.md                  # คู่มือและ flow การทำงาน
```

---

## 3. อธิบายหน้าที่แต่ละไฟล์

### backend/

- **main.py**  
  Entry point ของ FastAPI app, รวม GraphQL endpoint
- **db.py**  
  ตั้งค่า SQLAlchemy, สร้าง engine, session, base class
- **models.py**  
  ORM models: User, ExerciseResult, SampleVideo (โครงสร้างตารางใน PostgreSQL)
- **auth.py**  
  ฟังก์ชันสำหรับ hash/verify password, สร้างและถอดรหัส JWT token
- **graphql_schema.py**  
  กำหนด GraphQL schema, query, mutation, resolver (สมัคร, login, อัปโหลดผล, query ข้อมูล ฯลฯ)
- **init_db.py**  
  สคริปต์สำหรับสร้างตารางในฐานข้อมูลตาม models.py
- **requirements.txt**  
  รายการ dependencies สำหรับ backend
- **.gitignore**  
  ระบุไฟล์/โฟลเดอร์ที่ไม่ควรขึ้น git (เช่น .env, ไฟล์ข้อมูลขนาดใหญ่)

### scripts/

- **extract_landmarks.py**  
  ดึง landmark จากวิดีโอใน `videos/` แล้วบันทึกเป็น X.npy, y.npy สำหรับเทรน ML
- **train_model.py**  
  เทรน RandomForest จาก X.npy, y.npy แล้วบันทึกโมเดลเป็น exercise_classifier.joblib
- **predict_video.py**  
  CLI สำหรับทำนายท่า/feedback จากวิดีโอ (interactive, เขียน overlay, save output)
  - เรียกใช้ core logic จาก `ml_core.py`
- **ml_core.py**  
  Core ML logic: predict_exercise_from_video (ทำนายท่าออกกำลังกายจากวิดีโอ), calculate_angle, check_squat_form, score_squat_form (ฟีดแบ็ก/ประเมินฟอร์ม)
- **analyze_and_recommend.py**  
  ตัวอย่าง logic แนะนำโปรแกรมฝึกถัดไปตาม goal และประวัติ (demo, ไม่ผูกกับ backend จริง)

### data/

- **X.npy, y.npy**  
  ข้อมูล landmark features และ label สำหรับเทรน ML
- **exercise_classifier.joblib**  
  ไฟล์โมเดล ML ที่เทรนแล้ว (ใช้ทั้ง backend และ CLI)

### results/

- วิดีโอ output ที่ผ่านการประมวลผล (เช่น overlay label/feedback)

### videos/

- วิดีโอตัวอย่างสำหรับแต่ละท่า (เช่น Squat, Push-up, Plank)

---

## 4. Flow การทำงาน (ละเอียด)

### 4.1 สมัครสมาชิกและล็อกอิน

- ผู้ใช้สมัครสมาชิกผ่าน mutation `register` (GraphQL)
- รหัสผ่านถูก hash ก่อนบันทึกลงฐานข้อมูล
- เมื่อล็อกอิน (mutation `login`) จะได้รับ JWT token สำหรับยืนยันตัวตน

### 4.2 อัปโหลดวิดีโอและวิเคราะห์ด้วย ML

- ผู้ใช้ (หลังล็อกอิน) อัปโหลดวิดีโอฝึก (ผ่าน endpoint หรืออัปโหลดไฟล์เอง)
- **AI/ML ทั้งหมดจะประมวลผลผ่าน scripts เท่านั้น**
- Backend ไม่โหลดหรือรันโมเดล ML โดยตรง แต่จะอ่านผลลัพธ์ที่ scripts ประมวลผลไว้ใน data/ หรือ results/

### 4.3 บันทึกผลการฝึก

- ผลการวิเคราะห์ (label, feedback, score, path วิดีโอ) ถูกบันทึกลง PostgreSQL ผ่าน mutation `upload_exercise_result`
- ข้อมูลนี้ผูกกับ user แต่ละคน

### 4.4 Query & Dashboard

- ผู้ใช้ดึงข้อมูลผลการฝึกย้อนหลัง (query `exercise_results`)
- ดึงข้อมูล user ปัจจุบัน (query `me`)
- ดึงวิดีโอตัวอย่างแต่ละท่า (query `sample_videos`)

### 4.5 ตั้งเป้าหมาย

- ผู้ใช้ตั้งเป้าหมายการฝึก (mutation `set_goal`)
- ระบบนำเป้าหมายนี้ไป personalize การแนะนำโปรแกรมฝึกในอนาคต

### 4.6 Database Structure

- ข้อมูล user, ผลการฝึก, วิดีโอตัวอย่างเก็บใน PostgreSQL
- ไฟล์วิดีโอและโมเดล ML เก็บในโฟลเดอร์ `data/`, `videos/`, `results/`

### 4.7 Security

- ทุก mutation/query ที่เกี่ยวกับข้อมูลส่วนตัวต้องแนบ JWT token ใน header
- ข้อมูลสำคัญ (เช่น password, secret key) เก็บใน `.env` และไม่ควร commit ลง git

---

## 5. วิธีการใช้งานแอป (End-to-End)

### 5.1 เตรียมระบบและเทรนโมเดล

1. วางวิดีโอตัวอย่างแต่ละท่าใน `videos/` (แบ่งโฟลเดอร์ตามชื่อท่า)
2. รัน `python scripts/extract_landmarks.py` เพื่อสร้าง X.npy, y.npy
3. รัน `python scripts/train_model.py` เพื่อเทรนโมเดลและสร้าง exercise_classifier.joblib ใน data/

### 5.2 วิเคราะห์วิดีโอใหม่ (AI/ML)

1. รัน `python scripts/predict_video.py` เพื่อเลือกวิดีโอ input และประมวลผล (interactive)
2. ผลลัพธ์จะถูกบันทึกใน results/ และ (optionally) ใน data/user_results.json

### 5.3 ติดตั้งและรัน backend server

1. `cd backend`
2. `pip install -r requirements.txt`
3. ตั้งค่า `.env` (DATABASE_URL, SECRET_KEY)
4. สร้าง database และตาราง: `python init_db.py`
5. รันเซิร์ฟเวอร์: `uvicorn main:app --reload`
6. เปิดใช้งาน GraphQL ที่ http://localhost:8000/graphql

### 5.4 ใช้งาน GraphQL API

- สมัคร, login, อัปโหลดผล, query ข้อมูล ฯลฯ ผ่าน GraphQL playground หรือ frontend
- Backend จะไม่ประมวลผล AI/ML เอง แต่จะอ่านผลลัพธ์ที่ scripts ประมวลผลไว้

---

## 6. หมายเหตุและ Scaling สำหรับ 1000+ Users

- ข้อมูล user/result ทั้งหมดเก็บใน PostgreSQL (ไม่ใช้ JSON แล้ว)
- dependencies backend ใช้ไฟล์ `backend/requirements.txt`
- ข้อมูลสำคัญควรเก็บใน `.env` และไม่ควร commit ลง git
- หากต้องการขยายระบบ (เช่น เพิ่ม endpoint, dashboard, frontend) สามารถต่อยอดได้ทันที
- **รองรับผู้ใช้ 1000+ ได้** (ด้วย PostgreSQL, FastAPI, และการแยก process AI/ML ออกจาก backend)
- หากต้องการ scale เพิ่มเติม: deploy backend ด้วย Uvicorn+Gunicorn, ใช้ managed PostgreSQL, ทำ queue สำหรับ batch AI/ML, ใช้ cloud storage สำหรับวิดีโอ, เพิ่ม load balancer ฯลฯ

---

## 7. แนวทางการพัฒนา/ขยายระบบ (Development Roadmap)

1. **เพิ่มระบบ Upload/Download วิดีโอผ่าน API**
   - เพิ่ม FastAPI endpoint สำหรับ upload/download ไฟล์
   - เชื่อมโยงกับ user และผลการวิเคราะห์
2. **เพิ่ม Frontend (Web/Mobile)**
   - สร้าง dashboard สำหรับผู้ใช้ (React, Flutter ฯลฯ)
   - แสดงผล, กราฟ, feedback, progress
3. **ขยาย ML/Feedback**
   - รองรับท่าใหม่, เพิ่มฟีเจอร์ประเมินฟอร์ม, personalize feedback
   - เพิ่มระบบ retrain/monitoring โมเดล
4. **เพิ่มระบบแจ้งเตือน/เป้าหมาย/Leaderboard**
   - gamification, social, เป้าหมายรายวัน
5. **Security & Scaling**
   - เพิ่ม OAuth/social login, logging, monitoring, backup, scaling
6. **CI/CD & Testing**
   - เพิ่ม unit/integration test, pipeline, deploy อัตโนมัติ
