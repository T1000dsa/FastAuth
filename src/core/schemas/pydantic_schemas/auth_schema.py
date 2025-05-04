from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Token(BaseModel):
    """Response model for tokens"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshToken(BaseModel):
    """For creating new refresh tokens"""
    user_id: int
    token: str
    expires_at: datetime
    revoked: bool = False
    replaced_by_token: Optional[bool]
    family_id: str
    previous_token_id: Optional[int]