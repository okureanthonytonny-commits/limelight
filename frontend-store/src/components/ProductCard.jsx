import { Card, Button, Badge } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { useCart } from '../context/CartContext'; // Updated path

function ProductCard({ product }) {
    const { addToCart } = useCart();
  return (
    <Card className="h-100 shadow-sm border-0 position-relative">
    {/* Product number badge, if no products, sold out */}
      <Badge
        bg={product.stock === 0 ? "secondary" : "primary"}
        className="position-absolute top-0 end-0 m-2"
      >
        {product.stock === 0 ? "Sold out" : `${product.stock} Left`}
      </Badge>

      <Card.Img
        variant="top"
        src={product.image_url}  // Changed from product.image to product.image_url for API compatibility
        alt={product.name}
        style={{ height: '250px', objectFit: 'cover' }}
      />

      <Card.Body className="d-flex flex-column">
        <Card.Title className="fs-6 fw-bold text-truncate">{product.name}</Card.Title>
        <Card.Text className="text-muted mb-2">
          ${product.price.toFixed(2)}
        </Card.Text>

        <div className="mt-auto d-grid gap-2">
          <Button
            as={Link}
            to={`/product/${product.id}`}  // Assuming existing ProductDetail.jsx uses this path
            variant="outline-dark"
            size="sm"
          >
            View Details
          </Button>
            {/* onClick handler */}
            <Button
            variant="dark"
            size="sm"
            disabled={product.stock === 0}
            onClick={() => addToCart(product)}  // Add to cart using context
            >
            Add to Cart
            </Button>
        </div>
      </Card.Body>
    </Card>  );
}

export default ProductCard;