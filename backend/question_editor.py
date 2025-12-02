"""Sistema de Edição e Aprimoramento de Perguntas Jurídicas
Analisa perguntas e sugere melhorias para obter respostas mais precisas
"""

import logging
from typing import Dict, Any, List
from emergentintegrations.llm.chat import LlmChat, UserMessage

logger = logging.getLogger(__name__)


class QuestionEditor:
    """Editor inteligente de perguntas jurídicas"""
    
    def __init__(self, openai_api_key: str):
        """Inicializa editor
        
        Args:
            openai_api_key: OpenAI API Key
        """
        self.api_key = openai_api_key
    
    async def analyze_question(
        self,
        question: str,
        domain: str = None
    ) -> Dict[str, Any]:
        """Analisa uma pergunta e identifica pontos de melhoria
        
        Args:
            question: Pergunta original do usuário
            domain: Domínio jurídico (opcional)
            
        Returns:
            Dict com análise e sugestões
        """
        system_prompt = f"""Você é um especialista em análise de perguntas jurídicas.

**SUA TAREFA:**
Analise a pergunta do usuário e identifique:
1. Se está clara e completa
2. Informações faltantes importantes
3. Ambiguidades que podem gerar múltiplas interpretações
4. Contexto adicional necessário

**CRITÉRIOS DE CLAREZA:**
- ✅ CLARA: Pergunta específica, contexto suficiente, objetivo definido
- ⚠️ PARCIAL: Falta contexto ou detalhes importantes
- ❌ AMBÍGUA: Múltiplas interpretações possíveis

**FORMATO DE RESPOSTA (JSON):**
{{
  "status": "clara|parcial|ambigua",
  "score_clareza": 85,
  "problemas_identificados": [
    "Falta especificar se é pessoa física ou jurídica",
    "Não menciona prazo ou data dos fatos"
  ],
  "informacoes_faltantes": [
    "Qual é o valor envolvido?",
    "Houve tentativa de acordo?",
    "Há documentação que comprove?"
  ],
  "contexto_necessario": [
    "Período em que ocorreram os fatos",
    "Estado/município onde ocorreu",
    "Se já houve ação judicial prévia"
  ],
  "ambiguidades": [
    "Não está claro se refere a contrato de trabalho ou prestação de serviço"
  ],
  "sugestao_reformulacao": "Versão melhorada e mais específica da pergunta com todos os elementos necessários",
  "perguntas_clarificacao": [
    "Os fatos ocorreram em qual período?",
    "Você é pessoa física ou jurídica?",
    "Qual o valor aproximado envolvido?"
  ]
}}

**PERGUNTA DO USUÁRIO:** {question}
{f"**DOMÍNIO:** {domain}" if domain else ""}

Analise e responda APENAS com o JSON, sem texto adicional."""

        try:
            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"question_analysis_{hash(question)}",
                system_message=system_prompt
            )
            
            chat.with_model("openai", "gpt-4o")
            
            user_message = UserMessage(text="Analise esta pergunta jurídica e forneça a análise completa em JSON.")
            response_text = await chat.send_message(user_message)
            
            import json
            analysis = json.loads(response_text)
            
            logger.info(f"✅ Pergunta analisada: {analysis.get('status')} (score: {analysis.get('score_clareza')})")
            
            return {
                "success": True,
                "original_question": question,
                "analysis": analysis
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao analisar pergunta: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "original_question": question
            }
    
    async def suggest_improvements(
        self,
        question: str,
        domain: str = None,
        num_suggestions: int = 3
    ) -> List[str]:
        """Gera sugestões de melhorias para a pergunta
        
        Args:
            question: Pergunta original
            domain: Domínio jurídico
            num_suggestions: Número de sugestões
            
        Returns:
            Lista de sugestões de perguntas melhoradas
        """
        system_prompt = f"""Você é especialista em reformulação de perguntas jurídicas.

**SUA TAREFA:**
Gere {num_suggestions} versões MELHORADAS da pergunta do usuário.

**CRITÉRIOS DE MELHORIA:**
1. Mais específica e objetiva
2. Inclui contexto relevante
3. Remove ambiguidades
4. Foca no aspecto jurídico principal
5. Facilita resposta precisa

**EXEMPLO:**
Original: "Posso processar meu ex?"
Melhorada: "Tenho direito a ação de reparação de danos morais contra meu ex-cônjuge por difamação em redes sociais durante o processo de divórcio?"

**FORMATO DE RESPOSTA (JSON):**
{{
  "sugestoes": [
    "Versão melhorada 1 com mais contexto e especificidade",
    "Versão melhorada 2 focando em outro aspecto",
    "Versão melhorada 3 com abordagem diferente"
  ]
}}

**PERGUNTA ORIGINAL:** {question}
{f"**DOMÍNIO:** {domain}" if domain else ""}

Gere {num_suggestions} sugestões e responda APENAS com o JSON."""

        try:
            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"question_improve_{hash(question)}",
                system_message=system_prompt
            )
            
            chat.with_model("openai", "gpt-4o")
            
            user_message = UserMessage(text="Gere as sugestões de melhoria em JSON.")
            response_text = await chat.send_message(user_message)
            
            import json
            result = json.loads(response_text)
            
            suggestions = result.get("sugestoes", [])
            logger.info(f"✅ Geradas {len(suggestions)} sugestões de melhoria")
            
            return suggestions
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar sugestões: {str(e)}")
            return []
    
    async def expand_question(
        self,
        question: str,
        domain: str,
        user_answers: Dict[str, str]
    ) -> str:
        """Expande pergunta com base nas respostas do usuário
        
        Args:
            question: Pergunta original
            domain: Domínio jurídico
            user_answers: Respostas do usuário às perguntas de clarificação
            
        Returns:
            Pergunta expandida e melhorada
        """
        system_prompt = f"""Você é especialista em reformulação de perguntas jurídicas.

**SUA TAREFA:**
Combine a pergunta original com as informações adicionais fornecidas pelo usuário
para criar uma pergunta COMPLETA e BEM CONTEXTUALIZADA.

**CRITÉRIOS:**
1. Integrar naturalmente todas as informações
2. Manter foco jurídico
3. Ser específica e objetiva
4. Facilitar análise precisa

**PERGUNTA ORIGINAL:** {question}
**DOMÍNIO:** {domain}
**INFORMAÇÕES ADICIONAIS:** {user_answers}

Forneça APENAS a pergunta reformulada, sem explicações adicionais."""

        try:
            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"question_expand_{hash(question)}",
                system_message=system_prompt
            )
            
            chat.with_model("openai", "gpt-4o")
            
            user_message = UserMessage(text="Reformule a pergunta integrando as informações adicionais.")
            expanded = await chat.send_message(user_message)
            
            logger.info(f"✅ Pergunta expandida com sucesso")
            
            return expanded.strip()
            
        except Exception as e:
            logger.error(f"❌ Erro ao expandir pergunta: {str(e)}")
            return question  # Retornar original em caso de erro
