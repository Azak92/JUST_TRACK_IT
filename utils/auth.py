import os
from jose import jwt, JWTError
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# fastapi will read the "Authorization: Bearer <token>" header
bearer_scheme = HTTPBearer()

async def get_current_user_id(
    creds: HTTPAuthorizationCredentials = Security(bearer_scheme),
) -> str:
    token = creds.credentials
    try:
        # decode with your Supabase JWT secret
        payload = jwt.decode(
            token,
            os.getenv("SUPABASE_JWT_SECRET"),
            algorithms=["HS256"],
            options={"verify_aud": False},  # Supabase tokens may omit "aud"
        )
        user_id: str = payload.get("sub")
        if not user_id:
            raise JWTError("Missing subject claim")
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
        )
    return user_id
