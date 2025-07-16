# Virtual Trainer AI

Virtual Trainer AI คือโปรเจกต์สำหรับวิเคราะห์และจำแนกท่าออกกำลังกายจากวิดีโอ ด้วยเทคโนโลยี MediaPipe และ Machine Learning เหมาะสำหรับผู้เริ่มต้นที่ไม่มีพื้นฐานมาก่อน

---

## 1. โครงสร้างโปรเจกต์

```
virtual_trainer_ai/
├── videos/                # โฟลเดอร์เก็บวิดีโอตัวอย่าง (แบ่งตามท่า)
│   ├── Squat/
│   ├── Push-up/
│   └── Plank/
├── data/                  # โฟลเดอร์เก็บข้อมูลที่ประมวลผลแล้ว (ไม่ต้องสร้างเอง)
│   ├── X.npy              # Landmark features
│   ├── y.npy              # Labels
│   └── exercise_classifier.joblib  # โมเดลที่ train แล้ว
├── scripts/               # โฟลเดอร์เก็บสคริปต์หลัก
│   ├── extract_landmarks.py   # สร้าง dataset จากวิดีโอ
│   ├── train_model.py         # เทรนโมเดล ML
│   └── predict_video.py       # ทำนายท่าทางจากวิดีโอใหม่
├── requirements.txt       # รายการไลบรารีที่ต้องติดตั้ง
└── README.md              # คู่มือฉบับนี้
```

---

## 2. การเตรียมวิดีโอตัวอย่าง

1. สร้างโฟลเดอร์ย่อยใน `videos/` ตามชื่อท่าทาง เช่น `Squat`, `Push-up`, `Plank`
2. ใส่วิดีโอแต่ละท่าลงในโฟลเดอร์ย่อยนั้น (รองรับ .mp4, .avi, .mov)
3. **แนะนำ**: ควรมีวิดีโอหลายไฟล์ต่อท่า (อย่างน้อย 5-10 ไฟล์)
4. **ข้อควรระวัง:**
   - วิดีโอควรเห็นร่างกายเต็มตัว ชัดเจน แสงเพียงพอ
   - 1 วิดีโอ = 1 คน = 1 ท่า
   - ความละเอียดแนะนำ: 720p ขึ้นไป
   - ความยาววิดีโอ: 5-30 วินาที
   - มุมกล้อง: ด้านข้างหรือด้านหน้า (ให้เห็นท่าชัด)

---

## 3. การติดตั้งไลบรารี (Dependencies)

1. เปิด terminal/command prompt ที่โฟลเดอร์ `virtual_trainer_ai`
2. ติดตั้งไลบรารีด้วยคำสั่ง:

```bash
pip install -r requirements.txt
```

---

## 4. ขั้นตอนการใช้งาน

### 4.1 สร้าง dataset landmark จากวิดีโอ

```bash
python scripts/extract_landmarks.py
```

- จะได้ไฟล์ `data/X.npy` และ `data/y.npy` สำหรับใช้ train โมเดล
- **ถ้าไม่มีวิดีโอใน videos/ จะเกิด error**

### 4.2 เทรนโมเดล Machine Learning

```bash
python scripts/train_model.py
```

- จะได้ไฟล์ `data/exercise_classifier.joblib` (โมเดลที่ train แล้ว)
- จะแสดงผลการทดสอบโมเดล (classification report) ใน terminal

### 4.3 ทำนายท่าทางจากวิดีโอใหม่

```bash
python scripts/predict_video.py --input [input_video] --output [output_video]
```

- ตัวอย่าง:

```bash
python scripts/predict_video.py --input videos/test.mp4 --output results/output.mp4
```

- จะได้วิดีโอใหม่ที่มี label ท่าทางแสดงในแต่ละ frame

---

## 5. คำอธิบายแต่ละสคริปต์

- **extract_landmarks.py**: ดึง pose landmarks จากวิดีโอใน `videos/` แล้วบันทึกเป็นไฟล์ .npy
- **train_model.py**: เทรน RandomForestClassifier จากไฟล์ .npy แล้วบันทึกโมเดล
- **predict_video.py**: โหลดโมเดล ทำนายท่าทางจากวิดีโอใหม่ แล้วเขียน label ลงบนวิดีโอ

---

## 6. ข้อควรระวังและปัญหาที่พบบ่อย (Troubleshooting)

- **Error: No such file or directory: 'X.npy' หรือ 'y.npy'**
  - ต้องรัน extract_landmarks.py ก่อน
- **Error: No such file or directory: 'exercise_classifier.joblib'**
  - ต้องรัน train_model.py ก่อน
- **วิดีโอไม่มี label แสดง**
  - วิดีโออาจไม่เห็นร่างกายชัด หรือมุมกล้องไม่เหมาะสม
- **วิดีโอ input/output ไม่พบ**
  - ตรวจสอบ path และชื่อไฟล์ให้ถูกต้อง
- **ต้องการเพิ่มท่าใหม่**
  - สร้างโฟลเดอร์ใหม่ใน videos/ ใส่วิดีโอ แล้วรันใหม่ตั้งแต่ extract_landmarks.py

---

## 7. ตัวอย่างผลลัพธ์

- วิดีโอ output จะมีข้อความ "Prediction: [label]" แสดงในแต่ละ frame
- ตัวอย่างไฟล์ใน data/:
  - X.npy: ข้อมูล landmark vector
  - y.npy: label ของแต่ละ frame
  - exercise_classifier.joblib: โมเดลที่ train แล้ว

---

## 8. คำถามที่พบบ่อย (FAQ)

- **Q: ใช้กับวิดีโอที่มีหลายคนได้ไหม?**
  - A: ไม่แนะนำ ควรมีแค่ 1 คนต่อวิดีโอ
- **Q: เพิ่ม label ท่าใหม่ได้ไหม?**
  - A: ได้ แค่เพิ่มโฟลเดอร์ใหม่ใน videos/ แล้วใส่วิดีโอท่านั้น
- **Q: ใช้กับ webcam ได้ไหม?**
  - A: โค้ดนี้รองรับเฉพาะไฟล์วิดีโอเท่านั้น (mp4, avi, mov)

---

## 9. ติดต่อ/แจ้งปัญหา

หากพบปัญหา/ข้อสงสัย สามารถเปิด issue หรือสอบถามผู้ดูแลโปรเจกต์
