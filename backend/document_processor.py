"""Processador de Documentos Jurídicos para RAG
Chunking inteligente e geração de embeddings
"""

from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter
import re
import logging
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)

class BrazilianLegalChunker:
    """Chunker especializado para documentos jurídicos brasileiros"""
    
    def __init__(
        self,
        chunk_size: int = 800,
        chunk_overlap: int = 150,
        separators: List[str] = None
    ):
        """Inicializa chunker
        
        Args:
            chunk_size: Tamanho alvo dos chunks (caracteres)
            chunk_overlap: Sobreposição entre chunks
            separators: Separadores customizados
        """
        # Separadores específicos para documentos jurídicos
        if separators is None:
            separators = [
                "\n\nArt.",  # Artigos
                "\n\n§",     # Parágrafos
                "\n\nInciso", # Incisos
                "\n\nAlínea", # Alíneas
                "\n\nEMENTA", # Ementa
                "\n\nVOTO",   # Voto
                "\n\nDECISÃO", # Decisão
                "\n\n",
                "\n",
                ". ",
                " ",
                ""
            ]
        
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=separators,
            length_function=len,
            is_separator_regex=False
        )
    
    def chunk_legislation(
        self,
        text: str,
        metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Chunk de legislação preservando estrutura
        
        Args:
            text: Texto da legislação
            metadata: Metadados (tipo, ano, fonte, etc)
            
        Returns:
            Lista de chunks com texto e metadata
        """
        chunks = self.splitter.split_text(text)
        
        result = []
        for i, chunk_text in enumerate(chunks):
            # Extrair contexto (artigo, parágrafo, etc)
            context = self._extract_legal_context(chunk_text)
            
            chunk_id = self._generate_chunk_id(
                metadata.get("source_url", ""),
                i
            )
            
            result.append({
                "id": chunk_id,
                "text": chunk_text,
                "metadata": {
                    **metadata,
                    "chunk_index": i,
                    "chunk_total": len(chunks),
                    "document_type": "legislation",
                    **context
                }
            })
        
        return result
    
    def chunk_jurisprudence(
        self,
        text: str,
        metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Chunk de jurisprudência preservando seções
        
        Args:
            text: Texto da decisão judicial
            metadata: Metadados (tribunal, ano, etc)
            
        Returns:
            Lista de chunks com texto e metadata
        """
        # Identificar seções típicas
        sections = self._identify_jurisprudence_sections(text)
        
        result = []
        chunk_index = 0
        
        for section_name, section_text in sections.items():
            section_chunks = self.splitter.split_text(section_text)
            
            for i, chunk_text in enumerate(section_chunks):
                chunk_id = self._generate_chunk_id(
                    metadata.get("source_url", ""),
                    chunk_index
                )
                
                result.append({
                    "id": chunk_id,
                    "text": chunk_text,
                    "metadata": {
                        **metadata,
                        "chunk_index": chunk_index,
                        "document_type": "jurisprudence",
                        "section": section_name,
                        "section_part": i + 1
                    }
                })
                chunk_index += 1
        
        return result
    
    def chunk_consultation(
        self,
        text: str,
        metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Chunk de consultas anteriores
        
        Args:
            text: Texto da consulta
            metadata: Metadados (usuário, data, etc)
            
        Returns:
            Lista de chunks
        """
        chunks = self.splitter.split_text(text)
        
        result = []
        for i, chunk_text in enumerate(chunks):
            chunk_id = self._generate_chunk_id(
                f"consultation_{metadata.get('user_id', 'unknown')}",
                i
            )
            
            result.append({
                "id": chunk_id,
                "text": chunk_text,
                "metadata": {
                    **metadata,
                    "chunk_index": i,
                    "document_type": "consultation"
                }
            })
        
        return result
    
    def _extract_legal_context(self, text: str) -> Dict[str, Any]:
        """Extrai contexto legal do texto (artigos, parágrafos, etc)"""
        context = {}
        
        # Buscar artigo
        art_match = re.search(r'Art\.?\s+(\d+)', text)
        if art_match:
            context["article"] = art_match.group(1)
        
        # Buscar parágrafo
        par_match = re.search(r'§\s+(\d+)', text)
        if par_match:
            context["paragraph"] = par_match.group(1)
        
        # Buscar inciso
        inc_match = re.search(r'Inciso\s+([IVX]+)', text)
        if inc_match:
            context["inciso"] = inc_match.group(1)
        
        return context
    
    def _identify_jurisprudence_sections(self, text: str) -> Dict[str, str]:
        """Identifica seções típicas de jurisprudência"""
        sections = {}
        
        # Padrões de seções
        patterns = {
            "ementa": r'EMENTA[:\s]+(.*?)(?=VOTO|DECISÃO|RELATÓRIO|$)',
            "voto": r'VOTO[:\s]+(.*?)(?=DECISÃO|$)',
            "decisao": r'DECISÃO[:\s]+(.*?)$',
            "relatorio": r'RELATÓRIO[:\s]+(.*?)(?=VOTO|DECISÃO|$)'
        }
        
        for section_name, pattern in patterns.items():
            match = re.search(pattern, text, re.MULTILINE | re.DOTALL | re.IGNORECASE)
            if match:
                sections[section_name] = match.group(1).strip()
        
        # Se não encontrou seções, usar texto completo
        if not sections:
            sections["body"] = text
        
        return sections
    
    def _generate_chunk_id(self, source: str, index: int) -> str:
        """Gera ID único para o chunk"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        content_hash = hashlib.md5(f"{source}{index}{timestamp}".encode()).hexdigest()[:8]
        return f"chunk_{content_hash}_{index}"


class EmbeddingGenerator:
    """Gerador de embeddings usando OpenAI"""
    
    def __init__(self, openai_api_key: str):
        """Inicializa gerador de embeddings
        
        Args:
            openai_api_key: OpenAI API Key
        """
        from emergentintegrations.llm.chat import LlmChat
        self.api_key = openai_api_key
        self.model = "text-embedding-3-small"
        self.dimension = 1536
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Gera embedding para um texto
        
        Args:
            text: Texto para embedar
            
        Returns:
            Vetor de embedding (1536 dimensões)
        """
        import asyncio
        from openai import AsyncOpenAI
        
        client = AsyncOpenAI(api_key=self.api_key)
        
        # Limpar texto
        text = text.replace("\n", " ").strip()
        
        if not text:
            raise ValueError("Texto vazio")
        
        try:
            response = await client.embeddings.create(
                input=[text],
                model=self.model
            )
            
            embedding = response.data[0].embedding
            return embedding
            
        except Exception as e:
            logger.error(f"Erro ao gerar embedding: {str(e)}")
            raise
    
    async def generate_batch_embeddings(
        self,
        texts: List[str],
        batch_size: int = 32
    ) -> List[List[float]]:
        """Gera embeddings em lote
        
        Args:
            texts: Lista de textos
            batch_size: Tamanho do lote
            
        Returns:
            Lista de embeddings
        """
        import asyncio
        from openai import AsyncOpenAI
        
        client = AsyncOpenAI(api_key=self.api_key)
        
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            # Limpar textos
            batch = [text.replace("\n", " ").strip() for text in batch]
            
            try:
                response = await client.embeddings.create(
                    input=batch,
                    model=self.model
                )
                
                batch_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(batch_embeddings)
                
                logger.info(f"Batch {i//batch_size + 1}: {len(batch_embeddings)} embeddings gerados")
                
                # Pequena pausa entre batches
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Erro no batch {i}: {str(e)}")
                raise
        
        return all_embeddings


class DocumentProcessor:
    """Processador completo de documentos jurídicos"""
    
    def __init__(
        self,
        chunker: BrazilianLegalChunker,
        embedding_generator: EmbeddingGenerator
    ):
        """Inicializa processador
        
        Args:
            chunker: Chunker de documentos
            embedding_generator: Gerador de embeddings
        """
        self.chunker = chunker
        self.embedding_generator = embedding_generator
    
    async def process_legislation(
        self,
        text: str,
        metadata: Dict[str, Any]
    ) -> List[tuple]:
        """Processa legislação completa
        
        Args:
            text: Texto da legislação
            metadata: Metadados
            
        Returns:
            Lista de tuplas (id, embedding, metadata) para upsert
        """
        # Chunk do documento
        chunks = self.chunker.chunk_legislation(text, metadata)
        
        # Gerar embeddings
        texts = [chunk["text"] for chunk in chunks]
        embeddings = await self.embedding_generator.generate_batch_embeddings(texts)
        
        # Preparar vetores para upsert
        vectors = []
        for chunk, embedding in zip(chunks, embeddings):
            vectors.append((
                chunk["id"],
                embedding,
                chunk["metadata"]
            ))
        
        logger.info(f"Legislação processada: {len(vectors)} vetores")
        return vectors
    
    async def process_jurisprudence(
        self,
        text: str,
        metadata: Dict[str, Any]
    ) -> List[tuple]:
        """Processa jurisprudência completa
        
        Args:
            text: Texto da decisão
            metadata: Metadados
            
        Returns:
            Lista de tuplas para upsert
        """
        chunks = self.chunker.chunk_jurisprudence(text, metadata)
        
        texts = [chunk["text"] for chunk in chunks]
        embeddings = await self.embedding_generator.generate_batch_embeddings(texts)
        
        vectors = []
        for chunk, embedding in zip(chunks, embeddings):
            vectors.append((
                chunk["id"],
                embedding,
                chunk["metadata"]
            ))
        
        logger.info(f"Jurisprudência processada: {len(vectors)} vetores")
        return vectors
    
    async def process_consultation(
        self,
        text: str,
        metadata: Dict[str, Any]
    ) -> List[tuple]:
        """Processa consulta anterior
        
        Args:
            text: Texto da consulta
            metadata: Metadados
            
        Returns:
            Lista de tuplas para upsert
        """
        chunks = self.chunker.chunk_consultation(text, metadata)
        
        texts = [chunk["text"] for chunk in chunks]
        embeddings = await self.embedding_generator.generate_batch_embeddings(texts)
        
        vectors = []
        for chunk, embedding in zip(chunks, embeddings):
            vectors.append((
                chunk["id"],
                embedding,
                chunk["metadata"]
            ))
        
        logger.info(f"Consulta processada: {len(vectors)} vetores")
        return vectors
