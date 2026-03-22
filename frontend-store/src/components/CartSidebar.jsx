import { Offcanvas, ListGroup, Button } from 'react-bootstrap';
import { Link } from 'react-router-dom'; // Added for navigation
import { useCart } from '../context/CartContext'; // Updated path

function CartSidebar({ show, handleClose }) {
  const { cart } = useCart();

  // Calculate the total price of all items (now using cartTotal from context, but keeping local for consistency)
  const cartTotal = cart.reduce((total, item) => total + (item.product.price * (item.quantity || item.qty)), 0);

  return (
    <Offcanvas show={show} onHide={handleClose} placement="end">
      <Offcanvas.Header closeButton>
        <Offcanvas.Title>Your Cart</Offcanvas.Title>
      </Offcanvas.Header>

      <Offcanvas.Body className="d-flex flex-column">
        {cart.length === 0 ? (
          <p className="text-muted text-center mt-5">Your cart is empty.</p>
        ) : (
          <ListGroup variant="flush" className="mb-4">
            {cart.map((item, index) => (
              <ListGroup.Item key={index} className="d-flex justify-content-between align-items-center px-0">
                <div>
                  <h6 className="mb-0 fw-bold">{item.product.name}</h6>
                  <small className="text-muted">Qty: {item.quantity || item.qty} x ${item.product.price.toFixed(2)}</small>
                </div>
                <span className="fw-bold">${(item.product.price * (item.quantity || item.qty)).toFixed(2)}</span>
              </ListGroup.Item>
            ))}
          </ListGroup>
        )}

        {/* Total and Checkout locked to the bottom */}
        <div className="mt-auto border-top pt-3">
          <div className="d-flex justify-content-between mb-3">
            <span className="fs-5 fw-bold">Total:</span>
            <span className="fs-5 fw-bold">${cartTotal.toFixed(2)}</span>
          </div>
          <Button
            as={Link}
            to="/cart"  // Link to existing cart page
            variant="dark"
            size="lg"
            className="w-100"
            disabled={cart.length === 0}
            onClick={handleClose}  // Close sidebar on click
          >
            Proceed to Checkout
          </Button>
        </div>
      </Offcanvas.Body>
    </Offcanvas>
  );
}

export default CartSidebar;