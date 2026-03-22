import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

export default function Orders() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchOrders();
  }, []);

  const fetchOrders = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/store/orders', {
        credentials: 'include',
      });

      if (!response.ok) {
        if (response.status === 401) {
          navigate('/login');
          return;
        }
        throw new Error('Failed to fetch orders');
      }

      const data = await response.json();
      setOrders(data);
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
    return <div className="orders-container">Loading orders...</div>;
  }

  if (error) {
    return (
      <div className="orders-container">
        <p className="error-message">{error}</p>
        <button onClick={fetchOrders}>Retry</button>
      </div>
    );
  }

  if (orders.length === 0) {
    return (
      <div className="orders-container">
        <h1>Order History</h1>
        <p className="no-orders">No orders yet</p>
        <button onClick={() => navigate('/products')}>Start Shopping</button>
      </div>
    );
  }

  return (
    <div className="orders-container">
      <h1>Order History</h1>
      
      <div className="orders-list">
        {orders.map(order => (
          <div key={order.id} className="order-card">
            <div className="order-header">
              <div className="order-info">
                <h3>Order #{order.id}</h3>
                <p className="order-date">
                  {new Date(order.created_at).toLocaleDateString()}
                </p>
              </div>
              <div 
                className="order-status"
                style={{ backgroundColor: getStatusColor(order.status) }}
              >
                {order.status.charAt(0).toUpperCase() + order.status.slice(1)}
              </div>
            </div>
            
            <div className="order-items">
              <p className="item-count">{order.items.length} item(s)</p>
              {order.items.map(item => (
                <div key={item.id} className="order-item">
                  <span className="product-id">Product {item.product_id}</span>
                  <span className="qty">x{item.quantity}</span>
                  <span className="price">${(item.price * item.quantity).toFixed(2)}</span>
                </div>
              ))}
            </div>
            
            <div className="order-total">
              Total: $
              {order.items.reduce((sum, item) => sum + (item.price * item.quantity), 0).toFixed(2)}
            </div>
            
            <button 
              className="view-btn"
              onClick={() => navigate(`/order/${order.id}`, { state: { order } })}
            >
              View Details
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
