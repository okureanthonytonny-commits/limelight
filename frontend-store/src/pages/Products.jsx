import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Spinner, Alert } from 'react-bootstrap';
import ProductCard from '../components/ProductCard'; // Added import for ProductCard

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function Products() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    try {
      const response = await fetch(`${API_URL}/api/store/products`);
      if (!response.ok) throw new Error('Failed to fetch products');
      const data = await response.json();
      setProducts(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <Spinner animation="border" />;
  if (error) return <Alert variant="danger">{error}</Alert>;

  return (
    <Container className="py-5">
      <h1 className="mb-4">Our Products</h1>
      <Row xs={1} sm={2} lg={3} className="g-4">
        {products.map(product => (
          <Col key={product.id}>
            <ProductCard product={product} /> {/* Replaced inline card with ProductCard component */}
          </Col>
        ))}
      </Row>
    </Container>
  );
}
