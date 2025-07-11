# utils/auth.py
import os
from dotenv import load_dotenv
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client
from gotrue.errors import AuthApiError

# ─── Load .env (only for local dev) ───
load_dotenv()

# ─── Supabase client for Admin actions (service role) ───
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# security scheme for "Authorization: Bearer <token>"
bearer_scheme = HTTPBearer()

async def get_current_user_id(
    creds: HTTPAuthorizationCredentials = Security(bearer_scheme),
) -> str:
    """
    Validate the incoming JWT by calling Supabase Auth,
    return the user ID if valid, or raise 401 if not.
    """
    token = creds.credentials
    try:
        # This will raise AuthApiError if the token is invalid/expired
        resp = supabase.auth.get_user(token)
    except AuthApiError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired authentication token: {e}"
        )
    return resp.user.id

