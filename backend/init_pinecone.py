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
    
    # Criar gerenciador
    manager = PineconeManager(api_key=api_key)
    
    # Listar índices existentes
    print("📋 Verificando índices existentes...")
    existing_indexes = manager.list_indexes()
    print(f"   Encontrados: {len(existing_indexes)} índices")
    for idx in existing_indexes:
        print(f"   - {idx.get('name')}")
    print()
    
    # Criar índices para os 13 domínios
    print(f"🚀 Criando {len(LEGAL_DOMAINS)} índices para domínios jurídicos...")
    print()
    
    results = manager.create_all_indexes()
    
    print()
    print("="*60)
    print("RESUMO DA INICIALIZAÇÃO")
    print("="*60)
    print(f"✅ Criados com sucesso: {len(results['created'])}")
    print(f"❌ Falhas: {len(results['failed'])}")
    print()
    
    if results['created']:
        print("Índices criados:")
        for idx in results['created']:
            print(f"   ✓ {idx}")
    
    if results['failed']:
        print()
        print("Falhas:")
        for domain in results['failed']:
            print(f"   ✗ {domain}")
    
    print()
    print("="*60)
    print("INICIALIZAÇÃO CONCLUÍDA")
    print("="*60)

if __name__ == "__main__":
    main()
