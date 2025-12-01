"""Orquestrador Multi-AI Real - Doutor Legis 2.0 v3.0
Executa 5 IAs especializadas em paralelo e valida resultados
"""

import asyncio
import os
import logging
from typing import Dict, Any, List, Optional
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class MultiAIOrchestrator:
    """Orquestra múltiplas IAs especializadas em paralelo"""
    
    def __init__(
        self,
        openai_key: str,
        claude_key: str,
        google_key: str,
        perplexity_key: str
    ):
        """Inicializa orquestrador com todas as API keys"""
        self.openai_key = openai_key
        self.claude_key = claude_key
        self.google_key = google_key
        self.perplexity_key = perplexity_key
        
        # Pesos para resolução de conflitos
        self.weights = {
            "constitucional": 3.0,
            "jurisprudencial": 2.5,
            "infraconstitucional": 2.0,
            "metodologica": 1.5,
            "doutrinaria": 1.0
        }
    
    async def analyze_parallel(
        self,
        question: str,
        domain: str,
        context: str = "",
        oab_context: str = "",
        nucleo_prompt: str = ""
    ) -> Dict[str, Any]:
        """Executa análise paralela com 5 IAs especializadas
        
        Args:
            question: Pergunta jurídica
            domain: Domínio jurídico
            context: Contexto RAG recuperado
            oab_context: Contexto OAB
            nucleo_prompt: Prompt do núcleo especializado
            
        Returns:
            Dict com análises de todas as IAs e validação consolidada
        """
        start_time = datetime.now()
        
        logger.info(f"🚀 Iniciando análise Multi-AI paralela para domínio: {domain}")
        
        # Criar tarefas paralelas para cada IA
        tasks = [
            self._ia_constitucional(question, domain, context, oab_context, nucleo_prompt),
            self._ia_infraconstitucional(question, domain, context, oab_context, nucleo_prompt),
            self._ia_jurisprudencial(question, domain, context, oab_context, nucleo_prompt),
            self._ia_doutrinaria(question, domain, context, oab_context, nucleo_prompt),
            self._ia_metodologica(question, domain, context, oab_context, nucleo_prompt)
        ]
        
        # Executar todas as IAs em paralelo
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            logger.error(f"Erro na execução paralela: {str(e)}")
            results = [None] * 5
        
        # Extrair resultados
        ia_outputs = {
            "constitucional": results[0] if not isinstance(results[0], Exception) else None,
            "infraconstitucional": results[1] if not isinstance(results[1], Exception) else None,
            "jurisprudencial": results[2] if not isinstance(results[2], Exception) else None,
            "doutrinaria": results[3] if not isinstance(results[3], Exception) else None,
            "metodologica": results[4] if not isinstance(results[4], Exception) else None
        }
        
        # Contar IAs que responderam
        ias_responded = sum(1 for v in ia_outputs.values() if v is not None)
        logger.info(f"✅ {ias_responded}/5 IAs responderam com sucesso")
        
        # Se menos de 3 IAs responderam, falhar graciosamente
        if ias_responded < 3:
            logger.warning(f"⚠️ Apenas {ias_responded} IAs responderam. Análise comprometida.")
            return {
                "status": "degraded",
                "ias_responded": ias_responded,
                "message": "Análise comprometida. Tente novamente.",
                "ia_outputs": ia_outputs
            }
        
        # Validar e consolidar respostas
        consolidated = await self._ia_validadora(ia_outputs, question, domain)
        
        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info(f"⏱️ Análise Multi-AI concluída em {elapsed:.2f}s")
        
        return {
            "status": "success",
            "ias_responded": ias_responded,
            "ia_outputs": ia_outputs,
            "consolidated": consolidated,
            "elapsed_time": elapsed
        }
    
    def _extract_json_from_text(self, text: str) -> Dict[str, Any]:
        """Extrai JSON de texto que pode conter Markdown ou outros caracteres"""
        import re
        
        # Tentar parsear direto
        try:
            return json.loads(text)
        except:
            pass
        
        # Tentar extrair JSON de code block
        json_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
        match = re.search(json_pattern, text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except:
                pass
        
        # Tentar encontrar JSON em qualquer lugar do texto
        json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        matches = re.findall(json_pattern, text, re.DOTALL)
        for match in matches:
            try:
                result = json.loads(match)
                if isinstance(result, dict) and 'sintese' in result:
                    return result
            except:
                continue
        
        # Fallback: criar JSON mínimo do texto
        return {
            "sintese": text[:200] + "..." if len(text) > 200 else text,
            "conclusao": "Análise disponível no texto completo",
            "confianca": 70
        }
    
    async def _ia_constitucional(
        self,
        question: str,
        domain: str,
        context: str,
        oab_context: str,
        nucleo_prompt: str
    ) -> Dict[str, Any]:
        """IA-1: Análise Constitucional usando Claude Sonnet"""
        try:
            from anthropic import AsyncAnthropic
            
            client = AsyncAnthropic(api_key=self.claude_key)
            
            prompt = f"""Você é a IA Especializada em ANÁLISE CONSTITUCIONAL.

**CONTEXTO DO DOMÍNIO:** {domain}
{oab_context}
{nucleo_prompt}

**DOCUMENTOS RECUPERADOS (RAG):**
{context if context else "Nenhum documento específico recuperado."}

**SUA TAREFA:**
Analise a pergunta EXCLUSIVAMENTE sob a perspectiva CONSTITUCIONAL:
- Conformidade com CF/88
- Princípios constitucionais aplicáveis
- Competências federativas
- Direitos fundamentais
- Precedentes do STF

**FORMATO DE RESPOSTA (JSON):**
{{
  "sintese": "Resumo da análise constitucional",
  "dispositivos_cf": ["art. X, § Y, inciso Z, da CF/88", "..."],
  "principios": ["Princípio 1", "Princípio 2"],
  "precedentes_stf": [
    {{
      "identificacao": "STF, ADI XXXX",
      "tese": "Tese consolidada",
      "aplicacao_caso": "Como se aplica ao caso específico"
    }}
  ],
  "conclusao": "Posição fundamentada",
  "confianca": 85
}}

**PERGUNTA:** {question}

Responda APENAS com o JSON, sem texto adicional."""

            response = await client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response.content[0].text
            result = self._extract_json_from_text(content)
            result["ia"] = "constitucional"
            result["model"] = "claude-sonnet-4"
            
            logger.info("✅ IA-1 Constitucional respondeu")
            return result
            
        except Exception as e:
            logger.error(f"❌ IA-1 Constitucional falhou: {str(e)}")
            return None
    
    async def _ia_infraconstitucional(
        self,
        question: str,
        domain: str,
        context: str,
        oab_context: str,
        nucleo_prompt: str
    ) -> Dict[str, Any]:
        """IA-2: Análise Infraconstitucional usando GPT-4"""
        try:
            from openai import AsyncOpenAI
            
            client = AsyncOpenAI(api_key=self.openai_key)
            
            prompt = f"""Você é a IA Especializada em ANÁLISE INFRACONSTITUCIONAL.

**CONTEXTO DO DOMÍNIO:** {domain}
{oab_context}
{nucleo_prompt}

**DOCUMENTOS RECUPERADOS (RAG):**
{context if context else "Nenhum documento específico recuperado."}

**SUA TAREFA:**
Analise a pergunta EXCLUSIVAMENTE sob a perspectiva INFRACONSTITUCIONAL:
- Legislação ordinária aplicável
- Códigos (CC, CP, CPC, CPP, CLT, CDC, etc)
- Decretos e resoluções
- Hierarquia normativa
- Antinomias jurídicas

**FORMATO DE RESPOSTA (JSON):**
{{
  "sintese": "Resumo da análise legal",
  "leis_aplicaveis": ["art. X, § Y, da Lei N/Ano", "..."],
  "hierarquia": "Ordem hierárquica se relevante",
  "antinomias": "Conflitos identificados e resolução",
  "conclusao": "Posição fundamentada",
  "confianca": 85
}}

**PERGUNTA:** {question}

Responda APENAS com o JSON, sem texto adicional."""

            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            result = json.loads(content)
            result["ia"] = "infraconstitucional"
            result["model"] = "gpt-4o"
            
            logger.info("✅ IA-2 Infraconstitucional respondeu")
            return result
            
        except Exception as e:
            logger.error(f"❌ IA-2 Infraconstitucional falhou: {str(e)}")
            return None
    
    async def _ia_jurisprudencial(
        self,
        question: str,
        domain: str,
        context: str,
        oab_context: str,
        nucleo_prompt: str
    ) -> Dict[str, Any]:
        """IA-3: Análise Jurisprudencial usando Gemini ou GPT-4 (fallback)"""
        # Tentar Gemini primeiro
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=self.google_key)
            
            # Tentar modelos em ordem de preferência
            models_to_try = ['gemini-1.5-pro', 'gemini-1.5-flash', 'gemini-pro']
            
            for model_name in models_to_try:
                try:
                    model = genai.GenerativeModel(model_name)
            
            prompt = f"""Você é a IA Especializada em ANÁLISE JURISPRUDENCIAL.

**CONTEXTO DO DOMÍNIO:** {domain}
{oab_context}
{nucleo_prompt}

**DOCUMENTOS RECUPERADOS (RAG):**
{context if context else "Nenhum documento específico recuperado."}

**SUA TAREFA:**
Analise a pergunta EXCLUSIVAMENTE sob a perspectiva JURISPRUDENCIAL:
- Precedentes vinculantes (STF, STJ, TST)
- Súmulas aplicáveis
- Teses de repercussão geral
- Recursos repetitivos
- Evolução jurisprudencial

**FORMATO DE RESPOSTA (JSON):**
{{
  "sintese": "Resumo da análise jurisprudencial",
  "precedentes_vinculantes": [
    {{
      "tribunal": "STF/STJ/TST",
      "identificacao": "RE XXXXX",
      "tese": "Tese consolidada",
      "aplicacao_caso": "Como se aplica ao caso"
    }}
  ],
  "sumulas": ["Súmula X do Tribunal Y"],
  "tendencia": "Consolidada/Em evolução/Divergente",
  "conclusao": "Posição fundamentada",
  "confianca": 85
}}

**PERGUNTA:** {question}

Responda APENAS com o JSON, sem texto adicional."""

                    response = await asyncio.to_thread(
                        model.generate_content,
                        prompt
                    )
                    
                    content = response.text
                    result = self._extract_json_from_text(content)
                    result["ia"] = "jurisprudencial"
                    result["model"] = f"gemini-{model_name}"
                    
                    logger.info(f"✅ IA-3 Jurisprudencial respondeu ({model_name})")
                    return result
                    
                except Exception as model_error:
                    logger.warning(f"Gemini {model_name} falhou: {str(model_error)[:100]}")
                    continue
            
            # Se todos os modelos Gemini falharam, tentar fallback GPT-4
            logger.info("Gemini indisponível, usando GPT-4 como fallback")
            from openai import AsyncOpenAI
            
            client = AsyncOpenAI(api_key=self.openai_key)
            
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            result = json.loads(content)
            result["ia"] = "jurisprudencial"
            result["model"] = "gpt-4o-mini-fallback"
            
            logger.info("✅ IA-3 Jurisprudencial respondeu (GPT-4 fallback)")
            return result
            
        except Exception as e:
            logger.error(f"❌ IA-3 Jurisprudencial falhou completamente: {str(e)}")
            return None
    
    async def _ia_doutrinaria(
        self,
        question: str,
        domain: str,
        context: str,
        oab_context: str,
        nucleo_prompt: str
    ) -> Dict[str, Any]:
        """IA-4: Análise Doutrinária usando Perplexity"""
        try:
            from openai import AsyncOpenAI
            
            # Perplexity usa API compatível com OpenAI
            client = AsyncOpenAI(
                api_key=self.perplexity_key,
                base_url="https://api.perplexity.ai"
            )
            
            prompt = f"""Você é a IA Especializada em ANÁLISE DOUTRINÁRIA.

**CONTEXTO DO DOMÍNIO:** {domain}
{oab_context}
{nucleo_prompt}

**DOCUMENTOS RECUPERADOS (RAG):**
{context if context else "Nenhum documento específico recuperado."}

**SUA TAREFA:**
Analise a pergunta EXCLUSIVAMENTE sob a perspectiva DOUTRINÁRIA:
- Posições doutrinárias majoritárias
- Debates acadêmicos atuais
- Autores referência
- Consenso doutrinário

**FORMATO DE RESPOSTA (JSON):**
{{
  "sintese": "Resumo da análise doutrinária",
  "posicao_majoritaria": "Qual é e por quem defendida",
  "debates_atuais": "Controvérsias acadêmicas",
  "autores_referencia": ["Autor 1", "Autor 2"],
  "consenso": "Alto/Médio/Baixo",
  "conclusao": "Posição fundamentada",
  "confianca": 85
}}

**PERGUNTA:** {question}

Responda APENAS com o JSON, sem texto adicional."""

            # Modelos válidos da Perplexity
            models_to_try = [
                "sonar-pro",
                "sonar",
                "llama-3.1-sonar-huge-128k-online"
            ]
            
            result = None
            for model_name in models_to_try:
                try:
                    response = await client.chat.completions.create(
                        model=model_name,
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=2000
                    )
                    
                    content = response.choices[0].message.content
                    result = self._extract_json_from_text(content)
                    result["ia"] = "doutrinaria"
                    result["model"] = f"perplexity-{model_name}"
                    
                    logger.info(f"✅ IA-4 Doutrinária respondeu ({model_name})")
                    return result
                    
                except Exception as model_error:
                    logger.warning(f"Perplexity {model_name} falhou: {str(model_error)[:100]}")
                    continue
            
            # Se Perplexity falhou, usar GPT-4 como fallback
            logger.info("Perplexity indisponível, usando GPT-4 como fallback")
            from openai import AsyncOpenAI
            
            fallback_client = AsyncOpenAI(api_key=self.openai_key)
            
            response = await fallback_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            result = json.loads(content)
            result["ia"] = "doutrinaria"
            result["model"] = "gpt-4o-mini-fallback"
            
            logger.info("✅ IA-4 Doutrinária respondeu (GPT-4 fallback)")
            return result
            
        except Exception as e:
            logger.error(f"❌ IA-4 Doutrinária falhou completamente: {str(e)}")
            return None
    
    async def _ia_metodologica(
        self,
        question: str,
        domain: str,
        context: str,
        oab_context: str,
        nucleo_prompt: str
    ) -> Dict[str, Any]:
        """IA-5: Análise Metodológica usando Claude Opus"""
        try:
            from anthropic import AsyncAnthropic
            
            client = AsyncAnthropic(api_key=self.claude_key)
            
            prompt = f"""Você é a IA Especializada em MÉTODOS JURÍDICOS.

**CONTEXTO DO DOMÍNIO:** {domain}
{oab_context}
{nucleo_prompt}

**DOCUMENTOS RECUPERADOS (RAG):**
{context if context else "Nenhum documento específico recuperado."}

**SUA TAREFA:**
Analise a pergunta EXCLUSIVAMENTE sob a perspectiva METODOLÓGICA:
- Métodos de interpretação (literal, sistemático, teleológico, histórico)
- Teste de proporcionalidade (se houver colisão)
- Ponderação de direitos
- Resolução de antinomias

**FORMATO DE RESPOSTA (JSON):**
{{
  "sintese": "Resumo da análise metodológica",
  "metodos_aplicados": ["Literal", "Sistemático", "..."],
  "teste_proporcionalidade": {{
    "adequacao": "Análise",
    "necessidade": "Análise",
    "proporcionalidade_estrita": "Análise",
    "direito_prevalente": "Qual e por quê"
  }},
  "colisao_direitos": "Se houver, identificar",
  "conclusao": "Posição fundamentada",
  "confianca": 85
}}

**PERGUNTA:** {question}

Responda APENAS com o JSON, sem texto adicional."""

            # Tentar Claude Opus, senão usar Sonnet
            models_to_try = [
                ("claude-opus-4-20250514", "claude-opus-4"),
                ("claude-sonnet-4-20250514", "claude-sonnet-4")
            ]
            
            for model_id, model_name in models_to_try:
                try:
                    response = await client.messages.create(
                        model=model_id,
                        max_tokens=2000,
                        messages=[{"role": "user", "content": prompt}]
                    )
                    
                    content = response.content[0].text
                    result = self._extract_json_from_text(content)
                    result["ia"] = "metodologica"
                    result["model"] = model_name
                    
                    logger.info(f"✅ IA-5 Metodológica respondeu ({model_name})")
                    return result
                    
                except Exception as model_error:
                    logger.warning(f"Claude {model_name} falhou: {str(model_error)[:100]}")
                    continue
            
            logger.error("❌ IA-5 Metodológica falhou com todos os modelos Claude")
            return None
            
        except Exception as e:
            logger.error(f"❌ IA-5 Metodológica falhou: {str(e)}")
            return None
    
    async def _ia_validadora(
        self,
        ia_outputs: Dict[str, Any],
        question: str,
        domain: str
    ) -> Dict[str, Any]:
        """IA-6: Validadora - Consolida e valida todos os outputs"""
        try:
            from anthropic import AsyncAnthropic
            
            client = AsyncAnthropic(api_key=self.claude_key)
            
            # Preparar outputs das IAs
            outputs_text = json.dumps(ia_outputs, ensure_ascii=False, indent=2)
            
            prompt = f"""Você é a IA VALIDADORA que consolida análises de 5 IAs especializadas.

**OUTPUTS DAS IAs ESPECIALIZADAS:**
{outputs_text}

**PERGUNTA ORIGINAL:** {question}
**DOMÍNIO:** {domain}

**SUA TAREFA:**
1. Identificar concordâncias entre as IAs
2. Identificar divergências e resolvê-las usando critérios hierárquicos
3. Calcular consenso geral
4. Sintetizar resposta unificada em formato Markdown

**CRITÉRIOS DE RESOLUÇÃO:**
- Hierarquia: Constitucional > Jurisprudencial > Infraconstitucional > Metodológica > Doutrinária
- Votação ponderada com pesos fornecidos
- Consenso mínimo 70%

**FORMATO DE RESPOSTA:**
Gere uma análise completa em Markdown seguindo EXATAMENTE esta estrutura:

---
**DOUTOR LEGIS 2.0 - ANÁLISE MULTI-IA CONSOLIDADA**
Precisão Jurídica: [X%] | Consenso: [Y%] | IAs Consultadas: [N]
---

## ANÁLISE MULTI-DIMENSIONAL

### 🏛️ PERSPECTIVA CONSTITUCIONAL
[Síntese consolidada da IA-1]
**Dispositivos:** [citações completas]
**Confiança:** [X%]

### 📜 PERSPECTIVA INFRACONSTITUCIONAL
[Síntese consolidada da IA-2]
**Leis:** [citações completas]
**Confiança:** [X%]

### ⚖️ PERSPECTIVA JURISPRUDENCIAL
[Síntese consolidada da IA-3]
**Precedentes:** [citações completas com conexão ao caso]
**Confiança:** [X%]

### 📚 PERSPECTIVA DOUTRINÁRIA
[Síntese consolidada da IA-4]
**Autores:** [lista]
**Confiança:** [X%]

### 🔬 PERSPECTIVA METODOLÓGICA
[Síntese consolidada da IA-5]
**Métodos:** [lista]
**Confiança:** [X%]

---

## ✅ CONCLUSÃO UNIFICADA

### TESE JURÍDICA CONSOLIDADA
[Resposta objetiva em 1-2 frases]

### FUNDAMENTAÇÃO INTEGRADA
[3-4 parágrafos unindo todas perspectivas]

### DISPOSITIVOS NORMATIVOS APLICÁVEIS
1. **art. X, § Y, inciso Z:** [aplicação]

### PRECEDENTES VINCULANTES
1. **STF, [ID]:** [tese]. **Aplica-se porque** [conexão]

### RESPOSTA PRÁTICA
[O que acontece no caso concreto]

---

## 📊 ÍNDICES

**Precisão:** [X%] ████████░░
**Consenso:** [X%] ████████░░

### ✓ CONCORDÂNCIAS
- ✓ [Pontos de acordo]

### ⚠️ DIVERGÊNCIAS RESOLVIDAS
- ⚠️ [Se houver, como foi resolvida]

### 🛡️ SEGURANÇA JURÍDICA: [ALTO/MÉDIO/BAIXO]
[Justificativa]

### 🎯 RECOMENDAÇÃO
[Ação prática fundamentada]

Gere a resposta completa em Markdown."""

            response = await client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            consolidated_text = response.content[0].text
            
            # Calcular consenso
            confiancas = [
                ia_outputs[k].get("confianca", 0) 
                for k in ia_outputs 
                if ia_outputs[k] is not None
            ]
            consenso = sum(confiancas) / len(confiancas) if confiancas else 0
            
            logger.info("✅ IA-6 Validadora consolidou respostas")
            
            return {
                "analise_completa": consolidated_text,
                "consenso": round(consenso, 1),
                "ias_responded": len(confiancas),
                "formato": "multi_ai_real_parallel"
            }
            
        except Exception as e:
            logger.error(f"❌ IA-6 Validadora falhou: {str(e)}")
            # Fallback: retornar primeira IA que respondeu
            for ia_name, output in ia_outputs.items():
                if output:
                    return {
                        "analise_completa": f"**MODO DEGRADADO** - Apenas perspectiva {ia_name} disponível.\n\n{json.dumps(output, indent=2, ensure_ascii=False)}",
                        "consenso": output.get("confianca", 50),
                        "ias_responded": 1,
                        "formato": "fallback_single_ia"
                    }
            
            return {
                "analise_completa": "**ERRO** - Nenhuma IA conseguiu responder.",
                "consenso": 0,
                "ias_responded": 0,
                "formato": "error"
            }
