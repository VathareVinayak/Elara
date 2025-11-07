import os
import logging
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel, EmailStr
from urllib.parse import quote
from backend.app.db.supabase_client import supabase

router = APIRouter(prefix="/auth", tags=["Authentication"])

SUPABASE_URL = os.getenv("SUPABASE_URL")
REDIRECT_URL = os.getenv("GOOGLE_REDIRECT_URL", "http://localhost:8000/auth/callback")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ---------------------------- MODELS ----------------------------
class SignupModel(BaseModel):
    email: EmailStr
    password: str
    username: str | None = None


class LoginModel(BaseModel):
    email: EmailStr
    password: str


# ---------------------------- SIGNUP ----------------------------
@router.post("/signup")
async def signup_user(data: SignupModel):
    """
    Create a user using Supabase built-in auth
    """
    try:
        logger.info(f"Signup attempt for: {data.email}")
        response = supabase.auth.sign_up({
            "email": data.email,
            "password": data.password,
        })

        if response.user:
            logger.info(f"✅ Signup success for: {data.email}")
            return JSONResponse(content={
                "message": "User signed up successfully",
                "user": {
                    "id": response.user.id,
                    "email": response.user.email
                }
            })

        raise HTTPException(status_code=400, detail="Signup failed")

    except Exception as e:
        logger.error(f"❌ Signup error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


# ---------------------------- LOGIN ----------------------------
@router.post("/login")
async def login_user(data: LoginModel):
    """
    Login user using Supabase built-in password auth
    """
    try:
        logger.info(f"Login attempt for: {data.email}")
        response = supabase.auth.sign_in_with_password({
            "email": data.email,
            "password": data.password
        })

        if response.session:
            logger.info(f"✅ Login success for: {data.email}")
            return {
                "message": "Login successful",
                "access_token": response.session.access_token,
                "refresh_token": response.session.refresh_token,
                "user": {
                    "id": response.user.id,
                    "email": response.user.email
                }
            }

        raise HTTPException(status_code=401, detail="Invalid credentials")

    except Exception as e:
        logger.error(f"❌ Login failed: {str(e)}")
        raise HTTPException(status_code=401, detail=str(e))


# ---------------------------- GOOGLE OAUTH ----------------------------
@router.get("/login/google")
async def login_google():
    """
    Redirect user to Supabase Google OAuth page
    """
    redirect_url_encoded = quote(REDIRECT_URL, safe='')
    google_url = f"{SUPABASE_URL}/auth/v1/authorize?provider=google&redirect_to={redirect_url_encoded}"
    logger.info(f"🔗 Redirecting to Google OAuth: {google_url}")
    return RedirectResponse(url=google_url)


# ---------------------------- OAUTH CALLBACK ----------------------------
@router.get("/callback")
async def oauth_callback(request: Request):
    """
    Handle Google OAuth redirect callback
    """
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Missing OAuth 'code' parameter")

    try:
        response = supabase.auth.exchange_code_for_session({"code": code})
        if not response or not response.user:
            raise HTTPException(status_code=401, detail="OAuth login failed")

        logger.info(f"✅ Google OAuth login success: {response.user.email}")
        return {
            "message": "Google login successful",
            "user": {
                "email": response.user.email,
                "id": response.user.id
            },
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token
        }
    except Exception as e:
        logger.error(f"❌ OAuth callback failed: {str(e)}")
        raise HTTPException(status_code=401, detail=str(e))


# ---------------------------- CURRENT USER ----------------------------
@router.get("/user")
async def get_current_user(request: Request):
    """
    Validate access token and return the current user
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = auth_header.split("Bearer ")[1]
    try:
        response = supabase.auth.get_user(token)
        if response and response.user:
            return {"user": response.user}
        else:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
    except Exception as e:
        logger.error(f"❌ Token validation failed: {str(e)}")
        raise HTTPException(status_code=401, detail=str(e))


# ---------------------------- LOGOUT ----------------------------
@router.post("/logout")
async def logout_user():
    """
    Invalidate current Supabase session
    """
    try:
        supabase.auth.sign_out()
        logger.info("✅ User logged out successfully")
        return {"message": "Logged out successfully"}
    except Exception as e:
        logger.error(f"❌ Logout failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
