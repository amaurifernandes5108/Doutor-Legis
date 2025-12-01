"""Meta-Núcleo - Sistema de Auto-Aprendizado Doutor Legis 2.0 ULTRA
Aprende com cada consulta e melhora o sistema continuamente
"""

from typing import Dict, List, Optional
from datetime import datetime, timezone, timedelta
from collections import defaultdict
import statistics

class MetaNucleo:
    """Núcleo de Meta-Learning para auto-otimização do sistema"""
    
    def __init__(self):
        self.metricas = defaultdict(list)
        self.erros = []
        self.feedbacks = []
        self.ultima_atualizacao = datetime.now(timezone.utc)
    
    def registrar_consulta(
        self,
        dominio: str,
        confidence: int,
        processing_time: float,
        tokens_used: int,
        router_confidence: float
    ):
        """Registra métricas de uma consulta"""
        timestamp = datetime.now(timezone.utc)
        
        self.metricas[dominio].append({
            "timestamp": timestamp,
            "confidence": confidence,
            "processing_time": processing_time,
            "tokens_used": tokens_used,
            "router_confidence": router_confidence
        })
    
    def registrar_feedback(
        self,
        consulta_id: str,
        dominio: str,
        rating: int,  # 1-5 estrelas
        comentario: Optional[str] = None,
        usuario_id: str = None
    ):
        """Registra feedback do usuário"""
        self.feedbacks.append({
            "timestamp": datetime.now(timezone.utc),
            "consulta_id": consulta_id,
            "dominio": dominio,
            "rating": rating,
            "comentario": comentario,
            "usuario_id": usuario_id
        })
    
    def registrar_erro(
        self,
        dominio: str,
        tipo_erro: str,
        detalhes: Dict,
        pergunta: str = None
    ):
        """Registra erro para análise futura"""
        self.erros.append({
            "timestamp": datetime.now(timezone.utc),
            "dominio": dominio,
            "tipo_erro": tipo_erro,
            "detalhes": detalhes,
            "pergunta": pergunta
        })
    
    def analisar_performance(self) -> Dict:
        """Analisa performance geral do sistema"""
        agora = datetime.now(timezone.utc)
        ultimo_dia = agora - timedelta(days=1)
        ultima_semana = agora - timedelta(days=7)
        
        analise = {
            "timestamp": agora.isoformat(),
            "por_dominio": {},
            "geral": {},
            "alertas": []
        }
        
        # Analisar cada domínio
        for dominio, consultas in self.metricas.items():
            # Filtrar últimas 24h
            consultas_recentes = [
                c for c in consultas
                if c["timestamp"] > ultimo_dia
            ]
            
            if not consultas_recentes:
                continue
            
            # Calcular médias
            avg_confidence = statistics.mean([c["confidence"] for c in consultas_recentes])
            avg_time = statistics.mean([c["processing_time"] for c in consultas_recentes])
            avg_tokens = statistics.mean([c["tokens_used"] for c in consultas_recentes])
            avg_router = statistics.mean([c["router_confidence"] for c in consultas_recentes])
            
            analise["por_dominio"][dominio] = {
                "total_consultas": len(consultas_recentes),
                "confidence_media": round(avg_confidence, 2),
                "tempo_medio": round(avg_time, 2),
                "tokens_medio": round(avg_tokens, 0),
                "router_confidence_media": round(avg_router, 2)
            }
            
            # Alertas
            if avg_confidence < 80:
                analise["alertas"].append({
                    "tipo": "baixa_confianca",
                    "dominio": dominio,
                    "valor": avg_confidence,
                    "mensagem": f"Confiança média abaixo de 80% em {dominio}"
                })
            
            if avg_time > 6.0:
                analise["alertas"].append({
                    "tipo": "lentidao",
                    "dominio": dominio,
                    "valor": avg_time,
                    "mensagem": f"Tempo médio acima de 6s em {dominio}"
                })
        
        # Feedback analysis
        feedbacks_recentes = [
            f for f in self.feedbacks
            if f["timestamp"] > ultima_semana
        ]
        
        if feedbacks_recentes:
            avg_rating = statistics.mean([f["rating"] for f in feedbacks_recentes])
            analise["geral"]["rating_medio"] = round(avg_rating, 2)
            analise["geral"]["total_feedbacks"] = len(feedbacks_recentes)
            
            # NPS aproximado (5 estrelas = promotor, 3-4 = neutro, 1-2 = detrator)
            promotores = len([f for f in feedbacks_recentes if f["rating"] == 5])
            detratores = len([f for f in feedbacks_recentes if f["rating"] <= 2])
            nps = ((promotores - detratores) / len(feedbacks_recentes)) * 100
            analise["geral"]["nps_aproximado"] = round(nps, 1)
        
        # Erros
        erros_recentes = [
            e for e in self.erros
            if e["timestamp"] > ultimo_dia
        ]
        analise["geral"]["total_erros_24h"] = len(erros_recentes)
        
        if len(erros_recentes) > 10:
            analise["alertas"].append({
                "tipo": "muitos_erros",
                "valor": len(erros_recentes),
                "mensagem": f"Mais de 10 erros nas últimas 24h"
            })
        
        return analise
    
    def sugerir_otimizacoes(self) -> List[Dict]:
        """Sugere otimizações baseadas em análise"""
        analise = self.analisar_performance()
        sugestoes = []
        
        # Sugestões por domínio
        for dominio, metricas in analise["por_dominio"].items():
            if metricas["confidence_media"] < 85:
                sugestoes.append({
                    "prioridade": "alta",
                    "dominio": dominio,
                    "tipo": "melhorar_prompt",
                    "razao": f"Confiança média de {metricas['confidence_media']}% - abaixo do ideal (85%+)",
                    "acao": "Revisar e refinar prompts do domínio"
                })
            
            if metricas["tempo_medio"] > 5.0:
                sugestoes.append({
                    "prioridade": "media",
                    "dominio": dominio,
                    "tipo": "otimizar_velocidade",
                    "razao": f"Tempo médio de {metricas['tempo_medio']}s - acima do ideal (3-4s)",
                    "acao": "Otimizar chamadas LLM ou considerar cache"
                })
            
            if metricas["router_confidence_media"] < 70:
                sugestoes.append({
                    "prioridade": "alta",
                    "dominio": dominio,
                    "tipo": "melhorar_router",
                    "razao": f"Router com {metricas['router_confidence_media']}% confiança - baixo",
                    "acao": "Adicionar mais keywords ou ajustar pesos"
                })
        
        # Sugestões gerais
        if analise["geral"].get("rating_medio", 5) < 4.0:
            sugestoes.append({
                "prioridade": "alta",
                "dominio": "geral",
                "tipo": "melhorar_satisfacao",
                "razao": f"Rating médio de {analise['geral']['rating_medio']} - abaixo de 4.0",
                "acao": "Investigar feedbacks negativos e implementar melhorias"
            })
        
        return sorted(sugestoes, key=lambda x: 0 if x["prioridade"] == "alta" else 1)
    
    def get_dashboard_data(self) -> Dict:
        """Retorna dados para dashboard de monitoramento"""
        return {
            "analise": self.analisar_performance(),
            "sugestoes": self.sugerir_otimizacoes(),
            "ultima_atualizacao": self.ultima_atualizacao.isoformat(),
            "proxima_atualizacao": (self.ultima_atualizacao + timedelta(hours=6)).isoformat()
        }

# Instância global
meta_nucleo = MetaNucleo()
