from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ChatRequest(BaseModel):
    query: str = Field(..., example="Hello, how are you?")
    timestamp: Optional[datetime] = None 

class ChatResponse(BaseModel):
    status: str = Field(..., example="success")
    reply: str = Field(..., example="I'm doing well, thank you!")
    timestamp: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()  
        }