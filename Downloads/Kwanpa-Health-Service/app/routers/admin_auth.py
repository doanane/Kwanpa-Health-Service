
@router.post("/admin/create-user")
async def admin_create_user(
    email: str,
    role: str,
    current_admin: Admin = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    """Admin creates user with specific role"""
    
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    
    import secrets
    temp_password = secrets.token_urlsafe(12)
    
    user = User(
        email=email,
        hashed_password=get_password_hash(temp_password),
        is_email_verified=False,
        role=role  
    )
    
    db.add(user)
    db.commit()
    
    
    from app.services.email_service import email_service
    email_service.send_user_invitation(email, temp_password, role)
    
    return {
        "message": f"User created with {role} role",
        "temporary_password": temp_password,  
        "note": "User must change password on first login"
    }