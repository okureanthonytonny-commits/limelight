import { createContext, useState, useContext, useEffect } from 'react';

const CartContext = createContext();

export function CartProvider({ children }) {
  const [cart, setCart] = useState([]);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Helper: Convert backend item to localStorage shape for persistence
  const toLocalCartItem = (item) => ({
    id: item.product_id,
    name: item.product.name,
    price: item.product.price,
    image_url: item.product.image_url,
    qty: item.quantity,
  });

  // Helper: Normalize backend item to context shape
  const normalizeCartItem = (item) => ({
    product_id: item.product_id,
    product: {
      id: item.product.id,
      name: item.product.name,
      price: item.product.price,
      image_url: item.product.image_url,
    },
    quantity: item.quantity,
    added_at: item.added_at,
  });

  // Helper: Convert localStorage item to context shape
  const fromLocalCartItem = (item) => ({
    product_id: item.id,
    product: {
      id: item.id,
      name: item.name,
      price: item.price,
      image_url: item.image_url,
    },
    quantity: item.qty,
  });

  // Load and sync cart on mount
  useEffect(() => {
    const initializeCart = async () => {
      setLoading(true);
      setError(null);

      // Check if user is logged in
      try {
        const authResponse = await fetch('http://localhost:8000/api/store/me', {
          credentials: 'include',
        });
        const loggedIn = authResponse.ok;
        setIsLoggedIn(loggedIn);

        let mergedCart = [];

        if (loggedIn) {
          // Fetch backend cart
          const cartResponse = await fetch('http://localhost:8000/api/store/cart', {
            credentials: 'include',
          });
          if (cartResponse.ok) {
            const backendCart = await cartResponse.json();
            const normalizedBackend = backendCart.map(normalizeCartItem);

            // Load local cart
            const savedCart = localStorage.getItem('limelight_cart');
            const localCart = savedCart ? JSON.parse(savedCart).map(fromLocalCartItem) : [];

            // Merge: sum quantities for duplicates, cap by stock (assume stock is available or handle in API)
            const mergedMap = new Map();

            // Add backend items
            normalizedBackend.forEach(item => {
              mergedMap.set(item.product_id, { ...item });
            });

            // Merge local items
            localCart.forEach(localItem => {
              const existing = mergedMap.get(localItem.product_id);
              if (existing) {
                existing.quantity += localItem.quantity;
              } else {
                mergedMap.set(localItem.product_id, localItem);
              }
            });

            mergedCart = Array.from(mergedMap.values());

            // Push merged cart to backend (add/update items)
            for (const item of mergedCart) {
              try {
                await fetch(`http://localhost:8000/api/store/cart/items?product_id=${item.product_id}&quantity=${item.quantity}`, {
                  method: 'POST',
                  credentials: 'include',
                });
              } catch (err) {
                console.error('Failed to sync item to backend:', err);
              }
            }
          }
        } else {
          // Guest: load from localStorage only
          const savedCart = localStorage.getItem('limelight_cart');
          mergedCart = savedCart ? JSON.parse(savedCart).map(fromLocalCartItem) : [];
        }

        setCart(mergedCart);
      } catch (err) {
        console.error('Auth/cart sync failed:', err);
        setError('Failed to load cart');
        // Fallback to localStorage
        const savedCart = localStorage.getItem('limelight_cart');
        setCart(savedCart ? JSON.parse(savedCart).map(fromLocalCartItem) : []);
      } finally {
        setLoading(false);
      }
    };

    initializeCart();
  }, []);

  // Persist to localStorage on cart change
  useEffect(() => {
    const localCart = cart.map(toLocalCartItem);
    localStorage.setItem('limelight_cart', JSON.stringify(localCart));
  }, [cart]);

  // Manual sync function (for post-login)
  const syncCart = async () => {
    if (!isLoggedIn) return;
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/store/cart', {
        credentials: 'include',
      });
      if (response.ok) {
        const backendCart = await response.json();
        const normalized = backendCart.map(normalizeCartItem);
        setCart(normalized);
      }
    } catch (err) {
      console.error('Sync failed:', err);
    } finally {
      setLoading(false);
    }
  };

  // Add to cart (optimistic)
  const addToCart = async (product) => {
    const existingItem = cart.find(item => item.product_id === product.id);
    let newQuantity = 1;
    if (existingItem) {
      newQuantity = existingItem.quantity + 1;
    }

    // Optimistic update
    const newCart = existingItem
      ? cart.map(item =>
          item.product_id === product.id ? { ...item, quantity: newQuantity } : item
        )
      : [...cart, {
          product_id: product.id,
          product: {
            id: product.id,
            name: product.name,
            price: product.price,
            image_url: product.image_url,
          },
          quantity: 1,
        }];
    setCart(newCart);

    // Backend call if logged in
    if (isLoggedIn) {
      try {
        await fetch(`http://localhost:8000/api/store/cart/items?product_id=${product.id}&quantity=${newQuantity}`, {
          method: 'POST',
          credentials: 'include',
        });
      } catch (err) {
        console.error('Failed to add to backend cart:', err);
      }
    }
  };

  // Update quantity (optimistic)
  const updateQuantity = async (productId, newQty) => {
    if (newQty <= 0) {
      removeFromCart(productId);
      return;
    }

    // Optimistic update
    setCart(prevCart =>
      prevCart.map(item =>
        item.product_id === productId ? { ...item, quantity: newQty } : item
      )
    );

    // Backend call if logged in
    if (isLoggedIn) {
      try {
        await fetch(`http://localhost:8000/api/store/cart/items/${productId}?quantity=${newQty}`, {
          method: 'PUT',
          credentials: 'include',
        });
      } catch (err) {
        console.error('Failed to update backend cart:', err);
      }
    }
  };

  // Remove from cart (optimistic)
  const removeFromCart = async (productId) => {
    // Optimistic update
    setCart(prevCart => prevCart.filter(item => item.product_id !== productId));

    // Backend call if logged in
    if (isLoggedIn) {
      try {
        await fetch(`http://localhost:8000/api/store/cart/items/${productId}`, {
          method: 'DELETE',
          credentials: 'include',
        });
      } catch (err) {
        console.error('Failed to remove from backend cart:', err);
      }
    }
  };

  // Clear cart (optimistic)
  const clearCart = async () => {
    // Optimistic update
    setCart([]);

    // Backend call if logged in
    if (isLoggedIn) {
      try {
        await fetch('http://localhost:8000/api/store/cart', {
          method: 'DELETE',
          credentials: 'include',
        });
      } catch (err) {
        console.error('Failed to clear backend cart:', err);
      }
    }
  };

  // Calculate totals
  const cartCount = cart.reduce((total, item) => total + item.quantity, 0);
  const cartTotal = cart.reduce((total, item) => total + (item.product.price * item.quantity), 0);

  return (
    <CartContext.Provider value={{
      cart,
      isLoggedIn,
      loading,
      error,
      addToCart,
      updateQuantity,
      removeFromCart,
      clearCart,
      syncCart,
      cartCount,
      cartTotal
    }}>
      {children}
    </CartContext.Provider>
  );
}

// Custom hook
export const useCart = () => useContext(CartContext);