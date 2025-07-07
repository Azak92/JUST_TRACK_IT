from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from utils.auth import supabase

router = APIRouter(prefix="/auth", tags=["auth"])

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str

@router.post("/login", response_model=LoginResponse)
async def login(req: LoginRequest):
    """
    Sign in a user via Supabase Auth and return
    the access & refresh tokens.
    """
    resp = supabase.auth.sign_in_with_password({
        "email":    req.email,
        "password": req.password,
    })
    if resp.get("error"):
        # Supabase returns {"error": {...}} on failure
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=resp["error"]["message"]
        )
    # On success, `data.session` holds both tokens:
    session = resp["data"]["session"]
    return {
        "access_token":  session["access_token"],
        "refresh_token": session["refresh_token"],
    }
