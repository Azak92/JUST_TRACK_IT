# routers/weights.py

from fastapi import APIRouter, Depends, HTTPException, status, Path
from typing import List
from uuid import uuid4, UUID

from schemas import WeightIn, WeightOut
from database import get_pg_connection
from utils.auth import get_current_user_id

router = APIRouter(
    prefix="/weights",
    tags=["weights"],
)

@router.post(
    "/",
    response_model=WeightOut,
    status_code=status.HTTP_201_CREATED,
)
async def log_weight(
    entry: WeightIn,
    user_id: str = Depends(get_current_user_id),
    conn = Depends(get_pg_connection),
):
    """
    Create a new weight log for the authenticated user and return it.
    """
    new_id = str(uuid4())
    record = await conn.fetchrow(
        """
        INSERT INTO weight_logs (id, user_id, weight)
        VALUES ($1, $2, $3)
        RETURNING id, user_id, weight, logged_at
        """,
        new_id, user_id, entry.weight,
    )
    return dict(record)


@router.get(
    "/",
    response_model=List[WeightOut],
)
async def get_weights(
    user_id: str = Depends(get_current_user_id),
    conn = Depends(get_pg_connection),
):
    """
    Fetch all weight entries for the authenticated user, newest first.
    """
    rows = await conn.fetch(
        """
        SELECT id, user_id, weight, logged_at
        FROM weight_logs
        WHERE user_id = $1
        ORDER BY logged_at DESC
        """,
        user_id,
    )
    return [dict(r) for r in rows]


@router.get(
    "/latest",
    response_model=WeightOut,
)
async def get_latest_weight(
    user_id: str = Depends(get_current_user_id),
    conn = Depends(get_pg_connection),
):
    """
    Fetch the single most recent weight entry for the authenticated user.
    """
    record = await conn.fetchrow(
        """
        SELECT id, user_id, weight, logged_at
        FROM weight_logs
        WHERE user_id = $1
        ORDER BY logged_at DESC
        LIMIT 1
        """,
        user_id,
    )
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No weight log found"
        )
    return dict(record)


@router.delete(
    "/{entry_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_weight(
    entry_id: UUID = Path(..., description="ID of the weight entry to remove"),
    user_id: str = Depends(get_current_user_id),
    conn = Depends(get_pg_connection),
):
    """
    Permanently remove a weight log belonging to the authenticated user.
    Returns 204 No Content on success or 404 if not found.
    """
    result = await conn.execute(
        "DELETE FROM weight_logs WHERE id = $1 AND user_id = $2",
        str(entry_id), user_id,
    )
    if result == "DELETE 0":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Weight entry not found"
        )
    # 204 No Content implicitly returns None
