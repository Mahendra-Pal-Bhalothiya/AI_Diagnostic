import requests
import time
import random
from tabulate import tabulate

BASE_URL = "http://localhost:8000"

def run_demo():
    print("\n" + "="*60)
    print(" AI-DRIVEN ADAPTIVE DIAGNOSTIC ENGINE DEMO")
    print("="*60)
    
    # Start session
    response = requests.post(f"{BASE_URL}/start-session", 
                           json={"user_id": "demo_user"})
    session = response.json()
    session_id = session["session_id"]
    print(f"\n✅ Session started: {session_id}")
    
    # Answer questions
    question = session.get("first_question")
    results = []
    
    for i in range(10):
        print(f"\n📝 Question {i+1}/10")
        print(f"Topic: {question['topic']}")
        print(f"Difficulty: {question['difficulty']:.2f}")
        print(f"Q: {question['question_text']}")
        
        # Simulate answer (70% chance correct for demo)
        is_correct = random.random() < 0.7
        answer = question['correct_answer'] if is_correct else question['options'][1]
        
        print(f"Answer: {answer}")
        
        # Submit
        response = requests.post(f"{BASE_URL}/submit-answer", json={
            "session_id": session_id,
            "question_id": question['_id'],
            "user_answer": answer,
            "time_taken": random.uniform(10, 30)
        })
        
        result = response.json()
        results.append({
            "Q": i+1,
            "Topic": question['topic'][:10],
            "Difficulty": f"{question['difficulty']:.2f}",
            "Result": "✅" if result['is_correct'] else "❌",
            "Ability": f"{result['current_ability']:.2f}"
        })
        
        print(f"Result: {'✅ Correct' if result['is_correct'] else '❌ Incorrect'}")
        print(f"Ability Score: {result['current_ability']:.2f}")
        
        if result['session_completed']:
            break
            
        question = result['next_question']
        time.sleep(1)
    
    # Show summary
    print("\n" + "="*60)
    print(" PERFORMANCE SUMMARY")
    print("="*60)
    print(tabulate(results, headers="keys", tablefmt="grid"))
    
    # Get study plan
    print("\n" + "="*60)
    print(" GENERATING AI STUDY PLAN")
    print("="*60)
    
    response = requests.post(f"{BASE_URL}/generate-study-plan",
                           json={"session_id": session_id})
    
    if response.status_code == 200:
        plan = response.json()
        print("\n📚 YOUR PERSONALIZED STUDY PLAN:\n")
        
        for step, details in plan['study_plan'].items():
            if isinstance(details, dict):
                print(f"Step {step}: {details.get('title', '')}")
                print(f"  {details.get('description', '')}\n")
            else:
                print(f"{step}: {details}")
    else:
        print("❌ Failed to generate study plan")

if __name__ == "__main__":
    run_demo()