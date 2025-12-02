"""Sistema Automatizado de Atualização via RSS - Planalto
Monitora novas legislações e atualiza o banco RAG automaticamente
"""

import feedparser
import requests
from bs4 import BeautifulSoup
import asyncio
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Any
from pinecone_manager import PineconeManager
from document_processor import (
    BrazilianLegalChunker,
    EmbeddingGenerator,
    DocumentProcessor
)
from router_inteligente import classificar_pergunta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# URL do RSS do Planalto
RSS_URL = "https://www4.planalto.gov.br/legislacao/rss"

# Mapeamento de tipos de legislação para domínios
TIPO_TO_DOMAIN = {
    "constituição": "constitucional",
    "emenda constitucional": "constitucional",
    "código civil": "civil",
    "código de processo civil": "civil",
    "código de defesa do consumidor": "consumidor",
    "cdc": "consumidor",
    "clt": "trabalhista",
    "consolidação das leis do trabalho": "trabalhista",
    "código penal": "penal",
    "código de processo penal": "penal",
    "lei penal": "penal",
    "crime": "penal",
    "código tributário": "tributario",
    "tributo": "tributario",
    "imposto": "tributario",
    "previdência": "previdenciario",
    "aposentadoria": "previdenciario",
    "inss": "previdenciario",
    "oab": "etica_advocacia_oab",
    "ordem dos advogados": "etica_advocacia_oab",
    "estatuto da advocacia": "etica_advocacia_oab",
    "propriedade": "imobiliario",
    "registro de imóveis": "imobiliario",
    "usucapião": "imobiliario",
    "licitação": "publico",
    "contrato administrativo": "publico",
    "servidor público": "publico",
    "empresa": "empresarial",
    "societário": "empresarial",
    "falência": "empresarial",
    "tratado internacional": "internacional",
    "convenção": "internacional",
    "lgpd": "tecnologia",
    "proteção de dados": "tecnologia",
    "marco civil": "tecnologia"
}


class RSSLegislationUpdater:
    """Atualizador automático via RSS"""
    
    def __init__(
        self,
        pinecone_manager: PineconeManager,
        processor: DocumentProcessor
    ):
        """Inicializa o atualizador
        
        Args:
            pinecone_manager: Gerenciador Pinecone
            processor: Processador de documentos
        """
        self.pinecone = pinecone_manager
        self.processor = processor
        self.processed_ids = self._load_processed_ids()
    
    def _load_processed_ids(self) -> set:
        """Carrega IDs de legislações já processadas"""
        try:
            if os.path.exists("/tmp/processed_legislation_ids.txt"):
                with open("/tmp/processed_legislation_ids.txt", "r") as f:
                    return set(line.strip() for line in f)
        except:
            pass
        return set()
    
    def _save_processed_id(self, legislation_id: str):
        """Salva ID de legislação processada"""
        self.processed_ids.add(legislation_id)
        try:
            with open("/tmp/processed_legislation_ids.txt", "a") as f:
                f.write(f"{legislation_id}\n")
        except Exception as e:
            logger.warning(f"Erro ao salvar ID processado: {str(e)}")
    
    def fetch_rss_feed(self, retry=3) -> List[Dict[str, Any]]:
        """Busca feed RSS do Planalto com retry
        
        Args:
            retry: Número de tentativas
            
        Returns:
            Lista de entradas do feed
        """
        for attempt in range(retry):
            try:
                logger.info(f"📡 Tentativa {attempt + 1}/{retry}: Buscando feed RSS")
                
                # Tentar com requests primeiro (mais confiável)
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                response = requests.get(RSS_URL, headers=headers, timeout=30)
                response.raise_for_status()
                
                feed = feedparser.parse(response.content)
                
                if feed.bozo and hasattr(feed, 'bozo_exception'):
                    logger.warning(f"⚠️ Aviso RSS: {feed.bozo_exception}")
                
                if feed.entries:
                    logger.info(f"✅ Feed obtido: {len(feed.entries)} entradas")
                    return feed.entries
                
            except Exception as e:
                logger.warning(f"⚠️ Tentativa {attempt + 1} falhou: {str(e)}")
                if attempt < retry - 1:
                    import time
                    time.sleep(3)
                continue
        
        logger.error(f"❌ Todas as tentativas falharam")
        return []
    
    def filter_new_entries(
        self,
        entries: List[Any],
        days_back: int = 30
    ) -> List[Dict[str, Any]]:
        """Filtra apenas entradas novas e não processadas
        
        Args:
            entries: Entradas do feed
            days_back: Quantos dias atrás considerar
            
        Returns:
            Lista de entradas filtradas
        """
        cutoff_date = datetime.now() - timedelta(days=days_back)
        new_entries = []
        
        for entry in entries:
            # Gerar ID único da legislação
            entry_id = entry.get('id', entry.get('link', ''))
            
            # Pular se já processado
            if entry_id in self.processed_ids:
                continue
            
            # Verificar data
            published = entry.get('published_parsed')
            if published:
                pub_date = datetime(*published[:6])
                if pub_date < cutoff_date:
                    continue
            
            new_entries.append({
                'id': entry_id,
                'title': entry.get('title', ''),
                'link': entry.get('link', ''),
                'summary': entry.get('summary', ''),
                'published': entry.get('published', '')
            })
        
        logger.info(f"🔍 Filtradas {len(new_entries)} entradas novas")
        return new_entries
    
    def classify_domain(self, entry: Dict[str, Any]) -> str:
        """Classifica domínio jurídico da legislação
        
        Args:
            entry: Entrada do RSS
            
        Returns:
            Nome do domínio classificado
        """
        title = entry['title'].lower()
        summary = entry['summary'].lower()
        text = f"{title} {summary}"
        
        # Tentar mapeamento direto por palavras-chave
        for keyword, domain in TIPO_TO_DOMAIN.items():
            if keyword in text:
                logger.info(f"   Classificado como '{domain}' (keyword: {keyword})")
                return domain
        
        # Usar router inteligente como fallback
        try:
            domain, confidence, _ = classificar_pergunta(title)
            if confidence > 60:
                logger.info(f"   Classificado como '{domain}' (router: {confidence}%)")
                return domain
        except:
            pass
        
        # Default para público (legislação geral)
        logger.info(f"   Classificado como 'publico' (default)")
        return "publico"
    
    def fetch_legislation_content(self, url: str) -> str:
        """Busca conteúdo completo da legislação
        
        Args:
            url: URL da legislação
            
        Returns:
            Texto completo da legislação
        """
        try:
            logger.info(f"   📄 Baixando conteúdo de: {url}")
            
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Tentar extrair conteúdo principal
            # O Planalto usa diferentes estruturas, tentar várias
            content_selectors = [
                {'class': 'texto'},
                {'class': 'artigo'},
                {'id': 'conteudo'},
                {'class': 'conteudo'},
                {'id': 'texto'}
            ]
            
            text = ""
            for selector in content_selectors:
                elements = soup.find_all('div', selector)
                if elements:
                    text = '\n\n'.join(elem.get_text(strip=True) for elem in elements)
                    if len(text) > 500:  # Conteúdo substancial
                        break
            
            # Fallback: pegar todo o texto
            if len(text) < 500:
                # Remover scripts e styles
                for script in soup(['script', 'style']):
                    script.decompose()
                text = soup.get_text(separator='\n', strip=True)
            
            # Limpar texto
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            text = '\n'.join(lines)
            
            logger.info(f"   ✓ Conteúdo baixado: {len(text)} caracteres")
            return text
            
        except Exception as e:
            logger.error(f"   ✗ Erro ao baixar conteúdo: {str(e)}")
            # Retornar pelo menos o resumo
            return entry.get('summary', '')
    
    async def process_entry(
        self,
        entry: Dict[str, Any]
    ) -> bool:
        """Processa uma entrada do RSS
        
        Args:
            entry: Entrada a processar
            
        Returns:
            True se processado com sucesso
        """
        try:
            logger.info(f"\n📜 Processando: {entry['title']}")
            
            # Classificar domínio
            domain = self.classify_domain(entry)
            
            # Buscar conteúdo completo
            content = self.fetch_legislation_content(entry['link'])
            
            if len(content) < 200:
                logger.warning(f"   ⚠️ Conteúdo muito curto, pulando")
                return False
            
            # Preparar metadata
            metadata = {
                'source_url': entry['link'],
                'title': entry['title'],
                'published': entry['published'],
                'year': datetime.now().year,
                'law_type': 'Legislação Federal',
                'fetched_at': datetime.now().isoformat()
            }
            
            # Processar e vetorizar
            vectors = await self.processor.process_legislation(
                text=content,
                metadata=metadata
            )
            
            logger.info(f"   ✓ Gerados {len(vectors)} vetores")
            
            # Inserir no Pinecone
            self.pinecone.upsert_vectors(
                domain=domain,
                vectors=vectors,
                sub_namespace="legislation"
            )
            
            logger.info(f"   ✓ Armazenado no namespace '{domain}/legislation'")
            
            # Marcar como processado
            self._save_processed_id(entry['id'])
            
            return True
            
        except Exception as e:
            logger.error(f"   ✗ Erro ao processar entrada: {str(e)}")
            return False
    
    async def update_from_rss(
        self,
        days_back: int = 30,
        max_entries: int = 10
    ) -> Dict[str, Any]:
        """Atualiza banco RAG a partir do RSS
        
        Args:
            days_back: Quantos dias atrás buscar
            max_entries: Máximo de entradas a processar
            
        Returns:
            Dict com estatísticas da atualização
        """
        logger.info("="*70)
        logger.info("ATUALIZAÇÃO AUTOMÁTICA VIA RSS - PLANALTO")
        logger.info("="*70)
        print()
        
        start_time = datetime.now()
        
        # Buscar feed
        entries = self.fetch_rss_feed()
        if not entries:
            logger.warning("Nenhuma entrada encontrada no feed")
            return {'success': False, 'message': 'Feed vazio'}
        
        # Filtrar novas
        new_entries = self.filter_new_entries(entries, days_back)
        
        if not new_entries:
            logger.info("✅ Nenhuma legislação nova para processar")
            return {
                'success': True,
                'message': 'Sistema já está atualizado',
                'processed': 0,
                'total': len(entries)
            }
        
        # Limitar quantidade
        entries_to_process = new_entries[:max_entries]
        
        logger.info(f"🚀 Processando {len(entries_to_process)} legislações...")
        print()
        
        # Processar cada entrada
        processed = 0
        failed = 0
        
        for i, entry in enumerate(entries_to_process, 1):
            logger.info(f"[{i}/{len(entries_to_process)}]")
            
            success = await self.process_entry(entry)
            
            if success:
                processed += 1
            else:
                failed += 1
            
            # Pequena pausa entre requests
            await asyncio.sleep(2)
        
        elapsed = (datetime.now() - start_time).total_seconds()
        
        # Estatísticas finais
        print()
        logger.info("="*70)
        logger.info("RESUMO DA ATUALIZAÇÃO")
        logger.info("="*70)
        logger.info(f"✅ Processadas com sucesso: {processed}")
        logger.info(f"❌ Falhas: {failed}")
        logger.info(f"⏱️ Tempo decorrido: {elapsed:.2f}s")
        print()
        
        # Stats do Pinecone
        stats = self.pinecone.get_index_stats()
        logger.info(f"📊 Total de vetores no índice: {stats.get('total_vector_count', 0)}")
        print()
        
        return {
            'success': True,
            'processed': processed,
            'failed': failed,
            'total_entries': len(entries),
            'new_entries': len(new_entries),
            'elapsed_time': elapsed
        }


async def main():
    """Função principal"""
    # Inicializar componentes
    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    pinecone_manager = PineconeManager(api_key=pinecone_api_key)
    embedding_generator = EmbeddingGenerator(openai_api_key=openai_api_key)
    chunker = BrazilianLegalChunker()
    processor = DocumentProcessor(chunker, embedding_generator)
    
    # Criar updater
    updater = RSSLegislationUpdater(pinecone_manager, processor)
    
    # Executar atualização
    result = await updater.update_from_rss(
        days_back=30,  # Últimos 30 dias
        max_entries=5  # Máximo 5 legislações por execução
    )
    
    logger.info("="*70)
    logger.info("✅ ATUALIZAÇÃO CONCLUÍDA")
    logger.info("="*70)
    print()
    
    if result['success']:
        logger.info("💡 Dica: Execute este script periodicamente (ex: diariamente)")
        logger.info("   para manter o banco RAG sempre atualizado!")
    
    print()


if __name__ == "__main__":
    asyncio.run(main())
