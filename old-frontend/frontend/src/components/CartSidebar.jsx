import { Offcanvas, ListGroup, Button } from 'react-bootstrap';
import { useCart } from '../context/CartContext';

function CartSidebar({ show, handleClose }) {
  const { cart } = useCart();
  
  // Calculate the total price of all items
  const cartTotal = cart.reduce((total, item) => total + (item.price * item.qty), 0);

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
                  <h6 className="mb-0 fw-bold">{item.name}</h6>
                  <small className="text-muted">Qty: {item.qty} x ${item.price.toFixed(2)}</small>
                </div>
                <span className="fw-bold">${(item.price * item.qty).toFixed(2)}</span>
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
          <Button variant="dark" size="lg" className="w-100" disabled={cart.length === 0}>
            Proceed to Checkout
          </Button>
        </div>
      </Offcanvas.Body>
    </Offcanvas>
  );
}

export default CartSidebar;