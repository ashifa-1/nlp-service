from pydantic import BaseModel, Field
from typing import Optional, Any
from uuid import UUID

class ProcessRequest(BaseModel):
    text: str = Field(..., min_length=1)
    task_type: str = Field(..., regex="^(sentiment_analysis|named_entity_recognition)$")

class ProcessResponse(BaseModel):
    task_id: UUID
    status: str

class StatusResponse(BaseModel):
    task_id: UUID
    status: str
    result: Optional[Any] = None
    error_message: Optional[str] = None
    updated_at: Optional[str] = None
