import { useState, useEffect, useRef } from "react";
import axios from "axios";
import { toast } from "sonner";
import Footer from "@/components/Footer";
import "./Dashboard.css";
import { Search, Send, LogOut, Crown, Loader2, Menu, X } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function Dashboard({ user, setUser }) {
  const [domains, setDomains] = useState([]);
  const [selectedDomain, setSelectedDomain] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const chatEndRef = useRef(null);

  useEffect(() => {
    fetchDomains();
    fetchHistory();
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const fetchDomains = async () => {
    try {
      const response = await axios.get(`${API}/domains`);
      setDomains(response.data);
      if (response.data.length > 0) {
        setSelectedDomain(response.data[0]);
      }
    } catch (error) {
      console.error("Error fetching domains:", error);
      toast.error("Erro ao carregar domínios");
    }
  };

  const fetchHistory = async () => {
    try {
      const response = await axios.get(`${API}/history`, {
        withCredentials: true
      });
      setHistory(response.data);
    } catch (error) {
      console.error("Error fetching history:", error);
    }
  };

  const handleLogout = async () => {
    try {
      await axios.post(`${API}/auth/logout`, {}, {
        withCredentials: true
      });
      window.location.href = "/";
    } catch (error) {
      console.error("Logout error:", error);
    }
  };

  const handleUpgrade = async () => {
    try {
      const origin = window.location.origin;
      const response = await axios.post(
        `${API}/payments/checkout`,
        {
          package_id: "premium_monthly",
          origin_url: origin
        },
        { withCredentials: true }
      );
      
      window.location.href = response.data.checkout_url;
    } catch (error) {
      console.error("Upgrade error:", error);
      toast.error("Erro ao processar upgrade");
    }
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || !selectedDomain) return;
    
    if (user.token_balance < 1 && user.plan === "gratuito") {
      toast.error("Saldo insuficiente! Assine o plano Premium.");
      return;
    }

    const userMessage = inputMessage.trim();
    setInputMessage("");
    setMessages(prev => [...prev, { role: "user", content: userMessage }]);
    setLoading(true);

    try {
      // ULTRA: Classificar pergunta automaticamente (sugerir domínio)
      let dominioFinal = selectedDomain.id;
      try {
        const classResponse = await axios.post(
          `${API}/domains/classificar?pergunta=${encodeURIComponent(userMessage)}`
        );
        
        if (classResponse.data.confianca > 80 && 
            classResponse.data.dominio_sugerido !== selectedDomain.id) {
          const domSugerido = domains.find(d => d.id === classResponse.data.dominio_sugerido);
          if (domSugerido) {
            toast.info(`💡 Router Inteligente sugere: ${domSugerido.name}`);
          }
        }
      } catch (err) {
        console.log("Router classification optional error:", err);
      }

      const response = await axios.post(
        `${API}/consultation`,
        {
          domain: dominioFinal,
          question: userMessage
        },
        {
          withCredentials: true
        }
      );

      setMessages(prev => [
        ...prev,
        {
          role: "assistant",
          content: response.data.response,
          metadata: {
            confidence: response.data.confidence,
            tokens_used: response.data.tokens_used,
            processing_time: response.data.processing_time
          }
        }
      ]);

      // Update user token balance
      if (user.plan === "gratuito") {
        setUser(prev => ({ ...prev, token_balance: prev.token_balance - 1 }));
      }

      fetchHistory();
      toast.success("Consulta realizada com sucesso!");
    } catch (error) {
      console.error("Consultation error:", error);
      const errorMsg = error.response?.data?.detail || "Erro ao processar consulta";
      toast.error(errorMsg);
      setMessages(prev => prev.slice(0, -1)); // Remove user message on error
    } finally {
      setLoading(false);
    }
  };

  const handleFeedback = async (consultaId, rating) => {
    try {
      await axios.post(
        `${API}/feedback`,
        {
          consulta_id: consultaId,
          rating: rating
        },
        { withCredentials: true }
      );
      toast.success("Obrigado pelo feedback!");
    } catch (error) {
      console.error("Feedback error:", error);
    }
  };

  const filteredDomains = domains.filter(domain =>
    domain.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="dashboard" data-testid="dashboard-container">
      {/* Mobile Menu Button */}
      <button
        className="mobile-menu-btn"
        onClick={() => setSidebarOpen(!sidebarOpen)}
        data-testid="mobile-menu-btn"
      >
        {sidebarOpen ? <X size={24} /> : <Menu size={24} />}
      </button>

      {/* Sidebar - Domains */}
      <aside className={`sidebar ${sidebarOpen ? 'open' : ''}`} data-testid="sidebar">
        <div className="sidebar-header">
          <div className="logo-mini">
            <svg width="32" height="32" viewBox="0 0 40 40" fill="none">
              <path d="M20 5L30 15L20 25L10 15L20 5Z" fill="#D4AF37"/>
              <path d="M20 15L30 25L20 35L10 25L20 15Z" fill="#001F3F"/>
            </svg>
            <span>Doutor Legis</span>
          </div>
        </div>

        <div className="sidebar-search">
          <Search size={18} />
          <input
            type="text"
            placeholder="Buscar domínio..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            data-testid="domain-search-input"
          />
        </div>

        <div className="domains-list">
          {filteredDomains.map((domain) => (
            <button
              key={domain.id}
              className={`domain-item ${selectedDomain?.id === domain.id ? 'active' : ''}`}
              onClick={() => {
                setSelectedDomain(domain);
                setSidebarOpen(false);
              }}
              data-testid={`domain-item-${domain.id}`}
            >
              <div className="domain-name">{domain.name}</div>
              <div className="domain-accuracy">{domain.accuracy}%</div>
            </button>
          ))}
        </div>

        <div className="sidebar-footer">
          <div className="history-section">
            <h4>Histórico Recente</h4>
            {history.slice(0, 5).map((item) => (
              <div key={item.id} className="history-item" data-testid={`history-item-${item.id}`}>
                <span className="history-domain">{item.domain}</span>
                <span className="history-question">{item.question}</span>
              </div>
            ))}
          </div>
        </div>
      </aside>

      {/* Main Chat Area */}
      <main className="main-chat" data-testid="main-chat">
        <div className="chat-header">
          <div>
            <h2 data-testid="selected-domain-name">         {selectedDomain?.name || "Selecione um domínio"}
            </h2>
            <p className="domain-subtitle">{selectedDomain?.legislation}</p>
          </div>
          <div className="user-info">
            <div className="user-avatar" data-testid="user-avatar">
              {user.picture ? (
                <img src={user.picture} alt={user.name} />
              ) : (
                <div className="avatar-placeholder">{user.name[0]}</div>
              )}
            </div>
            <div className="user-details">
              <span className="user-name" data-testid="user-name">{user.name}</span>
              <span className="user-plan" data-testid="user-plan">
                {user.plan === "premium" ? (
                  <><Crown size={14} /> Premium</>
                ) : (
                  `${user.token_balance} consultas restantes`
                )}
              </span>
            </div>
            <button className="logout-btn" onClick={handleLogout} data-testid="logout-btn">
              <LogOut size={18} />
            </button>
          </div>
        </div>

        <div className="chat-messages" data-testid="chat-messages">
          {messages.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">⚖️</div>
              <h3>Bem-vindo ao Doutor Legis 2.0</h3>
              <p>
                Faça sua pergunta jurídica e receba uma análise completa com<br />
                legislação aplicável, jurisprudência e recomendações.
              </p>
            </div>
          ) : (
            messages.map((msg, idx) => (
              <div key={idx} className={`message ${msg.role}`} data-testid={`message-${msg.role}-${idx}`}>
                {msg.role === "user" ? (
                  <div className="message-content">{msg.content}</div>
                ) : (
                  <div className="assistant-response">
                    <div className="response-section">
                      <h4>📝 Resumo</h4>
                      <p>{msg.content.resumo}</p>
                    </div>
                    <div className="response-section">
                      <h4>📜 Legislação Aplicável</h4>
                      <p>{msg.content.legislacao_aplicavel}</p>
                    </div>
                    <div className="response-section">
                      <h4>⚖️ Jurisprudência</h4>
                      <p>{msg.content.jurisprudencia}</p>
                    </div>
                    <div className="response-section">
                      <h4>🔍 Análise Legal</h4>
                      <p>{msg.content.analise_legal}</p>
                    </div>
                    <div className="response-section">
                      <h4>⚠️ Riscos Jurídicos</h4>
                      <p>{msg.content.riscos_juridicos}</p>
                    </div>
                    <div className="response-section">
                      <h4>💡 Recomendações</h4>
                      <p>{msg.content.recomendacoes}</p>
                    </div>
                    <div className="response-section disclaimer">
                      <h4>👉 Próximos Passos</h4>
                      <p>{msg.content.proximos_passos}</p>
                    </div>
                    {msg.metadata && (
                      <div className="response-metadata">
                        <span className="confidence-badge">
                          Confiança: {msg.metadata.confidence}%
                        </span>
                        <span className="metadata-item">
                          {msg.metadata.processing_time}s
                        </span>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))
          )}
          {loading && (
            <div className="message assistant" data-testid="loading-message">
              <div className="loading-indicator">
                <Loader2 className="spin" size={20} />
                <span>Analisando sua questão...</span>
              </div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        <div className="chat-input-area">
          <div className="input-wrapper">
            <input
              type="text"
              placeholder="Digite sua questão jurídica..."
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && !loading && handleSendMessage()}
              disabled={loading}
              data-testid="chat-input"
            />
            <button
              onClick={handleSendMessage}
              disabled={loading || !inputMessage.trim()}
              className="send-btn"
              data-testid="send-message-btn"
            >
              <Send size={20} />
            </button>
          </div>
        </div>
      </main>

      {/* Right Panel - Domain Info */}
      <aside className="right-panel" data-testid="right-panel">
        {selectedDomain ? (
          <>
            <div className="panel-section">
              <h3>Informações do Domínio</h3>
              <div className="info-card">
                <div className="info-row">
                  <span className="info-label">Domínio:</span>
                  <span className="info-value">{selectedDomain.name}</span>
                </div>
                <div className="info-row">
                  <span className="info-label">Legislação:</span>
                  <span className="info-value">{selectedDomain.legislation}</span>
                </div>
                <div className="info-row">
                  <span className="info-label">Corte:</span>
                  <span className="info-value">{selectedDomain.court}</span>
                </div>
                <div className="info-row">
                  <span className="info-label">Acurácia:</span>
                  <span className="info-value accuracy">{selectedDomain.accuracy}%</span>
                </div>
              </div>
            </div>

            <div className="panel-section">
              <h3>Seu Plano</h3>
              <div className="plan-card">
                {user.plan === "premium" ? (
                  <>
                    <div className="plan-badge premium">
                      <Crown size={20} />
                      <span>Premium</span>
                    </div>
                    <p className="plan-description">
                      Consultas ilimitadas<br />
                      Acesso total a todos domínios
                    </p>
                  </>
                ) : (
                  <>
                    <div className="plan-badge free">Gratuito</div>
                    <p className="plan-description">
                      {user.token_balance} consultas restantes
                    </p>
                    <button className="upgrade-btn" onClick={handleUpgrade} data-testid="upgrade-btn">
                      <Crown size={18} />
                      Fazer Upgrade para Premium
                    </button>
                    <p className="plan-price">R$ 497/mês</p>
                  </>
                )}
              </div>
            </div>

            <div className="panel-section">
              <h3>Como Funciona</h3>
              <div className="help-card">
                <div className="help-step">
                  <span className="step-number">1</span>
                  <p>Selecione um domínio jurídico</p>
                </div>
                <div className="help-step">
                  <span className="step-number">2</span>
                  <p>Descreva sua questão em detalhes</p>
                </div>
                <div className="help-step">
                  <span className="step-number">3</span>
                  <p>Receba análise completa em 8 seções</p>
                </div>
              </div>
            </div>

            <div className="panel-section" style={{marginTop: 'auto'}}>
              <Footer />
            </div>
          </>
        ) : (
          <div className="panel-placeholder">
            <p>Selecione um domínio para começar</p>
          </div>
        )}
      </aside>
    </div>
  );
}

export default Dashboard;
