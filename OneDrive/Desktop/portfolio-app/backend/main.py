from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone
from bson import ObjectId
import asyncio

from database import get_database, get_sync_database
from models import Profile, ProfileUpdate, ProjectCreate, ContactMessage

app = FastAPI(title="Portfolio API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://127.0.0.1:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = get_database()
sync_db = get_sync_database()
profiles_collection = db.profiles
visitors_collection = db.visitors
messages_collection = db.messages

# FIX: Helper function to convert ObjectId to string
def convert_objectid_to_str(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, dict):
        return {key: convert_objectid_to_str(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_objectid_to_str(item) for item in obj]
    return obj

def initialize_default_profile():
    existing_profile = sync_db.profiles.find_one({"type": "main"})
    if not existing_profile:
        default_profile = {
            "type": "main",
            "name": "Alex Johnson",
            "title": "Full Stack Developer",
            "email": "alex.johnson@email.com",
            "location": "New York, USA",
            "bio": "Passionate developer creating amazing web experiences with Angular and FastAPI.",
            "experience": "3+ years",
            "skills": ["JavaScript", "TypeScript", "Angular", "Python", "FastAPI", "MongoDB"],
            "projects": [
                {
                    "id": str(ObjectId()),
                    "name": "E-Commerce Platform",
                    "description": "Full-stack e-commerce solution with Angular and FastAPI",
                    "technologies": ["Angular", "FastAPI", "MongoDB"],
                    "created_at": datetime.now(timezone.utc)
                }
            ],
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        sync_db.profiles.insert_one(default_profile)
        print("✅ Default profile created")

@app.on_event("startup")
async def startup_event():
    await asyncio.get_event_loop().run_in_executor(None, initialize_default_profile)

@app.get("/")
async def root():
    return {"message": "Portfolio API is running!"}

@app.get("/api/health")
async def health_check():
    try:
        await db.command("ping")
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }

@app.get("/api/profile")
async def get_profile():
    profile = await profiles_collection.find_one({"type": "main"})
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # FIX: Convert ObjectId to string
    profile = convert_objectid_to_str(profile)
    return profile

@app.put("/api/profile")
async def update_profile(profile_update: ProfileUpdate):
    update_data = {k: v for k, v in profile_update.dict().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    result = await profiles_collection.update_one(
        {"type": "main"},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Profile not found or no changes made")
    
    updated_profile = await profiles_collection.find_one({"type": "main"})
    # FIX: Convert ObjectId to string
    updated_profile = convert_objectid_to_str(updated_profile)
    return {"message": "Profile updated successfully", "profile": updated_profile}

@app.post("/api/projects")
async def create_project(project: ProjectCreate):
    new_project = {
        "id": str(ObjectId()),
        "name": project.name,
        "description": project.description,
        "technologies": project.technologies,
        "created_at": datetime.now(timezone.utc)
    }
    
    result = await profiles_collection.update_one(
        {"type": "main"},
        {"$push": {"projects": new_project}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return {"message": "Project added successfully", "project": new_project}

@app.get("/api/visitor-count")
async def get_visitor_count():
    visitor_data = await visitors_collection.find_one({"type": "counter"})
    
    if visitor_data:
        new_count = visitor_data["count"] + 1
        await visitors_collection.update_one(
            {"type": "counter"},
            {"$set": {"count": new_count, "last_visit": datetime.now(timezone.utc)}}
        )
    else:
        new_count = 1
        await visitors_collection.insert_one({
            "type": "counter",
            "count": new_count,
            "last_visit": datetime.now(timezone.utc)
        })
    
    return {"visitor_count": new_count}

@app.post("/api/contact")
async def submit_contact(message: ContactMessage):
    message_data = {
        "name": message.name,
        "email": message.email,
        "message": message.message,
        "created_at": datetime.now(timezone.utc)
    }
    
    result = await messages_collection.insert_one(message_data)
    
    return {"message": "Contact form submitted successfully", "id": str(result.inserted_id)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)