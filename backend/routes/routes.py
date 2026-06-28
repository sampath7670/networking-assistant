import sys
import os
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

# Ensure backend directory is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import get_db
from backend.models.models import Suggestion
from backend.services.nlp_service import nlp_service
from backend.services.wiki_service import wiki_service

router = APIRouter(prefix="/api")

# Pydantic schemas
class SuggestionRequest(BaseModel):
    event_description: str = Field(..., min_length=5, description="Event details")
    interests: list[str] = Field(..., description="User's networking interests")

class SuggestionResponse(BaseModel):
    id: int
    event_description: str
    interests: list[str]
    themes: list[str]
    starters: list[str]
    feedback: list[bool | None]
    created_at: str

    class Config:
        from_attributes = True

class FeedbackRequest(BaseModel):
    starter_index: int = Field(..., ge=0, le=2, description="Index of the starter (0, 1, or 2)")
    is_useful: bool | None = Field(..., description="True if useful, False if not, None to reset")

# Helper function to serialize model to response dict
def format_suggestion(suggestion: Suggestion) -> dict:
    return {
        "id": suggestion.id,
        "event_description": suggestion.event_description,
        "interests": [i.strip() for i in suggestion.interests.split(",") if i.strip()],
        "themes": [t.strip() for t in suggestion.themes.split(",") if t.strip()],
        "starters": suggestion.starters,
        "feedback": suggestion.feedback,
        "created_at": suggestion.created_at.isoformat()
    }

@router.post("/suggestions", response_model=dict)
def generate_suggestions(req: SuggestionRequest, db: Session = Depends(get_db)):
    try:
        # 1. Extract themes
        themes = nlp_service.extract_themes(req.event_description, top_n=3)
        
        # 2. Generate starters
        starters = nlp_service.generate_starters(req.event_description, themes, req.interests)
        
        # 3. Create suggestion entry in DB
        suggestion = Suggestion(
            event_description=req.event_description,
            interests=",".join(req.interests),
            themes=",".join(themes),
        )
        suggestion.starters = starters
        suggestion.feedback = [None] * len(starters) # Initialize empty feedback for each starter
        
        db.add(suggestion)
        db.commit()
        db.refresh(suggestion)
        
        return format_suggestion(suggestion)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to generate suggestions: {str(e)}")

@router.get("/history", response_model=list[dict])
def get_history(db: Session = Depends(get_db)):
    try:
        suggestions = db.query(Suggestion).order_by(Suggestion.created_at.desc()).all()
        return [format_suggestion(s) for s in suggestions]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch history: {str(e)}")

@router.post("/history/{suggestion_id}/feedback", response_model=dict)
def log_feedback(suggestion_id: int, req: FeedbackRequest, db: Session = Depends(get_db)):
    suggestion = db.query(Suggestion).filter(Suggestion.id == suggestion_id).first()
    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found")
        
    try:
        feedbacks = suggestion.feedback
        # Make sure feedback list size matches starters size
        if len(feedbacks) <= req.starter_index:
            feedbacks = [None] * len(suggestion.starters)
            
        feedbacks[req.starter_index] = req.is_useful
        suggestion.feedback = feedbacks
        
        db.commit()
        db.refresh(suggestion)
        
        return format_suggestion(suggestion)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to log feedback: {str(e)}")

@router.get("/verify", response_model=dict)
def verify_fact(query: str = Query(..., min_length=1, description="Fact or topic to verify")):
    res = wiki_service.verify_fact(query)
    if not res.get("success", False):
        raise HTTPException(status_code=400, detail=res.get("message", "Fact verification failed."))
    return res
