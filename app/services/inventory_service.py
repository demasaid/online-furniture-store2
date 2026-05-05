from typing import Dict, List, Optional

from app.models.furniture import Furniture


class InventoryService:
    def __init__(self) -> None:
        # In-memory storage: key=item_id, value=Furniture object.
        # تخزين مؤقت بالذاكرة: المفتاح id والقيمة كائن Furniture.
        self._items: Dict[int, Furniture] = {}

    def add_item(self, item: Furniture) -> None:
        # Prevent duplicate IDs to keep inventory consistent.
        # نمنع تكرار نفس الـ id للحفاظ على اتساق المخزون.
        if item.id in self._items:
            raise ValueError(f"Item with id {item.id} already exists.")
        self._items[item.id] = item

    def remove_item(self, item_id: int) -> None:
        # Remove item only if it exists.
        # نحذف العنصر فقط إذا كان موجود.
        if item_id not in self._items:
            raise KeyError(f"Item with id {item_id} not found.")
        del self._items[item_id]

    def update_quantity(self, item_id: int, quantity: int) -> None:
        # Quantity cannot be negative.
        # لا يمكن أن تكون الكمية سالبة.
        if quantity < 0:
            raise ValueError("Quantity cannot be negative.")
        if item_id not in self._items:
            raise KeyError(f"Item with id {item_id} not found.")
        self._items[item_id].stock = quantity

    def list_items(self) -> List[Furniture]:
        # Return all items as a list.
        # إرجاع كل العناصر على شكل قائمة.
        return list(self._items.values())

    def get_item(self, item_id: int) -> Optional[Furniture]:
        # Returns None if item does not exist.
        # ترجع None إذا العنصر غير موجود.
        return self._items.get(item_id)

    def search(
        self,
        name: Optional[str] = None,
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
    ) -> List[Furniture]:
        # Flexible filtering by name/category/price range.
        # بحث مرن حسب الاسم/التصنيف/مدى السعر.
        items = self.list_items()

        if name:
            name_lower = name.lower()
            items = [item for item in items if name_lower in item.name.lower()]
        if category:
            category_lower = category.lower()
            items = [item for item in items if item.category.lower() == category_lower]
        if min_price is not None:
            items = [item for item in items if item.price >= min_price]
        if max_price is not None:
            items = [item for item in items if item.price <= max_price]

        return items
