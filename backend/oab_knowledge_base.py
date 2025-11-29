"""Base de conhecimento OAB - Estatuto da Advocacia e Código de Ética"""

# Estatuto da Advocacia (Lei 8.906/1994) - Estrutura Principal
ESTATUTO_OAB = {
    "titulo": "Estatuto da Advocacia e da OAB - Lei 8.906/1994",
    "estrutura": {
        "atividade_advocacia": {
            "art_1": "Atividades privativas: postulação judicial, consultoria, assessoria e direção jurídicas",
            "art_2": "Advogado indispensável à administração da justiça, presta serviço público, exerce função social",
            "art_3": "Exercício privativo dos inscritos na OAB",
            "art_4": "Nulidade de atos praticados por não inscritos",
            "art_5": "Procuração e mandato. Renúncia com prazo de 10 dias"
        },
        "prerrogativas": {
            "art_6": "Sem hierarquia entre advogados, magistrados e MP. Tratamento digno e respeitoso",
            "art_7": """Direitos do advogado (principais):
            - Inviolabilidade de escritório, correspondência, instrumentos de trabalho (inc. II)
            - Comunicação reservada com clientes presos (inc. III)
            - Presença de OAB em prisão em flagrante (inc. IV)
            - Prisão em sala Estado-Maior ou domiciliar (inc. V)
            - Ingresso livre em tribunais, audiências, delegacias (inc. VI)
            - Sustentação oral após voto relator (inc. IX)
            - Exame de autos sem procuração (inc. XIII e XIV)
            - Assistir clientes investigados (inc. XXI)
            - Quebra de inviolabilidade apenas com decisão judicial motivada (§6º)
            - Presença obrigatória de OAB em busca e apreensão (§6º-C)
            - Vedação colaboração premiada contra cliente (§6º-I)""",
            "art_7A": "Direitos da advogada gestante, lactante, adotante",
            "art_7B": "Crime violar direitos/prerrogativas: detenção 2-4 anos + multa"
        },
        "inscricao": {
            "art_8": "Requisitos: capacidade civil, diploma direito, Exame OAB, idoneidade moral",
            "art_9": "Estagiário: admissão em estágio profissional (2 anos)",
            "art_10": "Inscrição principal no domicílio profissional",
            "art_11": "Cancelamento: pedido, exclusão, falecimento, incompatibilidade, perda requisitos",
            "art_12": "Licenciamento: pedido, incompatibilidade temporária, doença mental"
        },
        "sociedade_advogados": {
            "art_15": "Sociedade simples ou unipessoal de advocacia",
            "art_16": "Vedado: forma empresária, fantasia, sócio não-advogado",
            "art_17": "Responsabilidade subsidiária e ilimitada pelos danos",
            "art_17A_17B": "Associação entre advogados e sociedades"
        },
        "honorarios": {
            "art_22": "Direito aos honorários convencionados, arbitrados e de sucumbência",
            "art_23": "Honorários incluem serviços profissionais e extrajudiciais",
            "art_24": "Presunção de valor excessivo se superior a tabela",
            "art_25": "Suspensão de prestação de serviços por inadimplemento",
            "art_26": "Advogado substabelecido sem reserva responde por danos"
        },
        "incompatibilidades": {
            "art_28": """Incompatibilidades no exercício da advocacia:
            I - chefes Poder Executivo e membros Mesa Legislativo (durante mandato)
            II - membros Ministério Público, Magistratura, Tribunais Contas, diretoria OAB (durante função)
            III - ocupantes cargos/funções vinculadas atividade policial (qualquer natureza)
            IV - militares na ativa (qualquer tipo)
            V - servidores da administração direta, indireta, fundacional (contra Fazenda Pública que os remunere ou onde tenham função)""",
            "art_30": "Administradores de empresas públicas não podem advogar contra elas"
        },
        "infrações_sancoes": {
            "art_34": """Infrações disciplinares:
            I - exercer profissão quando impedido ou com inscrição cancelada
            II - manter sociedade profissional fora normas OAB
            III - vender participação em honorários de causa
            IV - angariar ou captar causas (captação indevida)
            V - assinar documentos elaborados por outro não-advogado
            VI - advogar contra direito ético-juridicamente indisponível
            VII - violar sem justa causa sigilo profissional
            VIII - prejudicar cliente por culpa grave
            IX - pagar/oferecer vantagem a intermediários
            X - omitir/distorcer fatos
            XI - abandonar causa sem motivo justo
            XII - recusar-se a prestar contas
            XIII - deixar de devolver bens/valores
            XIV - praticar crime infamante
            XV - manter conduta incompatível dignidade profissional
            XVI - fazer publicidade vedada
            XVII - tornar conflito judicial mais grave
            XVIII - solicitar/receber importâncias para aplicar desvirtuada finalidade
            XIX - aceitar defesa criminal recebendo dos sucessores do acusado se praticou crime contra vítima
            XX - lançar mão fato sigiloso para proveito próprio/terceiro
            XXI - permitir uso nome por não-advogado
            XXII - estabelecer entendimento Juiz, MP, serventuários para desvirtuar Justiça
            XXIII - receber valores de cliente sem recolher à conta bancária de depósito
            XXIV - reter abusivamente bens, valores de cliente ou terceiro
            XXV - incidir reiteradamente em punição disciplinar
            XXVI - prestar concurso a clientes/terceiros para ato contrário à lei
            XXVII - deixar de cumprir ordem legítima OAB
            XXVIII - tornar-se moralmente inidôneo exercício advocacia
            XXIX - praticar ato contrário Estatuto, Código Ética, Regulamento Geral
            XXX - fazer falsa prova de requisitos
            XXXI - deixar pagar anuidades ou preços de serviços""",
            "art_35": """Sanções disciplinares:
            I - censura (particular ou pública)
            II - suspensão (até 12 meses)
            III - exclusão
            IV - multa (não inferior nem superior a 10 vezes valor anuidade)""",
            "art_36": "Prescrição: 5 anos data fato / Interrupção com instauração processo",
            "art_37": "Reincidência: nova infração mesma natureza em até 2 anos",
            "art_38": "Reabilitação após 1 ano censura/suspensão; 3 anos exclusão"
        }
    }
}

# Código de Ética e Disciplina OAB (Resolução 02/2015)
CODIGO_ETICA_OAB = {
    "titulo": "Código de Ética e Disciplina da OAB - Resolução 02/2015",
    "principios_fundamentais": {
        "art_1": "Exercício exige conduta compatível com preceitos éticos, morais e profissionais",
        "art_2": """Advogado defensor Estado Democrático, direitos humanos, cidadania, moralidade, justiça, paz social.
        Deveres: preservar honra/dignidade, atuar com destemor/independência/honestidade, zelar reputação, 
        aperfeiçoamento contínuo, conciliação/mediação, abster-se influência indevida, pugnar cidadania""",
        "art_3": "Direito meio mitigar desigualdades, lei instrumento igualdade",
        "art_3A": "Perspectiva interseccional gênero e raça, afastando estereótipos",
        "art_4": "Zelar liberdade e independência mesmo vinculado emprego",
        "art_5": "Exercício advocacia incompatível atividades que lhe causem impedimento",
        "art_6": "Boa-fé presume-se em advogados",
        "art_7": "Relações cortesia/respeito entre advogados"
    },
    "relacoes_cliente": {
        "art_11": "Liberdade recusar patrocínio causa contrária consciência, orientação jurídico-política",
        "art_12": "Confidencialidade: dever sigilo sobre fatos conhecidos exercício profissional",
        "art_13": "Recusa causa: impossibilidade técnica, vínculo parentesco adversário, interesse conflitante",
        "art_14": "Substabelecimento com/sem reserva. Cliente informado",
        "art_15": "Impedir atuação junto a cliente anterior quando incompatível sigilo",
        "art_16": "Renúncia mandato mediante justa causa notificada",
        "art_17": "Desaconselhamento lide temerária",
        "art_18": "Dever zelo, dedicação, expedição processos"
    },
    "honorarios": {
        "art_35": "Honorários fixados mediante contrato escrito, clareza quantum",
        "art_36": "Proibido auferir honorários manifestamente excessivos/aviltantes",
        "art_37": "Quota litis: participação resultado lide, desde que razoável",
        "art_38": "Acordo sobre honorários honorífico, não prevalece sobre contrato",
        "art_39": "Honorários sucumbência pertencem advogado",
        "art_40": "Partilha honorários deve ser equitativa, prevista por escrito",
        "art_41": "Vedado valer-se procuração para transferir honorários a terceiro estranho mandato"
    },
    "publicidade": {
        "art_44": "Publicidade informativa, discreta, não mercantilista",
        "art_45": "Vedado: publicidade enganosa, comparação, mercantilização, captação clientela",
        "art_46": "Moderação e sobriedade publicidade",
        "art_47": "Anúncio: nome completo, inscrição, títulos, especializações verdadeiras",
        "art_48": "Vedado anúncio serviços mediante intermediários, agenciamento",
        "art_49": "Entrevistas mídia: moderação, proibido declarações extravagantes",
        "art_50": "Vedado divulgar informações exageradas, alardear êxito",
        "art_51": "Redes sociais e sites seguem mesmas regras publicidade"
    },
    "relacoes_colegas": {
        "art_20": "Urbanidade, cortesia, boa-fé nas relações profissionais",
        "art_21": "Respeito dignidade colega, evitar referências depreciativas",
        "art_22": "Comunicar ao colega ingresso causa onde já atuava",
        "art_23": "Devolver autos ao colega substabelecente quando solicitado",
        "art_24": "Conduta respeitosa em sustentações orais",
        "art_25": "Proibido oferecer serviços a clientes de colega"
    },
    "relacoes_justica": {
        "art_26": "Linguagem técnica, respeitosa, educada com autoridades",
        "art_27": "Defender prerrogativas sem exceder limites",
        "art_28": "Desagravo público quando ofendido no exercício",
        "art_29": "Proibido fazer referências ofensivas a magistrados, membros MP",
        "art_30": "Zelar pela dignidade e credibilidade Poder Judiciário"
    },
    "procedimento_disciplinar": {
        "art_59": "Representação deve ser escrita, fundamentada, identificar representado",
        "art_60": "Segredo justiça no processo ético-disciplinar até julgamento final",
        "art_61": "Notificação para apresentar defesa prévia (15 dias)",
        "art_62": "Revelia: nomeação defensor dativo",
        "art_63": "Instrução: oitiva testemunhas, juntada documentos",
        "art_64": "Razões finais (15 dias) antes julgamento",
        "art_65": "Julgamento por Tribunal Ética e Disciplina",
        "art_66": "Recursos ao Conselho Seccional e Conselho Federal",
        "art_69": "Reabilitação: após cumprimento sanção + provas bom comportamento"
    }
}

# Provimento 205/2021 - Publicidade na Advocacia (referência)
PROVIMENTO_205_2021 = {
    "titulo": "Provimento 205/2021 - Publicidade, Propaganda e Informação da Advocacia",
    "regras_principais": {
        "art_1": "Publicidade informativa, educativa, não mercantilista",
        "art_2": "Vedado: promessa resultado, captação, comparação, sensacionalismo",
        "art_3": "Nome completo, inscrição OAB, área atuação, especialização",
        "art_4": "Redes sociais: mesmas regras, discrição, não captação",
        "art_5": "Vedado: mensagens diretas não solicitadas, spam, anúncios pagos captação",
        "art_6": "Marketing conteúdo: permitido se informativo, educacional, técnico",
        "art_7": "Vedado: concursos, sorteios, promoções para captar clientes"
    }
}

def get_oab_context(domain: str) -> str:
    """Retorna contexto OAB específico para domínio de consulta"""
    
    base_context = f"""
**BASE DE CONHECIMENTO OAB INTEGRADA**

Estatuto da Advocacia e da OAB (Lei 8.906/1994) e Código de Ética e Disciplina (Resolução 02/2015) 
estão integrados a esta consulta.

**FONTES NORMATIVAS OFICIAIS:**
- Lei 8.906/1994 (Estatuto da Advocacia e da OAB)
- Resolução CFOAB 02/2015 (Código de Ética e Disciplina)
- Provimento CFOAB 205/2021 (Publicidade na Advocacia)
- Regulamento Geral da OAB

**DIRETRIZES DE RESPOSTA:**
1. Citar fundamento normativo específico (Ex: Art. 7º, II, EAOAB; Art. 44, CED; Prov. 205/2021)
2. Linguagem profissional, técnica, clara e acessível
3. Evitar interpretações extensivas sem sustentação no texto normativo
4. Manter coerência terminológica com documentos oficiais OAB
5. Ressaltar autonomia profissional em temas opinativos
6. JAMAIS oferecer consultoria jurídica personalizada (apenas análise normativa)
7. Observar especialmente:
   - Princípios fundamentais CED (arts. 1º a 7º)
   - Prerrogativas do advogado (EAOAB arts. 6º a 7-B)
   - Publicidade e marketing (Provimento 205/2021)
   - Procedimentos disciplinares aplicáveis
8. Adotar perspectiva interseccional gênero e raça (Art. 3º-A, CED)
9. Tom elegante, imparcial, ético, institucional
10. Distinguir claramente: "texto normativo", "interpretação" e "orientação"
"""
    
    if "etica" in domain.lower() or "advocacia" in domain.lower() or "oab" in domain.lower():
        return base_context + f"""

**DESTAQUES PARA ÉTICA E ADVOCACIA OAB:**

PRERROGATIVAS ESSENCIAIS (Art. 7º EAOAB):
- Inviolabilidade escritório e correspondência (inc. II)
- Comunicação reservada com clientes presos (inc. III)
- Presença OAB em prisão flagrante (inc. IV)
- Ingresso livre tribunais, delegacias (inc. VI)
- Exame de autos sem procuração (inc. XIII, XIV)
- Assistir clientes investigados (inc. XXI)

INFRAÇÕES MAIS FREQUENTES (Art. 34 EAOAB):
- Captação indevida de clientela (inc. IV)
- Publicidade irregular (inc. XVI)
- Violação sigilo profissional (inc. VII)
- Abandono de causa (inc. XI)
- Recusa prestar contas (inc. XII)
- Retenção abusiva valores (inc. XXIV)

PUBLICIDADE PROFISSIONAL (Arts. 44-51 CED + Prov. 205/2021):
- Deve ser informativa, discreta, não mercantilista
- Vedado: captação, promessa resultado, comparação
- Redes sociais: mesmas regras, conteúdo educacional permitido
- Proibido: mensagens diretas não solicitadas, anúncios captação

HONORÁRIOS (Arts. 35-41 CED):
- Contrato escrito, clareza no quantum
- Proibido valores aviltantes ou excessivos
- Quota litis: participação razoável no resultado
- Honorários sucumbência pertencem ao advogado

PROCEDIMENTO DISCIPLINAR:
- Representação escrita e fundamentada
- Segredo de justiça até julgamento final
- Ampla defesa: defesa prévia, instrução, razões finais
- Sanções: censura, suspensão (até 12 meses), exclusão, multa
- Prescrição: 5 anos da data do fato
- Reabilitação possível após cumprimento sanção
"""
    
    return base_context
