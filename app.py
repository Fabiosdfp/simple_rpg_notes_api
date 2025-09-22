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
    from schemas.campaign import CampaignPath, CampaignCreate, CampaignInDB
    from schemas.note import NoteCreate, NoteResponse, NotesSearchResponse, CampaignNamePath
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

# Depuração
@app.errorhandler(500)
def internal_error(error):
    print(f"Erro interno: {error}")
    traceback.print_exc()
    return {"error": "Erro interno do servidor", "details": str(error)}, 500

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

@app.get('/campaigns/<int:campaign_id>', tags=[campaign_tag], responses={"200": CampaignInDB, "404": ErrorSchema})
def get_campaign(path: CampaignPath):
    """Busca uma campanha pelo ID
    
    Args:
        campaign_id: ID da campanha a ser buscada
    """
    campaign_id = path.campaign_id
    session = Session()
    try:
        campaign = session.query(Campaign).filter_by(id=campaign_id).first()
        if campaign:
            return CampaignInDB.model_validate(campaign).model_dump(mode='json')
        return ErrorSchema(message="Campanha não encontrada.").model_dump(mode='json'), 404
    except Exception as e:
        print(f"Error getting campaign: {e}")
        traceback.print_exc()
        return ErrorSchema(message=f"Erro ao buscar campanha: {str(e)}").model_dump(mode='json'), 500
    finally:
        session.close()

# --- NOTAS (MENSAGENS) ---

@app.post('/notes', tags=[note_tag], responses={"201": NoteResponse, "400": ErrorSchema, "404": ErrorSchema})
def create_note(body: NoteCreate):
    """Cria uma nova nota para uma campanha"""
    print(f"Received note data: {body}")
    session = Session()
    try:
        # Verifica se a campanha existe
        campaign = session.query(Campaign).filter_by(name=body.campaign_name).first()
        if not campaign:
            return ErrorSchema(message=f"Campanha '{body.campaign_name}' não encontrada.").model_dump(mode='json'), 404
        
        # Cria a nota
        note = Notes(
            title=body.title,
            content=body.content,
            campaign_name=campaign.name
        )
        
        session.add(note)
        session.commit()
        session.refresh(note)
        
        # Prepara a resposta incluindo o nome da campanha
        note_dict = {
            'id': note.id,
            'title': note.title,
            'content': note.content,
            'campaign_name': campaign.name,
            'created_at': note.created_at,
            'updated_at': note.updated_at
        }
        
        result = NoteResponse.model_validate(note_dict)
        return result.model_dump(mode='json'), 201
        
    except IntegrityError as e:
        session.rollback()
        print(f"Integrity error creating note: {e}")
        return ErrorSchema(message="Erro de integridade ao criar nota.").model_dump(mode='json'), 400
    except Exception as e:
        session.rollback()
        print(f"Unexpected error creating note: {e}")
        traceback.print_exc()
        return ErrorSchema(message=f"Erro interno: {str(e)}").model_dump(mode='json'), 500
    finally:
        session.close()

@app.get('/notes', tags=[note_tag], responses={"200": NotesSearchResponse, "400": ErrorSchema})
def list_all_notes():
    """Lista todas as notas de todas as campanhas"""
    session = Session()
    try:
        notes = session.query(Notes).join(Campaign).all()
        
        note_list = []
        for note in notes:
            note_dict = {
                'id': note.id,
                'title': note.title,
                'content': note.content,
                'campaign_name': note.campaign.name,
                'created_at': note.created_at,
                'updated_at': note.updated_at
            }
            note_list.append(NoteResponse.model_validate(note_dict).model_dump(mode='json'))
        
        response = NotesSearchResponse(
            notes=note_list,
            total=len(note_list),
            campaign_name=None
        )
        
        return response.model_dump(mode='json')
        
    except Exception as e:
        print(f"Error listing notes: {e}")
        traceback.print_exc()
        return ErrorSchema(message=f"Erro ao listar notas: {str(e)}").model_dump(mode='json'), 500
    finally:
        session.close()

@app.get('/campaigns/<string:campaign_name>/notes', tags=[note_tag], responses={"200": NotesSearchResponse, "404": ErrorSchema, "400": ErrorSchema})
def list_notes_by_campaign(path: CampaignNamePath):
    """Lista todas as notas de uma campanha específica pelo nome da campanha
    
    Args:
        campaign_name: Nome da campanha para buscar as notas
    """
    # Decodifica o nome da campanha da URL
    campaign_name = unquote(path.campaign_name)
    
    session = Session()
    try:
        # Verifica se a campanha existe
        campaign = session.query(Campaign).filter_by(name=campaign_name).first()
        if not campaign:
            return ErrorSchema(message=f"Campanha '{campaign_name}' não encontrada.").model_dump(mode='json'), 404
        
        # Busca todas as notas da campanha
        notes = session.query(Notes).filter_by(campaign_name=campaign_name).all()
        
        # Converte as notas usando o método similar ao list_all_notes
        note_list = []
        for note in notes:
            note_dict = {
                'id': note.id,
                'title': note.title,
                'content': note.content,
                'campaign_name': note.campaign_name,
                'created_at': note.created_at,
                'updated_at': note.updated_at
            }
            note_list.append(NoteResponse.model_validate(note_dict).model_dump(mode='json'))
        
        response = NotesSearchResponse(
            notes=note_list,
            total=len(note_list),
            campaign_name=campaign_name
        )
        
        return response.model_dump(mode='json')
        
    except Exception as e:
        print(f"Error listing notes for campaign '{campaign_name}': {e}")
        traceback.print_exc()
        return ErrorSchema(message=f"Erro ao listar notas da campanha: {str(e)}").model_dump(mode='json'), 500
    finally:
        session.close()

