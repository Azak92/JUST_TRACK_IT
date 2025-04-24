import asyncpg
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Read values from .env
USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")
HOST = os.getenv("HOST")
PORT = os.getenv("PORT")
DBNAME = os.getenv("DBNAME")

# Create the connection URL
DATABASE_URL = f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}"

# Function to connect to the PostgreSQL database
async def get_pg_connection():
    return await asyncpg.connect(DATABASE_URL)
