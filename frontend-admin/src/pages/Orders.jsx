import React, { useState, useEffect } from 'react';
import '../styles/Orders.css';

export default function Orders() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [expandedOrder, setExpandedOrder] = useState(null);

  useEffect(() => {
    fetchOrders();
  }, []);

  const fetchOrders = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/admin/orders', {
        credentials: 'include',
      });

      if (!response.ok) {
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

  const handleStatusChange = async (orderId, newStatus) => {
    try {
      const response = await fetch(
        `http://localhost:8000/api/admin/orders/${orderId}/status`,
        {
          method: 'PATCH',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ status: newStatus }),
        }
      );

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to update order status');
      }

      const updatedOrder = await response.json();
      setOrders(orders.map(o => o.id === orderId ? updatedOrder : o));
    } catch (err) {
      alert(err.message);
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

  const getValidTransitions = (currentStatus) => {
    const transitions = {
      'pending': ['confirmed', 'cancelled'],
      'confirmed': ['shipped', 'cancelled'],
      'shipped': ['delivered'],
      'delivered': [],
      'cancelled': [],
    };
    return transitions[currentStatus] || [];
  };

  if (loading) {
    return <div className="admin-orders-container">Loading orders...</div>;
  }

  if (error) {
    return (
      <div className="admin-orders-container">
        <p className="error-message">{error}</p>
        <button onClick={fetchOrders}>Retry</button>
      </div>
    );
  }

  if (orders.length === 0) {
    return (
      <div className="admin-orders-container">
        <h1>Orders</h1>
        <p>No orders yet</p>
      </div>
    );
  }

  return (
    <div className="admin-orders-container">
      <h1>Order Management</h1>
      
      <table className="orders-table">
        <thead>
          <tr>
            <th>Order ID</th>
            <th>User ID</th>
            <th>Status</th>
            <th>Items</th>
            <th>Total</th>
            <th>Date</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {orders.map(order => {
            const total = order.items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
            const isExpanded = expandedOrder === order.id;
            
            return (
              <React.Fragment key={order.id}>
                <tr className={isExpanded ? 'expanded' : ''}>
                  <td>#{order.id}</td>
                  <td>{order.user_id}</td>
                  <td>
                    <span 
                      className="status-badge"
                      style={{ backgroundColor: getStatusColor(order.status) }}
                    >
                      {order.status}
                    </span>
                  </td>
                  <td>{order.items.length}</td>
                  <td>${total.toFixed(2)}</td>
                  <td>{new Date(order.created_at).toLocaleDateString()}</td>
                  <td>
                    <button 
                      className="expand-btn"
                      onClick={() => setExpandedOrder(isExpanded ? null : order.id)}
                    >
                      {isExpanded ? '−' : '+'}
                    </button>
                  </td>
                </tr>
                
                {isExpanded && (
                  <tr className="expanded-row">
                    <td colSpan="7">
                      <div className="order-details">
                        <div className="items-list">
                          <h4>Items:</h4>
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
                                  <td>{item.product_id}</td>
                                  <td>{item.quantity}</td>
                                  <td>${item.price.toFixed(2)}</td>
                                  <td>${(item.price * item.quantity).toFixed(2)}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                        
                        <div className="status-control">
                          <h4>Update Status:</h4>
                          <div className="status-buttons">
                            {getValidTransitions(order.status).map(status => (
                              <button
                                key={status}
                                className="status-btn"
                                onClick={() => handleStatusChange(order.id, status)}
                              >
                                Mark as {status.charAt(0).toUpperCase() + status.slice(1)}
                              </button>
                            ))}
                            {getValidTransitions(order.status).length === 0 && (
                              <p className="no-transitions">No valid status transitions</p>
                            )}
                          </div>
                        </div>
                      </div>
                    </td>
                  </tr>
                )}
              </React.Fragment>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
