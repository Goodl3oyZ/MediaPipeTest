# auth.py
# ฟังก์ชันสำหรับจัดการ authentication (hash password, JWT encode/decode)
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

# อ่าน secret key สำหรับ JWT
SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

# ตั้งค่า context สำหรับ hash password ด้วย bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    # แปลง plain password เป็น hash
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    # ตรวจสอบว่า plain password ตรงกับ hash หรือไม่
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    # สร้าง JWT token พร้อมวันหมดอายุ
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str):
    # ถอดรหัส JWT token เพื่อดึงข้อมูล user
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None