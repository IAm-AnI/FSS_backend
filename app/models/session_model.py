from sqlalchemy import Column, String, DateTime, JSON
from app.config.database import Base
from datetime import datetime

class SessionData(Base):
    __tablename__ = 'sessions'

    session_key = Column(String, primary_key=True, index=True)
    data = Column(JSON, default={})
    expires = Column(DateTime)