import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCart } from '../context/CartContext'; // Updated to use context

export default function Cart() {
  const { cart, removeFromCart, updateQuantity, clearCart } = useCart(); // Use context
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const total = cart.reduce((sum, item) => sum + (item.product.price * item.quantity), 0); // Use quantity

  const handleCheckout = async () => {
    if (cart.length === 0) {
      setError('Cart is empty');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await fetch('http://localhost:8000/api/store/orders', {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to place order');
      }

      const order = await response.json();
      
      // Clear cart after successful order
      clearCart();
      
      // Redirect to order confirmation
      navigate(`/order-confirmation/${order.id}`, {
        state: { order }
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (cart.length === 0) {
    return (
      <div className="cart-container">
        <h1>Your Cart</h1>
        <p className="empty-cart">Your cart is empty</p>
        <button onClick={() => navigate('/products')}>Continue Shopping</button>
      </div>
    );
  }

  return (
    <div className="cart-container">
      <h1>Your Cart</h1>
      
      {error && <div className="error-message">{error}</div>}
      
      <div className="cart-items">
        {cart.map(item => (
          <div key={item.product_id} className="cart-item"> {/* Use product_id */}
            <div className="item-details">
              <h3>{item.product.name}</h3>
              <p className="price">${item.product.price.toFixed(2)}</p>
            </div>
            
            <div className="quantity-control">
              <button 
                onClick={() => updateQuantity(item.product_id, Math.max(1, item.quantity - 1))}
                disabled={item.quantity <= 1}
              >
                -
              </button>
              <span>{item.quantity}</span> {/* Use quantity */}
              <button 
                onClick={() => updateQuantity(item.product_id, item.quantity + 1)}
              >
                +
              </button>
            </div>
            
            <div className="item-total">
              ${(item.product.price * item.quantity).toFixed(2)} {/* Use quantity */}
            </div>
            
            <button 
              className="remove-btn"
              onClick={() => removeFromCart(item.product_id)}
            >
              Remove
            </button>
          </div>
        ))}
      </div>
      
      <div className="cart-summary">
        <div className="summary-row">
          <span>Subtotal:</span>
          <span>${total.toFixed(2)}</span>
        </div>
        <div className="summary-row total">
          <span>Total:</span>
          <span>${total.toFixed(2)}</span>
        </div>
      </div>
      
      <div className="cart-actions">
        <button 
          onClick={() => navigate('/products')}
          className="btn-secondary"
        >
          Continue Shopping
        </button>
        
        <button 
          onClick={handleCheckout}
          className="btn-primary"
          disabled={loading || cart.length === 0}
        >
          {loading ? 'Processing...' : 'Checkout'}
        </button>
      </div>
    </div>
  );
}
