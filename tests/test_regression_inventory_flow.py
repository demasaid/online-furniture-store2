from fastapi.testclient import TestClient

from app.main import app, inventory

# Test client for end-to-end API flow.
# عميل اختبار لسيناريو API كامل.
client = TestClient(app)


def setup_function() -> None:
    # Reset state before each regression run.
    # تصفير الحالة قبل كل تشغيل للاختبار.
    inventory._items.clear()


def test_regression_inventory_lifecycle_flow() -> None:
    # Regression goal:
    # If this flow ever breaks, we catch it quickly.
    # هدف الاختبار:
    # إذا انكسر هذا السيناريو لاحقًا، نكتشف المشكلة مباشرة.

    # 1) Create a furniture item.
    # 1) إنشاء عنصر أثاث.
    create_response = client.post(
        "/furniture",
        json={
            "id": 100,
            "name": "Regression Sofa",
            "description": "Initial description",
            "price": 999.99,
            "dimensions": "220x90x85",
            "stock": 4,
            "category": "Sofa",
        },
    )
    assert create_response.status_code == 201

    # 2) Verify item appears in list endpoint.
    # 2) التأكد أن العنصر يظهر في قائمة العناصر.
    list_response = client.get("/furniture")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1
    assert list_response.json()[0]["id"] == 100

    # 3) Update only stock quantity.
    # 3) تحديث الكمية فقط.
    quantity_response = client.put("/inventory/100/quantity", json={"quantity": 10})
    assert quantity_response.status_code == 200
    assert quantity_response.json()["stock"] == 10

    # 4) Update full furniture details.
    # 4) تحديث كامل بيانات العنصر.
    update_response = client.put(
        "/furniture/100",
        json={
            "name": "Regression Sofa V2",
            "description": "Updated description",
            "price": 1299.99,
            "dimensions": "230x95x90",
            "stock": 8,
            "category": "Sofa",
        },
    )
    assert update_response.status_code == 200
    updated_item = update_response.json()
    assert updated_item["name"] == "Regression Sofa V2"
    assert updated_item["price"] == 1299.99
    assert updated_item["stock"] == 8

    # 5) Delete the item.
    # 5) حذف العنصر.
    delete_response = client.delete("/furniture/100")
    assert delete_response.status_code == 204

    # 6) Confirm item is gone from details endpoint.
    # 6) التأكد أن العنصر لم يعد موجودًا.
    get_deleted_response = client.get("/furniture/100")
    assert get_deleted_response.status_code == 404

    # 7) Confirm list endpoint is empty again.
    # 7) التأكد أن القائمة أصبحت فارغة.
    final_list_response = client.get("/furniture")
    assert final_list_response.status_code == 200
    assert final_list_response.json() == []
