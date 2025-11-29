import { useEffect, useState } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route, Navigate, useNavigate, useLocation } from "react-router-dom";
import axios from "axios";
import LandingPage from "@/pages/LandingPage";
import Dashboard from "@/pages/Dashboard";
import PaymentSuccess from "@/pages/PaymentSuccess";
import { Toaster } from "@/components/ui/sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function AuthHandler() {
  const navigate = useNavigate();
  const location = useLocation();
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState(null);

  useEffect(() => {
    const handleAuth = async () => {
      // Check for session_id in URL fragment
      const hash = window.location.hash;
      if (hash && hash.includes("session_id=")) {
        const sessionId = hash.split("session_id=")[1].split("&")[0];
        
        try {
          // Process session with backend
          const response = await axios.post(
            `${API}/auth/session`,
            {},
            {
              headers: { "X-Session-ID": sessionId },
              withCredentials: true
            }
          );
          
          setUser(response.data.user);
          
          // Clean URL
          window.history.replaceState(null, "", window.location.pathname);
          
          // Navigate to dashboard
          navigate("/dashboard", { replace: true });
        } catch (error) {
          console.error("Auth error:", error);
          setLoading(false);
        }
        return;
      }
      
      // Check existing session
      try {
        const response = await axios.get(`${API}/auth/me`, {
          withCredentials: true
        });
        setUser(response.data);
        
        // If on landing page, redirect to dashboard
        if (location.pathname === "/") {
          navigate("/dashboard", { replace: true });
        }
      } catch (error) {
        // No valid session
        setUser(null);
      } finally {
        setLoading(false);
      }
    };
    
    handleAuth();
  }, [navigate, location]);

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="spinner"></div>
        <p>Carregando...</p>
      </div>
    );
  }

  return (
    <Routes>
      <Route path="/" element={user ? <Navigate to="/dashboard" replace /> : <LandingPage />} />
      <Route
        path="/dashboard"
        element={user ? <Dashboard user={user} setUser={setUser} /> : <Navigate to="/" replace />}
      />
      <Route
        path="/payment-success"
        element={user ? <PaymentSuccess user={user} /> : <Navigate to="/" replace />}
      />
    </Routes>
  );
}

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <AuthHandler />
      </BrowserRouter>
      <Toaster />
    </div>
  );
}

export default App;
