import asyncio
import random
from motor.motor_asyncio import AsyncIOMotorClient
from app.models.database import connect_to_mongo, db

GRE_QUESTIONS = [
    {
        "question_text": "If 3x + 5 = 20, what is the value of x?",
        "difficulty": 0.3,
        "topic": "Algebra",
        "tags": ["linear equations", "basic algebra"],
        "correct_answer": "5",
        "options": ["3", "4", "5", "6", "7"],
        "explanation": "Subtract 5 from both sides: 3x = 15, then divide by 3: x = 5"
    },
    {
        "question_text": "Solve for x: x² - 5x + 6 = 0",
        "difficulty": 0.5,
        "topic": "Algebra",
        "tags": ["quadratic equations", "factoring"],
        "correct_answer": "2, 3",
        "options": ["1, 6", "2, 3", "-2, -3", "1, -6", "2, -3"],
        "explanation": "Factor to (x-2)(x-3)=0, so x=2 or x=3"
    },
    {
        "question_text": "What is the meaning of 'ephemeral'?",
        "difficulty": 0.3,
        "topic": "Vocabulary",
        "tags": ["definition", "word meaning"],
        "correct_answer": "Lasting for a short time",
        "options": [
            "Lasting for a short time",
            "Eternal and everlasting",
            "Related to insects",
            "Extremely large",
            "Spiritual in nature"
        ],
        "explanation": "Ephemeral means lasting for a very short time"
    },
    {
        "question_text": "What is the area of a circle with radius 5?",
        "difficulty": 0.3,
        "topic": "Geometry",
        "tags": ["circles", "area"],
        "correct_answer": "25π",
        "options": ["5π", "10π", "25π", "50π", "100π"],
        "explanation": "Area of a circle = πr² = π(5)² = 25π"
    },
    {
        "question_text": "In a right triangle, if one leg is 3 and the other is 4, what is the hypotenuse?",
        "difficulty": 0.3,
        "topic": "Geometry",
        "tags": ["Pythagorean theorem", "triangles"],
        "correct_answer": "5",
        "options": ["5", "6", "7", "8", "12"],
        "explanation": "Using Pythagorean theorem: a² + b² = c², so 3² + 4² = 9 + 16 = 25, √25 = 5"
    },
    {
        "question_text": "What is the mean of 2, 4, 6, 8, 10?",
        "difficulty": 0.2,
        "topic": "Data Analysis",
        "tags": ["statistics", "mean"],
        "correct_answer": "6",
        "options": ["4", "5", "6", "7", "8"],
        "explanation": "Mean = (2+4+6+8+10)/5 = 30/5 = 6"
    },
    {
        "question_text": "If log₂(x) = 5, what is x?",
        "difficulty": 0.7,
        "topic": "Algebra",
        "tags": ["logarithms", "exponents"],
        "correct_answer": "32",
        "options": ["10", "25", "32", "64", "128"],
        "explanation": "log₂(x) = 5 means 2⁵ = x, so x = 32"
    },
    {
        "question_text": "The word 'loquacious' most nearly means:",
        "difficulty": 0.6,
        "topic": "Vocabulary",
        "tags": ["advanced vocabulary", "synonyms"],
        "correct_answer": "Talkative",
        "options": ["Quiet", "Talkative", "Beautiful", "Intelligent", "Lazy"],
        "explanation": "Loquacious comes from Latin 'loqui' meaning to speak"
    },
    {
        "question_text": "What is the probability of rolling a sum of 7 with two dice?",
        "difficulty": 0.5,
        "topic": "Probability",
        "tags": ["probability", "combinations"],
        "correct_answer": "1/6",
        "options": ["1/12", "1/9", "1/6", "1/4", "1/3"],
        "explanation": "36 total outcomes, 6 ways to get sum 7: (1,6),(2,5),(3,4),(4,3),(5,2),(6,1)"
    },
    {
        "question_text": "If f(x) = 2x + 3, what is f(4)?",
        "difficulty": 0.2,
        "topic": "Algebra",
        "tags": ["functions"],
        "correct_answer": "11",
        "options": ["8", "11", "14", "5", "7"],
        "explanation": "f(4) = 2(4) + 3 = 8 + 3 = 11"
    },
    {
        "question_text": "What is the square root of 144?",
        "difficulty": 0.2,
        "topic": "Arithmetic",
        "tags": ["square roots"],
        "correct_answer": "12",
        "options": ["10", "11", "12", "13", "14"],
        "explanation": "12 × 12 = 144"
    },
    {
        "question_text": "Choose the synonym for 'ubiquitous'",
        "difficulty": 0.7,
        "topic": "Vocabulary",
        "tags": ["synonyms"],
        "correct_answer": "Omnipresent",
        "options": ["Rare", "Omnipresent", "Unique", "Strange", "Beautiful"],
        "explanation": "Ubiquitous means found everywhere, same as omnipresent"
    },
    {
        "question_text": "What is 15% of 200?",
        "difficulty": 0.3,
        "topic": "Arithmetic",
        "tags": ["percentages"],
        "correct_answer": "30",
        "options": ["15", "20", "25", "30", "35"],
        "explanation": "15% = 0.15, 0.15 × 200 = 30"
    },
    {
        "question_text": "Solve: 2(x + 3) = 14",
        "difficulty": 0.4,
        "topic": "Algebra",
        "tags": ["linear equations"],
        "correct_answer": "4",
        "options": ["4", "5", "6", "7", "8"],
        "explanation": "2x + 6 = 14, 2x = 8, x = 4"
    },
    {
        "question_text": "What is the volume of a cube with side 3?",
        "difficulty": 0.4,
        "topic": "Geometry",
        "tags": ["volume", "cube"],
        "correct_answer": "27",
        "options": ["9", "18", "27", "36", "54"],
        "explanation": "Volume = side³ = 3³ = 27"
    },
    {
        "question_text": "The word 'benevolent' means:",
        "difficulty": 0.5,
        "topic": "Vocabulary",
        "tags": ["word meaning"],
        "correct_answer": "Kind and generous",
        "options": ["Mean and cruel", "Kind and generous", "Indifferent", "Angry", "Confused"],
        "explanation": "Benevolent means well-meaning and kindly"
    },
    {
        "question_text": "What is the median of 3, 7, 2, 9, 5?",
        "difficulty": 0.4,
        "topic": "Statistics",
        "tags": ["median"],
        "correct_answer": "5",
        "options": ["3", "5", "7", "2", "9"],
        "explanation": "Order: 2,3,5,7,9; middle number is 5"
    },
    {
        "question_text": "If a circle has diameter 10, what is its circumference?",
        "difficulty": 0.4,
        "topic": "Geometry",
        "tags": ["circle", "circumference"],
        "correct_answer": "10π",
        "options": ["5π", "10π", "15π", "20π", "25π"],
        "explanation": "Circumference = π × diameter = 10π"
    },
    {
        "question_text": "What is 2⁵?",
        "difficulty": 0.2,
        "topic": "Arithmetic",
        "tags": ["exponents"],
        "correct_answer": "32",
        "options": ["10", "16", "25", "32", "64"],
        "explanation": "2⁵ = 2 × 2 × 2 × 2 × 2 = 32"
    },
    {
        "question_text": "Choose the antonym for 'arduous'",
        "difficulty": 0.6,
        "topic": "Vocabulary",
        "tags": ["antonyms"],
        "correct_answer": "Easy",
        "options": ["Difficult", "Easy", "Challenging", "Complex", "Hard"],
        "explanation": "Arduous means difficult, so antonym is easy"
    }
]

async def seed_database():
    """Seed the database with GRE questions"""
    await connect_to_mongo()
    
    count = await db.db.questions.count_documents({})
    
    if count == 0:
        print("📚 Seeding database with GRE questions...")
        
        # Ensure we have exactly 20 questions
        questions_to_insert = GRE_QUESTIONS[:20]
        result = await db.db.questions.insert_many(questions_to_insert)
        print(f"✅ Seeded {len(result.inserted_ids)} questions")
    else:
        print(f"✅ Database already has {count} questions")
    
    # Create indexes
    await db.db.questions.create_index("difficulty")
    await db.db.questions.create_index("topic")
    
    print("✅ Database seeding completed")
    return count

if __name__ == "__main__":
    asyncio.run(seed_database())