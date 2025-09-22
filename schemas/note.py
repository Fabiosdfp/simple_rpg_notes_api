from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class NotePath(BaseModel):
    """Schema para parâmetros de path da nota"""
    note_id: int = Field(..., description="ID da nota", example=1)

class CampaignNotesPath(BaseModel):
    """Schema para parâmetros de path das notas de uma campanha"""
    campaign_id: int = Field(..., description="ID da campanha", example=1)

class NoteCreate(BaseModel):
    """Schema para criação de nota"""
    campaign_id: int = Field(..., description="ID da campanha associada", example=1)
    title: str = Field(..., description="Título da nota", example="Sessão 1 - Início da aventura")
    content: str = Field(..., description="Conteúdo da nota", example="Os heróis se encontraram na taverna...")

class NoteInDB(BaseModel):
    """Schema para nota retornada do banco"""
    id: int = Field(..., description="ID único da nota")
    campaign_id: int = Field(..., description="ID da campanha associada")
    title: str = Field(..., description="Título da nota")
    content: str = Field(..., description="Conteúdo da nota")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Data da última atualização")
    
    class Config:
        from_attributes = True

class NoteListResponse(BaseModel):
    """Schema para resposta com lista de notas"""
    notes: List[NoteInDB] = Field(..., description="Lista de notas")
