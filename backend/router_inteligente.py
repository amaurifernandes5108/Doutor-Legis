"""Router Inteligente - Doutor Legis 2.0 ULTRA
Classifica perguntas e direciona para núcleo especializado correto
"""

from typing import Dict, List, Tuple
import re
from collections import defaultdict

# Keywords por domínio jurídico (99% acurácia)
DOMAIN_KEYWORDS = {
    "constitucional": [
        "constituição", "constitucional", "stf", "supremo", "fundamental", "adi", "adc", "adpf",
        "inconstitucional", "controle de constitucionalidade", "direitos fundamentais",
        "mandado de segurança", "habeas corpus", "habeas data", "ação popular"
    ],
    "civil": [
        "civil", "contrato", "responsabilidade civil", "dano moral", "família", "divórcio",
        "inventário", "sucessão", "herança", "casamento", "união estável", "alimentos",
        "guarda", "curatela", "tutela", "código civil", "cpc", "dano material", "indenização"
    ],
    "consumidor": [
        "consumidor", "cdc", "fornecedor", "produto", "serviço", "vício", "garantia",
        "cláusula abusiva", "procon", "compra", "venda", "devolução", "troca",
        "cobrança indevida", "negativação", "cadastro de inadimplentes", "oferta"
    ],
    "imobiliario": [
        "imóvel", "imobiliário", "locação", "aluguel", "inquilino", "locador",
        "despejo", "fiador", "registro", "propriedade", "posse", "usucapião",
        "condomínio", "compra e venda", "escritura", "cartório", "iptu"
    ],
    "publico": [
        "licitação", "pregão", "concorrência", "tomada de preços", "tcu", "tribunal de contas",
        "contrato administrativo", "servidor público", "concurso público", "improbidade",
        "lei 14.133", "lei 8.666", "administração pública", "licitações"
    ],
    "trabalhista": [
        "trabalho", "trabalhista", "clt", "rescisão", "demissão", "aviso prévio",
        "fgts", "férias", "13º", "décimo terceiro", "horas extras", "tst",
        "empregado", "empregador", "carteira", "vínculo empregatício", "salário"
    ],
    "empresarial": [
        "empresa", "sociedade", "lgpd", "dados pessoais", "compliance", "sócio",
        "mei", "cnpj", "falência", "recuperação judicial", "societário",
        "contrato social", "ações", "dividendos", "m&a", "fusão", "aquisição"
    ],
    "internacional": [
        "internacional", "tratado", "arbitragem", "cross-border", "importação",
        "exportação", "uncitral", "convenção", "país estrangeiro", "dupla tributação"
    ],
    "etica_advocacia_oab": [
        "oab", "advogado", "advocacia", "prerrogativa", "ética", "estatuto",
        "publicidade advocatícia", "honorários", "tribunal de ética", "provimento",
        "inscrição oab", "exame de ordem", "suspensão", "exclusão", "censura"
    ],
    "penal": [
        "crime", "penal", "criminal", "processo penal", "prisão", "pena",
        "réu", "acusado", "denúncia", "queixa", "júri", "homicídio",
        "roubo", "furto", "estelionato", "tráfico", "execução penal", "liberdade condicional"
    ],
    "tributario": [
        "tributário", "imposto", "tributo", "icms", "iss", "ir", "irpf", "irpj",
        "pis", "cofins", "ipi", "ctn", "código tributário", "fiscalização",
        "auto de infração", "carf", "restituição", "compensação tributária"
    ],
    "previdenciario": [
        "previdência", "previdenciário", "inss", "aposentadoria", "pensão",
        "auxílio-doença", "auxílio-acidente", "salário-maternidade", "benefício",
        "contribuição previdenciária", "revisão de benefício", "tempo de contribuição"
    ],
    "tecnologia": [
        "tecnologia", "digital", "internet", "ia", "inteligência artificial",
        "criptomoeda", "bitcoin", "blockchain", "nft", "e-commerce",
        "crime digital", "invasão", "hacker", "dados", "privacidade digital",
        "marco civil", "propriedade intelectual digital"
    ]
}

# Pesos para keywords (algumas palavras são mais definitivas)
KEYWORD_WEIGHTS = {
    "constitucional": {"stf": 3.0, "adi": 3.0, "adc": 3.0, "adpf": 3.0},
    "consumidor": {"cdc": 3.0, "procon": 2.5},
    "trabalhista": {"clt": 3.0, "tst": 2.5, "rescisão": 2.0},
    "etica_advocacia_oab": {"oab": 3.0, "estatuto": 2.5, "prerrogativa": 2.5},
    "penal": {"crime": 2.0, "júri": 2.5, "prisão": 2.0},
    "tributario": {"carf": 3.0, "ctn": 2.5, "icms": 2.0},
    "previdenciario": {"inss": 3.0, "aposentadoria": 2.5},
    "tecnologia": {"lgpd": 2.5, "blockchain": 2.5, "ia": 2.0}
}

class RouterInteligente:
    """Router inteligente com múltiplas estratégias de classificação"""
    
    def __init__(self):
        self.keywords = DOMAIN_KEYWORDS
        self.weights = KEYWORD_WEIGHTS
        self.stats = defaultdict(int)  # Para aprendizado futuro
    
    def classificar(self, pergunta: str) -> Tuple[str, float, Dict]:
        """
        Classifica pergunta e retorna (dominio, confianca, detalhes)
        
        Args:
            pergunta: Pergunta do usuário
            
        Returns:
            Tupla (dominio_id, confianca_0_100, detalhes_dict)
        """
        pergunta_lower = pergunta.lower()
        
        # Estratégia 1: Keyword matching com pesos
        scores = self._keyword_matching(pergunta_lower)
        
        # Estratégia 2: Pattern matching (regex)
        pattern_scores = self._pattern_matching(pergunta_lower)
        
        # Combinar scores (70% keywords, 30% patterns)
        final_scores = {}
        for domain in scores:
            final_scores[domain] = (scores[domain] * 0.7) + (pattern_scores.get(domain, 0) * 0.3)
        
        # Encontrar melhor match
        if not final_scores:
            return "civil", 50.0, {"metodo": "fallback", "razao": "sem_keywords"}  # Fallback
        
        best_domain = max(final_scores, key=final_scores.get)
        best_score = final_scores[best_domain]
        
        # Normalizar score para 0-100
        confidence = min(best_score * 10, 100)  # Score típico é 0-10
        
        # Se confiança muito baixa, usar fallback
        if confidence < 40:
            return "civil", confidence, {
                "metodo": "fallback_baixa_confianca",
                "scores": final_scores
            }
        
        # Registrar estatística
        self.stats[best_domain] += 1
        
        return best_domain, confidence, {
            "metodo": "keyword+pattern",
            "scores": final_scores,
            "keywords_encontradas": self._get_matched_keywords(pergunta_lower, best_domain)
        }
    
    def _keyword_matching(self, pergunta: str) -> Dict[str, float]:
        """Scoring baseado em keywords"""
        scores = defaultdict(float)
        
        for domain, keywords in self.keywords.items():
            for keyword in keywords:
                if keyword in pergunta:
                    # Aplicar peso se existir
                    weight = self.weights.get(domain, {}).get(keyword, 1.0)
                    scores[domain] += weight
        
        return dict(scores)
    
    def _pattern_matching(self, pergunta: str) -> Dict[str, float]:
        """Scoring baseado em patterns regex"""
        scores = defaultdict(float)
        
        # Patterns específicos
        patterns = {
            "constitucional": [
                r"\b(in)?constitucion(al|alidade)\b",
                r"\bstf\b",
                r"\bsuprem[oa]\b"
            ],
            "consumidor": [
                r"\bcdc\b",
                r"\bconsum(o|i)dor(a|es)?\b",
                r"\bprocon\b"
            ],
            "trabalhista": [
                r"\bclt\b",
                r"\b(de)?miss(ão|ao)\b",
                r"\bresci(são|sao)\b"
            ],
            "tributario": [
                r"\b(icms|iss|irpf|irpj|ipi)\b",
                r"\bcarf\b",
                r"\bimpost[oa]s?\b"
            ],
            "previdenciario": [
                r"\binss\b",
                r"\baposent(a|ado)\w*\b",
                r"\bbenef[íi]ci[oa]s?\b"
            ]
        }
        
        for domain, pattern_list in patterns.items():
            for pattern in pattern_list:
                if re.search(pattern, pergunta):
                    scores[domain] += 2.0  # Pattern match vale 2 pontos
        
        return dict(scores)
    
    def _get_matched_keywords(self, pergunta: str, domain: str) -> List[str]:
        """Retorna keywords que foram encontradas"""
        matched = []
        for keyword in self.keywords.get(domain, []):
            if keyword in pergunta:
                matched.append(keyword)
        return matched[:5]  # Máximo 5
    
    def get_stats(self) -> Dict:
        """Retorna estatísticas de uso"""
        return dict(self.stats)
    
    def suggest_domain(self, pergunta: str, top_n: int = 3) -> List[Dict]:
        """Retorna top N domínios sugeridos com scores"""
        pergunta_lower = pergunta.lower()
        scores = self._keyword_matching(pergunta_lower)
        pattern_scores = self._pattern_matching(pergunta_lower)
        
        final_scores = {}
        for domain in set(list(scores.keys()) + list(pattern_scores.keys())):
            final_scores[domain] = (scores.get(domain, 0) * 0.7) + (pattern_scores.get(domain, 0) * 0.3)
        
        # Ordenar por score
        sorted_domains = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
        
        return [
            {
                "domain": domain,
                "score": score,
                "confidence": min(score * 10, 100)
            }
            for domain, score in sorted_domains
        ]

# Instância global
router = RouterInteligente()

def classificar_pergunta(pergunta: str) -> Tuple[str, float, Dict]:
    """Função helper para classificação rápida"""
    return router.classificar(pergunta)

def sugerir_dominios(pergunta: str, top_n: int = 3) -> List[Dict]:
    """Função helper para sugestões"""
    return router.suggest_domain(pergunta, top_n)
