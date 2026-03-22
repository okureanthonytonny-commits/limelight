import { Container, Row, Col } from 'react-bootstrap';
import HeroSection from '../components/HeroSection';
import ProductCard from '../components/ProductCard';
import { mockProducts } from '../data/mockProducts';

function Home() {
  const featuredProducts = mockProducts.slice(0, 3);

  return (
    <>
      <HeroSection />
      <Container>
        <h2 className="mb-4 fw-bold">New Arrivals</h2>
        <Row>
          {featuredProducts.map((product) => (
            <Col key={product.id} sm={12} md={4} className="mb-4">
              <ProductCard product={product} />
            </Col>
          ))}
        </Row>
      </Container>
    </>
  );
}

export default Home;