import { useState } from 'react';
import { Navbar, Container, Nav, Button, Badge, Offcanvas, Form } from 'react-bootstrap';
import { Link, useLocation } from 'react-router-dom';
import { useCart } from '../context/CartContext';
import CartSidebar from './CartSidebar'; // 1. Added import

function NavigationBar() {
  // Menu state
  const [show, setShow] = useState(false);
  const handleClose = () => setShow(false);
  const handleShow = () => setShow(true);

  // Cart state
  const [showCart, setShowCart] = useState(false);
  const handleCloseCart = () => setShowCart(false);
  const handleShowCart = () => setShowCart(true);

  const { cartCount } = useCart();

  const location = useLocation();

  return (
    <> {/* React Fragment to wrap Navbar and Sidebar */}
      <Navbar bg="light" expand="lg" className="shadow-sm">
        <Container>
          <Navbar.Toggle 
            onClick={handleShow} 
            className="me-2 border-0" 
            style={{ transform: 'scale(0.8)' }} 
          />

          <Navbar.Brand as={Link} to="/" className="fw-bold fs-4 me-3">LimeLight</Navbar.Brand>
          
          <Form className="d-flex flex-grow-1 me-3 d-none d-lg-flex">
            <Form.Control
              type="search"
              placeholder="Search products..."
              className="me-2"
              aria-label="Search"
            />
            <Button variant="outline-dark">Search</Button>
          </Form>
          
          {/* onClick={handleShowCart} */}
          <Button 
            variant="dark" 
            className="position-relative d-flex align-items-center ms-auto ms-lg-0 me-3 me-lg-0"
            onClick={handleShowCart}
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
              <path d="M0 1.5A.5.5 0 0 1 .5 1H2a.5.5 0 0 1 .485.379L2.89 3H14.5a.5.5 0 0 1 .49.598l-1 5a.5.5 0 0 1-.465.401l-9.397.472L4.415 11H13a.5.5 0 0 1 0 1H4a.5.5 0 0 1-.491-.408L2.01 3.607 1.61 2H.5a.5.5 0 0 1-.5-.5zM3.102 4l.84 4.479 9.144-.459L13.89 4H3.102zM5 12a2 2 0 1 0 0 4 2 2 0 0 0 0-4zm7 0a2 2 0 1 0 0 4 2 2 0 0 0 0-4zm-7 1a1 1 0 1 1 0 2 1 1 0 0 1 0-2zm7 0a1 1 0 1 1 0 2 1 1 0 0 1 0-2z"/>
            </svg>
            <span className="d-none d-lg-inline ms-2">Cart</span>
            
            <Badge bg="warning" text="dark" pill className="position-absolute top-0 start-100 translate-middle border border-light">
              {cartCount}
            </Badge>
          </Button>
          
          <Navbar.Offcanvas
            show={show}
            onHide={handleClose}
            placement="start" 
          >
            <Offcanvas.Header closeButton>
              <Offcanvas.Title>Menu</Offcanvas.Title>
            </Offcanvas.Header>
            
            <Offcanvas.Body>
              <Form className="d-flex mb-3 d-lg-none">
                <Form.Control
                  type="search"
                  placeholder="Search products..."
                  className="me-2"
                />
                <Button variant="outline-dark">Search</Button>
              </Form>

              {/*Nav links*/}
              <Nav className="flex-grow-1 pe-3">
              {/* Conditional styling based on location.pathname */}
              <Nav.Link 
                as={Link} 
                to="/" 
                onClick={handleClose}
                className={location.pathname === '/' ? 'fw-bold text-primary' : ''}
              >
                Home
              </Nav.Link>

              <Nav.Link 
                as={Link} 
                to="/shop" 
                onClick={handleClose}
                className={location.pathname.includes('/shop') || location.pathname.includes('/product') ? 'fw-bold text-primary' : ''}
              >
                Shop
              </Nav.Link>
              </Nav>
            </Offcanvas.Body>
          </Navbar.Offcanvas>
        </Container>
      </Navbar>

      {/* CartSidebar Component */}
      <CartSidebar show={showCart} handleClose={handleCloseCart} />
    </>
  );
}

export default NavigationBar;