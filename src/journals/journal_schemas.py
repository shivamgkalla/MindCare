from pydantic import BaseModel, ConfigDict, Field, HttpUrl
from datetime import datetime
from typing import Optional



class JournalBase(BaseModel):
    title: str = Field(..., max_length=200, examples=["My first journal entry"])
    content: str = Field(..., examples=["Today, I started writing my daily journal"])
    image_url: Optional[HttpUrl] = Field(None, examples=["https://example.com/images/journal1.png"], description="Optional image attached to the journal")



class JournalCreate(JournalBase):
    pass



class JournalUpdate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=200, examples=["Updated Journal Title"])
    content: Optional[str] = Field(default=None, examples=["I updated my journal content to reflect new thoughts"])
    image_url: Optional[HttpUrl] = Field(None, examples=["https://example.com/images/journal1_updated.png"])
    updated_date: datetime = Field(default_factory=datetime.now, examples=["2025-08-26 14:30:00"])



class JournalOut(JournalBase):
    id: int = Field(..., examples=[1])
    user_id: Optional[int] = Field(None, examples=[42])
    created_at: datetime = Field(..., examples=["2025-08-26 12:34:56"])
    updated_date: Optional[datetime] = Field(None, examples=["2025-08-26 14:30:00"])

    model_config = ConfigDict(from_attributes=True, json_encoders={datetime: lambda v: v.strftime("%Y-%m-%d %H:%M:%S")})