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
    logged_at: datetime   # match your actual column name

@router.post("/", response_model=WeightResponse)
async def add_weight(
    req: WeightRequest,
    user_id: str = Depends(get_current_user_id),
):
    """
    Inserts a new row into the `weight_logs` table via Supabase REST.
    """
    row = {"user_id": user_id, "weight": req.weight}

    try:
        resp = (
            supabase
            .from_("weight_logs")   # ← your real table name
            .insert([row])          # insert expects a list
            .execute()
        )
    except APIError as e:
        # network/404/etc
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Supabase insert error: {e}"
        )

    # At this point resp.data should be a list with your new record
    try:
        inserted = resp.data[0]
    except (IndexError, TypeError):
        # truly unexpected: no data back
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Insert failed: no data returned"
        )

    # Return exactly what came back
    return WeightResponse(
        id=inserted["id"],
        user_id=inserted["user_id"],
        weight=inserted["weight"],
        logged_at=inserted["logged_at"],
    )
