from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class FoodIn(BaseModel):
    name: str
    calories: float
    protein: float
    carbohydrates: float
    fat: float

class FoodOut(FoodIn):
    id: UUID

# this is input from user
class WeightIn(BaseModel):
    user_id: UUID
    weight: float

# This is output and update from database
class WeightOut(WeightIn):
    id: UUID
    logged_at: datetime