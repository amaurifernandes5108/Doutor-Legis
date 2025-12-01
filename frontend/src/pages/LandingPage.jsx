import { useState } from "react";
import axios from "axios";
import Footer from "@/components/Footer";
import "./LandingPage.css";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function LandingPage() {
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/auth/google-login`);
      window.location.href = response.data.auth_url;
    } catch (error) {
      console.error("Login error:", error);
      setLoading(false);
    }
  };

  return (
    <div className="landing-page">
      {/* Themis Watermark */}
      <div className="themis-watermark"></div>

      {/* Header */}
      <header className="landing-header">
        <div className="container">
          <div className="logo">
            <svg width="40" height="40" viewBox="0 0 40 40" fill="none">
              <path d="M20 5L30 15L20 25L10 15L20 5Z" fill="#D4AF37"/>
              <path d="M20 15L30 25L20 35L10 25L20 15Z" fill="#001F3F"/>
            </svg>
            <span>Doutor Legis 2.0</span>
          </div>
          <button 
            className="btn btn-secondary" 
            onClick={handleLogin}
            disabled={loading}
            data-testid="header-login-btn"
          >
            {loading ? "Carregando..." : "Entrar"}
          </button>
        </div>
      </header>

      {/* Hero Section */}
      <section className="hero">
        <div className="container">
          <h1 data-testid="hero-title">
            Sua Assistência Jurídica<br/>
            Inteligente no Brasil
          </h1>
          <p className="hero-subtitle" data-testid="hero-subtitle">
            Análises jurídicas precisas com IA, baseadas na legislação brasileira<br/>
            e jurisprudência dos tribunais superiores
          </p>
          <div className="hero-cta">
            <button 
              className="btn btn-primary" 
              onClick={handleLogin}
              disabled={loading}
              data-testid="hero-cta-btn"
            >
              {loading ? "Carregando..." : "Começar Agora — 3 Consultas Grátis"}
            </button>
          </div>
          <div className="hero-trust">
            <span>✓ Baseado em legislação atual</span>
            <span>✓ 13 domínios jurídicos ULTRA</span>
            <span>✓ Análise em segundos</span>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="features">
        <div className="container">
          <h2 data-testid="features-title">Por que escolher o Doutor Legis?</h2>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">⚖️</div>
              <h3>13 Núcleos Jurídicos ULTRA</h3>
              <p>Constitucional, Civil, Consumidor, Imobiliário, Público, Trabalhista, Empresarial, Internacional, Ética OAB, Penal, Tributário, Previdenciário e Tecnologia</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">📚</div>
              <h3>Legislação Atualizada</h3>
              <p>Análises baseadas nas leis e códigos vigentes do Brasil</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">⚡</div>
              <h3>Respostas Rápidas</h3>
              <p>Análise completa em segundos, com 8 seções detalhadas</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🔒</div>
              <h3>Seguro e Privado</h3>
              <p>Suas consultas são protegidas e confidenciais</p>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section className="pricing">
        <div className="container">
          <h2 data-testid="pricing-title">Planos</h2>
          <div className="pricing-grid-4">
            <div className="pricing-card">
              <h3>Gratuito</h3>
              <div className="price">R$ 0<span>/mês</span></div>
              <ul>
                <li>✓ 3 consultas por mês</li>
                <li>✓ 1 domínio (Ética OAB)</li>
                <li>✓ Análise em 8 seções</li>
                <li>✓ Base conhecimento OAB</li>
              </ul>
              <button className="btn btn-secondary" onClick={handleLogin} data-testid="free-plan-btn">
                Começar Grátis
              </button>
            </div>

            <div className="pricing-card">
              <h3>Básico</h3>
              <div className="price">R$ 197<span>/mês</span></div>
              <p className="price-annual">R$ 1.773/ano (25% OFF)</p>
              <ul>
                <li>✓ 30 consultas/mês</li>
                <li>✓ 5 PDFs/mês</li>
                <li>✓ 3 domínios jurídicos</li>
                <li>✓ PDF simples</li>
                <li>✓ Suporte email (72h)</li>
                <li>✓ Trial 14 dias</li>
              </ul>
              <button className="btn btn-secondary" onClick={handleLogin} data-testid="basic-plan-btn">
                Assinar Básico
              </button>
            </div>

            <div className="pricing-card featured">
              <div className="badge">Recomendado</div>
              <h3>Intermediário</h3>
              <div className="price">R$ 497<span>/mês</span></div>
              <p className="price-annual">R$ 4.476/ano (25% OFF)</p>
              <ul>
                <li>✓ 150 consultas/mês</li>
                <li>✓ 25 PDFs/mês</li>
                <li>✓ 13 núcleos ULTRA (TODOS)</li>
                <li>✓ PDF profissional + Word</li>
                <li>✓ Dashboard avançado</li>
                <li>✓ Suporte email (24h)</li>
                <li>✓ Trial 14 dias</li>
              </ul>
              <button className="btn btn-primary" onClick={handleLogin} data-testid="intermediate-plan-btn">
                Assinar Intermediário
              </button>
            </div>

            <div className="pricing-card premium">
              <div className="badge premium-badge">Ilimitado</div>
              <h3>Avançado</h3>
              <div className="price">R$ 997<span>/mês</span></div>
              <p className="price-annual">R$ 8.976/ano (30% OFF)</p>
              <ul>
                <li>✓ Consultas ILIMITADAS</li>
                <li>✓ PDFs ILIMITADOS</li>
                <li>✓ 9 domínios (TODOS)</li>
                <li>✓ Histórico permanente</li>
                <li>✓ Suporte total (chat + email + tel)</li>
                <li>✓ Account Manager</li>
                <li>✓ API access</li>
                <li>✓ SLA 99.9%</li>
              </ul>
              <button className="btn btn-primary" onClick={handleLogin} data-testid="advanced-plan-btn">
                Contratar Avançado
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="landing-footer">
        <div className="container">
          <p className="disclaimer">
            Este serviço não constitui consultoria jurídica vinculativa.<br/>
            Recomenda-se sempre consultar um advogado para análises específicas.
          </p>
        </div>
      </footer>
      
      <Footer />
    </div>
  );
}

export default LandingPage;
