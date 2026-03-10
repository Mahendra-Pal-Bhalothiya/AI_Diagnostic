from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.models.database import connect_to_mongo, close_mongo_connection
from app.routes import questions, sessions

app = FastAPI(
    title="AI-Driven Adaptive Diagnostic Engine",
    description="Professional-grade adaptive testing system using IRT and AI",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Event handlers
@app.on_event("startup")
async def startup_event():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()

# Include routers
app.include_router(questions.router, prefix="/api/questions", tags=["questions"])
app.include_router(sessions.router, prefix="/api/sessions", tags=["sessions"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to AI Diagnostic System API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": [
            "/docs - API Documentation",
            "/start-session - Start new test session",
            "/submit-answer - Submit answer and get next question",
            "/generate-study-plan - Generate AI study plan",
            "/session/{session_id} - Get session status"
        ]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}