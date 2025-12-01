"""Configuração de Planos - Doutor Legis 2.0"""

from typing import Dict, List, Optional

class PlanoConfig:
    """Configuração de um plano"""
    def __init__(
        self,
        id: str,
        nome: str,
        preco_mensal: float,
        preco_anual: float,
        desconto_anual: int,
        consultas_mes: Optional[int],  # None = ilimitado
        pdfs_mes: Optional[int],  # None = ilimitado
        dominios_disponiveis: int,
        historico_meses: Optional[int],  # None = permanente
        features: List[str],
        suporte: Dict[str, any],
        trial_dias: int = 0,
        stripe_price_mensal: Optional[str] = None,
        stripe_price_anual: Optional[str] = None
    ):
        self.id = id
        self.nome = nome
        self.preco_mensal = preco_mensal
        self.preco_anual = preco_anual
        self.desconto_anual = desconto_anual
        self.consultas_mes = consultas_mes
        self.pdfs_mes = pdfs_mes
        self.dominios_disponiveis = dominios_disponiveis
        self.historico_meses = historico_meses
        self.features = features
        self.suporte = suporte
        self.trial_dias = trial_dias
        self.stripe_price_mensal = stripe_price_mensal
        self.stripe_price_anual = stripe_price_anual
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "nome": self.nome,
            "preco_mensal": self.preco_mensal,
            "preco_anual": self.preco_anual,
            "desconto_anual": self.desconto_anual,
            "economia_anual": round(self.preco_mensal * 12 - self.preco_anual, 2),
            "consultas_mes": self.consultas_mes,
            "pdfs_mes": self.pdfs_mes,
            "consultas_texto": "Ilimitadas" if self.consultas_mes is None else f"{self.consultas_mes}/mês",
            "pdfs_texto": "Ilimitados" if self.pdfs_mes is None else f"{self.pdfs_mes}/mês",
            "dominios_disponiveis": self.dominios_disponiveis,
            "historico_meses": self.historico_meses,
            "historico_texto": "Permanente" if self.historico_meses is None else f"{self.historico_meses} meses",
            "features": self.features,
            "suporte": self.suporte,
            "trial_dias": self.trial_dias,
            "tem_trial": self.trial_dias > 0
        }

# Configuração dos 4 planos
PLANOS = {
    "gratuito": PlanoConfig(
        id="gratuito",
        nome="Plano Gratuito",
        preco_mensal=0.0,
        preco_anual=0.0,
        desconto_anual=0,
        consultas_mes=3,
        pdfs_mes=0,
        dominios_disponiveis=1,  # Apenas Ética OAB
        historico_meses=0,
        features=[
            "3 consultas jurídicas por mês",
            "1 domínio (Ética e Advocacia OAB)",
            "Análise completa em 8 seções",
            "Acesso à base de conhecimento OAB"
        ],
        suporte={
            "email": False,
            "chat": False,
            "telefone": False,
            "tempo_resposta": None
        },
        trial_dias=0
    ),
    
    "basico": PlanoConfig(
        id="basico",
        nome="Plano Básico",
        preco_mensal=197.0,
        preco_anual=1773.0,  # 25% desconto
        desconto_anual=25,
        consultas_mes=30,
        pdfs_mes=5,
        dominios_disponiveis=3,
        historico_meses=3,
        features=[
            "30 consultas jurídicas por mês",
            "5 exportações PDF por mês",
            "3 domínios jurídicos",
            "PDF simples",
            "Histórico de 3 meses",
            "Suporte por email (72h)"
        ],
        suporte={
            "email": True,
            "chat": False,
            "telefone": False,
            "tempo_resposta": 72
        },
        trial_dias=14,
        stripe_price_mensal="price_basico_mensal",  # Substituir por IDs reais
        stripe_price_anual="price_basico_anual"
    ),
    
    "intermediario": PlanoConfig(
        id="intermediario",
        nome="Plano Intermediário",
        preco_mensal=497.0,
        preco_anual=4476.0,  # 25% desconto
        desconto_anual=25,
        consultas_mes=150,
        pdfs_mes=25,
        dominios_disponiveis=9,  # Todos
        historico_meses=12,
        features=[
            "150 consultas jurídicas por mês",
            "25 exportações PDF por mês",
            "9 domínios jurídicos (todos)",
            "PDF profissional",
            "Exportação Word",
            "Dashboard avançado",
            "Histórico de 12 meses",
            "Suporte por email prioritário (24h)"
        ],
        suporte={
            "email": True,
            "chat": False,
            "telefone": False,
            "tempo_resposta": 24
        },
        trial_dias=14,
        stripe_price_mensal="price_intermediario_mensal",
        stripe_price_anual="price_intermediario_anual"
    ),
    
    "avancado": PlanoConfig(
        id="avancado",
        nome="Plano Avançado",
        preco_mensal=997.0,
        preco_anual=8976.0,  # 30% desconto
        desconto_anual=30,
        consultas_mes=None,  # Ilimitado
        pdfs_mes=None,  # Ilimitado
        dominios_disponiveis=9,  # Todos
        historico_meses=None,  # Permanente
        features=[
            "Consultas ILIMITADAS",
            "PDFs ILIMITADOS",
            "9 domínios jurídicos (todos)",
            "PDF profissional + Word",
            "Dashboard completo",
            "Histórico permanente",
            "Suporte multicanal (chat, email, telefone)",
            "Chat support (resposta 1h)",
            "Email prioritário",
            "Suporte telefônico",
            "Account Manager dedicado",
            "Acesso à API",
            "Webhooks customizados",
            "SLA 99.9% uptime"
        ],
        suporte={
            "email": True,
            "chat": True,
            "telefone": True,
            "tempo_resposta": 1,
            "account_manager": True
        },
        trial_dias=14,
        stripe_price_mensal="price_avancado_mensal",
        stripe_price_anual="price_avancado_anual"
    )
}

# Domínios disponíveis por plano
DOMINIOS_POR_PLANO = {
    "gratuito": ["etica_advocacia_oab"],
    "basico": ["etica_advocacia_oab", "civil", "consumidor"],
    "intermediario": [
        "constitucional", "civil", "consumidor", "imobiliario", "publico", 
        "trabalhista", "empresarial", "internacional", "etica_advocacia_oab",
        "penal", "tributario", "previdenciario", "tecnologia"
    ],
    "avancado": [
        "constitucional", "civil", "consumidor", "imobiliario", "publico", 
        "trabalhista", "empresarial", "internacional", "etica_advocacia_oab",
        "penal", "tributario", "previdenciario", "tecnologia"
    ]
}

def get_plano_config(plano_id: str) -> Optional[PlanoConfig]:
    """Retorna configuração de um plano"""
    return PLANOS.get(plano_id)

def get_todos_planos() -> List[Dict]:
    """Retorna todos os planos como dicionários"""
    return [plano.to_dict() for plano in PLANOS.values()]

def verificar_limite_consultas(plano_id: str, usado: int) -> Dict:
    """Verifica se usuário atingiu limite de consultas"""
    plano = get_plano_config(plano_id)
    if not plano:
        return {"pode_usar": False, "mensagem": "Plano inválido"}
    
    if plano.consultas_mes is None:
        return {
            "pode_usar": True,
            "ilimitado": True,
            "usado": usado,
            "limite": None
        }
    
    restante = plano.consultas_mes - usado
    pode_usar = restante > 0
    
    return {
        "pode_usar": pode_usar,
        "ilimitado": False,
        "usado": usado,
        "limite": plano.consultas_mes,
        "restante": restante,
        "percentual_usado": round((usado / plano.consultas_mes) * 100, 1)
    }

def verificar_limite_pdfs(plano_id: str, usado: int) -> Dict:
    """Verifica se usuário atingiu limite de PDFs"""
    plano = get_plano_config(plano_id)
    if not plano:
        return {"pode_usar": False, "mensagem": "Plano inválido"}
    
    if plano.pdfs_mes is None:
        return {
            "pode_usar": True,
            "ilimitado": True,
            "usado": usado,
            "limite": None
        }
    
    restante = plano.pdfs_mes - usado
    pode_usar = restante > 0
    
    return {
        "pode_usar": pode_usar,
        "ilimitado": False,
        "usado": usado,
        "limite": plano.pdfs_mes,
        "restante": restante,
        "percentual_usado": round((usado / plano.pdfs_mes) * 100, 1) if plano.pdfs_mes > 0 else 0
    }

def verificar_acesso_dominio(plano_id: str, dominio_id: str) -> bool:
    """Verifica se usuário tem acesso a um domínio"""
    dominios_permitidos = DOMINIOS_POR_PLANO.get(plano_id, [])
    return dominio_id in dominios_permitidos

def get_dominios_disponiveis(plano_id: str) -> List[str]:
    """Retorna lista de domínios disponíveis para o plano"""
    return DOMINIOS_POR_PLANO.get(plano_id, [])
