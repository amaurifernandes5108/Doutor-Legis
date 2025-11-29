# Doutor Legis 2.0 - Documentação Completa

## 📋 Visão Geral

**Doutor Legis 2.0** é uma plataforma SaaS de assistência jurídica inteligente para o Brasil, utilizando IA (OpenAI GPT-4) para fornecer análises jurídicas completas em 8 domínios do direito brasileiro.

## 🎯 Funcionalidades Principais

### Consultas Jurídicas Inteligentes
- **8 Domínios Jurídicos**: Constitucional, Civil, Consumidor, Imobiliário, Público, Trabalhista, Empresarial, Internacional
- **Análise Estruturada**: Cada consulta retorna 8 seções completas:
  1. 📝 Resumo
  2. 📜 Legislação Aplicável
  3. ⚖️ Jurisprudência
  4. 🔍 Análise Legal
  5. ⚠️ Riscos Jurídicos
  6. 💡 Recomendações
  7. 👉 Próximos Passos
  8. 🎯 Badge de Confiança (70-95%)

### Sistema de Planos
- **Gratuito**: 3 consultas por mês
- **Premium**: R$ 497/mês, consultas ilimitadas

### Interface Premium
- Layout 3 colunas (sidebar domínios, chat central, painel informações)
- Design profissional: Ouro #D4AF37 + Azul Marinho #001F3F
- Background watermark: Deusa Themis (símbolo da Justiça)
- Fonte: Playfair Display (títulos) + Inter (corpo)
- Totalmente responsivo (mobile-first)

## 🏗️ Arquitetura Técnica

### Stack Tecnológico

**Backend:**
- FastAPI (Python 3.11)
- MongoDB (Motor async driver)
- Rate Limiting (SlowAPI - 60 req/min)
- JWT para autenticação

**Frontend:**
- React 19
- React Router DOM
- Axios
- Lucide React (ícones)
- Shadcn UI components
- Sonner (toasts)

**Integrações:**
1. **Emergent LLM** (OpenAI GPT-4)
   - Chave universal `EMERGENT_LLM_KEY`
   - Modelo: `gpt-4o`
   - Temperature: 0.3
   - Biblioteca: `emergentintegrations.llm.chat`

2. **Emergent Authentication** (Google OAuth)
   - Login social Google
   - Session tokens (7 dias)
   - Cookies httpOnly

3. **Stripe Payments**
   - Checkout sessions
   - Webhooks
   - Polling de status
   - Biblioteca: `emergentintegrations.payments.stripe.checkout`

### Collections MongoDB

```javascript
// users
{
  id: String (UUID),
  email: EmailStr,
  name: String,
  picture: String (optional),
  plan: String ("gratuito" | "premium"),
  token_balance: Int (default: 3),
  google_id: String (optional),
  created_at: DateTime,
  active: Boolean
}

// user_sessions
{
  user_id: String,
  session_token: String,
  expires_at: DateTime,
  created_at: DateTime
}

// consultations
{
  id: String (UUID),
  user_id: String,
  domain: String,
  question: String,
  response: String (JSON das 8 seções),
  confidence: Int (70-95),
  tokens_used: Int,
  processing_time: Float (segundos),
  created_at: DateTime,
  saved: Boolean
}

// payment_transactions
{
  id: String (UUID),
  session_id: String (Stripe),
  user_id: String,
  amount: Float,
  currency: String ("brl"),
  status: String ("initiated" | "completed" | "failed" | "expired"),
  payment_status: String ("unpaid" | "paid"),
  metadata: Object,
  created_at: DateTime
}
```

## 🚀 Deploy e Configuração

### Variáveis de Ambiente

**Backend (.env):**
```bash
MONGO_URL="mongodb://localhost:27017"
DB_NAME="doutor_legis_db"
CORS_ORIGINS="*"

# Emergent LLM Key (OpenAI, Anthropic, Gemini)
EMERGENT_LLM_KEY=sk-emergent-271EaC4A5399b0657F

# Optional: User's own OpenAI key
# OPENAI_API_KEY=your-key-here

# JWT Secret
JWT_SECRET=doutor-legis-super-secret-key-2025

# Stripe
STRIPE_API_KEY=sk_test_emergent

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
```

**Frontend (.env):**
```bash
REACT_APP_BACKEND_URL=https://themisbot.preview.emergentagent.com
WDS_SOCKET_PORT=443
REACT_APP_ENABLE_VISUAL_EDITS=false
ENABLE_HEALTH_CHECK=false
```

### Instalação de Dependências

**Backend:**
```bash
cd /app/backend
pip install emergentintegrations --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/
pip install httpx slowapi
pip freeze > requirements.txt
```

**Frontend:**
```bash
cd /app/frontend
yarn install
```

### Iniciar Serviços

```bash
# Restart services
sudo supervisorctl restart backend frontend

# Check status
sudo supervisorctl status

# View logs
tail -f /var/log/supervisor/backend.out.log
tail -f /var/log/supervisor/frontend.out.log
```

## 📡 Endpoints da API

### Autenticação

```bash
GET  /api/auth/google-login      # Retorna URL do Emergent Auth
POST /api/auth/session           # Processa session_id do Google
GET  /api/auth/me                # Perfil do usuário autenticado
POST /api/auth/logout            # Logout
```

### Consultas

```bash
GET  /api/domains                # Lista 8 domínios jurídicos
POST /api/consultation           # Cria nova consulta
GET  /api/consultation/{id}      # Detalhes de uma consulta
GET  /api/history                # Histórico de consultas
```

### Pagamentos

```bash
POST /api/payments/checkout      # Cria sessão Stripe
GET  /api/payments/status/{id}   # Status do pagamento
POST /api/webhook/stripe         # Webhook Stripe
```

### Geral

```bash
GET /api/health                  # Health check
```

## 🧪 Testes

### Teste Manual Backend

```bash
# Health check
curl https://themisbot.preview.emergentagent.com/api/health

# Listar domínios
curl https://themisbot.preview.emergentagent.com/api/domains

# Criar usuário de teste no MongoDB
mongosh --eval "
use('doutor_legis_db');
var userId = 'test-user-' + Date.now();
var sessionToken = 'test_session_' + Date.now();
db.users.insertOne({
  id: userId,
  email: 'test@example.com',
  name: 'Test User',
  plan: 'gratuito',
  token_balance: 3,
  created_at: new Date().toISOString(),
  active: true
});
db.user_sessions.insertOne({
  user_id: userId,
  session_token: sessionToken,
  expires_at: new Date(Date.now() + 7*24*60*60*1000).toISOString(),
  created_at: new Date().toISOString()
});
print('Session Token: ' + sessionToken);
"

# Testar autenticação
SESSION_TOKEN="seu_token_aqui"
curl -H "Authorization: Bearer $SESSION_TOKEN" \
  https://themisbot.preview.emergentagent.com/api/auth/me

# Testar consulta
curl -X POST \
  -H "Authorization: Bearer $SESSION_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"domain":"civil","question":"Quais os direitos do consumidor?"}' \
  https://themisbot.preview.emergentagent.com/api/consultation
```

### Teste Automatizado

O arquivo `/app/backend_test.py` contém suite completa de testes:

```bash
python3 /app/backend_test.py
```

## 🎨 Design System

### Paleta de Cores

```css
--gold: #D4AF37;          /* Dourado - CTAs, badges, destaques */
--navy: #001F3F;          /* Azul Marinho - Títulos, textos principais */
--white: #FFFFFF;         /* Branco - Backgrounds */
--gray-bg: #F5F7FA;       /* Cinza claro - Backgrounds secundários */
--gray-text: #6B7280;     /* Cinza - Textos secundários */
--gray-border: #E5E7EB;   /* Cinza - Bordas */
```

### Tipografia

```css
/* Títulos */
font-family: 'Playfair Display', serif;
font-weight: 700;

/* Corpo de texto */
font-family: 'Inter', sans-serif;
font-weight: 400-600;
```

### Hierarquia de Texto

```css
H1 (Hero): clamp(2.5rem, 5vw, 4rem)
H2 (Sections): clamp(2rem, 4vw, 3rem)
H3 (Cards): 1.5rem
Body: 1rem (base: 0.9rem mobile)
Small: 0.85rem
```

## 🔒 Segurança e Compliance

### LGPD
- ✅ Coleta mínima de dados (email, nome, foto do Google)
- ✅ Consentimento explícito no login Google
- ✅ Direito de remoção (logout deleta sessão)
- ✅ Aviso legal em todas consultas
- ✅ Logs de auditoria (timestamps em todas collections)

### Segurança
- ✅ HTTPS obrigatório
- ✅ Cookies httpOnly, Secure, SameSite=None
- ✅ JWT para sessões
- ✅ Rate limiting 60 req/min por IP
- ✅ Validação de inputs com Pydantic
- ✅ CORS configurável
- ✅ Secrets em variáveis de ambiente

## 📊 Métricas e Monitoramento

### Health Check

```bash
curl https://themisbot.preview.emergentagent.com/api/health
```

Retorna:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-29T20:44:05Z",
  "version": "2.0.0"
}
```

### Logs

```bash
# Backend logs
tail -f /var/log/supervisor/backend.out.log
tail -f /var/log/supervisor/backend.err.log

# Frontend logs
tail -f /var/log/supervisor/frontend.out.log

# MongoDB logs
sudo tail -f /var/log/mongodb/mongod.log
```

## 🎯 Próximos Passos Sugeridos

### Melhorias de Produto
1. **Exportação de Consultas**: PDF, DOCX
2. **Favoritos**: Marcar consultas importantes
3. **Compartilhamento**: Link público de consultas
4. **Notificações**: Email com resumo das consultas
5. **API Pública**: Para integrações externas

### Melhorias Técnicas
1. **Cache Redis**: Para respostas frequentes
2. **Queue System**: Celery para consultas longas
3. **Elasticsearch**: Busca avançada no histórico
4. **Analytics**: Mixpanel/Amplitude
5. **Testes E2E**: Playwright/Cypress completo
6. **CI/CD**: GitHub Actions
7. **Docker**: Containerização completa
8. **Kubernetes**: Deploy escalável

### Compliance
1. **LGPD Completo**: Portal de privacidade
2. **Termos de Uso**: Página dedicada
3. **Política de Privacidade**: Página dedicada
4. **Backups Automatizados**: MongoDB Atlas
5. **Disaster Recovery**: Plano documentado

## 📞 Suporte

- **URL da Aplicação**: https://themisbot.preview.emergentagent.com
- **Backend API**: https://themisbot.preview.emergentagent.com/api
- **Documentação API**: /api/docs (FastAPI auto-generated)

## 📝 Notas Importantes

1. **Aviso Legal**: Toda consulta inclui disclaimer: "Este conteúdo não constitui consultoria jurídica vinculativa. Recomenda-se consultar um advogado para análise específica do seu caso."

2. **Rate Limiting**: 60 requisições por minuto por IP. Usuários premium não têm limite de consultas.

3. **Tokens Balance**: Usuários gratuitos começam com 3 tokens. Cada consulta consome 1 token. Premium tem 999999 tokens (ilimitado na prática).

4. **Session Duration**: Sessions expiram em 7 dias. Renovação automática ao fazer login.

5. **Payment Polling**: Frontend deve fazer polling do status de pagamento por até 10 segundos (5 tentativas x 2s).

---

**Desenvolvido com ❤️ para revolucionar o acesso à justiça no Brasil**

*Versão 2.0.0 - Novembro 2025*
