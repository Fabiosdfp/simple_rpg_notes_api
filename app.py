from flask_openapi3 import OpenAPI, Info, Tag
from flask import redirect
from urllib.parse import unquote

from sqlalchemy.exc import IntegrityError

from model import Session, Campaign, Notes
from logger import logger
from schemas import *
from flask_cors import CORS

info = Info(
    title="RPG App API",
    version="1.0.0",
    description="API para gerenciamento de campanhas e notas de RPG"
)
app = OpenAPI(__name__, info=info)
CORS(app)

# definindo tags
home_tag = Tag(
    name="Documentação",
    description="Seleção de documentação: Swagger, Redoc ou RapiDoc"
)
campaign_tag = Tag(
    name="Campanha",
    description="Operações relacionadas a campanhas de RPG"
)
note_tag = Tag(
    name="Nota",
    description="Operações relacionadas a notas/sessões de campanhas"
)
error_tag = Tag(
    name="Erro",
    description="Mensagens de erro e respostas de exceção"
)

@app.get('/', tags=[home_tag])
def home():
    """Redireciona para /openapi, tela que permite a escolha do estilo de documentação.
    """
    return redirect('/openapi')



# --- CAMPANHAS ---

@app.post('/campaigns', tags=[campaign_tag], responses={"201": CampaignInDB, "400": ErrorSchema})
def create_campaign(body: CampaignCreate):
    """Cria uma nova campanha de RPG"""
    session = Session()
    try:
        campaign = Campaign(name=body.name, description=body.description)
        session.add(campaign)
        session.commit()
        return CampaignInDB.model_validate(campaign), 201
    except IntegrityError:
        session.rollback()
        return ErrorSchema(message="Erro de integridade ao criar campanha."), 400
    finally:
        session.close()

@app.get('/campaigns', tags=[campaign_tag])
def list_campaigns():
    """Lista todas as campanhas"""
    session = Session()
    campaigns = session.query(Campaign).all()
    campaign_list = [CampaignInDB.model_validate(c) for c in campaigns]
    session.close()
    return campaign_list

@app.get('/campaigns/<int:campaign_id>', tags=[campaign_tag], responses={"200": CampaignInDB, "404": ErrorSchema})
def get_campaign(campaign_id: int):
    """Busca uma campanha pelo ID"""
    session = Session()
    campaign = session.query(Campaign).filter_by(id=campaign_id).first()
    session.close()
    if campaign:
        return CampaignInDB.model_validate(campaign)
    return ErrorSchema(message="Campanha não encontrada."), 404

# --- NOTAS (MENSAGENS) ---

@app.post('/notes', tags=[note_tag], responses={"201": NoteInDB, "400": ErrorSchema})
def create_note(body: NoteCreate):
    """Cria uma nova nota associada a uma campanha"""
    session = Session()
    try:
        # Verifica se a campanha existe
        campaign = session.query(Campaign).filter_by(id=body.campaign_id).first()
        if not campaign:
            return ErrorSchema(message="Campanha não encontrada."), 400
        note = Notes(
            campaign_id=body.campaign_id,
            title=body.title,
            content=body.content
        )
        session.add(note)
        session.commit()
        return NoteInDB.model_validate(note), 201
    except IntegrityError:
        session.rollback()
        return ErrorSchema(message="Erro de integridade ao criar nota."), 400
    finally:
        session.close()

@app.get('/notes', tags=[note_tag])
def list_notes():
    """Lista todas as notas"""
    session = Session()
    notes = session.query(Notes).all()
    result = [NoteInDB.model_validate(n) for n in notes]
    session.close()
    return result

@app.get('/notes/<int:note_id>', tags=[note_tag], responses={"200": NoteInDB, "404": ErrorSchema})
def get_note(note_id: int):
    """Busca uma nota pelo ID"""
    session = Session()
    note = session.query(Notes).filter_by(id=note_id).first()
    session.close()
    if note:
        return NoteInDB.model_validate(note)
    return ErrorSchema(message="Nota não encontrada."), 404

@app.get('/campaigns/<int:campaign_id>/notes', tags=[note_tag], responses={"404": ErrorSchema})
def list_notes_by_campaign(campaign_id: int):
    """Lista todas as notas de uma campanha específica"""
    session = Session()
    notes = session.query(Notes).filter_by(campaign_id=campaign_id).all()
    session.close()
    if notes:
        return [NoteInDB.model_validate(n) for n in notes]
    return ErrorSchema(message="Nenhuma nota encontrada para esta campanha."), 404

# --- EXTRAS ÚTEIS ---

@app.delete('/campaigns/<int:campaign_id>', tags=[campaign_tag], responses={"404": ErrorSchema})
def delete_campaign(campaign_id: int):
    """Remove uma campanha pelo ID"""
    session = Session()
    campaign = session.query(Campaign).filter_by(id=campaign_id).first()
    if not campaign:
        session.close()
        return ErrorSchema(message="Campanha não encontrada."), 404
    session.delete(campaign)
    session.commit()
    session.close()
    return {"message": "Campanha removida com sucesso."}

@app.delete('/notes/<int:note_id>', tags=[note_tag], responses={"404": ErrorSchema})
def delete_note(note_id: int):
    """Remove uma nota pelo ID"""
    session = Session()
    note = session.query(Notes).filter_by(id=note_id).first()
    if not note:
        session.close()
        return ErrorSchema(message="Nota não encontrada."), 404
    session.delete(note)
    session.commit()
    session.close()
    return {"message": "Nota removida com sucesso."}