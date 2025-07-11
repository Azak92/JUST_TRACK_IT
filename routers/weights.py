from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from datetime import datetime
from utils.auth import supabase, get_current_user_id

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
    Inserts a new weight row via Supabase's PostgREST API.
    """
    # Build your row
    row = {
        "user_id": user_id,
        "weight": req.weight,
    }

    # Use the Supabase client to insert over HTTPS
    resp = (
        supabase
        .table("weights")
        .insert(row)
        .execute()
    )

    # Check for errors
    if resp.error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Insert failed: {resp.error.message}"
        )

    # resp.data is a list of the inserted rows
    inserted = resp.data[0]

    # Return as your Pydantic response model
    return WeightResponse(
        id=inserted["id"],
        user_id=inserted["user_id"],
        weight=inserted["weight"],
        recorded_at=inserted["recorded_at"],
    )
