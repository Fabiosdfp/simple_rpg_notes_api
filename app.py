from flask_openapi3 import OpenAPI, Info, Tag
from flask import redirect
from urllib.parse import unquote
import traceback

from sqlalchemy.exc import IntegrityError

# Garante que o modelo e a sessão sejam importados corretamente
try:
    from model import Session, Campaign, Notes
    from logger import logger
    from schemas.erro import ErrorSchema
    from schemas import *
    print("All imports successful!")
except ImportError as e:
    print(f"Import error: {e}")
    traceback.print_exc()
    raise

from flask_cors import CORS

info = Info(
    title="RPG App API",
    version="1.0.0",
    description="API para gerenciamento de campanhas e notas de RPG"
)
app = OpenAPI(__name__, info=info)
CORS(app)

# Debugging
@app.errorhandler(500)
def internal_error(error):
    print(f"Internal error: {error}")
    traceback.print_exc()
    return {"error": "Internal server error", "details": str(error)}, 500

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
    print(f"Received data: {body}")
    session = Session()
    try:
        campaign = Campaign(name=body.name, description=body.description)
        print(f"Created campaign object: {campaign}")
        session.add(campaign)
        session.commit()
        session.refresh(campaign)  
        print(f"Campaign saved: {campaign}")
        result = CampaignInDB.model_validate(campaign)
        print(f"Validated result: {result}")
        return result.model_dump(mode='json'), 201
    except IntegrityError as e:
        session.rollback()
        print(f"Integrity error creating campaign: {e}")
        logger.error(f"Integrity error creating campaign: {e}")
        return ErrorSchema(message="Erro de integridade ao criar campanha.").model_dump(mode='json'), 400
    except Exception as e:
        session.rollback()
        print(f"Unexpected error creating campaign: {e}")
        traceback.print_exc()
        logger.error(f"Unexpected error creating campaign: {e}")
        return ErrorSchema(message=f"Erro interno: {str(e)}").model_dump(mode='json'), 500
    finally:
        session.close()

@app.get('/campaigns', tags=[campaign_tag])
def list_campaigns():
    """Lista todas as campanhas"""
    session = Session()
    try:
        campaigns = session.query(Campaign).all()
        campaign_list = [CampaignInDB.model_validate(c).model_dump(mode='json') for c in campaigns]
        return campaign_list
    except Exception as e:
        print(f"Error listing campaigns: {e}")
        traceback.print_exc()
        return ErrorSchema(message=f"Erro ao listar campanhas: {str(e)}").model_dump(mode='json'), 500
    finally:
        session.close()




# --- NOTAS (MENSAGENS) ---

@app.post('/notes', tags=[note_tag], responses={"201": NoteInDB, "400": ErrorSchema})
def create_note(body: NoteCreate):
    """Cria uma nova nota associada a uma campanha"""
    session = Session()
    try:
        # Verifica se a campanha existe
        campaign = session.query(Campaign).filter_by(id=body.campaign_id).first()
        if not campaign:
            return ErrorSchema(message="Campanha não encontrada.").model_dump(mode='json'), 400
        note = Notes(
            campaign_id=body.campaign_id,
            title=body.title,
            content=body.content
        )
        session.add(note)
        session.commit()
        session.refresh(note)  # Refresh to get the generated ID and timestamps
        return NoteInDB.model_validate(note).model_dump(mode='json'), 201
    except IntegrityError as e:
        session.rollback()
        logger.error(f"Integrity error creating note: {e}")
        return ErrorSchema(message="Erro de integridade ao criar nota.").model_dump(mode='json'), 400
    except Exception as e:
        session.rollback()
        logger.error(f"Unexpected error creating note: {e}")
        traceback.print_exc()
        return ErrorSchema(message=f"Erro interno: {str(e)}").model_dump(mode='json'), 500
    finally:
        session.close()

@app.get('/notes', tags=[note_tag])
def list_notes():
    """Lista todas as notas"""
    session = Session()
    try:
        notes = session.query(Notes).all()
        result = [NoteInDB.model_validate(n).model_dump(mode='json') for n in notes]
        return result
    except Exception as e:
        print(f"Error listing notes: {e}")
        traceback.print_exc()
        return ErrorSchema(message=f"Erro ao listar notas: {str(e)}").model_dump(mode='json'), 500
    finally:
        session.close()

@app.get('/notes/<int:note_id>', tags=[note_tag], responses={"200": NoteInDB, "404": ErrorSchema})
def get_note(note_id: int):
    """Busca uma nota pelo ID"""
    session = Session()
    note = session.query(Notes).filter_by(id=note_id).first()
    session.close()
    if note:
        return NoteInDB.model_validate(note).model_dump(mode='json')
    return ErrorSchema(message="Nota não encontrada.").model_dump(mode='json'), 404

@app.get('/campaigns/<int:campaign_id>/notes', tags=[note_tag], responses={"404": ErrorSchema})
def list_notes_by_campaign(campaign_id: int):
    """Lista todas as notas de uma campanha específica"""
    session = Session()
    notes = session.query(Notes).filter_by(campaign_id=campaign_id).all()
    session.close()
    if notes:
        return [NoteInDB.model_validate(n).model_dump(mode='json') for n in notes]
    return ErrorSchema(message="Nenhuma nota encontrada para esta campanha.").model_dump(mode='json'), 404

