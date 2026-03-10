from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Optional
from app.models.database import db
from bson import ObjectId

router = APIRouter()

@router.get("/questions")
async def get_questions(
    topic: Optional[str] = None,
    difficulty_min: Optional[float] = None,
    difficulty_max: Optional[float] = None,
    limit: int = 20
):
    """Get questions with optional filters"""
    query = {}
    
    if topic:
        query["topic"] = topic
    if difficulty_min or difficulty_max:
        query["difficulty"] = {}
        if difficulty_min:
            query["difficulty"]["$gte"] = difficulty_min
        if difficulty_max:
            query["difficulty"]["$lte"] = difficulty_max
    
    cursor = db.db.questions.find(query).limit(limit)
    questions = await cursor.to_list(length=limit)
    
    # Convert ObjectId to string
    for q in questions:
        q["_id"] = str(q["_id"])
    
    return questions

@router.get("/questions/{question_id}")
async def get_question(question_id: str):
    """Get a specific question by ID"""
    try:
        question = await db.db.questions.find_one({"_id": ObjectId(question_id)})
        if question:
            question["_id"] = str(question["_id"])
            return question
        raise HTTPException(status_code=404, detail="Question not found")
    except:
        raise HTTPException(status_code=400, detail="Invalid question ID")

@router.get("/topics")
async def get_topics():
    """Get all unique topics"""
    topics = await db.db.questions.distinct("topic")
    return {"topics": topics}