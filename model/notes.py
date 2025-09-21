from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from datetime import datetime
from typing import Union
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from  model import Base


class Notes(Base):
    """
    Tabela de Notas - Representa uma nota/sessão de uma campanha
    """
    __tablename__ = 'notes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    campaign_id = Column(Integer, ForeignKey('campaigns.id'), nullable=False)
    title = Column(String(150), nullable=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def __init__(self, campaign_id, content, title=None):
        self.campaign_id = campaign_id
        self.content = content
        self.title = title
    
    def __repr__(self):
        return f'<Notes {self.id}: {self.title or "Sem título"}>'
    
    def to_dict(self):
        """Converte o objeto para dicionário (útil para JSON)"""
        return {
            'id': self.id,
            'campaign_id': self.campaign_id,
            'title': self.title,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }