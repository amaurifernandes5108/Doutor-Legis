"""Pinecone Vector Database Manager para Doutor Legis 2.0 ULTRA
Gerencia 13 índices separados para cada núcleo jurídico
"""

from pinecone import Pinecone, ServerlessSpec
from typing import List, Dict, Any, Optional
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)

# 13 Domínios Jurídicos do Sistema ULTRA
LEGAL_DOMAINS = [
    "constitucional",
    "civil",
    "consumidor",
    "imobiliario",
    "publico",
    "trabalhista",
    "empresarial",
    "internacional",
    "etica_advocacia_oab",
    "penal",
    "tributario",
    "previdenciario",
    "tecnologia"
]

class PineconeManager:
    """Gerenciador central de índices Pinecone com arquitetura de namespace único"""
    
    def __init__(self, api_key: str, index_name: str = "legal-ultra"):
        """Inicializa conexão com Pinecone
        
        Args:
            api_key: Pinecone API key
            index_name: Nome do índice único para todos os domínios
        """
        self.pc = Pinecone(api_key=api_key)
        self.index_name = index_name
        self.index = None
        
    def create_index(
        self,
        dimension: int = 1536,  # OpenAI text-embedding-3-small
        metric: str = "cosine",
        cloud: str = "aws",
        region: str = "us-east-1"
    ):
        """Cria o índice único Pinecone para todos os domínios
        
        Args:
            dimension: Dimensão dos vetores (1536 para OpenAI embedding-3-small)
            metric: Métrica de similaridade (cosine, euclidean, dotproduct)
            cloud: Provedor cloud (aws, gcp, azure)
            region: Região do servidor
        """
        try:
            # Verificar se índice já existe
            existing_indexes = self.pc.list_indexes()
            index_exists = any(idx['name'] == self.index_name for idx in existing_indexes)
            
            if index_exists:
                logger.info(f"Índice {self.index_name} já existe")
                self.index = self.pc.Index(self.index_name)
                return self.index_name
            
            logger.info(f"Criando índice único: {self.index_name}")
            
            # Criar índice serverless
            self.pc.create_index(
                name=self.index_name,
                dimension=dimension,
                metric=metric,
                spec=ServerlessSpec(
                    cloud=cloud,
                    region=region
                )
            )
            
            logger.info(f"✅ Índice {self.index_name} criado com sucesso")
            logger.info(f"📦 13 namespaces serão usados para separar domínios")
            
            self.index = self.pc.Index(self.index_name)
            return self.index_name
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar índice {self.index_name}: {str(e)}")
            raise
    
    def initialize(self):
        """Inicializa o índice único para todos os 13 domínios"""
        logger.info("🚀 Inicializando arquitetura com namespace único...")
        
        try:
            self.create_index()
            
            logger.info(f"""
✅ Inicialização completa!

Índice criado: {self.index_name}
Arquitetura: 1 índice com 13 namespaces
Namespaces disponíveis:
""")
            for i, domain in enumerate(LEGAL_DOMAINS, 1):
                logger.info(f"  {i}. {domain}")
            
            return {"success": True, "index": self.index_name, "namespaces": LEGAL_DOMAINS}
            
        except Exception as e:
            logger.error(f"Erro na inicialização: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_index(self, domain: str):
        """Obtém referência para um índice específico
        
        Args:
            domain: Nome do domínio jurídico
            
        Returns:
            Pinecone Index object
        """
        index_name = f"{self.index_prefix}{domain}"
        
        if domain not in self.indexes:
            self.indexes[domain] = self.pc.Index(index_name)
        
        return self.indexes[domain]
    
    def delete_index(self, domain: str):
        """Remove um índice Pinecone
        
        Args:
            domain: Nome do domínio jurídico
        """
        index_name = f"{self.index_prefix}{domain}"
        
        try:
            self.pc.delete_index(index_name)
            logger.info(f"Índice {index_name} removido")
            
            if domain in self.indexes:
                del self.indexes[domain]
                
        except Exception as e:
            logger.error(f"Erro ao remover índice {index_name}: {str(e)}")
            raise
    
    def list_indexes(self) -> List[Dict[str, Any]]:
        """Lista todos os índices Pinecone"""
        try:
            indexes = self.pc.list_indexes()
            return indexes
        except Exception as e:
            logger.error(f"Erro ao listar índices: {str(e)}")
            return []
    
    def get_index_stats(self, domain: str) -> Dict[str, Any]:
        """Obtém estatísticas de um índice
        
        Args:
            domain: Nome do domínio jurídico
            
        Returns:
            Dict com estatísticas (vector_count, dimension, etc)
        """
        try:
            index = self.get_index(domain)
            stats = index.describe_index_stats()
            return stats
        except Exception as e:
            logger.error(f"Erro ao obter stats de {domain}: {str(e)}")
            return {}
    
    def upsert_vectors(
        self,
        domain: str,
        vectors: List[tuple],
        namespace: str = ""
    ):
        """Insere/atualiza vetores em um índice
        
        Args:
            domain: Nome do domínio jurídico
            vectors: Lista de tuplas (id, values, metadata)
            namespace: Namespace para organizar vetores (opcional)
        """
        try:
            index = self.get_index(domain)
            response = index.upsert(
                vectors=vectors,
                namespace=namespace
            )
            
            logger.info(
                f"✅ Upsert em {domain}: {response.upserted_count} vetores"
            )
            return response
            
        except Exception as e:
            logger.error(f"❌ Erro no upsert para {domain}: {str(e)}")
            raise
    
    def query_vectors(
        self,
        domain: str,
        query_vector: List[float],
        top_k: int = 10,
        filter_metadata: Dict[str, Any] = None,
        namespace: str = "",
        include_metadata: bool = True
    ) -> List[Dict[str, Any]]:
        """Busca vetores similares
        
        Args:
            domain: Nome do domínio jurídico
            query_vector: Vetor de consulta (embedding)
            top_k: Número de resultados
            filter_metadata: Filtros de metadata
            namespace: Namespace para buscar
            include_metadata: Incluir metadata nos resultados
            
        Returns:
            Lista de matches com scores e metadata
        """
        try:
            index = self.get_index(domain)
            
            results = index.query(
                vector=query_vector,
                top_k=top_k,
                filter=filter_metadata,
                namespace=namespace,
                include_metadata=include_metadata,
                include_values=False
            )
            
            matches = []
            for match in results.matches:
                matches.append({
                    "id": match.id,
                    "score": match.score,
                    "metadata": match.metadata if include_metadata else None
                })
            
            logger.info(
                f"Busca em {domain}: {len(matches)} resultados (top_k={top_k})"
            )
            
            return matches
            
        except Exception as e:
            logger.error(f"Erro na busca em {domain}: {str(e)}")
            return []
    
    def delete_vectors(
        self,
        domain: str,
        ids: List[str],
        namespace: str = ""
    ):
        """Remove vetores de um índice
        
        Args:
            domain: Nome do domínio jurídico
            ids: IDs dos vetores a remover
            namespace: Namespace dos vetores
        """
        try:
            index = self.get_index(domain)
            index.delete(ids=ids, namespace=namespace)
            
            logger.info(f"✅ Removidos {len(ids)} vetores de {domain}")
            
        except Exception as e:
            logger.error(f"Erro ao remover vetores de {domain}: {str(e)}")
            raise
