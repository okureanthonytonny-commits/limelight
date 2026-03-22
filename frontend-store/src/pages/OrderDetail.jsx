import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';

export default function OrderDetail() {
  const { orderId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const [order, setOrder] = useState(location.state?.order || null);
  const [loading, setLoading] = useState(!order);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!order) {
      fetchOrder();
    }
  }, [orderId, order]);

  const fetchOrder = async () => {
    try {
      const response = await fetch(
        `http://localhost:8000/api/store/orders/${orderId}`,
        { credentials: 'include' }
      );

      if (!response.ok) {
        if (response.status === 401) {
          navigate('/login');
          return;
        }
        if (response.status === 403) {
          setError('You do not have permission to view this order');
          return;
        }
        throw new Error('Failed to fetch order');
      }

      const data = await response.json();
      setOrder(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      'pending': '#FFA500',
      'confirmed': '#4169E1',
      'shipped': '#20B2AA',
      'delivered': '#32CD32',
      'cancelled': '#DC143C',
    };
    return colors[status] || '#999';
  };

  if (loading) {
    return <div className="order-detail-container">Loading order details...</div>;
  }

  if (error) {
    return (
      <div className="order-detail-container">
        <p className="error-message">{error}</p>
        <button onClick={() => navigate('/orders')}>Back to Orders</button>
      </div>
    );
  }

  if (!order) {
    return (
      <div className="order-detail-container">
        <p>Order not found</p>
        <button onClick={() => navigate('/orders')}>Back to Orders</button>
      </div>
    );
  }

  const orderTotal = order.items.reduce((sum, item) => sum + (item.price * item.quantity), 0);

  return (
    <div className="order-detail-container">
      <button className="back-btn" onClick={() => navigate('/orders')}>← Back to Orders</button>
      
      <div className="order-detail-card">
        <h1>Order #{order.id}</h1>
        
        <div className="order-status-section">
          <div 
            className="status-badge"
            style={{ backgroundColor: getStatusColor(order.status) }}
          >
            {order.status.charAt(0).toUpperCase() + order.status.slice(1)}
          </div>
          
          <div className="order-dates">
            <p>
              <strong>Order Date:</strong> {new Date(order.created_at).toLocaleDateString()}
            </p>
            <p>
              <strong>Last Updated:</strong> {new Date(order.updated_at).toLocaleDateString()}
            </p>
          </div>
        </div>
        
        <div className="order-items-section">
          <h2>Items</h2>
          <table className="items-table">
            <thead>
              <tr>
                <th>Product ID</th>
                <th>Quantity</th>
                <th>Price</th>
                <th>Subtotal</th>
              </tr>
            </thead>
            <tbody>
              {order.items.map(item => (
                <tr key={item.id}>
                  <td>Product #{item.product_id}</td>
                  <td>{item.quantity}</td>
                  <td>${item.price.toFixed(2)}</td>
                  <td>${(item.price * item.quantity).toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        <div className="order-summary">
          <div className="summary-row">
            <span>Subtotal:</span>
            <span>${orderTotal.toFixed(2)}</span>
          </div>
          <div className="summary-row">
            <span>Shipping:</span>
            <span>FREE</span>
          </div>
          <div className="summary-row total">
            <span>Total:</span>
            <span>${orderTotal.toFixed(2)}</span>
          </div>
        </div>
        
        <div className="order-actions">
          <button 
            className="btn-secondary"
            onClick={() => navigate('/products')}
          >
            Continue Shopping
          </button>
          <button 
            className="btn-secondary"
            onClick={() => navigate('/orders')}
          >
            View All Orders
          </button>
        </div>
      </div>
    </div>
  );
}
