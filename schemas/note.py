from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class NoteCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Título da nota")
    content: str = Field(..., min_length=1, description="Conteúdo da nota")
    campaign_name: str = Field(..., min_length=1, max_length=100, description="Nome da campanha")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "A Busca pelo Cristal Perdido",
                "content": "Os aventureiros encontraram um dragão antigo na caverna...",
                "campaign_name": "Campanha Épica"
            }
        }


class NoteResponse(BaseModel):
    id: int
    title: str
    content: str
    campaign_name: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class CampaignNamePath(BaseModel):
    campaign_name: str = Field(..., description="Nome da campanha")


class NotesSearchResponse(BaseModel):
    notes: List[NoteResponse]
    total: int
    campaign_name: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "notes": [],
                "total": 0,
                "campaign_name": "Campanha Épica"
            }
        }

