import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import 'bootstrap/dist/css/bootstrap.min.css';
import './index.css';
import App from './App.jsx';
import { CartProvider } from './context/CartContext'; // 1. Import

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <CartProvider> {/* 2. Wrap App */}
      <App />
    </CartProvider>
  </StrictMode>,
);
