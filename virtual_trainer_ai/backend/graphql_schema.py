# graphql_schema.py
# กำหนด GraphQL schema, query, mutation และ resolver สำหรับระบบทั้งหมด
import strawberry
from typing import List, Optional
from .models import User as UserModel, ExerciseResult as ExerciseResultModel, SampleVideo as SampleVideoModel
from .db import SessionLocal
from .auth import hash_password, verify_password, create_access_token, decode_access_token
from .ml_predict import predict_exercise_from_video
from sqlalchemy.orm import Session

def get_db():
    # ฟังก์ชัน generator สำหรับดึง session ของ database
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# GraphQL type สำหรับ User
@strawberry.type
class User:
    id: int
    email: str
    display_name: Optional[str]
    goal: Optional[str]
    created_at: str

# GraphQL type สำหรับผลการฝึก
@strawberry.type
class ExerciseResult:
    id: int
    exercise_type: str
    input_video_path: str
    output_video_path: str
    feedback: Optional[str]
    score: Optional[float]
    created_at: str

# GraphQL type สำหรับวิดีโอตัวอย่าง
@strawberry.type
class SampleVideo:
    id: int
    exercise_type: str
    file_path: str

# Query หลักของระบบ
@strawberry.type
class Query:
    @strawberry.field
    def me(self, info) -> Optional[User]:
        # ดึงข้อมูล user ปัจจุบันจาก JWT token
        token = info.context["request"].headers.get("authorization")
        if not token:
            return None
        payload = decode_access_token(token.replace("Bearer ", ""))
        if not payload:
            return None
        db: Session = next(get_db())
        user = db.query(UserModel).filter(UserModel.id == payload["user_id"]).first()
        if not user:
            return None
        return User(
            id=user.id,
            email=user.email,
            display_name=user.display_name,
            goal=user.goal,
            created_at=str(user.created_at)
        )

    @strawberry.field
    def exercise_results(self, info, user_id: int) -> List[ExerciseResult]:
        # ดึงผลการฝึกทั้งหมดของ user ตาม user_id
        db: Session = next(get_db())
        results = db.query(ExerciseResultModel).filter(ExerciseResultModel.user_id == user_id).all()
        return [
            ExerciseResult(
                id=r.id,
                exercise_type=r.exercise_type,
                input_video_path=r.input_video_path,
                output_video_path=r.output_video_path,
                feedback=r.feedback,
                score=r.score,
                created_at=str(r.created_at)
            ) for r in results
        ]

    @strawberry.field
    def sample_videos(self, info, exercise_type: str) -> List[SampleVideo]:
        # ดึงวิดีโอตัวอย่างตามประเภทท่า
        db: Session = next(get_db())
        videos = db.query(SampleVideoModel).filter(SampleVideoModel.exercise_type == exercise_type).all()
        return [
            SampleVideo(
                id=v.id,
                exercise_type=v.exercise_type,
                file_path=v.file_path
            ) for v in videos
        ]

# Mutation หลักของระบบ
@strawberry.type
class Mutation:
    @strawberry.mutation
    def register(self, info, email: str, password: str, display_name: Optional[str] = None) -> User:
        # สมัครสมาชิกใหม่
        db: Session = next(get_db())
        user = UserModel(email=email, password_hash=hash_password(password), display_name=display_name)
        db.add(user)
        db.commit()
        db.refresh(user)
        return User(
            id=user.id,
            email=user.email,
            display_name=user.display_name,
            goal=user.goal,
            created_at=str(user.created_at)
        )

    @strawberry.mutation
    def login(self, info, email: str, password: str) -> str:
        # ล็อกอินและคืน JWT token
        db: Session = next(get_db())
        user = db.query(UserModel).filter(UserModel.email == email).first()
        if not user or not verify_password(password, user.password_hash):
            raise Exception("Invalid credentials")
        token = create_access_token({"user_id": user.id})
        return token

    @strawberry.mutation
    def upload_exercise_result(
        self, info, exercise_type: str, input_video_path: str, output_video_path: str, feedback: Optional[str], score: Optional[float]
    ) -> ExerciseResult:
        # อัปโหลดผลการฝึก (ต้อง auth)
        token = info.context["request"].headers.get("authorization")
        if not token:
            raise Exception("Not authenticated")
        payload = decode_access_token(token.replace("Bearer ", ""))
        if not payload:
            raise Exception("Invalid token")
        db: Session = next(get_db())
        result = ExerciseResultModel(
            user_id=payload["user_id"],
            exercise_type=exercise_type,
            input_video_path=input_video_path,
            output_video_path=output_video_path,
            feedback=feedback,
            score=score
        )
        db.add(result)
        db.commit()
        db.refresh(result)
        return ExerciseResult(
            id=result.id,
            exercise_type=result.exercise_type,
            input_video_path=result.input_video_path,
            output_video_path=result.output_video_path,
            feedback=result.feedback,
            score=result.score,
            created_at=str(result.created_at)
        )

    @strawberry.mutation
    def set_goal(self, info, goal: str) -> User:
        # ตั้งเป้าหมายการฝึกของ user
        token = info.context["request"].headers.get("authorization")
        if not token:
            raise Exception("Not authenticated")
        payload = decode_access_token(token.replace("Bearer ", ""))
        if not payload:
            raise Exception("Invalid token")
        db: Session = next(get_db())
        user = db.query(UserModel).filter(UserModel.id == payload["user_id"]).first()
        user.goal = goal
        db.commit()
        db.refresh(user)
        return User(
            id=user.id,
            email=user.email,
            display_name=user.display_name,
            goal=user.goal,
            created_at=str(user.created_at)
        )

# สร้าง GraphQL schema
schema = strawberry.Schema(query=Query, mutation=Mutation)