import sys
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure backend directory is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import engine, Base
from backend.routes.routes import router as api_router

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Personalized Networking Assistant",
    description="AI-powered assistant for generating personalized networking conversation starters.",
    version="1.0.0"
)

# Configure CORS so Streamlit client can interact with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(api_router)

@app.get("/")
def home():
    return {
        "message": "Personalized Networking Assistant API is running.",
        "docs_url": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)