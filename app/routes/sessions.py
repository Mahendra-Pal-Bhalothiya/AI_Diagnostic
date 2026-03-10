from fastapi import APIRouter, HTTPException, BackgroundTasks
from datetime import datetime
import uuid
from typing import Optional
from pydantic import BaseModel

from app.models.database import db, UserSession
from app.services.adaptive_algorithm import AdaptiveAlgorithm
from app.services.question_selector import QuestionSelector
from app.services.ai_insights import AIInsightsGenerator

router = APIRouter()

# Initialize services
adaptive_algo = AdaptiveAlgorithm()
question_selector = QuestionSelector()
ai_insights = AIInsightsGenerator()

# Request/Response Models
class StartSessionRequest(BaseModel):
    user_id: Optional[str] = None

class StartSessionResponse(BaseModel):
    session_id: str
    message: str
    first_question: Optional[dict] = None

class SubmitAnswerRequest(BaseModel):
    session_id: str
    question_id: str
    user_answer: str
    time_taken: Optional[float] = None

class SubmitAnswerResponse(BaseModel):
    is_correct: bool
    correct_answer: str
    explanation: Optional[str]
    next_question: Optional[dict]
    current_ability: float
    questions_remaining: int
    session_completed: bool

class StudyPlanRequest(BaseModel):
    session_id: str

class StudyPlanResponse(BaseModel):
    session_id: str
    performance_summary: dict
    study_plan: dict
    generated_by: str

@router.post("/start-session", response_model=StartSessionResponse)
async def start_session(request: StartSessionRequest):
    """Start a new testing session"""
    session_id = str(uuid.uuid4())
    
    session = UserSession(
        session_id=session_id,
        user_id=request.user_id,
        current_ability=0.5,
        estimated_theta=0.0,
        measurement_error=1.0,
        started_at=datetime.now()
    )
    
    await db.db.user_sessions.insert_one(session.dict(by_alias=True))
    
    # Get first question
    first_question = await question_selector.select_next_question(
        session_id=session_id,
        current_ability=0.5,
        measurement_error=1.0,
        answered_questions=[]
    )
    
    return StartSessionResponse(
        session_id=session_id,
        message="Session started successfully",
        first_question=first_question
    )

@router.post("/submit-answer", response_model=SubmitAnswerResponse)
async def submit_answer(request: SubmitAnswerRequest):
    """Submit an answer and get next question"""
    from bson import ObjectId
    
    # Get session
    session = await db.db.user_sessions.find_one({"session_id": request.session_id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get question
    try:
        question = await db.db.questions.find_one({"_id": ObjectId(request.question_id)})
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
    except:
        raise HTTPException(status_code=400, detail="Invalid question ID")
    
    # Check answer
    is_correct = request.user_answer.strip().lower() == question["correct_answer"].strip().lower()
    
    # Update ability using IRT
    response_value = 1 if is_correct else 0
    new_theta, new_error = adaptive_algo.update_ability(
        current_theta=session.get("estimated_theta", 0.0),
        difficulty=adaptive_algo._convert_difficulty_to_theta(question["difficulty"]),
        response=response_value,
        prior_variance=session.get("measurement_error", 1.0) ** 2
    )
    
    new_ability = adaptive_algo._convert_theta_to_difficulty(new_theta)
    
    # Track answer
    answered_questions = session.get("questions_answered", [])
    answered_questions.append({
        "question_id": request.question_id,
        "is_correct": is_correct,
        "difficulty": question["difficulty"],
        "topic": question["topic"],
        "time_taken": request.time_taken
    })
    
    # Update topics performance
    topics_performance = session.get("topics_performance", {})
    topic = question["topic"]
    if topic not in topics_performance:
        topics_performance[topic] = {"correct": 0, "total": 0, "accuracy": 0.0}
    
    topics_performance[topic]["total"] += 1
    if is_correct:
        topics_performance[topic]["correct"] += 1
    topics_performance[topic]["accuracy"] = (
        topics_performance[topic]["correct"] / topics_performance[topic]["total"]
    )
    
    question_count = session.get("question_count", 0) + 1
    session_completed = question_count >= 10
    
    # Update session
    await db.db.user_sessions.update_one(
        {"session_id": request.session_id},
        {"$set": {
            "current_ability": new_ability,
            "estimated_theta": new_theta,
            "measurement_error": new_error,
            "questions_answered": answered_questions,
            "question_count": question_count,
            "topics_performance": topics_performance,
            "completed_at": datetime.now() if session_completed else None
        }}
    )
    
    # Get next question if needed
    next_question = None
    questions_remaining = 0
    
    if not session_completed:
        answered_ids = [q["question_id"] for q in answered_questions]
        next_question = await question_selector.select_next_question(
            session_id=request.session_id,
            current_ability=new_theta,
            measurement_error=new_error,
            answered_questions=answered_ids
        )
        questions_remaining = 10 - question_count
    
    return SubmitAnswerResponse(
        is_correct=is_correct,
        correct_answer=question["correct_answer"],
        explanation=question.get("explanation", ""),
        next_question=next_question,
        current_ability=new_ability,
        questions_remaining=questions_remaining,
        session_completed=session_completed
    )

@router.post("/generate-study-plan", response_model=StudyPlanResponse)
async def generate_study_plan(request: StudyPlanRequest):
    """Generate AI-powered study plan"""
    
    session = await db.db.user_sessions.find_one({"session_id": request.session_id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    answered_questions = session.get("questions_answered", [])
    difficulties = [q["difficulty"] for q in answered_questions] if answered_questions else [0]
    
    performance_data = {
        "final_ability": session.get("current_ability", 0.5),
        "final_theta": session.get("estimated_theta", 0.0),
        "total_questions": session.get("question_count", 0),
        "topics_performance": session.get("topics_performance", {}),
        "min_difficulty": min(difficulties),
        "max_difficulty": max(difficulties),
        "correct_count": sum(1 for q in answered_questions if q["is_correct"]),
        "accuracy": sum(1 for q in answered_questions if q["is_correct"]) / len(answered_questions) if answered_questions else 0
    }
    
    study_plan_result = await ai_insights.generate_study_plan(performance_data)
    
    return StudyPlanResponse(
        session_id=request.session_id,
        performance_summary=performance_data,
        study_plan=study_plan_result["study_plan"],
        generated_by=study_plan_result.get("provider", "fallback")
    )

@router.get("/session/{session_id}")
async def get_session_status(session_id: str):
    """Get current session status"""
    session = await db.db.user_sessions.find_one({"session_id": session_id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session["_id"] = str(session["_id"])
    return session