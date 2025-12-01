# Sistema de Planos - Doutor Legis 2.0
## Documento Oficial de Referência Técnica

**Status:** ✅ Integrado à base de conhecimento  
**Versão:** 2.0  
**Data:** 29 de novembro de 2025

---

## 📋 VISÃO GERAL

Sistema completo de assinaturas e planos com:
- ✅ 4 níveis de plano (Gratuito, Básico, Intermediário, Avançado)
- ✅ Limites mensais por recurso (consultas, PDFs)
- ✅ Integração Stripe (pagamentos, assinaturas, webhooks)
- ✅ Sistema de trial (14 dias)
- ✅ Reset automático mensal
- ✅ Emails profissionais (SendGrid)
- ✅ Controle de uso e auditoria
- ✅ Reembolso automático
- ✅ Middleware de verificação

---

## 🎯 PLANOS DISPONÍVEIS

### 1. GRATUITO
- **Preço:** R$ 0,00
- **Consultas:** 3/mês
- **PDFs:** 0/mês
- **Domínios:** 1 (Ética e Advocacia OAB)
- **Histórico:** 0 meses
- **Suporte:** Base de conhecimento

### 2. BÁSICO
- **Preço Mensal:** R$ 197,00
- **Preço Anual:** R$ 1.773,00 (25% desconto)
- **Consultas:** 30/mês
- **PDFs:** 5/mês
- **Domínios:** 3
- **Histórico:** 3 meses
- **Recursos:** PDF Simples, Email support (72h)
- **Trial:** 14 dias

### 3. INTERMEDIÁRIO
- **Preço Mensal:** R$ 497,00
- **Preço Anual:** R$ 4.476,00 (25% desconto)
- **Consultas:** 150/mês
- **PDFs:** 25/mês
- **Domínios:** 9 (todos)
- **Histórico:** 12 meses
- **Recursos:** PDF Profissional, Word Export, Email support (24h), Dashboard
- **Trial:** 14 dias

### 4. AVANÇADO
- **Preço Mensal:** R$ 997,00
- **Preço Anual:** R$ 8.976,00 (30% desconto)
- **Consultas:** ILIMITADAS
- **PDFs:** ILIMITADOS
- **Domínios:** 9 (todos)
- **Histórico:** Permanente
- **Recursos:** TODOS + API, Webhooks, Chat support (1h), Telefone, Account Manager
- **SLA:** 99.9% uptime
- **Trial:** 14 dias

---

## 🗄️ ESTRUTURA DE DADOS (MongoDB)

### Collection: usuarios
```javascript
{
  id: String (UUID),
  email: String (unique, indexed),
  nome: String,
  foto: String,
  
  // Plano
  plano: String, // "gratuito", "basico", "intermediario", "avancado"
  
  // Stripe
  stripe_customer_id: String (unique),
  stripe_subscription_id: String (unique),
  
  // Datas
  data_plano_inicio: DateTime,
  data_plano_fim: DateTime,
  data_renovacao: DateTime,
  
  // Trial
  em_trial: Boolean (default: false),
  data_trial_inicio: DateTime,
  data_trial_fim: DateTime,
  
  // Uso mensal (reseta todo mês)
  consultas_mes_atual: Integer (default: 0),
  pdfs_mes_atual: Integer (default: 0),
  consultas_reset: DateTime,
  pdfs_reset: DateTime,
  
  // Auth
  google_id: String (unique),
  ativo: Boolean (default: true),
  
  // Timestamps
  criado_em: DateTime,
  atualizado_em: DateTime,
  ultimo_acesso: DateTime
}
```

### Collection: plano_configuracao
```javascript
{
  id: String (UUID),
  plano: String (unique, indexed), // "gratuito", "basico", etc
  
  // Preços (em centavos)
  preco_mensal: Integer,
  preco_anual: Integer,
  percentual_desconto_anual: Float,
  
  // Limites (null = ilimitado)
  consultas_por_mes: Integer,
  pdfs_por_mes: Integer,
  dominios_disponiveis: Integer,
  historico_meses: Integer,
  
  // Features
  pdf_simples: Boolean,
  pdf_profissional: Boolean,
  pdf_word_export: Boolean,
  compartilhamento_seguro: Boolean,
  
  // Suporte
  chat_support: Boolean,
  email_support: Boolean,
  telefone_support: Boolean,
  account_manager: Boolean,
  tempo_resposta_email: Integer (horas),
  tempo_resposta_chat: Integer (horas),
  
  // Integração
  api_access: Boolean,
  webhooks: Boolean,
  alertas_automaticos: Boolean,
  templates_customizaveis: Boolean,
  dashboard_avancado: Boolean,
  sla_uptime: Float,
  
  // Stripe
  stripe_price_id_mensal: String,
  stripe_price_id_anual: String,
  
  criado_em: DateTime,
  atualizado_em: DateTime
}
```

### Collection: uso_log
```javascript
{
  id: String (UUID),
  usuario_id: String (indexed),
  
  tipo: String, // "consulta", "pdf", "upgrade", "downgrade", "cancelamento"
  acao: String, // "create", "update", "delete", "iniciado", "concluido"
  plano_na_epoca: String,
  
  // Contadores no momento
  consultas_restantes: Integer,
  pdfs_restantes: Integer,
  
  // Detalhes (JSON)
  detalhes: Object,
  
  criado_em: DateTime (indexed)
}
```

### Collection: avisos
```javascript
{
  id: String (UUID),
  usuario_id: String (indexed),
  
  tipo: String, // "limite_proximo", "trial_expirando", "renovacao", "cancelamento"
  mensagem: String,
  lido: Boolean (default: false),
  
  criado_em: DateTime,
  lido_em: DateTime
}
```

---

## 🛣️ ROTAS DA API

### Planos e Perfil
```
GET    /api/planos/meu-plano              # Informações do plano atual
GET    /api/planos/todos-planos           # Lista todos planos disponíveis
GET    /api/planos/verificar-limite       # Verifica se pode usar recurso
```

### Upgrade/Downgrade
```
POST   /api/planos/upgrade                # Criar sessão checkout Stripe
POST   /api/planos/downgrade              # Voltar para gratuito
POST   /api/planos/cancelar               # Cancelar assinatura + reembolso
```

### Pagamentos
```
GET    /api/planos/pagamentos             # Histórico de pagamentos
POST   /api/webhook/stripe                # Webhook eventos Stripe
```

### Admin
```
POST   /admin/init-planos                 # Inicializar configurações (uma vez)
```

---

## 🔄 FLUXO DE UPGRADE

1. **Usuário clica em "Fazer Upgrade"**
   - Frontend chama `POST /api/planos/upgrade`
   - Body: `{plano: "intermediario", tipo_pagamento: "mensal"}`

2. **Backend cria checkout Stripe**
   - Verifica plano válido
   - Busca `stripe_price_id_mensal` ou `_anual`
   - Cria customer Stripe (se não existir)
   - Cria checkout session com trial 14 dias
   - Retorna URL do checkout

3. **Usuário paga no Stripe**
   - Stripe processa pagamento
   - Envia webhook para backend

4. **Webhook processa evento**
   - `customer.subscription.created`: Ativa assinatura, define trial
   - `invoice.payment_succeeded`: Cria registro pagamento, ativa plano
   - Atualiza usuário: plano, datas, limites
   - Envia email de boas-vindas

5. **Usuário acessa plano novo**
   - Limites atualizados
   - Recursos liberados

---

## ⚙️ MIDDLEWARE DE VERIFICAÇÃO

```python
@app.middleware("http")
async def verificar_limite_ao_consultar(request, call_next):
    if request.url.path == "/api/consultation" and request.method == "POST":
        # Obter usuário
        # Verificar limites
        if limite_atingido:
            return JSONResponse(
                status_code=402,
                content={
                    "erro": "limite_atingido",
                    "mensagem": "Limite atingido",
                    "usado": X,
                    "limite": Y,
                    "upgrade_url": "/api/planos/upgrade"
                }
            )
    return await call_next(request)
```

---

## 📅 RESET MENSAL AUTOMÁTICO

**Scheduler (APScheduler):**
- Roda diariamente à meia-noite UTC
- Verifica se mês mudou desde último reset
- Reseta `consultas_mes_atual = 0`
- Reseta `pdfs_mes_atual = 0`
- Atualiza `consultas_reset` e `pdfs_reset`

```python
scheduler.add_job(
    resetar_contadores_mensais,
    "cron",
    hour=0,
    minute=0
)
```

---

## 📧 EMAILS PROFISSIONAIS

**SendGrid Templates:**
1. **Boas-vindas** - Novo plano contratado
2. **Upgrade confirmado** - Após webhook Stripe
3. **Limite próximo** - 80% usado
4. **Trial expirando** - 3 dias antes
5. **Renovação** - Pagamento confirmado
6. **Cancelamento** - Plano cancelado
7. **Reembolso** - Valor devolvido
8. **Falha pagamento** - Cobrança recusada

**Design:**
- Header azul marinho (#001F3F)
- Botões ouro (#D4AF37)
- Layout responsivo
- Disclaimer jurídico sempre presente

---

## 💳 STRIPE WEBHOOKS

### Eventos Processados

**customer.subscription.created**
- Nova assinatura criada
- Define plano, trial, datas
- Envia email boas-vindas

**customer.subscription.updated**
- Upgrade/downgrade
- Mudança de status
- Atualiza usuário

**customer.subscription.deleted**
- Assinatura cancelada/expirada
- Volta para gratuito
- Reseta contadores

**invoice.payment_succeeded**
- Pagamento confirmado
- Cria registro Pagamento
- Envia email renovação

**invoice.payment_failed**
- Falha no pagamento
- Cria registro falha
- Envia email alerta
- Cancela assinatura se reincidente

---

## 💰 SISTEMA DE REEMBOLSO

### Regras
1. **Até 7 dias:** Reembolso total
2. **7-30 dias:** Reembolso pró-rata (dias restantes)
3. **Após 30 dias:** Sem reembolso

### Processo
1. Usuário cancela via `/api/planos/cancelar`
2. Backend calcula dias desde último pagamento
3. Se elegível, cria reembolso Stripe
4. Atualiza registro Pagamento
5. Envia email confirmação
6. Volta usuário para plano gratuito

```python
if dias_decorridos <= 7:
    valor_reembolso = ultimo_pagamento.valor_final
elif dias_decorridos < 30:
    dias_restantes = 30 - dias_decorridos
    valor_reembolso = int(
        ultimo_pagamento.valor_final * (dias_restantes / 30)
    )
```

---

## 🔐 SEGURANÇA

### Validação Webhook Stripe
```python
event = stripe.Webhook.construct_event(
    payload,
    sig_header,
    webhook_secret
)
```

### Rate Limiting
- 60 requisições/minuto por IP
- Middleware SlowAPI

### Validação de Limites
- Middleware verifica antes de processar
- Retorna 402 Payment Required se limite atingido

### Logs de Auditoria
- Toda ação registrada em `uso_log`
- Timestamp, tipo, ação, detalhes
- Retention: permanente

---

## 📊 MÉTRICAS E MONITORAMENTO

### Métricas por Plano
```javascript
{
  percentual_uso_consultas: (usado / limite) * 100,
  percentual_uso_pdfs: (usado / limite) * 100,
  consultas_restantes: limite - usado,
  pdfs_restantes: limite - usado
}
```

### Alertas Automáticos
- **80% usado:** Email "limite próximo"
- **100% usado:** Bloqueio + modal upgrade
- **Trial -3 dias:** Email "trial expirando"

---

## 🧪 TESTES

### Teste de Upgrade
```bash
curl -X POST https://legalai-18.preview.emergentagent.com/api/planos/upgrade \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"plano":"intermediario","tipo_pagamento":"mensal"}'
```

### Teste de Limite
```bash
curl https://legalai-18.preview.emergentagent.com/api/planos/verificar-limite?tipo=consulta \
  -H "Authorization: Bearer TOKEN"
```

### Teste Webhook Stripe (Local)
```bash
stripe listen --forward-to localhost:8000/api/webhook/stripe
stripe trigger customer.subscription.created
```

---

## 🚀 INICIALIZAÇÃO

### 1. Criar Produtos Stripe
```bash
# Criar produtos e prices no dashboard Stripe
# Copiar price IDs para .env
```

### 2. Inicializar Planos
```bash
curl -X POST https://legalai-18.preview.emergentagent.com/admin/init-planos
```

### 3. Configurar Webhook
```bash
# No dashboard Stripe:
# Webhooks → Add endpoint
# URL: https://legalai-18.preview.emergentagent.com/api/webhook/stripe
# Eventos: customer.subscription.*, invoice.*
# Copiar webhook secret para .env
```

### 4. Configurar SendGrid
```bash
# Criar conta SendGrid
# Criar API key
# Verificar domínio sender
# Copiar API key para .env
```

---

## 📝 VARIÁVEIS DE AMBIENTE

```bash
# Stripe
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
STRIPE_PRICE_BASICO_MENSAL=price_xxx
STRIPE_PRICE_BASICO_ANUAL=price_xxx
STRIPE_PRICE_INTERMEDIARIO_MENSAL=price_xxx
STRIPE_PRICE_INTERMEDIARIO_ANUAL=price_xxx
STRIPE_PRICE_AVANCADO_MENSAL=price_xxx
STRIPE_PRICE_AVANCADO_ANUAL=price_xxx

# SendGrid
SENDGRID_API_KEY=SG.xxx
SENDGRID_FROM_EMAIL=noreply@doutorlegis.com.br

# App
APP_URL=https://legalai-18.preview.emergentagent.com
```

---

## ✅ CHECKLIST DE IMPLEMENTAÇÃO

- [x] Modelos de dados MongoDB
- [x] Rotas de planos
- [x] Middleware de limite
- [ ] Scheduler reset mensal
- [x] Webhook Stripe
- [ ] Email service SendGrid
- [ ] Testes end-to-end
- [ ] Documentação usuário
- [ ] Dashboard admin
- [ ] Métricas e analytics

---

**Este documento é a fonte oficial para todas as questões sobre planos, assinaturas, limites e cobrança no Doutor Legis 2.0.**

*Atualizado em: 29/11/2025*
