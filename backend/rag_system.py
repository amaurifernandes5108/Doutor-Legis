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
    """Sistema completo de Retrieval-Augmented Generation"""
    
    def __init__(
        self,
        pinecone_manager: PineconeManager,
        embedding_generator: EmbeddingGenerator,
        openai_api_key: str
    ):
        """Inicializa sistema RAG
        
        Args:
            pinecone_manager: Gerenciador Pinecone
            embedding_generator: Gerador de embeddings
            openai_api_key: OpenAI API Key para LLM
        """
        self.pinecone = pinecone_manager
        self.embedder = embedding_generator
        self.openai_api_key = openai_api_key
    
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
        """Gera resposta usando contexto recuperado
        
        Args:
            domain: Domínio jurídico
            question: Pergunta do usuário
            context: Contexto construído dos documentos
            relevant_docs: Documentos relevantes
            
        Returns:
            Resposta estruturada do LLM
        """
        # Importar prompts dos núcleos especializados
        from nucleos_especializados import get_prompt_nucleo
        
        nucleo_prompt = get_prompt_nucleo(domain)
        
        system_prompt = f"""{nucleo_prompt}

---

**CONTEXTO RECUPERADO (RAG):**

Você recebeu os seguintes documentos jurídicos relevantes para responder à pergunta:

{context}

---

**INSTRUÇÕES IMPORTANTES:**

1. Use PRIORITARIAMENTE o contexto recuperado acima para fundamentar sua resposta
2. Cite explicitamente os documentos quando relevante
3. Se o contexto não for suficiente, indique claramente
4. Mantenha a estrutura JSON de resposta padrão
5. Inclua referências aos documentos recuperados na sua análise

Forneça uma análise jurídica completa e estruturada seguindo EXATAMENTE este formato JSON:

{{
  "resumo": "Breve resumo da questão (2-3 linhas)",
  "legislacao_aplicavel": "Leis, artigos e normas aplicáveis (cite os documentos recuperados)",
  "jurisprudencia": "Precedentes e jurisprudência relevante",
  "analise_legal": "Análise detalhada sob a perspectiva jurídica (use o contexto recuperado)",
  "riscos_juridicos": "Principais riscos e pontos de atenção",
  "recomendacoes": "Recomendações práticas e estratégicas",
  "proximos_passos": "Este conteúdo não constitui consultoria jurídica vinculativa. Recomenda-se consultar um advogado para análise específica do seu caso.",
  "confianca": 90,
  "fontes_utilizadas": ["Documento 1", "Documento 2"]
}}
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
        
        # Parse JSON response
        import json
        try:
            response_json = json.loads(response_text)
            
            # Adicionar informação sobre RAG
            response_json["rag_enabled"] = True
            response_json["documents_used"] = len(relevant_docs)
            
        except:
            # Fallback se não for JSON válido
            response_json = {
                "resumo": response_text[:200],
                "legislacao_aplicavel": "Baseado nos documentos recuperados",
                "jurisprudencia": "Consulte os documentos fornecidos",
                "analise_legal": response_text,
                "riscos_juridicos": "Análise requer avaliação específica",
                "recomendacoes": "Recomenda-se consultar um advogado",
                "proximos_passos": "Este conteúdo não constitui consultoria jurídica vinculativa.",
                "confianca": 75,
                "rag_enabled": True,
                "documents_used": len(relevant_docs)
            }
        
        return response_json
    
    async def _generate_without_context(
        self,
        domain: str,
        question: str
    ) -> Dict[str, Any]:
        """Gera resposta sem contexto (fallback)
        
        Args:
            domain: Domínio jurídico
            question: Pergunta do usuário
            
        Returns:
            Resposta com indicação de falta de contexto
        """
        from nucleos_especializados import get_prompt_nucleo
        
        nucleo_prompt = get_prompt_nucleo(domain)
        
        system_prompt = f"""{nucleo_prompt}

⚠️ AVISO: Nenhum documento específico foi encontrado no banco de dados vetorial.
Responda baseado no conhecimento geral, mas indique que a resposta pode ser mais precisa
com documentos específicos disponíveis.

Forneça análise jurídica no formato JSON padrão.
"""
        
        chat = LlmChat(
            api_key=self.openai_api_key,
            session_id=f"norag_{domain}_{hash(question)}",
            system_message=system_prompt
        )
        
        chat.with_model("openai", "gpt-4o")
        
        user_message = UserMessage(text=question)
        response_text = await chat.send_message(user_message)
        
        import json
        try:
            response_json = json.loads(response_text)
            response_json["rag_enabled"] = False
            response_json["warning"] = "Resposta gerada sem documentos específicos do banco de dados"
        except:
            response_json = {
                "resumo": response_text[:200],
                "analise_legal": response_text,
                "rag_enabled": False,
                "warning": "Resposta gerada sem documentos específicos"
            }
        
        return {
            "response": response_json,
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
                namespace="consultations"
            )
            
            logger.info(
                f"Consulta {consultation_id} armazenada no Pinecone "
                f"para aprendizado futuro ({len(vectors)} vetores)"
            )
            
        except Exception as e:
            logger.error(f"Erro ao armazenar consulta no Pinecone: {str(e)}")
