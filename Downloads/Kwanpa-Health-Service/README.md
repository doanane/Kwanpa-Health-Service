# HEWAL3 Health Management System

## Overview

HEWAL3 is an AI-powered health management system with emergency response capabilities, designed for chronic disease management with a focus on Ghanaian healthcare context.

## Features

- **User Authentication**: JWT-based auth with Google OAuth integration
- **Health Dashboard**: Track steps, heart rate, sleep, and nutrition
- **AI Food Analysis**: Upload meal images for nutritional analysis using Azure AI Vision
- **Caregiver Portal**: Family/friends can monitor patient health
- **Doctor Dashboard**: Medical professionals can monitor assigned patients
- **Emergency Alerts**: Real-time vital monitoring with SMS alerts
- **Progress Tracking**: Weekly progress and achievement system

## Tech Stack

- **Backend**: FastAPI, Python 3.11+
- **Database**: PostgreSQL (Azure/Render)
- **Authentication**: JWT, Google OAuth
- **AI Services**: Azure AI Vision, Azure OpenAI
- **Email**: SendGrid
- **SMS**: Infobip
- **Storage**: Azure Blob Storage
- **Deployment**: Render (Backend), Vercel (Frontend)

## 🚀 Quick Start

# One line terminal command to run the backend:

```PowerShell
python -m venv venv
if ($?) { .\venv\Scripts\Activate.ps1 }
if ($?) { pip install -r requirements.txt }
if ($?) { uvicorn app.main:app --reload --host 0.0.0.0 }
```

### Prerequisites

- Python 3.11+
- PostgreSQL
- Node.js (for frontend)

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/imaginehewal3-26.git
   cd imaginehewal3-26/back
   ```

2. **Create a virtual environment**

   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\activate
   ```

   <!-- # Linux/Mac -->
   <!-- source venv/bin/activate -->
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configuration**
   Copy the example environment file and update it with your credentials:

   ```bash
   cp .env.example .env
   ```

   _Make sure to set your `DATABASE_URL`, `AZURE_AI_VISION_KEY`, and `AZURE_OPENAI_KEY`._

5. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```
   The API will be available at `http://localhost:8000`.

### 🐳 Docker Support

You can also run the backend using Docker:

```bash
docker build -t hewal3-backend .
docker run -p 8000:8000 --env-file .env hewal3-backend
```

## 🔗 Links

- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **Redoc**: http://localhost:8000/redoc
