from dataclasses import dataclass
from typing import Dict, List

from app.models.furniture import Furniture


@dataclass
class CartItem:
    # One furniture item inside a user's cart.
    # عنصر واحد من الأثاث داخل سلة المستخدم.
    item_id: int
    quantity: int


class CartService:
    def __init__(self) -> None:
        # In-memory carts: {user_id: {item_id: CartItem}}
        # تخزين السلال بالذاكرة لكل مستخدم.
        self._carts: Dict[int, Dict[int, CartItem]] = {}

    def add_item(self, user_id: int, item_id: int, quantity: int) -> None:
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero.")
        user_cart = self._carts.setdefault(user_id, {})
        if item_id in user_cart:
            user_cart[item_id].quantity += quantity
        else:
            user_cart[item_id] = CartItem(item_id=item_id, quantity=quantity)

    def remove_item(self, user_id: int, item_id: int) -> None:
        user_cart = self._carts.get(user_id, {})
        if item_id not in user_cart:
            raise KeyError("Item not found in cart.")
        del user_cart[item_id]

    def clear_cart(self, user_id: int) -> None:
        self._carts[user_id] = {}

    def get_cart_items(self, user_id: int) -> List[CartItem]:
        return list(self._carts.get(user_id, {}).values())

    def get_cart_summary(self, user_id: int, inventory_items: Dict[int, Furniture], discount_percentage: float = 0) -> dict:
        # Build detailed cart response and calculate totals.
        # تجهيز تفاصيل السلة مع حساب الإجمالي والخصم.
        if not 0 <= discount_percentage <= 100:
            raise ValueError("Discount percentage must be between 0 and 100.")

        items: List[dict] = []
        subtotal = 0.0
        for cart_item in self.get_cart_items(user_id):
            furniture = inventory_items.get(cart_item.item_id)
            if furniture is None:
                continue
            line_total = round(furniture.price * cart_item.quantity, 2)
            subtotal += line_total
            items.append(
                {
                    "item_id": cart_item.item_id,
                    "name": furniture.name,
                    "unit_price": furniture.price,
                    "quantity": cart_item.quantity,
                    "line_total": line_total,
                }
            )

        discount_amount = round(subtotal * (discount_percentage / 100), 2)
        total_after_discount = round(subtotal - discount_amount, 2)
        return {
            "user_id": user_id,
            "items": items,
            "subtotal": round(subtotal, 2),
            "discount_percentage": discount_percentage,
            "discount_amount": discount_amount,
            "total": total_after_discount,
        }
