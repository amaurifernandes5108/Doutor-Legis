import { useState, useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import axios from "axios";
import { CheckCircle, Loader2, Crown } from "lucide-react";
import "./PaymentSuccess.css";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function PaymentSuccess({ user }) {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState("checking"); // checking, success, error
  const [message, setMessage] = useState("Verificando pagamento...");
  const sessionId = searchParams.get("session_id");

  useEffect(() => {
    if (!sessionId) {
      navigate("/dashboard");
      return;
    }

    checkPaymentStatus();
  }, [sessionId]);

  const checkPaymentStatus = async () => {
    let attempts = 0;
    const maxAttempts = 5;
    const pollInterval = 2000; // 2 seconds

    const poll = async () => {
      if (attempts >= maxAttempts) {
        setStatus("error");
        setMessage("Tempo esgotado ao verificar pagamento. Por favor, verifique seu email.");
        return;
      }

      try {
        const response = await axios.get(
          `${API}/payments/status/${sessionId}`,
          { withCredentials: true }
        );

        if (response.data.payment_status === "paid") {
          setStatus("success");
          setMessage("Pagamento confirmado! Seu plano foi atualizado para Premium.");
          
          // Redirect to dashboard after 3 seconds
          setTimeout(() => {
            navigate("/dashboard");
          }, 3000);
        } else if (response.data.status === "expired") {
          setStatus("error");
          setMessage("Sessão de pagamento expirada. Por favor, tente novamente.");
        } else {
          attempts++;
          setTimeout(poll, pollInterval);
        }
      } catch (error) {
        console.error("Payment status error:", error);
        setStatus("error");
        setMessage("Erro ao verificar pagamento. Por favor, entre em contato com o suporte.");
      }
    };

    poll();
  };

  return (
    <div className="payment-success-page" data-testid="payment-success-page">
      <div className="success-container">
        {status === "checking" && (
          <>
            <Loader2 className="icon spin" size={64} data-testid="payment-loading-icon" />
            <h1>Verificando Pagamento</h1>
            <p>{message}</p>
          </>
        )}

        {status === "success" && (
          <>
            <CheckCircle className="icon success" size={64} data-testid="payment-success-icon" />
            <h1>Pagamento Confirmado!</h1>
            <p>{message}</p>
            <div className="premium-badge">
              <Crown size={24} />
              <span>Bem-vindo ao Premium</span>
            </div>
            <div className="benefits">
              <h3>Seus Benefícios Premium:</h3>
              <ul>
                <li>✓ Consultas jurídicas ilimitadas</li>
                <li>✓ Acesso total a todos os 8 domínios</li>
                <li>✓ Análises detalhadas em 8 seções</li>
                <li>✓ Histórico completo de consultas</li>
                <li>✓ Prioridade no processamento</li>
              </ul>
            </div>
            <button 
              className="btn btn-primary" 
              onClick={() => navigate("/dashboard")}
              data-testid="go-to-dashboard-btn"
            >
              Ir para o Dashboard
            </button>
          </>
        )}

        {status === "error" && (
          <>
            <div className="icon error" data-testid="payment-error-icon">⚠️</div>
            <h1>Erro no Pagamento</h1>
            <p>{message}</p>
            <button 
              className="btn btn-primary" 
              onClick={() => navigate("/dashboard")}
              data-testid="back-to-dashboard-btn"
            >
              Voltar ao Dashboard
            </button>
          </>
        )}
      </div>
    </div>
  );
}

export default PaymentSuccess;
