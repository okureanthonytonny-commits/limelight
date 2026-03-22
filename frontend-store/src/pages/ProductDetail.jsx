import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Button, Alert, Spinner } from 'react-bootstrap';
import { useParams, useNavigate } from 'react-router-dom';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function ProductDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchProduct();
  }, [id]);

  const fetchProduct = async () => {
    try {
      const response = await fetch(`${API_URL}/api/store/products/${id}`);
      if (!response.ok) throw new Error('Product not found');
      const data = await response.json();
      setProduct(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <Spinner animation="border" />;
  if (error) return <Alert variant="danger">{error}</Alert>;
  if (!product) return <Alert variant="warning">Product not found</Alert>;

  return (
    <Container className="py-5">
      <Button variant="secondary" onClick={() => navigate('/products')} className="mb-4">
        ← Back to Products
      </Button>

      <Row>
        <Col md={6}>
          {product.image_url && (
            <Card className="shadow-sm">
              <Card.Img variant="top" src={product.image_url} />
            </Card>
          )}
        </Col>
        <Col md={6}>
          <h1>{product.name}</h1>
          <h2 className="text-primary my-3">${product.price.toFixed(2)}</h2>

          <div className="mb-4">
            <span className={`badge ${product.stock > 0 ? 'bg-success' : 'bg-danger'} fs-6`}>
              {product.stock > 0 ? `${product.stock} in stock` : 'Out of Stock'}
            </span>
          </div>

          <Card className="mb-4">
            <Card.Body>
              <h5>Description</h5>
              <p>{product.description || 'No description available'}</p>
            </Card.Body>
          </Card>

          <Button variant="primary" size="lg" disabled={product.stock === 0} className="w-100 mb-3">
            {product.stock > 0 ? 'Add to Cart' : 'Out of Stock'}
          </Button>

          <Card className="text-muted">
            <Card.Body>
              <small>
                Created: {new Date(product.created_at).toLocaleDateString()}<br />
                Last updated: {new Date(product.updated_at).toLocaleDateString()}
              </small>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
}
