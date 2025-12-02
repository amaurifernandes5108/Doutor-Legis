"""População Massiva do Banco RAG - Doutor Legis 2.0 ULTRA
Adiciona legislações, jurisprudências e documentos brasileiros
"""

import asyncio
import os
from dotenv import load_dotenv
from pinecone_manager import PineconeManager
from document_processor import (
    BrazilianLegalChunker,
    EmbeddingGenerator,
    DocumentProcessor
)
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Base de conhecimento jurídico brasileiro
LEGAL_KNOWLEDGE_BASE = {
    "constitucional": {
        "legislacao": [
            {
                "titulo": "Constituição Federal de 1988 - Direitos Fundamentais",
                "texto": """
Art. 5º Todos são iguais perante a lei, sem distinção de qualquer natureza, garantindo-se aos brasileiros e aos estrangeiros residentes no País a inviolabilidade do direito à vida, à liberdade, à igualdade, à segurança e à propriedade, nos termos seguintes:

I - homens e mulheres são iguais em direitos e obrigações, nos termos desta Constituição;
II - ninguém será obrigado a fazer ou deixar de fazer alguma coisa senão em virtude de lei;
III - ninguém será submetido a tortura nem a tratamento desumano ou degradante;
IV - é livre a manifestação do pensamento, sendo vedado o anonimato;
V - é assegurado o direito de resposta, proporcional ao agravo, além da indenização por dano material, moral ou à imagem;
VI - é inviolável a liberdade de consciência e de crença, sendo assegurado o livre exercício dos cultos religiosos e garantida, na forma da lei, a proteção aos locais de culto e a suas liturgias;
VII - é assegurada, nos termos da lei, a prestação de assistência religiosa nas entidades civis e militares de internação coletiva;
VIII - ninguém será privado de direitos por motivo de crença religiosa ou de convicção filosófica ou política, salvo se as invocar para eximir-se de obrigação legal a todos imposta e recusar-se a cumprir prestação alternativa, fixada em lei;
IX - é livre a expressão da atividade intelectual, artística, científica e de comunicação, independentemente de censura ou licença;
X - são invioláveis a intimidade, a vida privada, a honra e a imagem das pessoas, assegurado o direito a indenização pelo dano material ou moral decorrente de sua violação;
XI - a casa é asilo inviolável do indivíduo, ninguém nela podendo penetrar sem consentimento do morador, salvo em caso de flagrante delito ou desastre, ou para prestar socorro, ou, durante o dia, por determinação judicial;
XII - é inviolável o sigilo da correspondência e das comunicações telegráficas, de dados e das comunicações telefônicas, salvo, no último caso, por ordem judicial, nas hipóteses e na forma que a lei estabelecer para fins de investigação criminal ou instrução processual penal;
XIII - é livre o exercício de qualquer trabalho, ofício ou profissão, atendidas as qualificações profissionais que a lei estabelecer;
XIV - é assegurado a todos o acesso à informação e resguardado o sigilo da fonte, quando necessário ao exercício profissional;
XV - é livre a locomoção no território nacional em tempo de paz, podendo qualquer pessoa, nos termos da lei, nele entrar, permanecer ou dele sair com seus bens;

§ 1º As normas definidoras dos direitos e garantias fundamentais têm aplicação imediata.
§ 2º Os direitos e garantias expressos nesta Constituição não excluem outros decorrentes do regime e dos princípios por ela adotados, ou dos tratados internacionais em que a República Federativa do Brasil seja parte.
§ 3º Os tratados e convenções internacionais sobre direitos humanos que forem aprovados, em cada Casa do Congresso Nacional, em dois turnos, por três quintos dos votos dos respectivos membros, serão equivalentes às emendas constitucionais.
§ 4º O Brasil se submete à jurisdição de Tribunal Penal Internacional a cuja criação tenha manifestado adesão.
""",
                "metadata": {
                    "source_url": "http://www.planalto.gov.br/ccivil_03/constituicao/constituicao.htm",
                    "year": 1988,
                    "law_type": "Constituição Federal",
                    "article": "5"
                }
            },
            {
                "titulo": "CF/88 - Organização do Estado",
                "texto": """
Art. 18. A organização político-administrativa da República Federativa do Brasil compreende a União, os Estados, o Distrito Federal e os Municípios, todos autônomos, nos termos desta Constituição.

§ 1º Brasília é a Capital Federal.
§ 2º Os Territórios Federais integram a União, e sua criação, transformação em Estado ou reintegração ao Estado de origem serão reguladas em lei complementar.
§ 3º Os Estados podem incorporar-se entre si, subdividir-se ou desmembrar-se para se anexarem a outros, ou formarem novos Estados ou Territórios Federais, mediante aprovação da população diretamente interessada, através de plebiscito, e do Congresso Nacional, por lei complementar.
§ 4º A criação, a incorporação, a fusão e o desmembramento de Municípios, far-se-ão por lei estadual, dentro do período determinado por Lei Complementar Federal, e dependerão de consulta prévia, mediante plebiscito, às populações dos Municípios envolvidos, após divulgação dos Estudos de Viabilidade Municipal, apresentados e publicados na forma da lei.

Art. 19. É vedado à União, aos Estados, ao Distrito Federal e aos Municípios:
I - estabelecer cultos religiosos ou igrejas, subvencioná-los, embaraçar-lhes o funcionamento ou manter com eles ou seus representantes relações de dependência ou aliança, ressalvada, na forma da lei, a colaboração de interesse público;
II - recusar fé aos documentos públicos;
III - criar distinções entre brasileiros ou preferências entre si.
""",
                "metadata": {
                    "source_url": "http://www.planalto.gov.br/ccivil_03/constituicao/constituicao.htm",
                    "year": 1988,
                    "law_type": "Constituição Federal",
                    "article": "18-19"
                }
            }
        ]
    },
    
    "civil": {
        "legislacao": [
            {
                "titulo": "Código Civil - Capacidade Civil",
                "texto": """
Art. 1º Toda pessoa é capaz de direitos e deveres na ordem civil.

Art. 2º A personalidade civil da pessoa começa do nascimento com vida; mas a lei põe a salvo, desde a concepção, os direitos do nascituro.

Art. 3º São absolutamente incapazes de exercer pessoalmente os atos da vida civil os menores de 16 (dezesseis) anos.

Art. 4º São incapazes, relativamente a certos atos ou à maneira de os exercer:
I - os maiores de dezesseis e menores de dezoito anos;
II - os ébrios habituais e os viciados em tóxico;
III - aqueles que, por causa transitória ou permanente, não puderem exprimir sua vontade;
IV - os pródigos.

Parágrafo único. A capacidade dos indígenas será regulada por legislação especial.

Art. 5º A menoridade cessa aos dezoito anos completos, quando a pessoa fica habilitada à prática de todos os atos da vida civil.

Parágrafo único. Cessará, para os menores, a incapacidade:
I - pela concessão dos pais, ou de um deles na falta do outro, mediante instrumento público, independentemente de homologação judicial, ou por sentença do juiz, ouvido o tutor, se o menor tiver dezesseis anos completos;
II - pelo casamento;
III - pelo exercício de emprego público efetivo;
IV - pela colação de grau em curso de ensino superior;
V - pelo estabelecimento civil ou comercial, ou pela existência de relação de emprego, desde que, em função deles, o menor com dezesseis anos completos tenha economia própria.

Art. 6º A existência da pessoa natural termina com a morte; presume-se esta, quanto aos ausentes, nos casos em que a lei autoriza a abertura de sucessão definitiva.
""",
                "metadata": {
                    "source_url": "http://www.planalto.gov.br/ccivil_03/leis/2002/l10406compilada.htm",
                    "year": 2002,
                    "law_type": "Lei nº 10.406 - Código Civil",
                    "article": "1-6"
                }
            }
        ]
    },
    
    "consumidor": {
        "legislacao": [
            {
                "titulo": "CDC - Direito de Arrependimento",
                "texto": """
Art. 49. O consumidor pode desistir do contrato, no prazo de 7 dias a contar de sua assinatura ou do ato de recebimento do produto ou serviço, sempre que a contratação de fornecimento de produtos e serviços ocorrer fora do estabelecimento comercial, especialmente por telefone ou a domicílio.

Parágrafo único. Se o consumidor exercitar o direito de arrependimento previsto neste artigo, os valores eventualmente pagos, a qualquer título, durante o prazo de reflexão, serão devolvidos, de imediato, monetariamente atualizados.

Art. 50. A garantia contratual é complementar à legal e será conferida mediante termo escrito.

Parágrafo único. O termo de garantia ou equivalente deve ser padronizado e esclarecer, de maneira adequada em que consiste a mesma garantia, bem como a forma, o prazo e o lugar em que pode ser exercitada e os ônus a cargo do consumidor, devendo ser-lhe entregue, devidamente preenchido pelo fornecedor, no ato do fornecimento, acompanhado de manual de instrução, de instalação e uso do produto em linguagem didática, com ilustrações.
""",
                "metadata": {
                    "source_url": "http://www.planalto.gov.br/ccivil_03/leis/l8078compilado.htm",
                    "year": 1990,
                    "law_type": "Lei nº 8.078 - CDC",
                    "article": "49-50"
                }
            },
            {
                "titulo": "CDC - Práticas Abusivas",
                "texto": """
Art. 39. É vedado ao fornecedor de produtos ou serviços, dentre outras práticas abusivas:
I - condicionar o fornecimento de produto ou de serviço ao fornecimento de outro produto ou serviço, bem como, sem justa causa, a limites quantitativos;
II - recusar atendimento às demandas dos consumidores, na exata medida de suas disponibilidades de estoque, e, ainda, de conformidade com os usos e costumes;
III - enviar ou entregar ao consumidor, sem solicitação prévia, qualquer produto, ou fornecer qualquer serviço;
IV - prevalecer-se da fraqueza ou ignorância do consumidor, tendo em vista sua idade, saúde, conhecimento ou condição social, para impingir-lhe seus produtos ou serviços;
V - exigir do consumidor vantagem manifestamente excessiva;
VI - executar serviços sem a prévia elaboração de orçamento e autorização expressa do consumidor, ressalvadas as decorrentes de práticas anteriores entre as partes;
VII - repassar informação depreciativa, referente a ato praticado pelo consumidor no exercício de seus direitos;
VIII - colocar, no mercado de consumo, qualquer produto ou serviço em desacordo com as normas expedidas pelos órgãos oficiais competentes ou, se normas específicas não existirem, pela Associação Brasileira de Normas Técnicas ou outra entidade credenciada pelo Conselho Nacional de Metrologia, Normalização e Qualidade Industrial (Conmetro);
IX - recusar a venda de bens ou a prestação de serviços, diretamente a quem se disponha a adquiri-los mediante pronto pagamento, ressalvados os casos de intermediação regulados em leis especiais;
X - elevar sem justa causa o preço de produtos ou serviços;
XI - Dispositivo incluído pela MPV nº 1.890-67, de 22.10.1999, transformado em inciso XIII, quando da conversão na Lei nº 9.870, de 23.11.1999
XII - deixar de estipular prazo para o cumprimento de sua obrigação ou deixar a fixação de seu termo inicial a seu exclusivo critério;
XIII - aplicar fórmula ou índice de reajuste diverso do legal ou contratualmente estabelecido.
XIV - permitir o ingresso em estabelecimentos comerciais ou de serviços de um número maior de consumidores que o fixado pela autoridade administrativa como máximo.

Parágrafo único. Os serviços prestados e os produtos remetidos ou entregues ao consumidor, na hipótese prevista no inciso III, equiparam-se às amostras grátis, inexistindo obrigação de pagamento.
""",
                "metadata": {
                    "source_url": "http://www.planalto.gov.br/ccivil_03/leis/l8078compilado.htm",
                    "year": 1990,
                    "law_type": "Lei nº 8.078 - CDC",
                    "article": "39"
                }
            }
        ]
    },
    
    "trabalhista": {
        "legislacao": [
            {
                "titulo": "CLT - Férias",
                "texto": """
Art. 129. Todo empregado terá direito anualmente ao gozo de um período de férias, sem prejuízo da remuneração.

Art. 130. Após cada período de 12 (doze) meses de vigência do contrato de trabalho, o empregado terá direito a férias, na seguinte proporção:
I - 30 (trinta) dias corridos, quando não houver faltado ao serviço mais de 5 (cinco) vezes;
II - 24 (vinte e quatro) dias corridos, quando houver tido de 6 (seis) a 14 (quatorze) faltas;
III - 18 (dezoito) dias corridos, quando houver tido de 15 (quinze) a 23 (vinte e três) faltas;
IV - 12 (doze) dias corridos, quando houver tido de 24 (vinte e quatro) a 32 (trinta e duas) faltas.

§ 1º É vedado descontar, do período de férias, as faltas do empregado ao serviço.
§ 2º O período das férias será computado, para todos os efeitos, como tempo de serviço.

Art. 130-A. Na modalidade do regime de tempo parcial, após cada período de doze meses de vigência do contrato de trabalho, o empregado terá direito a férias, na seguinte proporção:
I - 18 (dezoito) dias, para a duração do trabalho semanal superior a 22 (vinte e duas) horas, até 25 (vinte e cinco) horas;
II - 16 (dezesseis) dias, para a duração do trabalho semanal superior a 20 (vinte) horas, até 22 (vinte e duas) horas;
III - 14 (quatorze) dias, para a duração do trabalho semanal superior a 15 (quinze) horas, até 20 (vinte) horas;
IV - 12 (doze) dias, para a duração do trabalho semanal superior a 10 (dez) horas, até 15 (quinze) horas;
V - 10 (dez) dias, para a duração do trabalho semanal superior a 5 (cinco) horas, até 10 (dez) horas;
VI - 8 (oito) dias, para a duração do trabalho semanal igual ou inferior a 5 (cinco) horas.

Parágrafo único. O empregado contratado sob o regime de tempo parcial que tiver mais de sete faltas injustificadas ao longo do período aquisitivo terá o seu período de férias reduzido à metade.
""",
                "metadata": {
                    "source_url": "http://www.planalto.gov.br/ccivil_03/decreto-lei/del5452.htm",
                    "year": 1943,
                    "law_type": "Decreto-Lei nº 5.452 - CLT",
                    "article": "129-130-A"
                }
            },
            {
                "titulo": "CLT - 13º Salário",
                "texto": """
Art. 1º (Lei 4.090/62) No mês de dezembro de cada ano, a todo empregado será paga, pelo empregador, uma gratificação salarial, independentemente da remuneração a que fizer jus.

§ 1º A gratificação corresponderá a 1/12 avos da remuneração devida em dezembro, por mês de serviço, do ano correspondente.
§ 2º A fração igual ou superior a 15 (quinze) dias de trabalho será havida como mês integral para os efeitos do parágrafo anterior.
§ 3º A gratificação será proporcional:
I - na extinção dos contratos a prazo, entre estes incluídos os de safra, ainda que a relação de emprego haja findado antes de dezembro;
II - na cessação da relação de emprego resultante da aposentadoria do trabalhador, ainda que verificada antes de dezembro.

Art. 2º (Lei 4.749/65) Entre os meses de fevereiro e novembro de cada ano, o empregador pagará, como adiantamento da gratificação referida no artigo precedente, de uma só vez, metade do salário recebido pelo respectivo empregado no mês anterior.

§ 1º O empregador não estará obrigado a pagar o adiantamento, no mesmo mês, a todos os seus empregados.
§ 2º O adiantamento será pago ao ensejo das férias do empregado, sempre que este o requerer no mês de janeiro do correspondente ano.
""",
                "metadata": {
                    "source_url": "http://www.planalto.gov.br/ccivil_03/leis/l4090.htm",
                    "year": 1962,
                    "law_type": "Lei nº 4.090/62 e Lei nº 4.749/65",
                    "article": "1-2"
                }
            }
        ]
    },
    
    "penal": {
        "legislacao": [
            {
                "titulo": "Código Penal - Furto",
                "texto": """
Art. 155 - Subtrair, para si ou para outrem, coisa alheia móvel:
Pena - reclusão, de um a quatro anos, e multa.

§ 1º - A pena aumenta-se de um terço, se o crime é praticado durante o repouso noturno.
§ 2º - Se o criminoso é primário, e é de pequeno valor a coisa furtada, o juiz pode substituir a pena de reclusão pela de detenção, diminuí-la de um a dois terços, ou aplicar somente a pena de multa.
§ 3º - Equipara-se à coisa móvel a energia elétrica ou qualquer outra que tenha valor econômico.

Furto qualificado

§ 4º - A pena é de reclusão de dois a oito anos, e multa, se o crime é cometido:
I - com destruição ou rompimento de obstáculo à subtração da coisa;
II - com abuso de confiança, ou mediante fraude, escalada ou destreza;
III - com emprego de chave falsa;
IV - mediante concurso de duas ou mais pessoas.

§ 5º - A pena é de reclusão de três a oito anos, se a subtração for de veículo automotor que venha a ser transportado para outro Estado ou para o exterior.

§ 6º A pena é de reclusão de 2 (dois) a 5 (cinco) anos se a subtração for de semovente domesticável de produção, ainda que abatido ou dividido em partes no local da subtração.

§ 7º A pena é de reclusão de 4 (quatro) a 10 (dez) anos e multa, se a subtração for de substâncias explosivas ou de acessórios que, conjunta ou isoladamente, possibilitem sua fabricação, montagem ou emprego.
""",
                "metadata": {
                    "source_url": "http://www.planalto.gov.br/ccivil_03/decreto-lei/del2848compilado.htm",
                    "year": 1940,
                    "law_type": "Decreto-Lei nº 2.848 - Código Penal",
                    "article": "155"
                }
            },
            {
                "titulo": "Código Penal - Roubo",
                "texto": """
Art. 157 - Subtrair coisa móvel alheia, para si ou para outrem, mediante grave ameaça ou violência a pessoa, ou depois de havê-la, por qualquer meio, reduzido à impossibilidade de resistência:
Pena - reclusão, de quatro a dez anos, e multa.

§ 1º - Na mesma pena incorre quem, logo depois de subtraída a coisa, emprega violência contra pessoa ou grave ameaça, a fim de assegurar a impunidade do crime ou a detenção da coisa para si ou para terceiro.

§ 2º - A pena aumenta-se de 1/3 (um terço) até metade:
I - se a violência ou ameaça é exercida com emprego de arma;
II - se há o concurso de duas ou mais pessoas;
III - se a vítima está em serviço de transporte de valores e o agente conhece tal circunstância;
IV - se a subtração for de veículo automotor que venha a ser transportado para outro Estado ou para o exterior;
V - se o agente mantém a vítima em seu poder, restringindo sua liberdade.

§ 2º-A A pena aumenta-se de 2/3 (dois terços):
I - se a violência ou ameaça é exercida com emprego de arma de fogo;
II - se há destruição ou rompimento de obstáculo mediante o emprego de explosivo ou de artefato análogo que cause perigo comum.

§ 3º Se da violência resulta:
I - lesão corporal grave, a pena é de reclusão de 7 (sete) a 18 (dezoito) anos, e multa;
II - morte, a pena é de reclusão de 20 (vinte) a 30 (trinta) anos, e multa.
""",
                "metadata": {
                    "source_url": "http://www.planalto.gov.br/ccivil_03/decreto-lei/del2848compilado.htm",
                    "year": 1940,
                    "law_type": "Decreto-Lei nº 2.848 - Código Penal",
                    "article": "157"
                }
            }
        ]
    },
    
    "tributario": {
        "legislacao": [
            {
                "titulo": "CTN - Fato Gerador do Tributo",
                "texto": """
Art. 114. Fato gerador da obrigação principal é a situação definida em lei como necessária e suficiente à sua ocorrência.

Art. 115. Fato gerador da obrigação acessória é qualquer situação que, na forma da legislação aplicável, impõe a prática ou a abstenção de ato que não configure obrigação principal.

Art. 116. Salvo disposição de lei em contrário, considera-se ocorrido o fato gerador e existentes os seus efeitos:
I - tratando-se de situação de fato, desde o momento em que o se verifiquem as circunstâncias materiais necessárias a que produza os efeitos que normalmente lhe são próprios;
II - tratando-se de situação jurídica, desde o momento em que esteja definitivamente constituída, nos termos de direito aplicável.

Parágrafo único. A autoridade administrativa poderá desconsiderar atos ou negócios jurídicos praticados com a finalidade de dissimular a ocorrência do fato gerador do tributo ou a natureza dos elementos constitutivos da obrigação tributária, observados os procedimentos a serem estabelecidos em lei ordinária.

Art. 117. Para os efeitos do inciso II do artigo anterior e salvo disposição de lei em contrário, os atos ou negócios jurídicos condicionais reputam-se perfeitos e acabados:
I - sendo suspensiva a condição, desde o momento de seu implemento;
II - sendo resolutória a condição, desde o momento da prática do ato ou da celebração do negócio.

Art. 118. A definição legal do fato gerador é interpretada abstraindo-se:
I - da validade jurídica dos atos efetivamente praticados pelos contribuintes, responsáveis, ou terceiros, bem como da natureza do seu objeto ou dos seus efeitos;
II - dos efeitos dos fatos efetivamente ocorridos.
""",
                "metadata": {
                    "source_url": "http://www.planalto.gov.br/ccivil_03/leis/l5172compilado.htm",
                    "year": 1966,
                    "law_type": "Lei nº 5.172 - Código Tributário Nacional",
                    "article": "114-118"
                }
            }
        ]
    },
    
    "previdenciario": {
        "legislacao": [
            {
                "titulo": "Lei de Benefícios - Aposentadoria por Idade",
                "texto": """
Art. 48. A aposentadoria por idade será devida ao segurado que, cumprida a carência exigida, completar 65 (sessenta e cinco) anos de idade, se homem, e 62 (sessenta e dois), se mulher.

§ 1º Os limites fixados no caput são reduzidos para sessenta e cinquenta e cinco anos no caso de trabalhadores rurais, respectivamente homens e mulheres, referidos na alínea a do inciso I, na alínea g do inciso V e nos incisos VI e VII do art. 11.

§ 2º Para os efeitos do disposto no § 1º deste artigo, o trabalhador rural deve comprovar o efetivo exercício de atividade rural, ainda que de forma descontínua, no período imediatamente anterior ao requerimento do benefício, por tempo igual ao número de meses de contribuição correspondente à carência do referido benefício.

§ 3º Os trabalhadores rurais de que trata o § 1º deste artigo que não atendam ao disposto no § 2º deste artigo, mas que satisfaçam essa condição, se forem considerados períodos de contribuição sob outras categorias do segurado, farão jus ao benefício ao completarem 65 (sessenta e cinco) anos de idade, se homem, e 60 (sessenta) anos, se mulher.

§ 4º Para efeito do § 3º deste artigo, o cálculo da renda mensal do benefício será apurado de acordo com o disposto no inciso II do caput do art. 29 desta Lei, considerando-se como salário-de-contribuição mensal do período como segurado especial o limite mínimo de salário-de-contribuição da Previdência Social.

Art. 49. A aposentadoria por idade será devida:
I - ao segurado empregado, inclusive o doméstico, a partir:
a) da data do desligamento do emprego, quando requerida até essa data ou até 90 (noventa) dias depois dela; ou
b) da data do requerimento, quando não houver desligamento do emprego ou quando for requerida após o prazo previsto na alínea "a";
II - para os demais segurados, da data da entrada do requerimento.
""",
                "metadata": {
                    "source_url": "http://www.planalto.gov.br/ccivil_03/leis/l8213cons.htm",
                    "year": 1991,
                    "law_type": "Lei nº 8.213/91 - Lei de Benefícios",
                    "article": "48-49"
                }
            }
        ]
    }
}


async def populate_domain(
    domain: str,
    documents: dict,
    processor: DocumentProcessor,
    pinecone_manager: PineconeManager
):
    """Popula um domínio específico com documentos"""
    logger.info(f"\n{'='*70}")
    logger.info(f"POPULANDO DOMÍNIO: {domain.upper()}")
    logger.info(f"{'='*70}")
    
    total_vectors = 0
    
    # Processar legislações
    if "legislacao" in documents:
        logger.info(f"\n📜 Processando {len(documents['legislacao'])} legislações...")
        
        for i, doc in enumerate(documents['legislacao'], 1):
            logger.info(f"\n  [{i}/{len(documents['legislacao'])}] {doc['titulo']}")
            
            try:
                # Processar legislação
                vectors = await processor.process_legislation(
                    text=doc["texto"],
                    metadata=doc["metadata"]
                )
                
                logger.info(f"     ✓ Gerados {len(vectors)} chunks com embeddings")
                
                # Inserir no Pinecone
                pinecone_manager.upsert_vectors(
                    domain=domain,
                    vectors=vectors,
                    sub_namespace="legislation"
                )
                
                total_vectors += len(vectors)
                logger.info(f"     ✓ Armazenado no namespace '{domain}/legislation'")
                
            except Exception as e:
                logger.error(f"     ✗ Erro: {str(e)}")
                continue
    
    logger.info(f"\n✅ Domínio '{domain}' populado com {total_vectors} vetores\n")
    return total_vectors


async def main():
    """Função principal de população"""
    logger.info("="*70)
    logger.info("POPULAÇÃO MASSIVA DO BANCO RAG - DOUTOR LEGIS 2.0 ULTRA")
    logger.info("="*70)
    print()
    
    # Inicializar componentes
    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    pinecone_manager = PineconeManager(api_key=pinecone_api_key)
    embedding_generator = EmbeddingGenerator(openai_api_key=openai_api_key)
    chunker = BrazilianLegalChunker()
    processor = DocumentProcessor(chunker, embedding_generator)
    
    # Estatísticas iniciais
    logger.info("📊 ESTATÍSTICAS INICIAIS")
    initial_stats = pinecone_manager.get_index_stats()
    logger.info(f"   Total de vetores: {initial_stats.get('total_vector_count', 0)}")
    print()
    
    # Processar cada domínio
    total_added = 0
    domains_processed = []
    
    for domain, documents in LEGAL_KNOWLEDGE_BASE.items():
        vectors_added = await populate_domain(
            domain=domain,
            documents=documents,
            processor=processor,
            pinecone_manager=pinecone_manager
        )
        total_added += vectors_added
        domains_processed.append((domain, vectors_added))
    
    # Estatísticas finais
    logger.info("="*70)
    logger.info("RESUMO DA POPULAÇÃO")
    logger.info("="*70)
    print()
    
    final_stats = pinecone_manager.get_index_stats()
    logger.info(f"📊 ESTATÍSTICAS FINAIS:")
    logger.info(f"   Total de vetores no índice: {final_stats.get('total_vector_count', 0)}")
    logger.info(f"   Vetores adicionados nesta execução: {total_added}")
    print()
    
    logger.info(f"📦 DOMÍNIOS POPULADOS:")
    for domain, count in domains_processed:
        logger.info(f"   ✓ {domain}: +{count} vetores")
    
    print()
    logger.info("="*70)
    logger.info("✅ POPULAÇÃO CONCLUÍDA COM SUCESSO!")
    logger.info("="*70)
    print()
    logger.info("💡 PRÓXIMOS PASSOS:")
    logger.info("   1. Teste o sistema com consultas dos domínios populados")
    logger.info("   2. Adicione mais jurisprudências e súmulas")
    logger.info("   3. Monitore a precisão das respostas")
    print()


if __name__ == "__main__":
    asyncio.run(main())
