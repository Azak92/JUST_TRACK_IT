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
    """
    Inserts a new row into the `weight_logs` table via Supabase's REST API.
    """
    row = {"user_id": user_id, "weight": req.weight}

    try:
        resp = (
            supabase
            .from_("weight_logs")      # ← use your actual table name
            .insert([row])             # insert expects a list of rows
            .execute()
        )
    except APIError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Supabase insert error: {e}"
        )

    if resp.error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Insert failed: {resp.error.message}"
        )

    inserted = resp.data[0]

    return WeightResponse(
        id=inserted["id"],
        user_id=inserted["user_id"],
        weight=inserted["weight"],
        recorded_at=inserted["recorded_at"],
    )
