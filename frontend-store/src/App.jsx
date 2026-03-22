import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import NavigationBar from './components/NavigationBar';
import HeroSection from './components/HeroSection';
import Products from './pages/Products';
import ProductDetail from './pages/ProductDetail';
import Cart from './pages/Cart';
import Orders from './pages/Orders';
import OrderDetail from './pages/OrderDetail';

function App() {
  return (
    <Router>
      {/* Persistent Navigation Bar (includes CartSidebar) */}
      <NavigationBar />

      {/* Page Content */}
      <Routes>
        <Route path="/" element={
          <>
            <HeroSection />
            <Products /> {/* Homepage shows hero and products */}
          </>
        } />
        <Route path="/products" element={<Products />} />
        <Route path="/product/:id" element={<ProductDetail />} />
        <Route path="/cart" element={<Cart />} />
        <Route path="/orders" element={<Orders />} />
        <Route path="/orders/:id" element={<OrderDetail />} />
      </Routes>
    </Router>
  );
}

export default App;