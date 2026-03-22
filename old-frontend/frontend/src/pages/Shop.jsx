import { Container, Row, Col } from 'react-bootstrap';
import ProductCard from '../components/ProductCard';
import { mockProducts } from '../data/mockProducts';

function Shop() {
  return (
    <Container className="py-5">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2 className="fw-bold">All Products</h2>
        <span className="text-muted">{mockProducts.length} Items Found</span>
      </div>
      
      <Row>
        {mockProducts.map((product) => (
          <Col key={product.id} xs={6} md={4} lg={3} className="mb-4">
            <ProductCard product={product} />
          </Col>
        ))}
      </Row>
    </Container>
  );
}

export default Shop;