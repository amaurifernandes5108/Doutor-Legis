import React from 'react';
import './Footer.css';

function Footer() {
  return (
    <footer className="site-footer" data-testid="site-footer">
      <div className="footer-content">
        <p className="footer-copyright">
          © 2025 Doutor Legis 2.0 — Criado e Idealizado por{' '}
          <strong>Amauri Gonçalves Fernandes</strong>.
        </p>
        <p className="footer-rights">Todos os direitos reservados.</p>
      </div>
    </footer>
  );
}

export default Footer;
