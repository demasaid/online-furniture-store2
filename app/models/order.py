from dataclasses import dataclass
from typing import List


@dataclass
class OrderItem:
    # Snapshot of purchased item at checkout time.
    # نسخة محفوظة من العنصر وقت إتمام الشراء.
    item_id: int
    name: str
    unit_price: float
    quantity: int
    line_total: float


@dataclass
class Order:
    # Order entity stored after checkout.
    # كيان الطلب الذي يُحفظ بعد الدفع.
    id: int
    user_id: int
    items: List[OrderItem]
    total_price: float
    status: str
