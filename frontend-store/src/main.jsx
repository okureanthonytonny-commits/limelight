import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import 'bootstrap/dist/css/bootstrap.min.css';
import { CartProvider } from './context/CartContext.jsx' // Added CartProvider import
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <CartProvider>  {/* Wrapped App with CartProvider for global cart state */}
      <App />
    </CartProvider>
  </StrictMode>,
)
