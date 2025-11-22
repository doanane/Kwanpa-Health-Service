import smtplib
import os
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from bson import ObjectId
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv  

from database import get_database, get_sync_database
from models import Profile, ProfileUpdate, ProjectCreate, ContactMessage

load_dotenv()

# Print debug info about environment variables
print(" Environment Variables Debug:")
print(f"   EMAIL_USER exists: {'EMAIL_USER' in os.environ}")
print(f"   EMAIL_PASSWORD exists: {'EMAIL_PASSWORD' in os.environ}")
print(f"   EMAIL_USER value: {os.getenv('EMAIL_USER', 'NOT_SET')}")
print(f"   EMAIL_PASSWORD length: {len(os.getenv('EMAIL_PASSWORD', ''))}")

from database import get_database, get_sync_database
from models import Profile, ProfileUpdate, ProjectCreate, ContactMessage

app = FastAPI(title="Portfolio API", version="1.0.0")

# CORS middleware - allow frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://frontend", "http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = get_database()
sync_db = get_sync_database()
profiles_collection = db.profiles
visitors_collection = db.visitors
messages_collection = db.messages

# Helper function to convert ObjectId to string
def convert_objectid_to_str(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, dict):
        return {key: convert_objectid_to_str(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_objectid_to_str(item) for item in obj]
    return obj

def initialize_default_profile():
    try:
        existing_profile = sync_db.profiles.find_one({"type": "main"})
        if not existing_profile:
            default_profile = {
                "type": "main",
                "name": "Desmond Opoku Anane",
                "title": "Software Engineer & Cybersecurity Analyst",
                "email": "anane365221@gmail.com",
                "phone": "+233 (0) 554640252",
                "location": "Accra, Ghana",
                "bio": "I am a Software Engineer and Cybersecurity Analyst committed to advancing my career in software development by working collaboratively with motivated, results-driven teams within dynamic and structured organizational environments.",
                "experience": "2+ years",
                "skills": ["React Native", "Python", "FastAPI", "Django", "TypeScript", "Node.js", "MySQL", "MongoDB", "AWS", "Cybersecurity"],
                "projects": [
                    {
                        "id": str(ObjectId()),
                        "name": "Saloon Connect",
                        "description": "A location-based platform connecting customers with nearby salons for easy booking and payments.",
                        "technologies": ["FastAPI", "React", "MongoDB", "JWT", "Payment Integration"],
                        "created_at": datetime.now(timezone.utc)
                    },
                    {
                        "id": str(ObjectId()),
                        "name": "AWS Employee Reward System",
                        "description": "Contributed to development of a global employee rewards monitoring system for AWS.",
                        "technologies": ["Next.js", "React", "REST APIs", "Data Visualization"],
                        "created_at": datetime.now(timezone.utc)
                    }
                ],
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            sync_db.profiles.insert_one(default_profile)
            print(" Default profile created in MongoDB")
        else:
            print(" Profile already exists in MongoDB")
    except Exception as e:
        print(f" Error initializing profile: {e}")

@app.on_event("startup")
async def startup_event():
    print("Starting FastAPI server...")
    print("Connecting to MongoDB...")
    await asyncio.get_event_loop().run_in_executor(None, initialize_default_profile)
    print(" Startup complete")

@app.get("/")
async def root():
    return {"message": "Portfolio API is running with Docker!"}

@app.get("/api/health")
async def health_check():
    try:
        await db.command("ping")
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": "All systems operational with Docker"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@app.get("/api/profile")
async def get_profile():
    try:
        profile = await profiles_collection.find_one({"type": "main"})
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        profile = convert_objectid_to_str(profile)
        return profile
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

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

# Email notification function
def send_email_notification(name: str, email: str, message: str):
    try:
        # Get environment variables with debugging
        sender_email = os.getenv("EMAIL_USER")
        sender_password = os.getenv("EMAIL_PASSWORD")
        
        print(f" DEBUG - Email Configuration:")
        print(f"   Sender Email: {sender_email}")
        print(f"   Password Length: {len(sender_password) if sender_password else 0}")
        print(f"   Password Set: {bool(sender_password)}")
        
        # Check if environment variables are set
        if not sender_email or not sender_password:
            print(" Email environment variables not set properly")
            print(f"   EMAIL_USER: {'SET' if sender_email else 'NOT SET'}")
            print(f"   EMAIL_PASSWORD: {'SET' if sender_password else 'NOT SET'}")
            return False
            
        receiver_email = "anane365221@gmail.com"
        
        print(f" Preparing to send email:")
        print(f"   From: {sender_email}")
        print(f"   To: {receiver_email}")
        print(f"   Subject: New contact from {name}")
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = f" Portfolio Contact: {name}"
        
        # Create email body
        body = f"""
        New contact form submission from your portfolio:
        
        Name: {name}
        Email: {email}
        Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}
        
        Message:
        {message}
        
        ---
        Sent from your portfolio website.
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        print(f" Connecting to SMTP server...")
        
        # Send email
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            print(f"    Connected to SMTP")
            server.starttls()
            print(f"    TLS started")
            (f"Attempting login...")
            server.login(sender_email, sender_password)
            print(f"    Login successful")
            print(f"    Sending message...")
            server.send_message(msg)
            print(f"    Message sent successfully!")
            
        print(f" Email sent successfully to {receiver_email}")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f" SMTP Authentication Failed: {e}")
        print(" Check your App Password and make sure 2FA is enabled")
        return False
        
    except Exception as e:
        print(f" Error sending email: {str(e)}")
        print(f"   Error type: {type(e).__name__}")
        return False
        
@app.post("/api/send-notification")
async def send_notification(notification: dict):
    try:
        name = notification.get('name', 'Unknown')
        email = notification.get('email', 'Unknown')
        message = notification.get('message', 'No message')
        subject = notification.get('subject', 'New Portfolio Contact')
        
        print(f" Received notification: {name} <{email}>")
        print(f" Message: {message}")
        
        # Try to send email
        email_sent = send_email_notification(name, email, message)
        
        if email_sent:
            response = {
                "message": " Email sent successfully!", 
                "email_sent": True,
                "notification": {
                    "name": name,
                    "email": email,
                    "subject": subject
                }
            }
            print(f" Notification processed: {response}")
            return response
        else:
            response = {
                "message": " Email not sent - check server logs", 
                "email_sent": False,
                "notification": {
                    "name": name,
                    "email": email,
                    "subject": subject
                }
            }
            print(f"Notification failed: {response}")
            return response
            
    except Exception as e:
        print(f" Error in send-notification: {e}")
        return {
            "message": f"Notification processing failed: {str(e)}",
            "email_sent": False,
            "error": str(e)
        }


@app.get("/api/debug-env")
async def debug_env():
    return {
        "email_user": os.getenv("EMAIL_USER", "NOT_SET"),
        "email_password_length": len(os.getenv("EMAIL_PASSWORD", "")),
        "email_password_set": bool(os.getenv("EMAIL_PASSWORD")),
        "all_env_vars": dict(os.environ)  # Be careful with this in production
    }

@app.post("/api/contact")
async def submit_contact(message: ContactMessage):
    try:
        message_data = {
            "name": message.name,
            "email": message.email,
            "message": message.message,
            "created_at": datetime.now(timezone.utc)
        }
        
        result = await messages_collection.insert_one(message_data)
        
        # Try to send notification (but don't fail if it doesn't work)
        try:
            notification_result = await send_notification({
                "name": message.name,
                "email": message.email,
                "message": message.message,
                "subject": "New Contact Form Submission"
            })
            print(f" Notification result: {notification_result}")
        except Exception as e:
            print(f" Notification failed but contact was saved: {e}")
        
        return {
            "message": "Contact form submitted successfully", 
            "id": str(result.inserted_id),
            "email_sent": True
        }
        
    except Exception as e:
        print(f" Error in contact submission: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)