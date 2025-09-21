from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from model import Base

class Campaign(Base):
    """
    Tabela de Campanhas - Representa uma campanha de RPG
    """
    __tablename__ = 'campaigns'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    notes = relationship('Notes', backref='campaign', lazy=True, cascade='all, delete-orphan')

    def __init__(self, name, description=None):
        self.name = name
        self.description = description

    def __repr__(self):
        return f'<Campaign {self.id}: {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }