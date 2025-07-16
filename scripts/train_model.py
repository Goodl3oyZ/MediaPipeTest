import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
import os

# กำหนด path สำหรับโฟลเดอร์ข้อมูล landmark ที่เตรียมไว้
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

# โหลดข้อมูล feature (X) และ label (y) ที่ได้จาก extract_landmarks.py
X = np.load(os.path.join(DATA_DIR, 'X.npy'))
y = np.load(os.path.join(DATA_DIR, 'y.npy'))

# แบ่งข้อมูลเป็นชุด train/test (test 20%) เพื่อประเมินประสิทธิภาพโมเดล
# ใช้ random_state เพื่อให้ผล reproducible
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# สร้าง Random Forest classifier
# - n_estimators=100: ใช้ต้นไม้ 100 ต้น เพื่อความแม่นยำและลด overfit
# - random_state=42: เพื่อ reproducibility
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)  # เทรนโมเดลด้วยข้อมูล train

# บันทึกโมเดลที่เทรนแล้วไว้ในไฟล์ สำหรับนำไปใช้ทำนายจริง
joblib.dump(clf, os.path.join(DATA_DIR, 'exercise_classifier.joblib'))

print("Model saved to data/exercise_classifier.joblib")
print("Test set classification report:")
# ประเมินโมเดลบน test set และแสดง classification report
print(classification_report(y_test, clf.predict(X_test))) 