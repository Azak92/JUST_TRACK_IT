from fastapi import FastAPI
from routers import weights, foods, auth  # importing modular route groups
from dotenv import load_dotenv

load_dotenv() 
app = FastAPI()

# Plug in routers (all route logic is elsewhere)
app.include_router(auth.router)
app.include_router(foods.router)
app.include_router(weights.router)

# Optional root route
@app.get("/")
async def read_root():
    return {"message": "Hello FastAPI"}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=10000,
        reload=True
    )
