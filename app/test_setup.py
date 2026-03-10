import os
from dotenv import load_dotenv
import pymongo
import requests

load_dotenv()

print("\n🔧 TESTING SETUP\n")

# Test MongoDB
try:
    client = pymongo.MongoClient(os.getenv("MONGODB_URL"))
    client.admin.command('ping')
    print("✅ MongoDB: Connected")
    
    # Check database
    db = client[os.getenv("MONGODB_DB_NAME", "adaptive_testing")]
    count = db.questions.count_documents({})
    print(f"✅ Database: {count} questions found")
except Exception as e:
    print(f"❌ MongoDB: {e}")

# Test API
try:
    response = requests.get("http://localhost:8000/")
    if response.status_code == 200:
        print("✅ API Server: Running")
    else:
        print("❌ API Server: Not responding correctly")
except:
    print("❌ API Server: Not running (start with 'uvicorn app.main:app --reload')")

# Check environment
print(f"\n✅ Python path: {os.getcwd()}")
print(f"✅ Virtual env: {os.environ.get('VIRTUAL_ENV', 'Not activated')}")