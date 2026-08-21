from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
import json

from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="user", nullable=False) # 'user' or 'creator'

    # Relationship to the creator profile if role == 'creator'
    creator_profile = relationship("CreatorProfile", back_populates="user", uselist=False)

class CreatorProfile(Base):
    __tablename__ = "creator_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)

    instagram_id = Column(String, unique=True, index=True)
    instagram_username = Column(String, index=True)
    full_name = Column(String)
    biography = Column(Text)
    followers_count = Column(Integer)
    business_category = Column(String)

    # Store the AI analysis as a JSON string
    ai_analysis_json = Column(Text)

    # Store the Meta Access token (In a real production app, this should be encrypted)
    meta_access_token = Column(String)

    user = relationship("User", back_populates="creator_profile")

    @property
    def ai_analysis(self):
        if self.ai_analysis_json:
            return json.loads(self.ai_analysis_json)
        return None

    @ai_analysis.setter
    def ai_analysis(self, value):
        self.ai_analysis_json = json.dumps(value)
