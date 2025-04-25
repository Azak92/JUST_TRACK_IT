from fastapi import FastAPI, HTTPException
from database import get_pg_connection
from schemas import FoodIn, FoodOut
import uuid
from routers import weights

app = FastAPI()
app.include_router(weights.router)

# CREATE: Add a new food
@app.post("/foods", response_model=FoodOut)
async def add_food(food: FoodIn):
    conn = await get_pg_connection()

    # Generate new UUID
    food_id = str(uuid.uuid4())

    # Check if food already exists
    existing = await conn.fetchval("SELECT COUNT(*) FROM foods WHERE name = $1", food.name)
    if existing > 0:
        raise HTTPException(status_code=400, detail="Food already exists")

    # Insert new food
    await conn.execute(
        "INSERT INTO foods (id, name, calories, protein, carbohydrates, fat) VALUES ($1, $2, $3, $4, $5, $6)",
        food_id, food.name, food.calories, food.protein, food.carbohydrates, food.fat
    )
    await conn.close()
    return FoodOut(id=food_id, **food.dict())

# READ: Get all foods
@app.get("/foods")
async def get_foods():
    conn = await get_pg_connection()
    rows = await conn.fetch("SELECT * FROM foods")
    await conn.close()
    return {"foods": [dict(row) for row in rows]}

# READ: Get a single food by UUID
@app.get("/foods/{food_id}", response_model=FoodOut)
async def get_food(food_id: uuid.UUID):
    conn = await get_pg_connection()
    food = await conn.fetchrow("SELECT * FROM foods WHERE id = $1", str(food_id))
    await conn.close()

    if not food:
        raise HTTPException(status_code=404, detail="Food not found")
    return FoodOut(**dict(food))

# UPDATE: Modify an Existing Food by UUID
@app.put("/foods/{food_id}", response_model=FoodOut)
async def update_food(food_id: uuid.UUID, food: FoodIn):
    conn = await get_pg_connection()

    # Check if food exists
    existing = await conn.fetchval("SELECT COUNT(*) FROM foods WHERE id = $1", str(food_id))
    if existing == 0:
        raise HTTPException(status_code=404, detail="Food not found")

    # Update food
    await conn.execute(
        "UPDATE foods SET name = $1, calories = $2, protein = $3, carbohydrates = $4, fat = $5 WHERE id = $6",
        food.name, food.calories, food.protein, food.carbohydrates, food.fat, str(food_id)
    )
    await conn.close()
    return FoodOut(id=food_id, **food.dict())

# DELETE: Remove a Food Item by UUID
@app.delete("/foods/{food_id}")
async def delete_food(food_id: uuid.UUID):
    conn = await get_pg_connection()

    # Check if food exists
    existing = await conn.fetchval("SELECT COUNT(*) FROM foods WHERE id = $1", str(food_id))
    if existing == 0:
        raise HTTPException(status_code=404, detail="Food not found")

    # Delete food
    await conn.execute("DELETE FROM foods WHERE id = $1", str(food_id))
    await conn.close()
    return {"message": "Food deleted successfully!"}

# Root endpoint
@app.get("/")
async def read_root():
    return {"message": "Hello FastAPI"}
