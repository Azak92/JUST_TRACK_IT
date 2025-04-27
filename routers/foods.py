from fastapi import APIRouter, Depends, HTTPException, status, Path
from typing import List
from uuid import uuid4, UUID

from database import get_pg_connection
from schemas import FoodIn, FoodOut

router = APIRouter(
    prefix="/foods",
    tags=["foods"],
)

@router.post(
    "/",
    response_model=FoodOut,
    status_code=status.HTTP_201_CREATED,
)
async def add_food(
    food: FoodIn,
    conn = Depends(get_pg_connection),
):
    """
    Create a new food item. Enforces uniqueness at the DB level.
    """
    new_id = str(uuid4())
    try:
        row = await conn.fetchrow(
            """
            INSERT INTO foods (id, name, calories, protein, carbohydrates, fat)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING id, name, calories, protein, carbohydrates, fat
            """,
            new_id, food.name, food.calories,
            food.protein, food.carbohydrates, food.fat
        )
    except Exception as e:
        # e.g. UNIQUE violation
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Food with that name already exists."
        )
    return row


@router.get(
    "/",
    response_model=List[FoodOut]
)
async def get_foods(
    conn = Depends(get_pg_connection),
):
    """
    Return all foods.
    """
    rows = await conn.fetch(
        "SELECT id, name, calories, protein, carbohydrates, fat FROM foods"
    )
    return rows


@router.get(
    "/{food_id}",
    response_model=FoodOut
)
async def get_food(
    food_id: UUID = Path(..., description="UUID of the food item"),
    conn = Depends(get_pg_connection),
):
    """
    Fetch a single food by its ID.
    """
    row = await conn.fetchrow(
        "SELECT id, name, calories, protein, carbohydrates, fat FROM foods WHERE id = $1",
        str(food_id)
    )
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food not found")
    return row


@router.put(
    "/{food_id}",
    response_model=FoodOut
)
async def update_food(
    food_id: UUID = Path(..., description="UUID of the food item"),
    food: FoodIn = ...,
    conn = Depends(get_pg_connection),
):
    """
    Update all nutritional fields of a food item.
    """
    row = await conn.fetchrow(
        """
        UPDATE foods
        SET name = $1, calories = $2, protein = $3, carbohydrates = $4, fat = $5
        WHERE id = $6
        RETURNING id, name, calories, protein, carbohydrates, fat
        """,
        food.name, food.calories,
        food.protein, food.carbohydrates, food.fat,
        str(food_id)
    )
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food not found")
    return row


@router.delete(
    "/{food_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_food(
    food_id: UUID = Path(..., description="UUID of the food item"),
    conn = Depends(get_pg_connection),
):
    """
    Permanently remove a food item.
    """
    result = await conn.execute(
        "DELETE FROM foods WHERE id = $1",
        str(food_id)
    )
    if result == "DELETE 0":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food not found")
    # returns 204 No Content
