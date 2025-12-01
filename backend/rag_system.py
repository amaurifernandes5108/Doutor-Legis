"""Sistema RAG (Retrieval-Augmented Generation) para Doutor Legis 2.0 ULTRA
Integra busca semântica com Pinecone e geração com LLM
"""

from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
from pinecone_manager import PineconeManager
from document_processor import EmbeddingGenerator
from emergentintegrations.llm.chat import LlmChat, UserMessage

logger = logging.getLogger(__name__)

class RAGSystem:
    """Sistema completo de Retrieval-Augmented Generation com Multi-AI"""
    
    def __init__(
        self,
        pinecone_manager: PineconeManager,
        embedding_generator: EmbeddingGenerator,
        openai_api_key: str,
        claude_api_key: str = None,
        google_api_key: str = None,
        perplexity_api_key: str = None
    ):
        """Inicializa sistema RAG com suporte Multi-AI
        
        Args:
            pinecone_manager: Gerenciador Pinecone
            embedding_generator: Gerador de embeddings
            openai_api_key: OpenAI API Key
            claude_api_key: Claude API Key (opcional, para Multi-AI)
            google_api_key: Google AI Studio Key (opcional, para Multi-AI)
            perplexity_api_key: Perplexity Key (opcional, para Multi-AI)
        """
        self.pinecone = pinecone_manager
        self.embedder = embedding_generator
        self.openai_api_key = openai_api_key
        
        # Multi-AI orchestrator (se todas as keys estiverem disponíveis)
        self.multi_ai_enabled = all([
            claude_api_key,
            google_api_key,
            perplexity_api_key
        ])
        
        if self.multi_ai_enabled:
            from multi_ai_orchestrator import MultiAIOrchestrator
            self.orchestrator = MultiAIOrchestrator(
                openai_key=openai_api_key,
                claude_key=claude_api_key,
                google_key=google_api_key,
                perplexity_key=perplexity_api_key
            )
            logger.info("✅ Multi-AI Orchestrator ativado (5 IAs paralelas)")
        else:
            self.orchestrator = None
            logger.info("⚠️ Multi-AI desativado (keys insuficientes). Usando modo single-LLM.")
    
    async def query_with_rag(
        self,
        domain: str,
        question: str,
        top_k: int = 5,
        filter_metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Realiza consulta com RAG
        
        Args:
            domain: Domínio jurídico
            question: Pergunta do usuário
            top_k: Número de documentos relevantes a buscar
            filter_metadata: Filtros de metadata
            
        Returns:
            Dict com resposta, contexto e metadados
        """
        try:
            # 1. Gerar embedding da pergunta
            logger.info(f"RAG: Gerando embedding para pergunta em {domain}")
            question_embedding = await self.embedder.generate_embedding(question)
            
            # 2. Buscar documentos relevantes no Pinecone
            logger.info(f"RAG: Buscando {top_k} documentos relevantes")
            relevant_docs = self.pinecone.query_vectors(
                domain=domain,
                query_vector=question_embedding,
                top_k=top_k,
                filter_metadata=filter_metadata,
                sub_namespace="legislation",  # Buscar em legislation primeiro
                include_metadata=True
            )
            
            if not relevant_docs:
                logger.warning(f"RAG: Nenhum documento relevante encontrado em {domain}")
                return await self._generate_without_context(domain, question)
            
            # 3. Construir contexto
            context = self._build_context(relevant_docs)
            
            # 4. Gerar resposta com LLM usando contexto
            logger.info(f"RAG: Gerando resposta com {len(relevant_docs)} documentos")
            response = await self._generate_with_context(
                domain=domain,
                question=question,
                context=context,
                relevant_docs=relevant_docs
            )
            
            return {
                "response": response,
                "context": context,
                "relevant_documents": relevant_docs,
                "document_count": len(relevant_docs),
                "rag_enabled": True
            }
            
        except Exception as e:
            logger.error(f"Erro no RAG: {str(e)}")
            # Fallback para geração sem contexto
            return await self._generate_without_context(domain, question)
    
    def _build_context(self, relevant_docs: List[Dict[str, Any]]) -> str:
        """Constrói contexto a partir dos documentos relevantes
        
        Args:
            relevant_docs: Documentos retornados do Pinecone
            
        Returns:
            String formatada com contexto
        """
        context_parts = []
        
        for i, doc in enumerate(relevant_docs, 1):
            metadata = doc.get("metadata", {})
            text = metadata.get("text", "")
            
            # Informações sobre a fonte
            doc_type = metadata.get("document_type", "documento")
            source = metadata.get("source_url", "fonte desconhecida")
            year = metadata.get("year", "")
            
            context_parts.append(f"""
### Documento {i} ({doc_type}) - Score: {doc.get('score', 0):.3f}
Fonte: {source} ({year})
Conteúdo: {text}
""")
        
        return "\n".join(context_parts)
    
    async def _generate_with_context(
        self,
        domain: str,
        question: str,
        context: str,
        relevant_docs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Gera resposta usando contexto recuperado com sistema Multi-AI
        
        Args:
            domain: Domínio jurídico
            question: Pergunta do usuário
            context: Contexto construído dos documentos
            relevant_docs: Documentos relevantes
            
        Returns:
            Resposta estruturada do LLM
        """
        # Importar sistema Multi-AI
        from multi_ai_prompt_system import get_multi_ai_prompt
        from nucleos_especializados import get_prompt_nucleo
        from oab_knowledge_base import get_oab_context
        
        # Obter contextos
        nucleo_prompt = get_prompt_nucleo(domain)
        oab_context = get_oab_context(domain)
        
        # Gerar prompt Multi-AI
        multi_ai_system = get_multi_ai_prompt(domain, oab_context, nucleo_prompt)
        
        system_prompt = f"""{multi_ai_system}

---

**CONTEXTO RECUPERADO (RAG) - DOCUMENTOS JURÍDICOS:**

{context}

---

**INSTRUÇÕES CRÍTICAS PARA USO DO RAG:**

1. **PRIORIZE** os documentos recuperados acima na sua análise
2. **CITE EXPLICITAMENTE** cada documento usado com formato completo
3. **CONECTE** cada citação ao caso específico do usuário
4. Cada documento tem score de relevância - use os de maior score primeiro
5. Se documento não for suficiente, complemente com conhecimento geral mas INDIQUE claramente

**FORMATO DE RESPOSTA:**

Forneça a resposta seguindo EXATAMENTE a estrutura Multi-Dimensional definida no sistema prompt, incluindo:
- Análise das 5 perspectivas (Constitucional, Infraconstitucional, Jurisprudencial, Doutrinária, Metodológica)
- Conclusão unificada com tese jurídica consolidada
- Dispositivos normativos aplicáveis (dos documentos RAG)
- Precedentes vinculantes (dos documentos RAG)
- Índices de qualidade
- Nível de segurança jurídica

**IMPORTANTE:** Use Markdown para formatação (títulos com ##, listas com -, negrito com **).
"""
        
        # Criar sessão LLM
        chat = LlmChat(
            api_key=self.openai_api_key,
            session_id=f"rag_{domain}_{hash(question)}",
            system_message=system_prompt
        )
        
        chat.with_model("openai", "gpt-4o")
        
        # Gerar resposta
        user_message = UserMessage(text=question)
        response_text = await chat.send_message(user_message)
        
        # Resposta em formato Markdown estruturado
        response_data = {
            "analise_completa": response_text,  # Texto completo em Markdown
            "rag_enabled": True,
            "documents_used": len(relevant_docs),
            "confianca": 90,  # Alta confiança quando usa RAG
            "formato": "multi_ai_markdown"
        }
        
        return response_data
    
    async def _generate_without_context(
        self,
        domain: str,
        question: str
    ) -> Dict[str, Any]:
        """Gera resposta sem contexto RAG usando sistema Multi-AI
        
        Args:
            domain: Domínio jurídico
            question: Pergunta do usuário
            
        Returns:
            Resposta com indicação de falta de contexto RAG
        """
        from multi_ai_prompt_system import get_multi_ai_prompt
        from nucleos_especializados import get_prompt_nucleo
        from oab_knowledge_base import get_oab_context
        
        # Obter contextos
        nucleo_prompt = get_prompt_nucleo(domain)
        oab_context = get_oab_context(domain)
        
        # Gerar prompt Multi-AI
        multi_ai_system = get_multi_ai_prompt(domain, oab_context, nucleo_prompt)
        
        system_prompt = f"""{multi_ai_system}

---

⚠️ **AVISO IMPORTANTE - MODO SEM RAG:**

Nenhum documento específico foi encontrado no banco de dados vetorial para este domínio.

**INSTRUÇÕES:**
1. Responda baseado no conhecimento jurídico geral consolidado
2. Indique claramente áreas onde documentos específicos seriam benéficos
3. Ajuste nível de confiança conforme falta de precedentes específicos
4. Siga RIGOROSAMENTE a estrutura Multi-Dimensional

**FORMATO DE RESPOSTA:** Markdown estruturado conforme sistema Multi-AI.
"""
        
        chat = LlmChat(
            api_key=self.openai_api_key,
            session_id=f"norag_{domain}_{hash(question)}",
            system_message=system_prompt
        )
        
        chat.with_model("openai", "gpt-4o")
        
        user_message = UserMessage(text=question)
        response_text = await chat.send_message(user_message)
        
        # Resposta em Markdown sem RAG
        response_data = {
            "analise_completa": response_text,
            "rag_enabled": False,
            "warning": "⚠️ Resposta gerada sem documentos específicos do banco RAG",
            "confianca": 75,  # Confiança reduzida sem RAG
            "formato": "multi_ai_markdown"
        }
        
        return {
            "response": response_data,
            "context": None,
            "relevant_documents": [],
            "document_count": 0,
            "rag_enabled": False
        }
    
    async def store_consultation_feedback(
        self,
        domain: str,
        consultation_id: str,
        question: str,
        response: str,
        user_id: str,
        rating: int = None
    ):
        """Armazena consulta anterior no Pinecone para aprendizado futuro
        
        Args:
            domain: Domínio jurídico
            consultation_id: ID da consulta
            question: Pergunta original
            response: Resposta gerada
            user_id: ID do usuário
            rating: Rating do usuário (opcional)
        """
        from document_processor import DocumentProcessor, BrazilianLegalChunker
        
        # Combinar pergunta e resposta para contexto completo
        full_text = f"PERGUNTA: {question}\n\nRESPOSTA: {response}"
        
        metadata = {
            "consultation_id": consultation_id,
            "user_id": user_id,
            "source_url": f"consultation_{consultation_id}",
            "year": datetime.now().year,
            "document_type": "consultation",
            "domain": domain,
            "rating": rating if rating else 0,
            "created_at": datetime.now().isoformat()
        }
        
        try:
            # Processar consulta
            chunker = BrazilianLegalChunker()
            processor = DocumentProcessor(chunker, self.embedder)
            
            vectors = await processor.process_consultation(full_text, metadata)
            
            # Armazenar no Pinecone
            self.pinecone.upsert_vectors(
                domain=domain,
                vectors=vectors,
                sub_namespace="consultations"
            )
            
            logger.info(
                f"Consulta {consultation_id} armazenada no Pinecone "
                f"para aprendizado futuro ({len(vectors)} vetores)"
            )
            
        except Exception as e:
            logger.error(f"Erro ao armazenar consulta no Pinecone: {str(e)}")
