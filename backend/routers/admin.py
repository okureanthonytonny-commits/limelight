from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
import os
from pathlib import Path

from database import get_db
from dependencies import require_admin
from models import Product, ProductCreate, ProductRead, ProductUpdate, Order, OrderRead, OrderItemRead, OrderStatusUpdate, OrderItem

# Status transition validation
VALID_STATUS_TRANSITIONS = {
    "pending": ["confirmed", "cancelled"],
    "confirmed": ["shipped", "cancelled"],
    "shipped": ["delivered"],
    "delivered": [],
    "cancelled": []
}

router = APIRouter()

# Create static/images directory if not exists
STATIC_IMAGES_DIR = Path("static/images")
STATIC_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/products", response_model=ProductRead)
async def create_product(
    name: str = Form(...),
    description: Optional[str] = Form(None),
    price: float = Form(...),
    stock: int = Form(0),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin)
):
    """Create a new product (admin only)"""
    # Handle image upload
    image_url = None
    if image:
        # Generate unique filename
        file_extension = Path(image.filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = STATIC_IMAGES_DIR / unique_filename

        # Save file
        with open(file_path, "wb") as buffer:
            content = await image.read()
            buffer.write(content)

        image_url = f"/static/images/{unique_filename}"

    # Create product
    product_data = ProductCreate(
        name=name,
        description=description,
        price=price,
        stock=stock,
        image_url=image_url
    )

    db_product = Product(**product_data.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return ProductRead(**db_product.model_dump())

@router.get("/products", response_model=List[ProductRead])
def list_products(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin)
):
    """List all products (admin only)"""
    products = db.query(Product).offset(skip).limit(limit).all()
    return [ProductRead(**product.model_dump()) for product in products]

@router.get("/products/{product_id}", response_model=ProductRead)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin)
):
    """Get a single product (admin only)"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return ProductRead(**product.model_dump())

@router.put("/products/{product_id}", response_model=ProductRead)
async def update_product(
    product_id: int,
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    price: Optional[float] = Form(None),
    stock: Optional[int] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin)
):
    """Update a product (admin only)"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Handle image upload
    image_url = product.image_url
    if image:
        # Delete old image if exists
        if product.image_url:
            old_path = Path(f"static{product.image_url}")
            if old_path.exists():
                old_path.unlink()

        # Save new image
        file_extension = Path(image.filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = STATIC_IMAGES_DIR / unique_filename

        with open(file_path, "wb") as buffer:
            content = await image.read()
            buffer.write(content)

        image_url = f"/static/images/{unique_filename}"

    # Update product
    update_data = {}
    if name is not None:
        update_data["name"] = name
    if description is not None:
        update_data["description"] = description
    if price is not None:
        update_data["price"] = price
    if stock is not None:
        update_data["stock"] = stock
    if image_url != product.image_url:
        update_data["image_url"] = image_url

    for field, value in update_data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    return ProductRead(**product.model_dump())

@router.delete("/products/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin)
):
    """Delete a product (admin only)"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Delete image file if exists
    if product.image_url:
        image_path = Path(f"static{product.image_url}")
        if image_path.exists():
            image_path.unlink()

    db.delete(product)
    db.commit()
    return {"message": "Product deleted successfully"}


# ============================================================
# ADMIN ORDER MANAGEMENT
# ============================================================

@router.get("/orders", response_model=List[OrderRead])
def list_all_orders(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin)
):
    """List all orders (admin only, paginated)"""
    orders = (
        db.query(Order)
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
def get_order_admin(
    order_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin)
):
    """Get order details (admin only)"""
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
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


@router.patch("/orders/{order_id}/status", response_model=OrderRead)
def update_order_status(
    order_id: int,
    status_update: OrderStatusUpdate,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin)
):
    """Update order status (admin only). Validates status transitions."""
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Validate status transition
    current_status = order.status
    new_status = status_update.status
    
    if new_status not in VALID_STATUS_TRANSITIONS.get(current_status, []):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status transition: {current_status} -> {new_status}"
        )
    
    order.status = new_status
    db.commit()
    db.refresh(order)
    
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