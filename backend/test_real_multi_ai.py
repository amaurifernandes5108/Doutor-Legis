"""Teste do Sistema Multi-AI REAL - 5 IAs em Paralelo
Valida execução paralela de Claude, GPT-4, Gemini, Perplexity
"""

import asyncio
import os
from dotenv import load_dotenv
from pinecone_manager import PineconeManager
from document_processor import EmbeddingGenerator
from rag_system import RAGSystem

load_dotenv()

async def test_real_multi_ai():
    """Testa sistema Multi-AI REAL com 5 IAs em paralelo"""
    
    print("="*70)
    print("TESTE DO SISTEMA MULTI-AI REAL - 5 IAs EM PARALELO")
    print("="*70)
    print()
    
    # Verificar keys
    keys_available = {
        "Pinecone": bool(os.getenv("PINECONE_API_KEY")),
        "OpenAI": bool(os.getenv("OPENAI_API_KEY")),
        "Claude": bool(os.getenv("CLAUDE_API_KEY")),
        "Google AI": bool(os.getenv("GOOGLE_AI_STUDIO_KEY")),
        "Perplexity": bool(os.getenv("PERPLEXITY_API_KEY"))
    }
    
    print("🔑 API Keys Disponíveis:")
    for provider, available in keys_available.items():
        status = "✅" if available else "❌"
        print(f"   {status} {provider}")
    print()
    
    multi_ai_possible = all(keys_available.values())
    if not multi_ai_possible:
        print("⚠️ Multi-AI Real não disponível (faltam keys)")
        print("   Sistema usará fallback Single-LLM")
    else:
        print("✅ Multi-AI Real ATIVADO - 5 IAs em paralelo")
    print()
    print("-" * 70)
    print()
    
    # Inicializar sistema RAG com Multi-AI
    pinecone_manager = PineconeManager(api_key=os.getenv("PINECONE_API_KEY"))
    embedding_generator = EmbeddingGenerator(openai_api_key=os.getenv("OPENAI_API_KEY"))
    
    rag_system = RAGSystem(
        pinecone_manager=pinecone_manager,
        embedding_generator=embedding_generator,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        claude_api_key=os.getenv("CLAUDE_API_KEY"),
        google_api_key=os.getenv("GOOGLE_AI_STUDIO_KEY"),
        perplexity_api_key=os.getenv("PERPLEXITY_API_KEY")
    )
    
    # Teste: Consulta trabalhista (tem dados RAG)
    print("📊 TESTE: Análise Multi-AI Real + RAG")
    print("-" * 70)
    
    question = "Um trabalhador trabalha 10 horas por dia sem receber hora extra há 3 meses. Isso é legal? Quais são seus direitos?"
    
    print(f"Pergunta: {question}")
    print()
    print("⏳ Executando 5 IAs em paralelo...")
    print("   IA-1: Claude Sonnet (Constitucional)")
    print("   IA-2: GPT-4 (Infraconstitucional)")
    print("   IA-3: Gemini Pro (Jurisprudencial)")
    print("   IA-4: Perplexity (Doutrinária)")
    print("   IA-5: Claude Opus (Metodológica)")
    print("   IA-6: Claude Sonnet (Validadora)")
    print()
    
    import time
    start = time.time()
    
    result = await rag_system.query_with_rag(
        domain="trabalhista",
        question=question,
        top_k=3
    )
    
    elapsed = time.time() - start
    
    response = result.get("response", {})
    analise = response.get("analise_completa", "")
    
    print(f"⏱️ Tempo de execução: {elapsed:.2f}s")
    print()
    print("=" * 70)
    print("RESPOSTA CONSOLIDADA")
    print("=" * 70)
    print()
    print(analise[:2000])  # Primeiros 2000 caracteres
    print()
    if len(analise) > 2000:
        print(f"... [resposta completa tem {len(analise)} caracteres]")
    print()
    print("=" * 70)
    print()
    
    # Métricas
    print("📊 MÉTRICAS DO SISTEMA")
    print("-" * 70)
    print(f"✅ RAG Ativado: {result.get('rag_enabled', False)}")
    print(f"✅ Multi-AI Real: {response.get('multi_ai', False)}")
    print(f"✅ IAs Responderam: {response.get('ias_responded', 0)}/5")
    print(f"✅ Documentos RAG Usados: {result.get('document_count', 0)}")
    print(f"✅ Consenso entre IAs: {response.get('consenso', 'N/A')}%")
    print(f"✅ Confiança Final: {response.get('confianca', 'N/A')}%")
    print(f"✅ Formato: {response.get('formato', 'N/A')}")
    print()
    
    # Verificações
    print("🔍 VERIFICAÇÕES DE QUALIDADE")
    print("-" * 70)
    
    checks = []
    
    # Check 1: Multi-AI foi usado
    multi_ai_used = response.get('multi_ai', False)
    checks.append(("Multi-AI Real Ativado", multi_ai_used))
    
    # Check 2: Todas ou maioria das IAs responderam
    ias_ok = response.get('ias_responded', 0) >= 3
    checks.append(("Mínimo 3 IAs Responderam", ias_ok))
    
    # Check 3: RAG funcionou
    rag_ok = result.get('document_count', 0) > 0
    checks.append(("RAG com Documentos", rag_ok))
    
    # Check 4: Resposta tem estrutura esperada
    has_structure = all([
        "PERSPECTIVA" in analise or "ANÁLISE" in analise,
        "CONCLUSÃO" in analise or "TESE" in analise,
        len(analise) > 1000
    ])
    checks.append(("Estrutura Multi-Dimensional", has_structure))
    
    # Check 5: Consenso alto
    consenso_ok = response.get('consenso', 0) >= 70
    checks.append(("Consenso ≥ 70%", consenso_ok))
    
    for check_name, passed in checks:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {check_name}")
    
    print()
    print("=" * 70)
    
    total_passed = sum(1 for _, p in checks if p)
    total_checks = len(checks)
    
    if total_passed == total_checks:
        print(f"✅ TESTE COMPLETO: {total_passed}/{total_checks} PASSED")
        print("🎉 Sistema Multi-AI Real funcionando perfeitamente!")
    else:
        print(f"⚠️ TESTE PARCIAL: {total_passed}/{total_checks} PASSED")
        if not multi_ai_used:
            print("   Multi-AI não foi ativado (verifique keys)")
    
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_real_multi_ai())
