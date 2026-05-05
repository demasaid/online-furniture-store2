import pytest

from app.models.furniture import Chair
from app.services.inventory_service import InventoryService


def test_add_and_get_item() -> None:
    # Create service instance for this unit test.
    # إنشاء نسخة خدمة للمخزون لهذا الاختبار.
    service = InventoryService()
    # Build sample chair object.
    # تجهيز عنصر كرسي تجريبي.
    chair = Chair(
        id=1,
        name="Office Chair",
        description="Ergonomic chair",
        price=250.0,
        dimensions="60x60x100",
        stock=5,
        category="Chair",
    )

    # Add item then retrieve it by ID.
    # إضافة العنصر ثم جلبه عبر الـ ID.
    service.add_item(chair)

    stored = service.get_item(1)
    # Verify item exists and fields match expected values.
    # التأكد أن العنصر موجود وأن القيم صحيحة.
    assert stored is not None
    assert stored.name == "Office Chair"


def test_update_quantity() -> None:
    # Start with one item in inventory.
    # بدء الاختبار بعنصر واحد في المخزون.
    service = InventoryService()
    chair = Chair(
        id=2,
        name="Dining Chair",
        description="Wooden chair",
        price=120.0,
        dimensions="45x45x90",
        stock=3,
        category="Chair",
    )
    service.add_item(chair)

    # Update stock from 3 to 9.
    # تحديث الكمية من 3 إلى 9.
    service.update_quantity(2, 9)

    assert service.get_item(2).stock == 9


def test_search_by_category_and_price() -> None:
    # Add two chairs with different prices.
    # إضافة عنصرين من نفس التصنيف بأسعار مختلفة.
    service = InventoryService()
    service.add_item(
        Chair(
            id=3,
            name="Basic Chair",
            description="Simple chair",
            price=80.0,
            dimensions="40x40x85",
            stock=10,
            category="Chair",
        )
    )
    service.add_item(
        Chair(
            id=4,
            name="Premium Chair",
            description="Comfort chair",
            price=300.0,
            dimensions="50x50x95",
            stock=4,
            category="Chair",
        )
    )

    # Search by category + price range.
    # البحث حسب التصنيف ومدى السعر.
    results = service.search(category="chair", min_price=100, max_price=350)
    # Only the premium chair should match.
    # فقط الكرسي الأغلى لازم يظهر.
    assert len(results) == 1
    assert results[0].id == 4


def test_duplicate_add_raises_value_error() -> None:
    # Adding same ID twice should raise ValueError.
    # إضافة نفس الـ ID مرتين يجب أن تعطي خطأ ValueError.
    service = InventoryService()
    item = Chair(
        id=5,
        name="Study Chair",
        description="Student chair",
        price=70.0,
        dimensions="42x42x80",
        stock=7,
        category="Chair",
    )
    service.add_item(item)

    with pytest.raises(ValueError):
        service.add_item(item)
