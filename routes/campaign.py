from flask_openapi3 import APIBlueprint
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from model import Base, Session
from schemas import CampaignCreate, CampaignUpdate, CampaignInDB, CampaignListResponse, ErrorSchema

api = APIBlueprint('campaigns', __name__, url_prefix='/campaigns')

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
    
    


@api.get(
    "/",
    responses={200: CampaignListResponse, 404: ErrorSchema}
)
def list_campaigns():
    """Lista todas as campanhas"""
    session = Session()
    try:
        campaigns = session.query(Campaign).all()
        campaigns_data = [CampaignInDB.model_validate(c.__dict__) for c in campaigns]
        return CampaignListResponse(campaigns=campaigns_data)
    finally:
        session.close()

@api.get(
    "/<int:campaign_id>",
    responses={200: CampaignInDB, 404: ErrorSchema}
)
def get_campaign(path: int):
    """Retorna uma campanha por ID"""
    session = Session()
    try:
        campaign = session.query(Campaign).filter_by(id=path).first()
        if not campaign:
            return ErrorSchema(message="Campanha não encontrada").model_dump(), 404
        return CampaignInDB.model_validate(campaign.__dict__).model_dump()
    finally:
        session.close()