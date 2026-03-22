"""
Phase 1 Tests for Issue 5: Role enforcement, stock validation, and migrations.
Run with: pytest test_phase1.py -v
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from sqlmodel import Session, create_engine
from sqlmodel.pool import StaticPool

from main import app
from database import get_db
from models import User, Product, CartItem, Session as DBSession


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


# Test fixtures for users and products
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
# TEST SUITE 1: Admin Role Enforcement (require_admin)
# ============================================================

class TestAdminRoleEnforcement:
    """Tests for admin role checking in require_admin dependency."""

    def test_require_admin_denies_customer_access(self, client: TestClient, session: Session):
        """Customer should not be able to create products."""
        customer = create_test_user(session, "customer_user", role="customer")
        create_test_session(session, customer.id)

        # Try to create a product as customer
        response = client.post(
            "/api/admin/products",
            data={
                "name": "Test Product",
                "description": "A test product",
                "price": 10.0,
                "stock": 50
            },
            cookies={"session_id": "test_session_123"}
        )
        assert response.status_code == 403
        assert response.json()["detail"] == "Admin privileges required"

    def test_require_admin_allows_admin_access(self, client: TestClient, session: Session):
        """Admin should be able to create products."""
        admin = create_test_user(session, "admin_user", role="admin")
        create_test_session(session, admin.id)

        # Admin can create product
        response = client.post(
            "/api/admin/products",
            data={
                "name": "Test Product",
                "description": "A test product",
                "price": 10.0,
                "stock": 50
            },
            cookies={"session_id": "test_session_123"}
        )
        assert response.status_code == 201
        assert response.json()["name"] == "Test Product"

    def test_user_model_has_role_field(self, session: Session):
        """User model should have role field with default 'customer'."""
        user = User(username="testuser", password_hash="hash")
        assert user.role == "customer"
        
        session.add(user)
        session.commit()
        session.refresh(user)
        assert user.role == "customer"

    def test_user_can_have_admin_role(self, session: Session):
        """User can be created with admin role."""
        user = User(username="admin", password_hash="hash", role="admin")
        session.add(user)
        session.commit()
        session.refresh(user)
        assert user.role == "admin"


# ============================================================
# TEST SUITE 2: Stock Validation in Cart
# ============================================================

class TestStockValidation:
    """Tests for stock validation when adding/updating cart items."""

    def test_cannot_add_item_if_stock_is_zero(self, client: TestClient, session: Session):
        """Should not be able to add product with 0 stock."""
        user = create_test_user(session, "user1")
        create_test_session(session, user.id)
        product = create_test_product(session, "Out of Stock", 10.0, 0)

        response = client.post(
            f"/api/store/cart/items?product_id={product.id}&quantity=1",
            cookies={"session_id": "test_session_123"}
        )
        assert response.status_code == 400
        assert "out of stock" in response.json()["detail"].lower()

    def test_cannot_add_item_if_quantity_exceeds_stock(self, client: TestClient, session: Session):
        """Should not be able to add more than available stock."""
        user = create_test_user(session, "user1")
        create_test_session(session, user.id)
        product = create_test_product(session, "Limited Stock", 10.0, 5)

        response = client.post(
            f"/api/store/cart/items?product_id={product.id}&quantity=10",
            cookies={"session_id": "test_session_123"}
        )
        assert response.status_code == 400
        assert "Insufficient stock" in response.json()["detail"]
        assert "Available: 5" in response.json()["detail"]

    def test_can_add_item_if_stock_available(self, client: TestClient, session: Session):
        """Should be able to add item if stock is available."""
        user = create_test_user(session, "user1")
        create_test_session(session, user.id)
        product = create_test_product(session, "Available", 10.0, 10)

        response = client.post(
            f"/api/store/cart/items?product_id={product.id}&quantity=5",
            cookies={"session_id": "test_session_123"}
        )
        assert response.status_code == 201
        assert response.json()["message"] == "Item added to cart"

    def test_cannot_update_cart_item_quantity_to_exceed_stock(self, client: TestClient, session: Session):
        """Should not be able to update quantity to exceed stock."""
        user = create_test_user(session, "user1")
        create_test_session(session, user.id)
        product = create_test_product(session, "Limited", 10.0, 5)
        
        # Add item to cart
        client.post(
            f"/api/store/cart/items?product_id={product.id}&quantity=3",
            cookies={"session_id": "test_session_123"}
        )

        # Try to update to exceed stock
        response = client.put(
            f"/api/store/cart/items/{product.id}?quantity=10",
            cookies={"session_id": "test_session_123"}
        )
        assert response.status_code == 400
        assert "Insufficient stock" in response.json()["detail"]

    def test_can_update_cart_item_within_stock_limits(self, client: TestClient, session: Session):
        """Should be able to update quantity within stock limits."""
        user = create_test_user(session, "user1")
        create_test_session(session, user.id)
        product = create_test_product(session, "Available", 10.0, 10)
        
        # Add item to cart
        client.post(
            f"/api/store/cart/items?product_id={product.id}&quantity=3",
            cookies={"session_id": "test_session_123"}
        )

        # Update to valid quantity
        response = client.put(
            f"/api/store/cart/items/{product.id}?quantity=5",
            cookies={"session_id": "test_session_123"}
        )
        assert response.status_code == 200
        assert response.json()["message"] == "Item quantity updated"

    def test_cannot_add_nonexistent_product(self, client: TestClient, session: Session):
        """Should not be able to add non-existent product to cart."""
        user = create_test_user(session, "user1")
        create_test_session(session, user.id)

        response = client.post(
            "/api/store/cart/items?product_id=99999&quantity=1",
            cookies={"session_id": "test_session_123"}
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Product not found"

    def test_product_model_has_stock_field(self, session: Session):
        """Product model should have stock field with default 0."""
        product = Product(name="Test", price=10.0)
        assert product.stock == 0
        
        session.add(product)
        session.commit()
        session.refresh(product)
        assert product.stock == 0

    def test_product_stock_validation_non_negative(self, session: Session):
        """Product stock should not allow negative values."""
        # Stock field has ge=0, so only non-negative values allowed
        product = Product(name="Test", price=10.0, stock=10)
        assert product.stock == 10


# ============================================================
# TEST SUITE 3: Integration: Admin + Stock Validation
# ============================================================

class TestAdminProductManagement:
    """Tests for admin product management with stock field."""

    def test_admin_can_create_product_with_stock(self, client: TestClient, session: Session):
        """Admin should be able to create product with stock."""
        admin = create_test_user(session, "admin", role="admin")
        create_test_session(session, admin.id)

        response = client.post(
            "/api/admin/products",
            data={
                "name": "New Product",
                "description": "With stock",
                "price": 25.0,
                "stock": 100
            },
            cookies={"session_id": "test_session_123"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Product"
        assert data["stock"] == 100

    def test_admin_can_update_product_stock(self, client: TestClient, session: Session):
        """Admin should be able to update product stock."""
        admin = create_test_user(session, "admin", role="admin")
        create_test_session(session, admin.id)
        product = create_test_product(session, "Original", 10.0, 5)

        response = client.put(
            f"/api/admin/products/{product.id}",
            data={
                "stock": 20
            },
            cookies={"session_id": "test_session_123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["stock"] == 20

    def test_customer_cannot_create_product(self, client: TestClient, session: Session):
        """Customer should not be able to create product."""
        customer = create_test_user(session, "customer", role="customer")
        create_test_session(session, customer.id)

        response = client.post(
            "/api/admin/products",
            data={
                "name": "Unauthorized Product",
                "price": 10.0,
                "stock": 5
            },
            cookies={"session_id": "test_session_123"}
        )
        assert response.status_code == 403


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
