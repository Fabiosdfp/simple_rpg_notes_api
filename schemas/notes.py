from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class NoteBase(BaseModel):
    campaign_id: int = Field(..., description="ID da campanha associada", example=1)
    title: Optional[str] = Field(None, max_length=150, description="Título da nota", example="Sessão 1")
    content: str = Field(..., description="Conteúdo da nota", example="Resumo da sessão de RPG.")

class NoteCreate(NoteBase):
    """Schema para criação de nota"""
    pass

class NoteUpdate(BaseModel):
    """Schema para atualização de nota"""
    title: Optional[str] = Field(None, max_length=150, description="Título atualizado da nota", example="Sessão 2")
    content: Optional[str] = Field(None, description="Conteúdo atualizado da nota", example="Resumo atualizado.")

class NoteInDB(NoteBase):
    """Schema de nota retornada do banco de dados"""
    id: int = Field(..., example=1, description="ID da nota")
    created_at: datetime = Field(..., example="2023-09-17T12:00:00", description="Data de criação da nota")
    updated_at: datetime = Field(..., example="2023-09-17T13:00:00", description="Data de atualização da nota")

    class Config:
        orm_mode = True