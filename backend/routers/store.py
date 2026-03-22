from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from database import get_db
from dependencies import get_current_user
from models import Product, ProductRead, User, CartItem, Order, OrderItem, OrderCreate, OrderRead, OrderItemRead

router = APIRouter()

@router.get("/")
def store_root():
    return {"message": "Store API endpoint"}

@router.get("/products", response_model=List[ProductRead])
def list_products(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get public list of products (paginated, no auth required)"""
    products = db.query(Product).offset(skip).limit(limit).all()
    return [ProductRead(**product.model_dump()) for product in products]

@router.get("/products/{product_id}", response_model=ProductRead)
def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    """Get public product detail (no auth required)"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return ProductRead(**product.model_dump())

@router.get("/me", response_model=dict)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "oauth_provider": current_user.oauth_provider,
        "oauth_id": current_user.oauth_id
    }


# ============================================================
# ORDER ENDPOINTS
# ============================================================

@router.post("/orders", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
def place_order(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Place an order from the user's cart.
    
    - Fetches all cart items for the user
    - Validates stock availability (with row-level locking)
    - Creates order and order items (with product price snapshot)
    - Decrements product stock
    - Clears user's cart
    - Returns the created order
    """
    try:
        # Fetch cart items for user
        cart_items = db.query(CartItem).filter(CartItem.user_id == current_user.id).all()
        
        if not cart_items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cart is empty. Cannot place order."
            )
        
        # Collect product IDs for locking
        product_ids = [item.product_id for item in cart_items]
        
        # Lock and validate all products (SELECT FOR UPDATE)
        products = db.query(Product).filter(Product.id.in_(product_ids)).with_for_update().all()
        products_dict = {p.id: p for p in products}
        
        # Validate stock for all items
        for cart_item in cart_items:
            product = products_dict.get(cart_item.product_id)
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product {cart_item.product_id} not found"
                )
            if product.stock < cart_item.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient stock for {product.name}. Available: {product.stock}, Requested: {cart_item.quantity}"
                )
        
        # Create order
        order = Order(
            user_id=current_user.id,
            status="pending"
        )
        db.add(order)
        db.flush()  # Flush to get order.id without committing yet
        
        # Create order items and decrement stock
        for cart_item in cart_items:
            product = products_dict[cart_item.product_id]
            
            # Create order item (snapshot of product price)
            order_item = OrderItem(
                order_id=order.id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                price=float(product.price)  # Snapshot price
            )
            db.add(order_item)
            
            # Decrement product stock
            product.stock -= cart_item.quantity
            db.add(product)
        
        # Clear user's cart
        db.query(CartItem).filter(CartItem.user_id == current_user.id).delete()
        
        # Commit all changes
        db.commit()
        db.refresh(order)
        
        # Manually build response since we need eager-loaded items
        order_items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
        return OrderRead(
            id=order.id,
            user_id=order.user_id,
            status=order.status,
            created_at=order.created_at,
            updated_at=order.updated_at,
            items=[
                OrderItemRead(
                    id=item.id,
                    order_id=item.order_id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    price=float(item.price)
                )
                for item in order_items
            ]
        )
    
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to place order: {str(e)}"
        )


@router.get("/orders", response_model=List[OrderRead])
def get_user_orders(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's order history (paginated)"""
    orders = (
        db.query(Order)
        .filter(Order.user_id == current_user.id)
        .order_by(Order.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    result = []
    for order in orders:
        items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
        result.append(OrderRead(
            id=order.id,
            user_id=order.user_id,
            status=order.status,
            created_at=order.created_at,
            updated_at=order.updated_at,
            items=[
                OrderItemRead(
                    id=item.id,
                    order_id=item.order_id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    price=float(item.price)
                )
                for item in items
            ]
        ))
    
    return result


@router.get("/orders/{order_id}", response_model=OrderRead)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific order (only if it belongs to the user)"""
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Verify ownership
    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this order"
        )
    
    items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
    return OrderRead(
        id=order.id,
        user_id=order.user_id,
        status=order.status,
        created_at=order.created_at,
        updated_at=order.updated_at,
        items=[
            OrderItemRead(
                id=item.id,
                order_id=item.order_id,
                product_id=item.product_id,
                quantity=item.quantity,
                price=float(item.price)
            )
            for item in items
        ]
    )