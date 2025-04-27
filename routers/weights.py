# routers/weights.py

from fastapi import APIRouter, Depends, HTTPException, status, Path
from typing import List
from uuid import uuid4, UUID

from schemas import WeightIn, WeightOut
from database import get_pg_connection

router = APIRouter(
    prefix="/weights",
    tags=["weights"],
)

@router.post(
    "/",
    response_model=WeightOut,
    status_code=status.HTTP_201_CREATED
)
async def log_weight(
    entry: WeightIn,
    conn = Depends(get_pg_connection),
):
    """
    Insert a new weight entry and return it (including generated id + logged_at).
    """
    new_id = str(uuid4())
    row = await conn.fetchrow(
        """
        INSERT INTO weight_logs (id, user_id, weight)
        VALUES ($1, $2, $3)
        RETURNING id, user_id, weight, logged_at
        """,
        new_id, str(entry.user_id), entry.weight
    )
    return row


@router.get(
    "/{user_id}",
    response_model=List[WeightOut]
)
async def get_weights(
    user_id: UUID = Path(..., description="UUID of the user"),
    conn = Depends(get_pg_connection),
):
    """
    Fetch all weight entries for a given user, newest first.
    """
    rows = await conn.fetch(
        """
        SELECT id, user_id, weight, logged_at
        FROM weight_logs
        WHERE user_id = $1
        ORDER BY logged_at DESC
        """,
        str(user_id)
    )
    return rows


@router.get(
    "/latest/{user_id}",
    response_model=WeightOut
)
async def get_latest_weight(
    user_id: UUID = Path(..., description="UUID of the user"),
    conn = Depends(get_pg_connection),
):
    """
    Fetch the single most recent weight entry for a user.
    """
    row = await conn.fetchrow(
        """
        SELECT id, user_id, weight, logged_at
        FROM weight_logs
        WHERE user_id = $1
        ORDER BY logged_at DESC
        LIMIT 1
        """,
        str(user_id)
    )
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No weight log found")
    return row


@router.delete(
    "/{entry_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a weight entry by its ID",
)
async def delete_weight(
    entry_id: UUID = Path(..., description="ID of the weight entry to remove"),
    conn = Depends(get_pg_connection),
):
    """
    Permanently remove a weight log. Returns 204 No Content on success,
    or 404 if no such entry exists.
    """
    result = await conn.execute(
        "DELETE FROM weight_logs WHERE id = $1",
        str(entry_id),
    )
    if result == "DELETE 0":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Weight entry not found"
        )
    # 204 No Content – nothing to return
