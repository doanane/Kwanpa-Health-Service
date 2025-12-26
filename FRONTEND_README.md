# HEWAL3 Backend API - Ready for Frontend Integration

## Base URL
- Local: `http://localhost:8000`
- Production: `https://hewal3-backend-api-aya3dzgefte4b3c3.southafricanorth-01.azurewebsites.net`

## Quick Start
1. Make sure backend is running: `python start.py`
2. Visit `http://localhost:8000/docs` for interactive API docs
3. Use endpoints below

## Key Endpoints

### Authentication
- `POST /auth/signup` - Register new user
- `POST /auth/login` - Login with email/password
- `POST /auth/login/otp/request` - Request OTP login
- `POST /auth/login/otp/verify` - Verify OTP
- `POST /auth/forgot-password` - Request password reset
- `POST /auth/reset-password` - Reset password
- `GET /auth/me` - Get current user info
- `POST /auth/logout` - Logout

### User Management
- `GET /users/profile` - Get user profile
- `PUT /users/profile` - Update profile
- `GET /users/me` - Get current user
- `GET /users/search` - Search users

### Health Data
- `GET /health/dashboard` - Health dashboard
- `POST /health/health-data` - Add health data
- `GET /health/health-snapshot` - Latest health data
- `POST /health/food-log` - Log food

### Food Analysis
- `POST /api/analyze-meal` - Analyze food image
- `GET /api/recent-meals` - Get recent meals
- `GET /api/daily-tip` - Get daily health tip

### Caregivers
- `GET /caregivers/profile` - Get caregiver profile
- `GET /caregivers/patients` - Get assigned patients
- `POST /caregivers/connect-patient` - Connect with patient
- `GET /caregivers/my-id` - Get caregiver ID

### Doctors
- `POST /doctors/login` - Doctor login
- `GET /doctors/me` - Get doctor profile
- `GET /doctors/dashboard` - Doctor dashboard
- `GET /doctors/patients` - Get doctor's patients
- `GET /doctors/patients/{id}/dashboard` - Patient dashboard

### Notifications
- `GET /notifications/` - Get all notifications
- `GET /notifications/unread-count` - Unread count

### Leaderboard
- `GET /leaderboard/weekly` - Weekly leaderboard
- `GET /leaderboard/history` - Progress history

## Authentication Flow
1. User signs up at `/auth/signup`
2. Gets JWT token in response
3. Include token in header: `Authorization: Bearer <token>`
4. Token expires in 30 minutes, refresh if needed

## Testing Credentials
For testing without email verification, you can:
1. Sign up any email
2. Manually set `is_email_verified = true` in database
3. Or use OTP login which doesn't require verification

## Error Responses
All endpoints return standard HTTP status codes:
- 200: Success
- 400: Bad request
- 401: Unauthorized
- 403: Forbidden
- 404: Not found
- 500: Server error

## File Uploads
For profile images and food analysis:
- Use `multipart/form-data`
- Max file size: 5MB for images
- Supported formats: JPG, PNG, GIF, WebP

## Need Help?
- Check `/docs` for interactive API testing
- Check `/health` for system status
- Check logs for detailed errors