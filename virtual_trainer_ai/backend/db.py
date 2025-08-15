# db.py
# ตั้งค่าและเชื่อมต่อฐานข้อมูล PostgreSQL ด้วย SQLAlchemy ORM
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

# โหลด environment variables จาก .env
load_dotenv()

# อ่าน DATABASE_URL จาก environment (รองรับ fallback)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:mypassword@db:5432/fitnessai")

# สร้าง engine สำหรับเชื่อมต่อฐานข้อมูล
engine = create_engine(DATABASE_URL)
# สร้าง session factory สำหรับใช้งานกับ ORM
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# สร้าง base class สำหรับ declarative models
Base = declarative_base()