from typing import List, Optional
from app.models.database import db
from app.services.adaptive_algorithm import AdaptiveAlgorithm
from bson import ObjectId

class QuestionSelector:
    def __init__(self):
        self.adaptive_algo = AdaptiveAlgorithm()
    
    async def select_next_question(self, 
                                  session_id: str, 
                                  current_ability: float,
                                  measurement_error: float,
                                  answered_questions: List[str]) -> Optional[dict]:
        """Select the next optimal question"""
        
        target_difficulty = self.adaptive_algo.select_next_difficulty(
            current_ability, 
            measurement_error,
            answered_questions
        )
        
        # Convert string IDs to ObjectId for query
        answered_obj_ids = []
        for qid in answered_questions:
            try:
                answered_obj_ids.append(ObjectId(qid))
            except:
                pass
        
        query = {
            "_id": {"$nin": answered_obj_ids},
            "difficulty": {
                "$gte": max(0.1, target_difficulty - 0.15),
                "$lte": min(1.0, target_difficulty + 0.15)
            }
        }
        
        cursor = db.db.questions.find(query)
        questions = await cursor.to_list(length=10)
        
        if not questions:
            # Fallback: get any unanswered question
            cursor = db.db.questions.find({
                "_id": {"$nin": answered_obj_ids}
            })
            questions = await cursor.to_list(length=10)
        
        if not questions:
            return None
        
        # Select question closest to target difficulty
        selected = min(questions, 
                      key=lambda q: abs(q["difficulty"] - target_difficulty))
        
        if selected:
            selected["_id"] = str(selected["_id"])
        
        return selected