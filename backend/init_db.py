# init_db.py
# สคริปต์สำหรับสร้างตารางในฐานข้อมูลตาม models.py
import os
import sys

# ตรวจสอบว่าอยู่ใน Docker container หรือไม่
def is_docker():
    return os.path.exists('/.dockerenv')

# ตั้งค่า DATABASE_URL ตาม environment
if is_docker():
    # ใน Docker container ใช้ hostname 'db'
    os.environ['DATABASE_URL'] = 'postgresql://postgres:mypassword@db:5432/fitnessai'
else:
    # ใน Windows host ใช้ localhost
    os.environ['DATABASE_URL'] = 'postgresql://postgres:mypassword@localhost:5432/fitnessai'

from db import Base, engine
from models import User, ExerciseResult, SampleVideo

# สร้างตารางทั้งหมดในฐานข้อมูล
Base.metadata.create_all(bind=engine)
print("Database initialized.")