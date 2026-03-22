"""
Comprehensive test suite for Phase 2: Full Order System
Run with: pytest test_phase2.py -v
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from sqlmodel import Session, create_engine
from sqlmodel.pool import StaticPool

from main import app
from database import get_db
from models import (
    User, Product, CartItem, Order, OrderItem, Session as DBSession
)


# Test database setup
@pytest.fixture(name="session")
def session_fixture():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    from sqlmodel import SQLModel
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create a test client with our test database."""
    def get_session_override():
        return session

    app.dependency_overrides[get_db] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


# Fixtures for creating test data
def create_test_user(session: Session, username: str, role: str = "customer") -> User:
    """Create a test user."""
    user = User(
        username=username,
        password_hash="hashed_password",
        role=role
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def create_test_product(session: Session, name: str, price: float, stock: int) -> Product:
    """Create a test product."""
    product = Product(
        name=name,
        price=price,
        stock=stock,
        description="Test product"
    )
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


def create_test_session(session: Session, user_id: int) -> DBSession:
    """Create a test session."""
    db_session = DBSession(
        session_id="test_session_123",
        user_id=user_id,
        expires_at=datetime.utcnow() + timedelta(hours=24)
    )
    session.add(db_session)
    session.commit()
    session.refresh(db_session)
    return db_session


# ============================================================
# TEST SUITE 1: Order Creation
# ============================================================

class TestOrderCreation:
    """Tests for placing orders."""

    def test_place_order_success(self, client: TestClient, session: Session):
        """Successfully place an order from cart."""
        user = create_test_user(session, "user1")
        create_test_session(session, user.id)
        product = create_test_product(session, "Product 1", 10.0, 100)

        # Add item to cart
        client.post(
            f"/api/store/cart/items?product_id={product.id}&quantity=5",
            cookies={"session_id": "test_session_123"}
        )

        # Place order
        response = client.post(
            "/api/store/orders",
            cookies={"session_id": "test_session_123"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["user_id"] == user.id
        assert data["status"] == "pending"
        assert len(data["items"]) == 1
        assert data["items"][0]["quantity"] == 5
        assert data["items"][0]["price"] == 10.0

    def test_place_order_insufficient_stock(self, client: TestClient, session: Session):
        """Cannot place order with insufficient stock."""
        user = create_test_user(session, "user1")
        create_test_session(session, user.id)
        product = create_test_product(session, "Limited Stock", 10.0, 3)

        # Add 5 items to cart (only 3 available)
        client.post(
            f"/api/store/cart/items?product_id={product.id}&quantity=5",
            cookies={"session_id": "test_session_123"}
        )

        # Try to place order
        response = client.post(
            "/api/store/orders",
            cookies={"session_id": "test_session_123"}
        )

        assert response.status_code == 400
        assert "Insufficient stock" in response.json()["detail"]

    def test_place_order_empty_cart(self, client: TestClient, session: Session):
        """Cannot place order with empty cart."""
        user = create_test_user(session, "user1")
        create_test_session(session, user.id)

        # Try to place order without items
        response = client.post(
            "/api/store/orders",
            cookies={"session_id": "test_session_123"}
        )

        assert response.status_code == 400
        assert "Cart is empty" in response.json()["detail"]

    def test_place_order_clears_cart(self, client: TestClient, session: Session):
        """Placing order should clear the cart."""
        user = create_test_user(session, "user1")
        create_test_session(session, user.id)
        product = create_test_product(session, "Product 1", 10.0, 100)

        # Add to cart
        client.post(
            f"/api/store/cart/items?product_id={product.id}&quantity=3",
            cookies={"session_id": "test_session_123"}
        )

        # Verify cart has items
        cart_response = client.get(
            "/api/store/cart",
            cookies={"session_id": "test_session_123"}
        )
        assert len(cart_response.json()) == 1

        # Place order
        client.post(
            "/api/store/orders",
            cookies={"session_id": "test_session_123"}
        )

        # Verify cart is empty
        cart_response = client.get(
            "/api/store/cart",
            cookies={"session_id": "test_session_123"}
        )
        assert len(cart_response.json()) == 0

    def test_place_order_decrements_stock(self, client: TestClient, session: Session):
        """Placing order should decrement product stock."""
        user = create_test_user(session, "user1")
        create_test_session(session, user.id)
        product = create_test_product(session, "Product 1", 10.0, 100)

        # Add to cart
        client.post(
            f"/api/store/cart/items?product_id={product.id}&quantity=25",
            cookies={"session_id": "test_session_123"}
        )

        # Verify initial stock
        initial_stock = session.query(Product).filter(Product.id == product.id).first().stock
        assert initial_stock == 100

        # Place order
        client.post(
            "/api/store/orders",
            cookies={"session_id": "test_session_123"}
        )

        # Verify stock decreased
        updated_stock = session.query(Product).filter(Product.id == product.id).first().stock
        assert updated_stock == 75

    def test_place_order_multiple_items(self, client: TestClient, session: Session):
        """Place order with multiple cart items."""
        user = create_test_user(session, "user1")
        create_test_session(session, user.id)
        product1 = create_test_product(session, "Product 1", 10.0, 50)
        product2 = create_test_product(session, "Product 2", 20.0, 50)

        # Add multiple items to cart
        client.post(
            f"/api/store/cart/items?product_id={product1.id}&quantity=3",
            cookies={"session_id": "test_session_123"}
        )
        client.post(
            f"/api/store/cart/items?product_id={product2.id}&quantity=2",
            cookies={"session_id": "test_session_123"}
        )

        # Place order
        response = client.post(
            "/api/store/orders",
            cookies={"session_id": "test_session_123"}
        )

        assert response.status_code == 201
        data = response.json()
        assert len(data["items"]) == 2
        assert data["items"][0]["quantity"] == 3
        assert data["items"][1]["quantity"] == 2

    def test_place_order_requires_auth(self, client: TestClient):
        """Order creation requires authentication."""
        response = client.post("/api/store/orders")
        assert response.status_code == 401


# ============================================================
# TEST SUITE 2: Order History (Customer)
# ============================================================

class TestOrderHistory:
    """Tests for customer order history access."""

    def test_get_user_orders(self, client: TestClient, session: Session):
        """Get list of user's orders."""
        user = create_test_user(session, "user1")
        create_test_session(session, user.id)
        product = create_test_product(session, "Product 1", 10.0, 100)

        # Place order
        client.post(
            f"/api/store/cart/items?product_id={product.id}&quantity=2",
            cookies={"session_id": "test_session_123"}
        )
        client.post(
            "/api/store/orders",
            cookies={"session_id": "test_session_123"}
        )

        # Get orders
        response = client.get(
            "/api/store/orders",
            cookies={"session_id": "test_session_123"}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["status"] == "pending"

    def test_get_single_order(self, client: TestClient, session: Session):
        """Get details of a single order."""
        user = create_test_user(session, "user1")
        create_test_session(session, user.id)
        product = create_test_product(session, "Product 1", 10.0, 100)

        # Place order
        client.post(
            f"/api/store/cart/items?product_id={product.id}&quantity=2",
            cookies={"session_id": "test_session_123"}
        )
        order_response = client.post(
            "/api/store/orders",
            cookies={"session_id": "test_session_123"}
        )
        order_id = order_response.json()["id"]

        # Get order
        response = client.get(
            f"/api/store/orders/{order_id}",
            cookies={"session_id": "test_session_123"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == order_id
        assert len(data["items"]) == 1

    def test_cannot_access_others_order(self, client: TestClient, session: Session):
        """User cannot access another user's order."""
        user1 = create_test_user(session, "user1")
        user2 = create_test_user(session, "user2")
        create_test_session(session, user1.id)

        product = create_test_product(session, "Product 1", 10.0, 100)

        # User1 places order
        client.post(
            f"/api/store/cart/items?product_id={product.id}&quantity=2",
            cookies={"session_id": "test_session_123"}
        )
        order_response = client.post(
            "/api/store/orders",
            cookies={"session_id": "test_session_123"}
        )
        order_id = order_response.json()["id"]

        # Create session for user2
        user2_session = DBSession(
            session_id="user2_session",
            user_id=user2.id,
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )
        session.add(user2_session)
        session.commit()

        # User2 tries to access user1's order
        response = client.get(
            f"/api/store/orders/{order_id}",
            cookies={"session_id": "user2_session"}
        )

        assert response.status_code == 403

    def test_get_orders_requires_auth(self, client: TestClient):
        """Order history requires authentication."""
        response = client.get("/api/store/orders")
        assert response.status_code == 401


# ============================================================
# TEST SUITE 3: Admin Order Management
# ============================================================

class TestAdminOrderManagement:
    """Tests for admin order management."""

    def test_admin_list_all_orders(self, client: TestClient, session: Session):
        """Admin can list all orders."""
        admin = create_test_user(session, "admin", role="admin")
        create_test_session(session, admin.id)

        user = create_test_user(session, "user1")
        product = create_test_product(session, "Product 1", 10.0, 100)

        # Create order for user
        user_session = DBSession(
            session_id="user_session",
            user_id=user.id,
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )
        session.add(user_session)
        session.commit()

        # User places order
        client.post(
            f"/api/store/cart/items?product_id={product.id}&quantity=2",
            cookies={"session_id": "user_session"}
        )
        client.post(
            "/api/store/orders",
            cookies={"session_id": "user_session"}
        )

        # Admin lists all orders
        response = client.get(
            "/api/admin/orders",
            cookies={"session_id": "test_session_123"}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    def test_admin_get_single_order(self, client: TestClient, session: Session):
        """Admin can get details of any order."""
        admin = create_test_user(session, "admin", role="admin")
        create_test_session(session, admin.id)

        user = create_test_user(session, "user1")
        product = create_test_product(session, "Product 1", 10.0, 100)

        # Create order
        user_session = DBSession(
            session_id="user_session",
            user_id=user.id,
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )
        session.add(user_session)
        session.commit()

        client.post(
            f"/api/store/cart/items?product_id={product.id}&quantity=2",
            cookies={"session_id": "user_session"}
        )
        order_response = client.post(
            "/api/store/orders",
            cookies={"session_id": "user_session"}
        )
        order_id = order_response.json()["id"]

        # Admin gets order
        response = client.get(
            f"/api/admin/orders/{order_id}",
            cookies={"session_id": "test_session_123"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == order_id

    def test_admin_update_order_status(self, client: TestClient, session: Session):
        """Admin can update order status."""
        admin = create_test_user(session, "admin", role="admin")
        create_test_session(session, admin.id)

        user = create_test_user(session, "user1")
        product = create_test_product(session, "Product 1", 10.0, 100)

        # Create order
        user_session = DBSession(
            session_id="user_session",
            user_id=user.id,
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )
        session.add(user_session)
        session.commit()

        client.post(
            f"/api/store/cart/items?product_id={product.id}&quantity=2",
            cookies={"session_id": "user_session"}
        )
        order_response = client.post(
            "/api/store/orders",
            cookies={"session_id": "user_session"}
        )
        order_id = order_response.json()["id"]

        # Update status
        response = client.patch(
            f"/api/admin/orders/{order_id}/status",
            json={"status": "confirmed"},
            cookies={"session_id": "test_session_123"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "confirmed"

    def test_admin_invalid_status_transition(self, client: TestClient, session: Session):
        """Admin cannot perform invalid status transitions."""
        admin = create_test_user(session, "admin", role="admin")
        create_test_session(session, admin.id)

        user = create_test_user(session, "user1")
        product = create_test_product(session, "Product 1", 10.0, 100)

        # Create order
        user_session = DBSession(
            session_id="user_session",
            user_id=user.id,
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )
        session.add(user_session)
        session.commit()

        client.post(
            f"/api/store/cart/items?product_id={product.id}&quantity=2",
            cookies={"session_id": "user_session"}
        )
        order_response = client.post(
            "/api/store/orders",
            cookies={"session_id": "user_session"}
        )
        order_id = order_response.json()["id"]

        # Try invalid transition (pending -> shipped, should go through confirmed first)
        response = client.patch(
            f"/api/admin/orders/{order_id}/status",
            json={"status": "shipped"},
            cookies={"session_id": "test_session_123"}
        )

        assert response.status_code == 400
        assert "Invalid status transition" in response.json()["detail"]

    def test_customer_cannot_manage_orders(self, client: TestClient, session: Session):
        """Customer cannot access admin order management."""
        customer = create_test_user(session, "customer", role="customer")
        create_test_session(session, customer.id)

        # Try to list all orders
        response = client.get(
            "/api/admin/orders",
            cookies={"session_id": "test_session_123"}
        )

        assert response.status_code == 403

    def test_admin_orders_require_auth(self, client: TestClient):
        """Admin order endpoints require authentication."""
        response = client.get("/api/admin/orders")
        assert response.status_code == 401


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
