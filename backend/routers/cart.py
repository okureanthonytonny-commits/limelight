from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from database import get_db
from dependencies import get_current_user
from models import CartItem, Product, User

router = APIRouter()


@router.get("/cart", response_model=List[dict])
def get_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's cart items with product details."""
    cart_items = (
        db.query(CartItem)
        .options(joinedload(CartItem.product))
        .filter(CartItem.user_id == current_user.id)
        .all()
    )

    # Format response with product details
    result = []
    for item in cart_items:
        if item.product:
            result.append({
                "id": item.id,
                "product_id": item.product_id,
                "quantity": item.quantity,
                "product": {
                    "id": item.product.id,
                    "name": item.product.name,
                    "price": item.product.price,
                    "image_url": item.product.image_url,
                },
                "added_at": item.added_at,
                "updated_at": item.updated_at,
            })

    return result


@router.post("/cart/items", status_code=status.HTTP_201_CREATED)
def add_or_update_cart_item(
    product_id: int = Query(..., gt=0),
    quantity: int = Query(1, ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add or update an item in the cart."""
    # Check if product exists and has stock
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    if product.stock <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product is out of stock"
        )
    if quantity > product.stock:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient stock. Available: {product.stock}"
        )

    # Check if item already in cart
    cart_item = (
        db.query(CartItem)
        .filter(CartItem.user_id == current_user.id, CartItem.product_id == product_id)
        .first()
    )

    if cart_item:
        # Update quantity
        cart_item.quantity = quantity
        cart_item.updated_at = None  # Will auto-update
    else:
        # Create new cart item
        cart_item = CartItem(
            user_id=current_user.id,
            product_id=product_id,
            quantity=quantity
        )
        db.add(cart_item)

    db.commit()
    db.refresh(cart_item)
    return {"message": "Item added to cart", "cart_item_id": cart_item.id}


@router.put("/cart/items/{product_id}")
def update_cart_item_quantity(
    product_id: int,
    quantity: int = Query(..., ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update quantity of a cart item. If quantity <= 0, remove the item."""
    cart_item = (
        db.query(CartItem)
        .filter(CartItem.user_id == current_user.id, CartItem.product_id == product_id)
        .first()
    )

    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found in cart"
        )

    if quantity <= 0:
        # Remove item
        db.delete(cart_item)
        db.commit()
        return {"message": "Item removed from cart"}

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    if product.stock <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product is out of stock"
        )
    if quantity > product.stock:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient stock. Available: {product.stock}"
        )

    # Update quantity
    cart_item.quantity = quantity
    cart_item.updated_at = None  # Will auto-update
    db.commit()
    db.refresh(cart_item)
    return {"message": "Item quantity updated", "cart_item_id": cart_item.id}


@router.delete("/cart/items/{product_id}")
def remove_cart_item(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove an item from the cart."""
    cart_item = (
        db.query(CartItem)
        .filter(CartItem.user_id == current_user.id, CartItem.product_id == product_id)
        .first()
    )

    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found in cart"
        )

    db.delete(cart_item)
    db.commit()
    return {"message": "Item removed from cart"}


@router.delete("/cart")
def clear_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Clear the entire cart."""
    db.query(CartItem).filter(CartItem.user_id == current_user.id).delete()
    db.commit()
    return {"message": "Cart cleared"}