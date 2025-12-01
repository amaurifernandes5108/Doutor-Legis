"""Demonstração do Sistema RAG com Pinecone
Popula o banco com dados de exemplo e realiza buscas
"""

import os
import asyncio
from dotenv import load_dotenv
from pinecone_manager import PineconeManager
from document_processor import (
    BrazilianLegalChunker,
    EmbeddingGenerator,
    DocumentProcessor
)
from rag_system import RAGSystem

# Carregar variáveis de ambiente
load_dotenv()

# Dados de exemplo para demonstração
SAMPLE_LEGISLATION = {
    "constitucional": {
        "text": """
Art. 5º Todos são iguais perante a lei, sem distinção de qualquer natureza, garantindo-se aos brasileiros e aos estrangeiros residentes no País a inviolabilidade do direito à vida, à liberdade, à igualdade, à segurança e à propriedade.

I - homens e mulheres são iguais em direitos e obrigações;
II - ninguém será obrigado a fazer ou deixar de fazer alguma coisa senão em virtude de lei;
III - ninguém será submetido a tortura nem a tratamento desumano ou degradante;
IV - é livre a manifestação do pensamento, sendo vedado o anonimato;
V - é assegurado o direito de resposta, proporcional ao agravo;

§ 1º As normas definidoras dos direitos e garantias fundamentais têm aplicação imediata.
§ 2º Os direitos e garantias expressos nesta Constituição não excluem outros decorrentes do regime e dos princípios por ela adotados.
""",
        "metadata": {
            "source_url": "https://www.planalto.gov.br/ccivil_03/constituicao/constituicao.htm",
            "year": 1988,
            "law_type": "Constituição Federal",
            "article": "5"
        }
    },
    "consumidor": {
        "text": """
Art. 6º São direitos básicos do consumidor:

I - a proteção da vida, saúde e segurança contra os riscos provocados por práticas no fornecimento de produtos e serviços considerados perigosos ou nocivos;

II - a educação e divulgação sobre o consumo adequado dos produtos e serviços, asseguradas a liberdade de escolha e a igualdade nas contratações;

III - a informação adequada e clara sobre os diferentes produtos e serviços, com especificação correta de quantidade, características, composição, qualidade, tributos incidentes e preço, bem como sobre os riscos que apresentem;

IV - a proteção contra a publicidade enganosa e abusiva, métodos comerciais coercitivos ou desleais, bem como contra práticas e cláusulas abusivas ou impostas no fornecimento de produtos e serviços;

V - a modificação das cláusulas contratuais que estabeleçam prestações desproporcionais ou sua revisão em razão de fatos supervenientes que as tornem excessivamente onerosas;

VI - a efetiva prevenção e reparação de danos patrimoniais e morais, individuais, coletivos e difusos;

VII - o acesso aos órgãos judiciários e administrativos com vistas à prevenção ou reparação de danos patrimoniais e morais, individuais, coletivos ou difusos, assegurada a proteção Jurídica, administrativa e técnica aos necessitados;

VIII - a facilitação da defesa de seus direitos, inclusive com a inversão do ônus da prova, a seu favor, no processo civil, quando, a critério do juiz, for verossímil a alegação ou quando for ele hipossuficiente, segundo as regras ordinárias de experiências.
""",
        "metadata": {
            "source_url": "http://www.planalto.gov.br/ccivil_03/leis/l8078compilado.htm",
            "year": 1990,
            "law_type": "Lei nº 8.078 - Código de Defesa do Consumidor",
            "article": "6"
        }
    },
    "trabalhista": {
        "text": """
Art. 58. A duração normal do trabalho, para os empregados em qualquer atividade privada, não excederá de 8 (oito) horas diárias, desde que não seja fixado expressamente outro limite.

§ 1º Não serão descontadas nem computadas como jornada extraordinária as variações de horário no registro de ponto não excedentes de cinco minutos, observado o limite máximo de dez minutos diários.

§ 2º O tempo despendido pelo empregado desde a sua residência até a efetiva ocupação do posto de trabalho e para o seu retorno, caminhando ou por qualquer meio de transporte, inclusive o fornecido pelo empregador, não será computado na jornada de trabalho, salvo quando, tratando-se de local de difícil acesso ou não servido por transporte público, o empregador fornecer a condução.

§ 3º Poderão ser fixados, para as microempresas e empresas de pequeno porte, por meio de acordo ou convenção coletiva, em caso de transporte fornecido pelo empregador, em local de difícil acesso ou não servido por transporte público, o tempo médio despendido pelo empregado, bem como a forma e a natureza da remuneração.

Art. 59. A duração diária do trabalho poderá ser acrescida de horas extras, em número não excedente de duas, por acordo individual, convenção coletiva ou acordo coletivo de trabalho.

§ 1º A remuneração da hora extra será, pelo menos, 50% (cinquenta por cento) superior à da hora normal.
""",
        "metadata": {
            "source_url": "http://www.planalto.gov.br/ccivil_03/decreto-lei/del5452.htm",
            "year": 1943,
            "law_type": "Decreto-Lei nº 5.452 - CLT",
            "article": "58-59"
        }
    }
}


async def populate_sample_data():
    """Popula o banco com dados de exemplo"""
    print("="*70)
    print("POPULANDO BANCO DE DADOS COM LEGISLAÇÕES DE EXEMPLO")
    print("="*70)
    print()
    
    # Inicializar componentes
    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    pinecone_manager = PineconeManager(api_key=pinecone_api_key)
    embedding_generator = EmbeddingGenerator(openai_api_key=openai_api_key)
    chunker = BrazilianLegalChunker()
    processor = DocumentProcessor(chunker, embedding_generator)
    
    # Processar e inserir cada legislação
    for domain, data in SAMPLE_LEGISLATION.items():
        print(f"📄 Processando: {domain}")
        print(f"   Lei: {data['metadata']['law_type']}")
        
        # Processar legislação
        vectors = await processor.process_legislation(
            text=data["text"],
            metadata=data["metadata"]
        )
        
        print(f"   ✓ Gerados {len(vectors)} chunks com embeddings")
        
        # Inserir no Pinecone
        pinecone_manager.upsert_vectors(
            domain=domain,
            vectors=vectors,
            sub_namespace="legislation"
        )
        
        print(f"   ✓ Armazenado no namespace '{domain}/legislation'")
        print()
    
    print("✅ Dados de exemplo inseridos com sucesso!")
    print()


async def test_rag_queries():
    """Testa consultas RAG"""
    print("="*70)
    print("TESTANDO SISTEMA RAG - CONSULTAS DE EXEMPLO")
    print("="*70)
    print()
    
    # Inicializar sistema RAG
    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    pinecone_manager = PineconeManager(api_key=pinecone_api_key)
    embedding_generator = EmbeddingGenerator(openai_api_key=openai_api_key)
    rag_system = RAGSystem(pinecone_manager, embedding_generator, openai_api_key)
    
    # Consultas de teste
    test_queries = [
        {
            "domain": "constitucional",
            "question": "Quais são os direitos fundamentais garantidos pela Constituição?"
        },
        {
            "domain": "consumidor",
            "question": "O consumidor pode devolver um produto comprado online?"
        },
        {
            "domain": "trabalhista",
            "question": "Qual é a jornada máxima de trabalho permitida por dia?"
        }
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"🔍 Consulta {i}: {query['domain'].upper()}")
        print(f"   Pergunta: {query['question']}")
        print()
        
        # Realizar consulta RAG
        result = await rag_system.query_with_rag(
            domain=query['domain'],
            question=query['question'],
            top_k=3
        )
        
        print(f"   RAG Ativado: {result.get('rag_enabled')}")
        print(f"   Documentos Usados: {result.get('document_count')}")
        
        if result.get('relevant_documents'):
            print(f"   Documentos Relevantes:")
            for doc in result['relevant_documents'][:2]:
                score = doc.get('score', 0)
                metadata = doc.get('metadata', {})
                law_type = metadata.get('law_type', 'N/A')
                print(f"      - {law_type} (Score: {score:.3f})")
        
        print()
        print(f"   📝 Resumo da Resposta:")
        response = result.get('response', {})
        resumo = response.get('resumo', 'N/A')
        print(f"      {resumo[:150]}...")
        
        print()
        print("-" * 70)
        print()


async def show_stats():
    """Mostra estatísticas do índice"""
    print("="*70)
    print("ESTATÍSTICAS DO PINECONE")
    print("="*70)
    print()
    
    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    manager = PineconeManager(api_key=pinecone_api_key)
    
    # Stats gerais
    stats = manager.get_index_stats()
    
    print(f"📊 Índice: legal-ultra")
    print(f"   Dimensão: {stats.get('dimension')}")
    print(f"   Total de Vetores: {stats.get('total_vector_count', 0)}")
    print()
    
    # Stats por namespace
    namespaces = stats.get('namespaces', {})
    if namespaces:
        print("📦 Namespaces populados:")
        for ns, ns_stats in namespaces.items():
            vector_count = ns_stats.get('vector_count', 0)
            print(f"   - {ns}: {vector_count} vetores")
    else:
        print("   Nenhum namespace populado ainda")
    
    print()


async def main():
    """Função principal"""
    print()
    print("🚀 DEMONSTRAÇÃO DO SISTEMA RAG - DOUTOR LEGIS 2.0 ULTRA")
    print()
    
    # 1. Popular dados
    await populate_sample_data()
    
    # 2. Mostrar estatísticas
    await show_stats()
    
    # 3. Testar consultas
    await test_rag_queries()
    
    print("="*70)
    print("✅ DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
    print("="*70)
    print()
    print("💡 Próximos passos:")
    print("   1. Adicionar mais legislações e jurisprudências")
    print("   2. Integrar RAG com endpoint /api/consultation")
    print("   3. Implementar feedback loop para aprendizado")
    print()


if __name__ == "__main__":
    asyncio.run(main())
