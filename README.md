# HEWAL3 Health Management System

## 🏥 Overview
HEWAL3 is an AI-powered health management system with emergency response capabilities, designed for chronic disease management with a focus on Ghanaian healthcare context.

## 🚀 Features
- **User Authentication**: JWT-based auth with Google OAuth integration
- **Health Dashboard**: Track steps, heart rate, sleep, and nutrition
- **AI Food Analysis**: Upload meal images for nutritional analysis using Azure AI Vision
- **Caregiver Portal**: Family/friends can monitor patient health
- **Doctor Dashboard**: Medical professionals can monitor assigned patients
- **Emergency Alerts**: Real-time vital monitoring with SMS alerts
- **Progress Tracking**: Weekly progress and achievement system

## 🏗️ Tech Stack
- **Backend**: FastAPI, Python 3.11+
- **Database**: PostgreSQL (Azure/Render)
- **Authentication**: JWT, Google OAuth
- **AI Services**: Azure AI Vision, Azure OpenAI
- **Email**: SendGrid
- **SMS**: Infobip
- **Storage**: Azure Blob Storage
- **Deployment**: Render (Backend), Vercel (Frontend)


API: http://localhost:8000

Docs: http://localhost:8000/docs

Redoc: http://localhost:8000/redoc