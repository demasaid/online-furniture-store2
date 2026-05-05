from dataclasses import asdict
from typing import Dict, List

from app.models.furniture import Furniture
from app.models.order import Order, OrderItem
from app.services.cart_service import CartService


class OrderService:
    def __init__(self) -> None:
        self._orders: Dict[int, List[Order]] = {}
        self._next_order_id = 1

    def checkout(self, user_id: int, cart_service: CartService, inventory_items: Dict[int, Furniture], payment_method: str) -> Order:
        # Validates cart and stock, then creates order and decrements inventory.
        # يتحقق من السلة والمخزون ثم ينشئ الطلب ويخصم الكمية.
        if not payment_method.strip():
            raise ValueError("Payment method is required.")

        cart_items = cart_service.get_cart_items(user_id)
        if not cart_items:
            raise ValueError("Cart is empty.")

        order_items: List[OrderItem] = []
        total = 0.0

        for cart_item in cart_items:
            furniture = inventory_items.get(cart_item.item_id)
            if furniture is None:
                raise ValueError(f"Furniture item {cart_item.item_id} not found.")
            if furniture.stock < cart_item.quantity:
                raise ValueError(f"Insufficient stock for item {furniture.id}.")

            line_total = round(furniture.price * cart_item.quantity, 2)
            total += line_total
            order_items.append(
                OrderItem(
                    item_id=furniture.id,
                    name=furniture.name,
                    unit_price=furniture.price,
                    quantity=cart_item.quantity,
                    line_total=line_total,
                )
            )

        # Update stock only after validation passes for all items.
        # تحديث المخزون بعد نجاح التحقق الكامل.
        for cart_item in cart_items:
            inventory_items[cart_item.item_id].stock -= cart_item.quantity

        order = Order(
            id=self._next_order_id,
            user_id=user_id,
            items=order_items,
            total_price=round(total, 2),
            status="pending",
        )
        self._next_order_id += 1
        self._orders.setdefault(user_id, []).append(order)
        cart_service.clear_cart(user_id)
        return order

    def list_user_orders(self, user_id: int) -> List[Order]:
        return self._orders.get(user_id, [])

    def update_order_status(self, user_id: int, order_id: int, status: str) -> Order:
        if status not in {"pending", "shipped", "delivered"}:
            raise ValueError("Invalid order status.")
        for order in self._orders.get(user_id, []):
            if order.id == order_id:
                order.status = status
                return order
        raise KeyError("Order not found.")

    @staticmethod
    def to_dict(order: Order) -> dict:
        order_dict = asdict(order)
        return order_dict
