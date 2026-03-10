from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class Question(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    question_text: str
    difficulty: float  # 0.1 to 1.0
    topic: str
    tags: List[str]
    correct_answer: str
    options: List[str]
    explanation: Optional[str] = None
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class Answer(BaseModel):
    question_id: str
    user_answer: str
    is_correct: bool
    time_taken: Optional[float] = None

class UserSession(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    session_id: str
    user_id: Optional[str] = None
    started_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    current_ability: float = 0.5
    questions_answered: List[Dict[str, Any]] = []
    estimated_theta: float = 0.0
    measurement_error: float = 1.0
    question_count: int = 0
    topics_performance: Dict[str, Dict[str, float]] = {}
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class Database:
    client: AsyncIOMotorClient = None
    db = None

db = Database()

async def connect_to_mongo():
    db.client = AsyncIOMotorClient(os.getenv("MONGODB_URL", "mongodb+srv://bt23cs022_db_user:Mahendra250704@aidiagnostic.bpndeph.mongodb.net/"))
    db.db = db.client[os.getenv("MONGODB_DB_NAME", "adaptive_testing")]
    
    # Create indexes
    await db.db.questions.create_index("difficulty")
    await db.db.questions.create_index("topic")
    await db.db.questions.create_index("tags")
    await db.db.user_sessions.create_index("session_id")
    await db.db.user_sessions.create_index([("started_at", -1)])
    
    print("✅ Connected to MongoDB")

async def close_mongo_connection():
    db.client.close()
    print("✅ Disconnected from MongoDB")