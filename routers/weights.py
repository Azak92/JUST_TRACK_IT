from fastapi import APIRouter, HTTPException
from schemas import WeightIn, WeightOut
from database import get_pg_connection
import uuid

router = APIRouter()

# POST: log new weight
@router.post("/weights", response_model=WeightOut)
async def log_weight(entry: WeightIn):
    conn = await get_pg_connection()
    weight_id = str(uuid.uuid4())

    await conn.execute(
        """
        INSERT INTO weight_logs (id, user_id, weight)
        VALUES ($1, $2, $3)
        """,
        weight_id, entry.user_id, entry.weight
    )

    weight_row = await conn.fetchrow(
        "SELECT * FROM weight_logs WHERE id = $1", weight_id
    )

    await conn.close()
    return dict(weight_row)

# GET: all weights for a user
@router.get("/weights/{user_id}", response_model=list[WeightOut])
async def get_weights(user_id: uuid.UUID):
    conn = await get_pg_connection()
    rows = await conn.fetch(
        "SELECT * FROM weight_logs WHERE user_id = $1 ORDER BY logged_at DESC",
        str(user_id)
    )
    await conn.close()
    return [dict(row) for row in rows]

# GET: latest weight for a user
@router.get("/weights/latest/{user_id}", response_model=WeightOut)
async def get_latest_weight(user_id: uuid.UUID):
    conn = await get_pg_connection()
    row = await conn.fetchrow(
        """
        SELECT * FROM weight_logs
        WHERE user_id = $1
        ORDER BY logged_at DESC
        LIMIT 1
        """,
        str(user_id)
    )
    await conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="No weight log found")

    return dict(row)
