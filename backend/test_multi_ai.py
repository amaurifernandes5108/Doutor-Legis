"""Teste do Sistema Multi-AI Doutor Legis 2.0 v3.0
Valida análise multi-dimensional com precisão aprimorada
"""

import asyncio
import os
from dotenv import load_dotenv
from pinecone_manager import PineconeManager
from document_processor import EmbeddingGenerator
from rag_system import RAGSystem

load_dotenv()

async def test_multi_ai_system():
    """Testa sistema Multi-AI com consulta real"""
    
    print("="*70)
    print("TESTE DO SISTEMA MULTI-AI - DOUTOR LEGIS 2.0 v3.0")
    print("="*70)
    print()
    
    # Inicializar sistema RAG
    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    pinecone_manager = PineconeManager(api_key=pinecone_api_key)
    embedding_generator = EmbeddingGenerator(openai_api_key=openai_api_key)
    rag_system = RAGSystem(pinecone_manager, embedding_generator, openai_api_key)
    
    # Teste 1: Consulta com RAG (domínio com dados)
    print("📊 TESTE 1: Análise Multi-AI COM RAG (Trabalhista)")
    print("-" * 70)
    
    question_1 = "Meu empregador me obriga a trabalhar 10 horas por dia sem hora extra. Isso é legal? O que posso fazer?"
    
    print(f"Pergunta: {question_1}")
    print()
    print("Processando análise multi-dimensional...")
    print()
    
    result_1 = await rag_system.query_with_rag(
        domain="trabalhista",
        question=question_1,
        top_k=3
    )
    
    response_1 = result_1.get("response", {})
    analise = response_1.get("analise_completa", "")
    
    print(analise[:1500])  # Mostrar primeiros 1500 caracteres
    print()
    print(f"... [resposta completa tem {len(analise)} caracteres]")
    print()
    print(f"✅ RAG Ativado: {result_1.get('rag_enabled')}")
    print(f"✅ Documentos Usados: {result_1.get('document_count')}")
    print(f"✅ Confiança: {response_1.get('confianca', 'N/A')}%")
    print()
    print("=" * 70)
    print()
    
    # Teste 2: Consulta sem RAG (domínio sem dados)
    print("📊 TESTE 2: Análise Multi-AI SEM RAG (Penal)")
    print("-" * 70)
    
    question_2 = "Quais são as penas previstas para furto simples? Há diferença se for furto qualificado?"
    
    print(f"Pergunta: {question_2}")
    print()
    print("Processando análise multi-dimensional...")
    print()
    
    result_2 = await rag_system.query_with_rag(
        domain="penal",
        question=question_2,
        top_k=3
    )
    
    response_2 = result_2.get("response", {})
    analise_2 = response_2.get("analise_completa", "")
    
    print(analise_2[:1500])  # Mostrar primeiros 1500 caracteres
    print()
    print(f"... [resposta completa tem {len(analise_2)} caracteres]")
    print()
    print(f"✅ RAG Ativado: {result_2.get('rag_enabled')}")
    print(f"✅ Documentos Usados: {result_2.get('document_count')}")
    print(f"✅ Confiança: {response_2.get('confianca', 'N/A')}%")
    if response_2.get('warning'):
        print(f"⚠️  Warning: {response_2.get('warning')}")
    print()
    print("=" * 70)
    print()
    
    # Verificações
    print("🔍 VERIFICAÇÕES DE QUALIDADE")
    print("-" * 70)
    
    checks = []
    
    # Check 1: Resposta tem estrutura Multi-AI
    has_perspectives = all([
        "PERSPECTIVA CONSTITUCIONAL" in analise or "CONSTITUCIONAL" in analise,
        "PERSPECTIVA" in analise or "ANÁLISE" in analise
    ])
    checks.append(("Estrutura Multi-Dimensional", has_perspectives))
    
    # Check 2: Tem conclusão unificada
    has_conclusion = "CONCLUSÃO" in analise or "TESE JURÍDICA" in analise
    checks.append(("Conclusão Unificada", has_conclusion))
    
    # Check 3: RAG funcionou corretamente
    rag_ok = result_1.get('document_count', 0) > 0
    checks.append(("RAG com documentos", rag_ok))
    
    # Check 4: Fallback sem RAG funcionou
    no_rag_ok = result_2.get('document_count', 0) == 0 and not result_2.get('rag_enabled')
    checks.append(("Fallback sem RAG", no_rag_ok))
    
    for check_name, passed in checks:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {check_name}")
    
    print()
    print("=" * 70)
    print("✅ TESTE DO SISTEMA MULTI-AI CONCLUÍDO")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_multi_ai_system())
