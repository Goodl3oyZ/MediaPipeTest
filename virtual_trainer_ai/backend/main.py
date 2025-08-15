from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
import shutil
import subprocess
import uuid
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
from jose import jwt, JWTError

# --- ตั้งค่าเบื้องต้น ---
app = FastAPI()

# --- CORS สำหรับ frontend ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- JWT Secret ---
SECRET_KEY = "changeme"  # ควรเปลี่ยนใน production
ALGORITHM = "HS256"

# --- DB Connection ---
DB_URL = os.getenv("DATABASE_URL", "dbname=fitnessai user=postgres password=mypassword host=db")
def get_db():
    conn = psycopg2.connect(DB_URL, cursor_factory=RealDictCursor)
    return conn

# --- User Model ---
class User(BaseModel):
    username: str
    password: str

# --- Auth Helper ---
def create_access_token(data: dict, expires_delta: timedelta = timedelta(days=1)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# --- Auth Dependency ---
def get_current_user(token: str = Depends(lambda token: token)):
    return verify_token(token)

# --- API: Register ---
@app.post("/api/register")
def register(user: User):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username=%s", (user.username,))
    if cur.fetchone():
        raise HTTPException(status_code=400, detail="Username exists")
    cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (user.username, user.password))
    conn.commit()
    cur.close()
    conn.close()
    return {"msg": "registered"}

# --- API: Login ---
@app.post("/api/login")
def login(user: User):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username=%s AND password=%s", (user.username, user.password))
    db_user = cur.fetchone()
    cur.close()
    conn.close()
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": user.username})
    return {"access_token": token}

# --- API: Upload Video & Analyze ---
@app.post("/api/upload")
def upload_video(user_id: str = Form(...), file: UploadFile = File(...)):
    # --- บันทึกไฟล์ ---
    save_dir = "../data/uploads"
    os.makedirs(save_dir, exist_ok=True)
    file_id = str(uuid.uuid4())
    file_path = os.path.join(save_dir, f"{file_id}_{file.filename}")
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    # --- เรียก predict_video.py ---
    result_path = file_path.replace('.mp4', '_summary.json')
    subprocess.run(["python", "../scripts/predict_video.py", "--input", file_path, "--output", file_path.replace('.mp4', '_out.mp4'), "--user", user_id])
    # --- คืนผลลัพธ์ summary ---
    if os.path.exists(result_path):
        return FileResponse(result_path, media_type="application/json")
    else:
        return JSONResponse({"error": "Analysis failed"}, status_code=500)

# --- API: Get Workout Summary ---
@app.get("/api/summary")
def get_summary(user_id: str):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM results WHERE user_id=%s ORDER BY datetime DESC", (user_id,))
    results = cur.fetchall()
    cur.close()
    conn.close()
    return results

# --- API: Program Goal ---
@app.get("/api/program")
def get_program(goal: str):
    # TODO: ดึงโปรแกรมฝึกจาก analyze_and_recommend.py หรือ DB
    return {"goal": goal, "program": ["Squat", "Push-up", "Plank"]}

# --- API: Admin (ตัวอย่าง) ---
@app.get("/api/admin/users")
def admin_users():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users")
    users = cur.fetchall()
    cur.close()
    conn.close()
    return users

# --- API: Health Check ---
@app.get("/api/health")
def health():
    return {"status": "ok"}

# --- main ---
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)