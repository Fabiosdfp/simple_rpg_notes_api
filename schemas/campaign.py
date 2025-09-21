from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class CampaignBase(BaseModel):
    """Define como uma nova campanha deve ser representada"""
    name: str = Field(..., example="Campanha Épica", max_length=100, description="Nome da campanha")
    description: Optional[str] = Field(None, example="Uma aventura fantástica", description="Descrição da campanha")

class CampaignCreate(CampaignBase):
    """Schema para criação de campanha"""
    pass

class CampaignUpdate(BaseModel):
    """Schema para atualização de campanha"""
    name: Optional[str] = Field(None, example="Nova Campanha", max_length=100, description="Nome atualizado da campanha")
    description: Optional[str] = Field(None, example="Descrição atualizada", description="Descrição atualizada da campanha")

class CampaignInDB(CampaignBase):
    """Schema de campanha retornada do banco de dados"""
    id: int = Field(..., example=1, description="ID da campanha")
    created_at: datetime = Field(..., example="2023-09-17T12:00:00", description="Data de criação da campanha")

    class Config:
        from_attributes = True

class CampaignListResponse(BaseModel):
    """Schema for campaign list responses"""
    campaigns: List["CampaignInDB"] = Field(..., description="Lista de campanhas")