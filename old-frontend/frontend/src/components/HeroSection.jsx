import { Container, Button } from 'react-bootstrap';
import { Link } from 'react-router-dom';

function HeroSection() {
  return (
    <div className="bg-dark text-white text-center py-5 mb-5 rounded shadow-sm">
      <Container>
        <h1 className="display-4 fw-bold mb-3">Upgrade Your Style</h1>
        <p className="lead mb-4">Discover the latest trends in fashion and accessories.</p>
        <Button as={Link} to="/shop" variant="light" size="lg" className="fw-bold">
          Shop New Arrivals
        </Button>
      </Container>
    </div>
  );
}

export default HeroSection;