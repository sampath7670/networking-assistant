import json
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from backend.database import Base

class Suggestion(Base):
    __tablename__ = "suggestions"

    id = Column(Integer, primary_key=True, index=True)
    event_description = Column(String, nullable=False)
    interests = Column(String, nullable=False)        # Store comma-separated interests
    themes = Column(String, nullable=False)           # Store comma-separated themes
    starters_json = Column(String, nullable=False)    # JSON string representation of list of starters
    feedback_json = Column(String, nullable=False)    # JSON string representation of feedback per starter
    created_at = Column(DateTime, default=datetime.utcnow)

    @property
    def starters(self):
        try:
            return json.loads(self.starters_json)
        except Exception:
            return []

    @starters.setter
    def starters(self, value):
        self.starters_json = json.dumps(value)

    @property
    def feedback(self):
        try:
            return json.loads(self.feedback_json)
        except Exception:
            return []

    @feedback.setter
    def feedback(self, value):
        self.feedback_json = json.dumps(value)
