"""Script de inicialização dos índices Pinecone
Cria os 13 índices para os núcleos jurídicos
"""

import os
import sys
import asyncio
from dotenv import load_dotenv
from pinecone_manager import PineconeManager, LEGAL_DOMAINS

# Carregar variáveis de ambiente
load_dotenv()

def main():
    """Função principal de inicialização"""
    print("="*60)
    print("INICIALIZAÇÃO DOS ÍNDICES PINECONE - DOUTOR LEGIS 2.0 ULTRA")
    print("="*60)
    print()
    
    # Obter API key
    api_key = os.getenv("PINECONE_API_KEY")
    if not api_key:
        print("❌ ERRO: PINECONE_API_KEY não encontrada no .env")
        sys.exit(1)
    
    print(f"✅ API Key encontrada: {api_key[:10]}...")
    print()
    
    # Criar gerenciador com índice único
    manager = PineconeManager(api_key=api_key, index_name="legal-ultra")
    
    # Listar índices existentes
    print("📋 Verificando índices existentes...")
    existing_indexes = manager.list_indexes()
    print(f"   Encontrados: {len(existing_indexes)} índices")
    for idx in existing_indexes:
        print(f"   - {idx.get('name')}")
    print()
    
    # Criar índice único com namespaces
    print(f"🚀 Criando índice único com {len(LEGAL_DOMAINS)} namespaces...")
    print()
    
    results = manager.initialize()
    
    print()
    print("="*60)
    print("RESUMO DA INICIALIZAÇÃO")
    print("="*60)
    
    if results['success']:
        print(f"✅ Índice criado: {results['index']}")
        print(f"📦 Namespaces disponíveis: {len(results['namespaces'])}")
        print()
        print("Domínios jurídicos (namespaces):")
        for i, domain in enumerate(results['namespaces'], 1):
            print(f"   {i}. {domain}")
    else:
        print(f"❌ Erro: {results.get('error')}")
    
    print()
    print("="*60)
    print("INICIALIZAÇÃO CONCLUÍDA")
    print("="*60)

if __name__ == "__main__":
    main()
