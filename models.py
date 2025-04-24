import uuid
from sqlalchemy import Column, Text, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Food(Base):
    __tablename__ = "foods"  # Matches the Supabase table name

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = Column(Text, unique=True, nullable=False)  # Matches "text" type in Supabase
    calories = Column(Numeric(5,2), nullable=False)
    protein = Column(Numeric(5,2), nullable=False)
    carbohydrates = Column(Numeric(5,2), nullable=False)  # Matches your "carbohydrates" column
    fat = Column(Numeric(5,2), nullable=False)  # Matches "fat" column instead of "fats"

