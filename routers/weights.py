# routers/weights.py

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from datetime import datetime
from utils.auth import supabase, get_current_user_id
from postgrest.exceptions import APIError

router = APIRouter(prefix="/weights", tags=["weights"])

class WeightRequest(BaseModel):
    weight: float

class WeightResponse(BaseModel):
    id: int
    user_id: str
    weight: float
    recorded_at: datetime

@router.post("/", response_model=WeightResponse)
async def add_weight(
    req: WeightRequest,
    user_id: str = Depends(get_current_user_id),
):
    row = {"user_id": user_id, "weight": req.weight}

    try:
        resp = (
            supabase
            .from_("weight_logs")   # ← your actual table name
            .insert([row])          # always wrap row in a list
            .execute()
        )
    except APIError as e:
        # network or path‐not‐found errors bubble up as APIError
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Supabase insert error: {e}"
        )

    # Now check the HTTP status code instead of resp.error
    code = getattr(resp, "status_code", None)
    if code is None or code >= 300:
        # resp.data might contain more info in error cases
        detail = resp.data or f"HTTP {code}"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Insert failed: {detail}"
        )

    # resp.data is a list of inserted records
    inserted = resp.data[0]

    return WeightResponse(
        id=inserted["id"],
        user_id=inserted["user_id"],
        weight=inserted["weight"],
        recorded_at=inserted["recorded_at"],
    )
