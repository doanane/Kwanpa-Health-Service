from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Project(BaseModel):
    id: str
    name: str
    description: str
    technologies: List[str] = []
    created_at: datetime

class Profile(BaseModel):
    id: Optional[str] = None
    name: str
    title: str
    email: str
    location: str
    bio: str
    experience: str
    skills: List[str] = []
    projects: List[Project] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    title: Optional[str] = None
    email: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    experience: Optional[str] = None
    skills: Optional[List[str]] = None

class ProjectCreate(BaseModel):
    name: str
    description: str
    technologies: List[str] = []

class ContactMessage(BaseModel):
    name: str
    email: str
    message: str