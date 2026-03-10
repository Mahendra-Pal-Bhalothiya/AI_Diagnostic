from fastapi import APIRouter, HTTPException
from app.models.database import get_collection_async
from bson import ObjectId
from typing import Optional

router = APIRouter()

@router.get("/")
async def get_users():
    """Get all users"""
    try:
        collection = await get_collection_async("users")
        users = await collection.find().to_list(100)
        
        # Convert ObjectId to string for JSON serialization
        for user in users:
            user["_id"] = str(user["_id"])
        
        return {"users": users}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}")
async def get_user(user_id: str):
    """Get a specific user by ID"""
    try:
        collection = await get_collection_async("users")
        user = await collection.find_one({"_id": ObjectId(user_id)})
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user["_id"] = str(user["_id"])
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
async def create_user(user_data: dict):
    """Create a new user"""
    try:
        collection = await get_collection_async("users")
        result = await collection.insert_one(user_data)
        
        created_user = await collection.find_one({"_id": result.inserted_id})
        created_user["_id"] = str(created_user["_id"])
        
        return created_user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))