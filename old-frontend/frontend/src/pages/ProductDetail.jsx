import { useParams, useNavigate } from 'react-router-dom';
import { Container, Row, Col, Button, Image, Badge } from 'react-bootstrap';
import { mockProducts } from '../data/mockProducts';
import { useCart } from '../context/CartContext';

function ProductDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { addToCart } = useCart();
  
  // Find the exact product from mock data using id
  const product = mockProducts.find((p) => p.id === parseInt(id));

  if (!product) {
    return <Container className="mt-5 text-center"><h3>Product not found</h3></Container>;
  }

  return (
    <Container className="py-5">
    {/* Back Button */}
      <Button 
        variant="outline-dark" 
        onClick={() => navigate(-1)} 
        className="mb-4"
        aria-label="Go back"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
          <path fillRule="evenodd" d="M15 8a.5.5 0 0 0-.5-.5H2.707l3.147-3.146a.5.5 0 1 0-.708-.708l-4 4a.5.5 0 0 0 0 .708l4 4a.5.5 0 0 0 .708-.708L2.707 8.5H14.5A.5.5 0 0 0 15 8z"/>
        </svg>
      </Button>

      <Row>
        <Col md={6} className="mb-4">
          <Image src={product.image} alt={product.name} fluid rounded className="shadow-sm w-100" />
        </Col>
        
        <Col md={6}>
          <div className="d-flex gap-2 mb-2">
            <Badge bg="secondary">{product.category}</Badge>
            <Badge bg={product.stock === 0 ? "secondary" : "primary"}>
              {product.stock === 0 ? "Sold out" : `${product.stock} Left`}
            </Badge>
          </div>
          <h1 className="fw-bold mb-3">{product.name}</h1>
          <h3 className="text-success mb-4">${product.price.toFixed(2)}</h3>
          
          <hr />
          <p className="lead text-muted mb-4">{product.description}</p>
          
          <div className="d-grid gap-2">
            <Button 
              variant="dark" 
              size="lg" 
              disabled={product.stock === 0}
              onClick={() => addToCart(product)}
            >
              {product.stock > 0 ? 'Add to Cart' : 'Out of Stock'}
            </Button>
          </div>
        </Col>
      </Row>
    </Container>
  );
}

export default ProductDetail;