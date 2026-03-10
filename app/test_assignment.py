import requests
import json

BASE_URL = "http://localhost:8000"

def test_assignment_requirements():
    print("\n📋 TESTING ASSIGNMENT REQUIREMENTS\n")
    
    tests_passed = 0
    total_tests = 6
    
    # 1. Test API is running
    try:
        response = requests.get(BASE_URL)
        if response.status_code == 200:
            print("✅ API is running")
            tests_passed += 1
        else:
            print("❌ API not responding")
    except:
        print("❌ Cannot connect to API")
    
    # 2. Test start session
    response = requests.post(f"{BASE_URL}/start-session", 
                           json={"user_id": "test"})
    if response.status_code == 200:
        data = response.json()
        if "session_id" in data and "first_question" in data:
            print("✅ Can start session and get first question")
            tests_passed += 1
            session_id = data["session_id"]
        else:
            print("❌ Start session response missing fields")
    else:
        print("❌ Cannot start session")
    
    # 3. Test answer submission
    if 'session_id' in locals():
        # Get first question
        response = requests.get(f"{BASE_URL}/session/{session_id}")
        if response.status_code == 200:
            print("✅ Can get session status")
            tests_passed += 1
    
    # 4. Test database seeding
    response = requests.get(f"{BASE_URL}/api/questions/questions")
    if response.status_code == 200:
        questions = response.json()
        if len(questions) >= 20:
            print(f"✅ Database has {len(questions)} questions (minimum 20)")
            tests_passed += 1
        else:
            print(f"❌ Only {len(questions)} questions found")
    else:
        print("❌ Cannot fetch questions")
    
    # 5. Test topics
    response = requests.get(f"{BASE_URL}/api/questions/topics")
    if response.status_code == 200:
        topics = response.json().get("topics", [])
        if len(topics) > 0:
            print(f"✅ Found {len(topics)} topics: {', '.join(topics[:3])}")
            tests_passed += 1
        else:
            print("❌ No topics found")
    
    # 6. Test adaptive algorithm (simulate one answer)
    if 'session_id' in locals():
        # Get first question
        start_resp = requests.post(f"{BASE_URL}/start-session", 
                                  json={"user_id": "test"})
        if start_resp.status_code == 200:
            session = start_resp.json()
            question = session["first_question"]
            
            # Submit answer
            answer_resp = requests.post(f"{BASE_URL}/submit-answer", json={
                "session_id": session["session_id"],
                "question_id": question["_id"],
                "user_answer": question["correct_answer"],
                "time_taken": 30
            })
            
            if answer_resp.status_code == 200:
                result = answer_resp.json()
                if "current_ability" in result:
                    print("✅ Adaptive algorithm working")
                    tests_passed += 1
                else:
                    print("❌ Adaptive algorithm not returning ability")
            else:
                print("❌ Cannot submit answer")
    
    # Summary
    print(f"\n📊 Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("\n🎉 All requirements met! Ready for submission!")
    else:
        print(f"\n⚠️  {total_tests - tests_passed} requirements not met")

if __name__ == "__main__":
    test_assignment_requirements()