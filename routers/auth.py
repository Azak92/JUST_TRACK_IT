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
async def login(req: LoginRequest) -> LoginResponse:
    """
    Sign in a user via Supabase Auth and return
    the access & refresh tokens.
    """
    # sign_in_with_password() returns an AuthResponse object
    resp = supabase.auth.sign_in_with_password({
        "email":    req.email,
        "password": req.password,
    })

    # Use attribute access, not dict.get()
    if resp.error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=resp.error.message or "Authentication failed"
        )

    # resp.data.session is a Session object with .access_token and .refresh_token
    session = resp.data.session

    # Return your Pydantic model explicitly
    return LoginResponse(
        access_token=session.access_token,
        refresh_token=session.refresh_token,
    )
