import os
import logging
from urllib.parse import quote
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel, EmailStr
from backend.app.db.supabase_client import supabase

router = APIRouter(prefix="/auth", tags=["Authentication"])

SUPABASE_URL = os.getenv("SUPABASE_URL")
REDIRECT_URL = os.getenv("GOOGLE_REDIRECT_URL", "http://localhost:8000/auth/callback")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SignupModel(BaseModel):
    username: str
    email: EmailStr
    password: str

class LoginModel(BaseModel):
    email: EmailStr
    password: str

@router.post("/signup")
async def signup_user(data: SignupModel):
    logger.info(f"Signup attempt for email: {data.email}")
    response = supabase.auth.sign_up({
        "email": data.email,
        "password": data.password
    })
    if response.user:
        supabase.auth.api.update_user_by_id(
            response.user.id,
            {"data": {"username": data.username}}
        )
        logger.info(f"User signed up successfully: {data.email}")
        return JSONResponse(content={"message": "User signed up successfully", "email": response.user.email})
    else:
        logger.warning(f"Signup failed for email: {data.email}, reason: {response.message}")
        raise HTTPException(status_code=400, detail=response.message or "Signup failed")

@router.post("/login")
async def login_user(data: LoginModel):
    logger.info(f"Login attempt for email: {data.email}")
    response = supabase.auth.sign_in_with_password({
        "email": data.email,
        "password": data.password
    })
    if response.user:
        logger.info(f"User logged in successfully: {data.email}")
        return {
            "message": "Login successful",
            "access_token": response.session.access_token,
            "user": response.user.email
        }
    else:
        logger.warning(f"Login failed for email: {data.email}")
        raise HTTPException(status_code=401, detail="Invalid credentials")

@router.get("/login/google")
async def login_google():
    redirect_url_encoded = quote(REDIRECT_URL, safe='')
    google_login_url = f"{SUPABASE_URL}/auth/v1/authorize?provider=google&redirect_to={redirect_url_encoded}"
    logger.info(f"Redirecting to Google OAuth login: {google_login_url}")
    return RedirectResponse(url=google_login_url)

@router.get("/callback")
async def oauth_callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        logger.error("OAuth callback missing 'code' parameter")
        raise HTTPException(status_code=400, detail="Invalid OAuth callback: missing 'code'")
    
    response = supabase.auth.exchange_code_for_session({"code": code})
    if not response or not response.user:
        logger.error("OAuth login failed, invalid response from Supabase")
        raise HTTPException(status_code=401, detail="OAuth login failed")

    logger.info(f"Google OAuth login successful for user: {response.user.email}")
    return {
        "message": "Google login successful",
        "user": response.user.email,
        "access_token": response.session.access_token
    }
