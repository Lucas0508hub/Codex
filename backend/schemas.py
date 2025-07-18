from pydantic import BaseModel
from typing import List, Optional

class UserCreate(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'

class SegmentUpdate(BaseModel):
    start: Optional[float]
    end: Optional[float]
    transcript: Optional[str]

class SegmentOut(BaseModel):
    id: int
    start: float
    end: float
    transcript: str
    class Config:
        orm_mode = True

class AudioJobOut(BaseModel):
    id: int
    language: str
    filename: str
    segments: List[SegmentOut]
    class Config:
        orm_mode = True
