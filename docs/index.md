# HEWAL3 Health API Documentation

This is the backend API for HEWAL3 Health Management System.

## API Endpoints

- `POST /auth/login` - User login
- `POST /auth/signup` - User registration
- `POST /admin/create-doctor` - Create doctor accounts
- `GET /health/dashboard` - Get health dashboard
- etc.

## Development

To run locally:
```bash
uvicorn app.main:app --reload