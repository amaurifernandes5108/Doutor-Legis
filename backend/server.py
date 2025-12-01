from fastapi import FastAPI, APIRouter, HTTPException, Request, Response, Depends, Header
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import time
import httpx
import jwt
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from emergentintegrations.llm.chat import LlmChat, UserMessage
from emergentintegrations.payments.stripe.checkout import (
    StripeCheckout,
    CheckoutSessionRequest,
    CheckoutSessionResponse,
    CheckoutStatusResponse
)
from oab_knowledge_base import get_oab_context
from planos_config import (
    get_plano_config,
    get_todos_planos,
    verificar_limite_consultas,
    verificar_limite_pdfs,
    verificar_acesso_dominio,
    get_dominios_disponiveis,
    PLANOS
)
from router_inteligente import classificar_pergunta, sugerir_dominios
from meta_nucleo import meta_nucleo
from nucleos_especializados import get_prompt_nucleo

# Pinecone RAG imports
from pinecone_manager import PineconeManager
from document_processor import EmbeddingGenerator
from rag_system import RAGSystem

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env', override=False)

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Pinecone RAG System initialization
pinecone_api_key = os.getenv("PINECONE_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")
rag_system = None

if pinecone_api_key and openai_api_key:
    try:
        pinecone_manager = PineconeManager(api_key=pinecone_api_key)
        embedding_generator = EmbeddingGenerator(openai_api_key=openai_api_key)
        rag_system = RAGSystem(pinecone_manager, embedding_generator, openai_api_key)
        logging.info("✅ Sistema RAG Pinecone inicializado")
    except Exception as e:
        logging.warning(f"⚠️  RAG System não inicializado: {str(e)}")
        rag_system = None
else:
    logging.warning("⚠️  Credenciais Pinecone/OpenAI não encontradas - RAG desativado")

# Rate limiting
limiter = Limiter(key_func=get_remote_address)

# Create the main app
app = FastAPI(title="Doutor Legis 2.0 API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# =============================================================================
# MODELS
# =============================================================================

class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    email: EmailStr
    name: str
    picture: Optional[str] = None
    plan: str = "gratuito"  # gratuito, basico, intermediario, avancado
    
    # Role de usuário
    role: str = "user"  # user, admin_master
    
    # Stripe
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    
    # Uso mensal (reseta todo mês)
    consultas_mes_atual: int = 0
    pdfs_mes_atual: int = 0
    
    # Datas
    data_plano_inicio: Optional[datetime] = None
    data_renovacao: Optional[datetime] = None
    
    # Trial
    em_trial: bool = False
    data_trial_fim: Optional[datetime] = None
    
    # Legacy (manter para compatibilidade)
    token_balance: int = 3
    
    google_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    active: bool = True

class UserSession(BaseModel):
    user_id: str
    session_token: str
    expires_at: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Consultation(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    user_id: str
    domain: str
    question: str
    response: str
    confidence: int
    tokens_used: int
    processing_time: float
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    saved: bool = True

class PaymentTransaction(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    session_id: str
    user_id: Optional[str] = None
    amount: float
    currency: str
    status: str  # initiated, completed, failed, expired
    payment_status: str  # unpaid, paid
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Request/Response Models
class ConsultationRequest(BaseModel):
    domain: str
    question: str

class ConsultationResponse(BaseModel):
    id: str
    domain: str
    question: str
    response: Dict[str, Any]
    confidence: int
    tokens_used: int
    processing_time: float
    created_at: datetime

class DomainInfo(BaseModel):
    id: str
    name: str
    legislation: str
    court: str
    accuracy: int

class CheckoutRequest(BaseModel):
    package_id: str  # "premium_monthly"
    origin_url: str

# =============================================================================
# DOMAIN DEFINITIONS
# =============================================================================

DOMAINS = [
    {
        "id": "constitucional",
        "name": "Direito Constitucional",
        "legislation": "Constituição Federal de 1988",
        "court": "STF (Supremo Tribunal Federal)",
        "accuracy": 95,
        "nucleo": 1,
        "expertise": "Direitos fundamentais, Controle de constitucionalidade, ADI/ADC/ADPF"
    },
    {
        "id": "civil",
        "name": "Direito Civil",
        "legislation": "Código Civil (Lei 10.406/2002), CPC/2015",
        "court": "STJ (Superior Tribunal de Justiça)",
        "accuracy": 92,
        "nucleo": 2,
        "expertise": "Contratos, Responsabilidade civil, Família, Sucessões"
    },
    {
        "id": "consumidor",
        "name": "Direito do Consumidor",
        "legislation": "CDC (Lei 8.078/1990), Lei 14.933/2024",
        "court": "STJ, PROCON",
        "accuracy": 93,
        "nucleo": 3,
        "expertise": "Relação consumidor-fornecedor, Cláusulas abusivas, Garantias"
    },
    {
        "id": "imobiliario",
        "name": "Direito Imobiliário",
        "legislation": "Lei 8.245/91 (Locações), Lei 6.015/73 (Registros)",
        "court": "Tribunais de Justiça Estaduais",
        "accuracy": 89,
        "nucleo": 4,
        "expertise": "Locação, Compra e venda, Registro, Condomínio"
    },
    {
        "id": "publico",
        "name": "Direito Público/Licitações",
        "legislation": "Lei 14.133/21, Lei 8.666/93",
        "court": "TCU, TJ, TRF",
        "accuracy": 88,
        "nucleo": 5,
        "expertise": "Licitações, Contratos públicos, Improbidade administrativa"
    },
    {
        "id": "trabalhista",
        "name": "Direito Trabalhista",
        "legislation": "CLT, Lei 8.213/91 (Benefícios)",
        "court": "TST (Tribunal Superior do Trabalho)",
        "accuracy": 91,
        "nucleo": 6,
        "expertise": "Rescisão, FGTS, Horas extras, Direitos coletivos"
    },
    {
        "id": "empresarial",
        "name": "Direito Empresarial",
        "legislation": "Lei 6.404/76 (S.A.), LGPD, Lei Anticorrupção",
        "court": "STJ, Tribunais Estaduais",
        "accuracy": 90,
        "nucleo": 7,
        "expertise": "Sociedades, LGPD, Compliance, M&A"
    },
    {
        "id": "internacional",
        "name": "Direito Internacional",
        "legislation": "Tratados Internacionais, UNCITRAL",
        "court": "STJ, TRF, Cortes Internacionais",
        "accuracy": 87,
        "nucleo": 8,
        "expertise": "Contratos cross-border, Arbitragem, Tratados"
    },
    {
        "id": "etica_advocacia_oab",
        "name": "Ética e Advocacia OAB",
        "legislation": "Estatuto OAB (Lei 8.906/94), Código Ética (Res. 02/2015), Prov. 205/2021",
        "court": "Tribunais de Ética e Disciplina OAB, Conselhos Seccionais",
        "accuracy": 97,
        "nucleo": 9,
        "expertise": "Prerrogativas, Ética profissional, Publicidade, Procedimento disciplinar"
    },
    # ⭐ NOVOS DOMÍNIOS - ULTRA
    {
        "id": "penal",
        "name": "Direito Penal",
        "legislation": "Código Penal, CPP, Lei de Execução Penal",
        "court": "STF, STJ, Tribunais de Justiça",
        "accuracy": 97,
        "nucleo": 10,
        "expertise": "Crimes, Processo penal, Execução, Júri, Defesa criminal"
    },
    {
        "id": "tributario",
        "name": "Direito Tributário",
        "legislation": "CTN, CF/88, Leis tributárias (IR, ICMS, ISS, PIS/COFINS)",
        "court": "STF, STJ, CARF",
        "accuracy": 98,
        "nucleo": 11,
        "expertise": "Impostos, Processo administrativo, Planejamento tributário, CARF"
    },
    {
        "id": "previdenciario",
        "name": "Direito Previdenciário",
        "legislation": "Lei 8.213/91, Lei 8.212/91, Lei 14.331/22",
        "court": "STJ, TRF, JEF",
        "accuracy": 99,
        "nucleo": 12,
        "expertise": "Aposentadoria, Pensão, Auxílio-doença, INSS, Revisão"
    },
    {
        "id": "tecnologia",
        "name": "Direito da Tecnologia",
        "legislation": "LGPD, Marco Civil, Lei 14.155/21 (E-commerce)",
        "court": "STJ, Tribunais Estaduais",
        "accuracy": 95,
        "nucleo": 13,
        "expertise": "IA, Criptomoedas, Blockchain, Crimes digitais, Propriedade intelectual digital"
    }
]

# Payment packages
PAYMENT_PACKAGES = {
    "premium_monthly": {"amount": 497.00, "currency": "brl", "name": "Plano Premium Mensal"}
}

# =============================================================================
# AUTHENTICATION HELPERS
# =============================================================================

def is_admin_master(user: User) -> bool:
    """Verifica se usuário é Administrador Master Fundador"""
    return user.role == "admin_master"

def is_founder_email(email: str) -> bool:
    """Verifica se é email do fundador"""
    return email.lower() == "amaurifernandes1975@gmail.com"

async def get_current_user(request: Request, authorization: Optional[str] = Header(None)) -> User:
    """Get current user from session token (cookie or header)"""
    session_token = None
    
    # Try to get from cookie first
    session_token = request.cookies.get("session_token")
    
    # Fallback to Authorization header
    if not session_token and authorization:
        if authorization.startswith("Bearer "):
            session_token = authorization.replace("Bearer ", "")
    
    if not session_token:
        raise HTTPException(status_code=401, detail="Não autenticado")
    
    # Check session in database
    session = await db.user_sessions.find_one({"session_token": session_token})
    if not session:
        raise HTTPException(status_code=401, detail="Sessão inválida")
    
    # Check if session expired
    expires_at = session["expires_at"]
    if isinstance(expires_at, str):
        expires_at = datetime.fromisoformat(expires_at)
    
    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Sessão expirada")
    
    # Get user
    user_doc = await db.users.find_one({"id": session["user_id"]}, {"_id": 0})
    if not user_doc:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Convert datetime strings to datetime objects if needed
    if isinstance(user_doc.get('created_at'), str):
        user_doc['created_at'] = datetime.fromisoformat(user_doc['created_at'])
    
    return User(**user_doc)

# =============================================================================
# AUTHENTICATION ROUTES
# =============================================================================

@api_router.get("/auth/google-login")
async def google_login(request: Request):
    """Redirect to Emergent Auth with correct redirect URL"""
    # redirect_url should point to main app (dashboard), not landing
    host = str(request.base_url).rstrip('/')
    redirect_url = f"{host}/dashboard"
    auth_url = f"https://auth.emergentagent.com/?redirect={redirect_url}"
    return {"auth_url": auth_url}

@api_router.post("/auth/session")
async def process_session(request: Request, response: Response, session_id: str = Header(..., alias="X-Session-ID")):
    """Process session_id from Emergent Auth and create user session"""
    try:
        # Get user data from Emergent Auth
        async with httpx.AsyncClient() as http_client:
            auth_response = await http_client.get(
                "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
                headers={"X-Session-ID": session_id},
                timeout=10.0
            )
            
            if auth_response.status_code != 200:
                raise HTTPException(status_code=401, detail="Session ID inválido")
            
            user_data = auth_response.json()
        
        # Check if user exists
        existing_user = await db.users.find_one({"email": user_data["email"]}, {"_id": 0})
        
        if existing_user:
            user_id = existing_user["id"]
            # Se for fundador e ainda não tem role admin, atualizar
            if is_founder_email(user_data["email"]) and existing_user.get("role") != "admin_master":
                await db.users.update_one(
                    {"id": user_id},
                    {"$set": {"role": "admin_master"}}
                )
        else:
            # Create new user
            user_id = str(uuid.uuid4())
            # Verificar se é fundador
            role = "admin_master" if is_founder_email(user_data["email"]) else "user"
            new_user = User(
                id=user_id,
                email=user_data["email"],
                name=user_data.get("name", "Usuário"),
                picture=user_data.get("picture"),
                google_id=user_data.get("id"),
                plan="gratuito",
                role=role,
                token_balance=3
            )
            user_dict = new_user.model_dump()
            user_dict['created_at'] = user_dict['created_at'].isoformat()
            await db.users.insert_one(user_dict)
        
        # Create session
        session_token = user_data["session_token"]
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        
        new_session = UserSession(
            user_id=user_id,
            session_token=session_token,
            expires_at=expires_at
        )
        session_dict = new_session.model_dump()
        session_dict['expires_at'] = session_dict['expires_at'].isoformat()
        session_dict['created_at'] = session_dict['created_at'].isoformat()
        
        # Delete old sessions for this user
        await db.user_sessions.delete_many({"user_id": user_id})
        await db.user_sessions.insert_one(session_dict)
        
        # Set httpOnly cookie
        response.set_cookie(
            key="session_token",
            value=session_token,
            httponly=True,
            secure=True,
            samesite="none",
            path="/",
            max_age=7*24*60*60  # 7 days
        )
        
        # Get user for response
        user_doc = await db.users.find_one({"id": user_id}, {"_id": 0})
        
        return {
            "user": {
                "id": user_doc["id"],
                "email": user_doc["email"],
                "name": user_doc["name"],
                "picture": user_doc.get("picture"),
                "plan": user_doc["plan"],
                "token_balance": user_doc["token_balance"]
            },
            "session_token": session_token
        }
    
    except Exception as e:
        logger.error(f"Session processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao processar sessão: {str(e)}")

@api_router.get("/auth/me")
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "picture": current_user.picture,
        "plan": current_user.plan,
        "role": current_user.role,
        "is_admin": is_admin_master(current_user),
        "token_balance": current_user.token_balance,
        "created_at": current_user.created_at.isoformat()
    }

@api_router.post("/auth/logout")
async def logout(request: Request, response: Response, current_user: User = Depends(get_current_user)):
    """Logout user"""
    session_token = request.cookies.get("session_token")
    if session_token:
        await db.user_sessions.delete_one({"session_token": session_token})
    
    response.delete_cookie(key="session_token", path="/")
    return {"message": "Logout realizado com sucesso"}

@api_router.get("/auth/admin-status")
async def get_admin_status(current_user: User = Depends(get_current_user)):
    """Verifica status de administrador"""
    is_admin = is_admin_master(current_user)
    
    return {
        "is_admin_master": is_admin,
        "role": current_user.role,
        "email": current_user.email,
        "privilegios": {
            "consultas_ilimitadas": is_admin,
            "pdfs_ilimitados": is_admin,
            "acesso_todos_dominios": is_admin,
            "acesso_analytics": is_admin,
            "bypass_limites_plano": is_admin,
            "historico_permanente": is_admin
        },
        "plano_atual": current_user.plan,
        "message": "Administrador Master Fundador - Acesso Pleno" if is_admin else "Usuário padrão"
    }

# =============================================================================
# CONSULTATION ROUTES
# =============================================================================

@api_router.get("/domains")
async def get_domains():
    """Get all legal domains"""
    return DOMAINS

@api_router.post("/domains/classificar")
async def classificar_dominio(pergunta: str):
    """Classifica pergunta e sugere domínio (Router Inteligente)"""
    dominio, confianca, detalhes = classificar_pergunta(pergunta)
    sugestoes = sugerir_dominios(pergunta, top_n=3)
    
    return {
        "dominio_sugerido": dominio,
        "confianca": round(confianca, 1),
        "detalhes": detalhes,
        "sugestoes_alternativas": sugestoes
    }

@api_router.post("/consultation", response_model=ConsultationResponse)
@limiter.limit("60/minute")
async def create_consultation(
    request: Request,
    consultation_req: ConsultationRequest,
    current_user: User = Depends(get_current_user)
):
    """Create a new legal consultation"""
    start_time = time.time()
    
    # Check if domain is valid
    domain_info = next((d for d in DOMAINS if d["id"] == consultation_req.domain), None)
    if not domain_info:
        raise HTTPException(status_code=400, detail="Domínio inválido")
    
    # Admin Master tem acesso pleno - bypass de limites
    if not is_admin_master(current_user):
        # Verificar acesso ao domínio
        if not verificar_acesso_dominio(current_user.plan, consultation_req.domain):
            plano_config = get_plano_config(current_user.plan)
            raise HTTPException(
                status_code=403,
                detail=f"Seu plano {plano_config.nome} não tem acesso a este domínio. Faça upgrade para acessar."
            )
        
        # Verificar limite de consultas
        limite = verificar_limite_consultas(current_user.plan, current_user.consultas_mes_atual)
        if not limite["pode_usar"]:
            raise HTTPException(
                status_code=402,
                detail=f"Limite de consultas atingido ({limite['usado']}/{limite['limite']}). Faça upgrade para mais consultas."
            )
    
    try:
        # ULTRA: Classificar automaticamente se não especificado domínio correto
        dominio_sugerido, router_confidence, router_detalhes = classificar_pergunta(consultation_req.question)
        
        # Se domínio selecionado diferente do sugerido e router tem alta confiança, avisar
        if consultation_req.domain != dominio_sugerido and router_confidence > 80:
            logger.info(f"Router sugere {dominio_sugerido} (conf: {router_confidence}%), usuário selecionou {consultation_req.domain}")
        
        # Get OAB context if applicable
        oab_context = get_oab_context(consultation_req.domain)
        
        # ULTRA: Get specialized prompt from núcleo
        nucleo_prompt = get_prompt_nucleo(consultation_req.domain)
        
        # Build prompt for legal analysis
        system_prompt = f"""{oab_context}

{nucleo_prompt}

---

Você é o Doutor Legis, um assistente jurídico especializado em Direito Brasileiro.

Domínio: {domain_info['name']}
Legislação: {domain_info['legislation']}
Corte Competente: {domain_info['court']}
Núcleo: {domain_info['nucleo']}
Expertise: {domain_info['expertise']}

Forneça uma análise jurídica completa e estruturada seguindo EXATAMENTE este formato JSON:

{{
  "resumo": "Breve resumo da questão (2-3 linhas)",
  "legislacao_aplicavel": "Leis, artigos e normas aplicáveis",
  "jurisprudencia": "Precedentes e jurisprudência relevante",
  "analise_legal": "Análise detalhada sob a perspectiva jurídica",
  "riscos_juridicos": "Principais riscos e pontos de atenção",
  "recomendacoes": "Recomendações práticas e estratégicas",
  "proximos_passos": "Este conteúdo não constitui consultoria jurídica vinculativa. Recomenda-se consultar um advogado para análise específica do seu caso.",
  "confianca": 85
}}

IMPORTANTE:
- Use linguagem profissional, técnica e juridicamente precisa
- Seja clara, acessível e didática
- Cite legislação específica quando possível (com artigos)
- O campo 'confianca' deve ser um número entre 70 e 95
- Responda APENAS com o JSON, sem texto adicional
- Mantenha respostas concisas mas completas
- Adote tom elegante, imparcial, ético e institucional
- Preserve coerência terminológica com os documentos normativos
"""

        # Initialize LLM
        api_key = os.getenv("OPENAI_API_KEY") or os.getenv("EMERGENT_LLM_KEY")
        session_id = f"consult_{current_user.id}_{int(time.time())}"
        
        chat = LlmChat(
            api_key=api_key,
            session_id=session_id,
            system_message=system_prompt
        )
        
        # Use GPT-4o or GPT-5.1 (latest available)
        chat.with_model("openai", "gpt-4o")
        
        # Create user message
        user_message = UserMessage(text=consultation_req.question)
        
        # Get response
        response_text = await chat.send_message(user_message)
        
        # Parse JSON response
        import json
        try:
            response_json = json.loads(response_text)
        except:
            # If response is not valid JSON, create a structured response
            response_json = {
                "resumo": response_text[:200],
                "legislacao_aplicavel": "Não especificado",
                "jurisprudencia": "Consulte um advogado",
                "analise_legal": response_text,
                "riscos_juridicos": "Análise requer avaliação específica",
                "recomendacoes": "Recomenda-se consultar um advogado",
                "proximos_passos": "Este conteúdo não constitui consultoria jurídica vinculativa.",
                "confianca": 75
            }
        
        # Calculate metrics
        processing_time = time.time() - start_time
        tokens_used = len(response_text) // 4  # Rough estimate
        confidence = response_json.get("confianca", 80)
        
        # Save consultation
        consultation_id = str(uuid.uuid4())
        consultation = Consultation(
            id=consultation_id,
            user_id=current_user.id,
            domain=consultation_req.domain,
            question=consultation_req.question,
            response=json.dumps(response_json),
            confidence=confidence,
            tokens_used=tokens_used,
            processing_time=processing_time
        )
        
        consultation_dict = consultation.model_dump()
        consultation_dict['created_at'] = consultation_dict['created_at'].isoformat()
        await db.consultations.insert_one(consultation_dict)
        
        # ULTRA: Registrar no Meta-Núcleo para aprendizado
        meta_nucleo.registrar_consulta(
            dominio=consultation_req.domain,
            confidence=confidence,
            processing_time=processing_time,
            tokens_used=tokens_used,
            router_confidence=router_confidence
        )
        
        # Incrementar contador de consultas (exceto admin_master e plano avançado)
        if not is_admin_master(current_user):
            plano_config = get_plano_config(current_user.plan)
            if plano_config.consultas_mes is not None:  # Não é ilimitado
                await db.users.update_one(
                    {"id": current_user.id},
                    {"$inc": {"consultas_mes_atual": 1}}
                )
            
            # Legacy: também decrementar token_balance para compatibilidade
            if current_user.plan == "gratuito":
                await db.users.update_one(
                    {"id": current_user.id},
                    {"$inc": {"token_balance": -1}}
                )
        
        return ConsultationResponse(
            id=consultation_id,
            domain=consultation_req.domain,
            question=consultation_req.question,
            response=response_json,
            confidence=confidence,
            tokens_used=tokens_used,
            processing_time=round(processing_time, 2),
            created_at=consultation.created_at
        )
    
    except Exception as e:
        logger.error(f"Consultation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao processar consulta: {str(e)}")

@api_router.get("/consultation/{consultation_id}")
async def get_consultation(
    consultation_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get a specific consultation"""
    consultation = await db.consultations.find_one(
        {"id": consultation_id, "user_id": current_user.id},
        {"_id": 0}
    )
    
    if not consultation:
        raise HTTPException(status_code=404, detail="Consulta não encontrada")
    
    # Parse response JSON
    import json
    consultation['response'] = json.loads(consultation['response'])
    
    return consultation

@api_router.get("/history")
async def get_history(
    domain: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Get consultation history"""
    query = {"user_id": current_user.id}
    if domain:
        query["domain"] = domain
    
    consultations = await db.consultations.find(
        query,
        {"_id": 0}
    ).sort("created_at", -1).limit(50).to_list(50)
    
    # Return simplified list
    return [
        {
            "id": c["id"],
            "domain": c["domain"],
            "question": c["question"][:100] + "..." if len(c["question"]) > 100 else c["question"],
            "confidence": c["confidence"],
            "created_at": c["created_at"]
        }
        for c in consultations
    ]

# =============================================================================
# PLANOS ROUTES
# =============================================================================

@api_router.get("/planos/todos")
async def listar_todos_planos():
    """Lista todos os planos disponíveis"""
    return {
        "planos": get_todos_planos(),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@api_router.get("/planos/meu-plano")
async def meu_plano_atual(current_user: User = Depends(get_current_user)):
    """Informações do plano atual do usuário"""
    plano_config = get_plano_config(current_user.plan)
    
    if not plano_config:
        raise HTTPException(status_code=404, detail="Configuração de plano não encontrada")
    
    # Admin Master tem privilégios especiais
    if is_admin_master(current_user):
        return {
            "usuario": {
                "id": current_user.id,
                "nome": current_user.name,
                "email": current_user.email,
                "plano": current_user.plan,
                "role": "admin_master"
            },
            "admin_master": True,
            "privilegios": {
                "consultas": "ILIMITADAS",
                "pdfs": "ILIMITADOS",
                "dominios": "TODOS (13 núcleos)",
                "historico": "PERMANENTE",
                "analytics": "ACESSO COMPLETO",
                "suporte": "PRIORIDADE MÁXIMA"
            },
            "mensagem": "🌟 Administrador Master Fundador - Acesso Pleno ao Doutor Legis 2.0 ULTRA"
        }
    
    # Verificar limites para usuários normais
    limite_consultas = verificar_limite_consultas(current_user.plan, current_user.consultas_mes_atual)
    limite_pdfs = verificar_limite_pdfs(current_user.plan, current_user.pdfs_mes_atual)
    
    return {
        "usuario": {
            "id": current_user.id,
            "nome": current_user.name,
            "email": current_user.email,
            "plano": current_user.plan
        },
        "plano": plano_config.to_dict(),
        "uso": {
            "consultas": limite_consultas,
            "pdfs": limite_pdfs
        },
        "trial": {
            "ativo": current_user.em_trial,
            "termina_em": current_user.data_trial_fim.isoformat() if current_user.data_trial_fim else None
        } if current_user.em_trial else None,
        "proxima_renovacao": current_user.data_renovacao.isoformat() if current_user.data_renovacao else None
    }

@api_router.get("/planos/verificar-limite")
async def verificar_limite(
    tipo: str,  # "consulta" ou "pdf"
    current_user: User = Depends(get_current_user)
):
    """Verifica se usuário pode usar um recurso"""
    if tipo == "consulta":
        limite = verificar_limite_consultas(current_user.plan, current_user.consultas_mes_atual)
    elif tipo == "pdf":
        limite = verificar_limite_pdfs(current_user.plan, current_user.pdfs_mes_atual)
    else:
        raise HTTPException(status_code=400, detail="Tipo inválido. Use 'consulta' ou 'pdf'")
    
    return limite

# =============================================================================
# PAYMENT ROUTES
# =============================================================================

class CheckoutRequestNew(BaseModel):
    plano: str  # "basico", "intermediario", "avancado"
    tipo_pagamento: str  # "mensal" ou "anual"
    origin_url: str

@api_router.post("/planos/upgrade")
async def upgrade_plano(
    request: CheckoutRequestNew,
    current_user: User = Depends(get_current_user)
):
    """Criar checkout para upgrade de plano"""
    # Validar plano
    if request.plano not in ["basico", "intermediario", "avancado"]:
        raise HTTPException(status_code=400, detail="Plano inválido")
    
    # Validar tipo de pagamento
    if request.tipo_pagamento not in ["mensal", "anual"]:
        raise HTTPException(status_code=400, detail="Tipo de pagamento inválido. Use 'mensal' ou 'anual'")
    
    plano_config = get_plano_config(request.plano)
    if not plano_config:
        raise HTTPException(status_code=404, detail="Configuração de plano não encontrada")
    
    # Verificar se não está fazendo downgrade (não permitido via checkout)
    planos_ordem = ["gratuito", "basico", "intermediario", "avancado"]
    if planos_ordem.index(request.plano) <= planos_ordem.index(current_user.plan):
        raise HTTPException(status_code=400, detail="Use a rota /planos/downgrade para reduzir seu plano")
    
    try:
        # Determinar preço
        valor = plano_config.preco_anual if request.tipo_pagamento == "anual" else plano_config.preco_mensal
        
        # Construir URLs
        origin = request.origin_url.rstrip('/')
        success_url = f"{origin}/payment-success?session_id={{{{CHECKOUT_SESSION_ID}}}}&plano={request.plano}"
        cancel_url = f"{origin}/dashboard"
        
        # Inicializar Stripe
        api_key = os.getenv("STRIPE_API_KEY")
        webhook_url = f"{origin}/api/webhook/stripe"
        stripe_checkout = StripeCheckout(api_key=api_key, webhook_url=webhook_url)
        
        # Criar checkout session
        session_request = CheckoutSessionRequest(
            amount=valor,
            currency="brl",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "user_id": current_user.id,
                "plano": request.plano,
                "tipo_pagamento": request.tipo_pagamento,
                "email": current_user.email
            }
        )
        
        session: CheckoutSessionResponse = await stripe_checkout.create_checkout_session(session_request)
        
        # Criar payment transaction
        transaction_id = str(uuid.uuid4())
        transaction = PaymentTransaction(
            id=transaction_id,
            session_id=session.session_id,
            user_id=current_user.id,
            amount=valor,
            currency="brl",
            status="initiated",
            payment_status="unpaid",
            metadata=session_request.metadata
        )
        
        transaction_dict = transaction.model_dump()
        transaction_dict['created_at'] = transaction_dict['created_at'].isoformat()
        await db.payment_transactions.insert_one(transaction_dict)
        
        return {
            "checkout_url": session.url,
            "session_id": session.session_id,
            "plano": request.plano,
            "valor": valor,
            "tipo": request.tipo_pagamento
        }
    
    except Exception as e:
        logger.error(f"Checkout error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao criar checkout: {str(e)}")

@api_router.post("/planos/downgrade")
async def downgrade_plano(current_user: User = Depends(get_current_user)):
    """Fazer downgrade para plano gratuito"""
    if current_user.plan == "gratuito":
        raise HTTPException(status_code=400, detail="Você já está no plano gratuito")
    
    try:
        # Atualizar usuário para gratuito
        await db.users.update_one(
            {"id": current_user.id},
            {
                "$set": {
                    "plan": "gratuito",
                    "consultas_mes_atual": 0,
                    "pdfs_mes_atual": 0,
                    "em_trial": False,
                    "data_trial_fim": None,
                    "stripe_subscription_id": None
                }
            }
        )
        
        return {
            "message": "Downgrade realizado com sucesso",
            "plano_atual": "gratuito",
            "nova_renovacao": None
        }
    
    except Exception as e:
        logger.error(f"Downgrade error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao fazer downgrade: {str(e)}")

@api_router.post("/payments/checkout")
async def create_checkout(
    checkout_req: CheckoutRequest,
    current_user: User = Depends(get_current_user)
):
    """Create Stripe checkout session (legacy - usar /planos/upgrade)"""
    # Validate package
    if checkout_req.package_id not in PAYMENT_PACKAGES:
        raise HTTPException(status_code=400, detail="Pacote inválido")
    
    package = PAYMENT_PACKAGES[checkout_req.package_id]
    
    # Build success and cancel URLs
    origin = checkout_req.origin_url.rstrip('/')
    success_url = f"{origin}/payment-success?session_id={{{{CHECKOUT_SESSION_ID}}}}"
    cancel_url = f"{origin}/dashboard"
    
    try:
        # Initialize Stripe
        api_key = os.getenv("STRIPE_API_KEY")
        webhook_url = f"{origin}/api/webhook/stripe"
        stripe_checkout = StripeCheckout(api_key=api_key, webhook_url=webhook_url)
        
        # Create checkout session
        session_request = CheckoutSessionRequest(
            amount=package["amount"],
            currency=package["currency"],
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "user_id": current_user.id,
                "package_id": checkout_req.package_id,
                "email": current_user.email
            }
        )
        
        session: CheckoutSessionResponse = await stripe_checkout.create_checkout_session(session_request)
        
        # Create payment transaction record
        transaction_id = str(uuid.uuid4())
        transaction = PaymentTransaction(
            id=transaction_id,
            session_id=session.session_id,
            user_id=current_user.id,
            amount=package["amount"],
            currency=package["currency"],
            status="initiated",
            payment_status="unpaid",
            metadata=session_request.metadata
        )
        
        transaction_dict = transaction.model_dump()
        transaction_dict['created_at'] = transaction_dict['created_at'].isoformat()
        await db.payment_transactions.insert_one(transaction_dict)
        
        return {"checkout_url": session.url, "session_id": session.session_id}
    
    except Exception as e:
        logger.error(f"Checkout error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao criar sessão de pagamento: {str(e)}")

@api_router.get("/payments/status/{session_id}")
async def get_payment_status(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get payment status"""
    try:
        # Get transaction from database
        transaction = await db.payment_transactions.find_one(
            {"session_id": session_id, "user_id": current_user.id},
            {"_id": 0}
        )
        
        if not transaction:
            raise HTTPException(status_code=404, detail="Transação não encontrada")
        
        # If already completed, return current status
        if transaction["payment_status"] == "paid":
            return {
                "status": "completed",
                "payment_status": "paid",
                "message": "Pagamento já processado"
            }
        
        # Check with Stripe
        api_key = os.getenv("STRIPE_API_KEY")
        webhook_url = "https://placeholder.com/webhook"  # Not used for status check
        stripe_checkout = StripeCheckout(api_key=api_key, webhook_url=webhook_url)
        
        checkout_status: CheckoutStatusResponse = await stripe_checkout.get_checkout_status(session_id)
        
        # Update transaction
        await db.payment_transactions.update_one(
            {"session_id": session_id},
            {
                "$set": {
                    "status": checkout_status.status,
                    "payment_status": checkout_status.payment_status
                }
            }
        )
        
        # If payment successful and not yet processed
        if checkout_status.payment_status == "paid" and transaction["payment_status"] != "paid":
            # Upgrade user to premium
            await db.users.update_one(
                {"id": current_user.id},
                {"$set": {"plan": "premium", "token_balance": 999999}}  # Unlimited for premium
            )
        
        return {
            "status": checkout_status.status,
            "payment_status": checkout_status.payment_status,
            "amount": checkout_status.amount_total / 100,  # Convert from cents
            "currency": checkout_status.currency
        }
    
    except Exception as e:
        logger.error(f"Payment status error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao verificar status: {str(e)}")

@api_router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks"""
    try:
        body = await request.body()
        signature = request.headers.get("Stripe-Signature")
        
        api_key = os.getenv("STRIPE_API_KEY")
        webhook_url = "placeholder"  # Not used in handle_webhook
        stripe_checkout = StripeCheckout(api_key=api_key, webhook_url=webhook_url)
        
        webhook_response = await stripe_checkout.handle_webhook(body, signature)
        
        logger.info(f"Webhook received: {webhook_response.event_type}")
        
        return {"received": True}
    
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return JSONResponse(status_code=400, content={"error": str(e)})

# =============================================================================
# GENERAL ROUTES
# =============================================================================

@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "2.0.0-ULTRA",
        "oab_integration": "active",
        "nucleos_ativos": 13,
        "router_inteligente": "active",
        "meta_nucleo": "active"
    }

# =============================================================================
# ULTRA - ANALYTICS & META-NÚCLEO
# =============================================================================

@api_router.get("/analytics/performance")
async def get_performance_analytics(current_user: User = Depends(get_current_user)):
    """Retorna analytics do Meta-Núcleo"""
    # Apenas para usuários plano avançado ou admin master
    if current_user.plan != "avancado" and not is_admin_master(current_user):
        raise HTTPException(
            status_code=403,
            detail="Analytics disponível apenas no Plano Avançado ou Administradores"
        )
    
    return meta_nucleo.get_dashboard_data()

@api_router.get("/analytics/router-stats")
async def get_router_stats():
    """Estatísticas do Router Inteligente"""
    from router_inteligente import router
    return {
        "stats": router.get_stats(),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@api_router.post("/feedback")
async def enviar_feedback(
    consulta_id: str,
    rating: int,
    comentario: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Enviar feedback sobre uma consulta"""
    if rating < 1 or rating > 5:
        raise HTTPException(status_code=400, detail="Rating deve ser entre 1 e 5")
    
    # Buscar consulta
    consulta = await db.consultations.find_one(
        {"id": consulta_id, "user_id": current_user.id},
        {"_id": 0, "domain": 1}
    )
    
    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta não encontrada")
    
    # Salvar feedback no MongoDB
    feedback_doc = {
        "id": str(uuid.uuid4()),
        "consulta_id": consulta_id,
        "usuario_id": current_user.id,
        "dominio": consulta["domain"],
        "rating": rating,
        "comentario": comentario,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.feedbacks.insert_one(feedback_doc)
    
    # ULTRA: Registrar no Meta-Núcleo
    meta_nucleo.registrar_feedback(
        consulta_id=consulta_id,
        dominio=consulta["domain"],
        rating=rating,
        comentario=comentario,
        usuario_id=current_user.id
    )
    
    return {
        "message": "Feedback registrado com sucesso",
        "rating": rating
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def create_indexes():
    """Criar índices MongoDB para performance"""
    try:
        # Índices de usuário
        await db.users.create_index("id", unique=True)
        await db.users.create_index("email", unique=True)
        await db.users.create_index("google_id", unique=True, sparse=True)
        await db.users.create_index("stripe_customer_id", unique=True, sparse=True)
        
        # Índices de sessão
        await db.user_sessions.create_index("session_token", unique=True)
        await db.user_sessions.create_index("user_id")
        await db.user_sessions.create_index("expires_at")
        
        # Índices de consultas
        await db.consultations.create_index([("user_id", 1), ("created_at", -1)])
        await db.consultations.create_index([("user_id", 1), ("domain", 1), ("created_at", -1)])
        await db.consultations.create_index("id", unique=True)
        
        # Índices de pagamentos
        await db.payment_transactions.create_index("session_id", unique=True)
        await db.payment_transactions.create_index("user_id")
        await db.payment_transactions.create_index([("user_id", 1), ("created_at", -1)])
        
        logger.info("MongoDB indexes created successfully")
    except Exception as e:
        logger.warning(f"Index creation warning: {str(e)}")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
