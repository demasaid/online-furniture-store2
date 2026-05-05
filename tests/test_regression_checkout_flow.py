from fastapi.testclient import TestClient

from app.main import app, carts, inventory, orders, users

client = TestClient(app)


def setup_function() -> None:
    inventory._items.clear()
    users._users_by_id.clear()
    users._id_by_email.clear()
    carts._carts.clear()
    orders._orders.clear()
    orders._next_order_id = 1


def test_regression_checkout_updates_everything() -> None:
    # This regression protects the "checkout updates all components" requirement.
    # هذا الاختبار يحمي سيناريو "الشراء يحدّث كل المكونات".
    client.post(
        "/users/register",
        json={
            "id": 22,
            "name": "Reem",
            "email": "reem@example.com",
            "password": "pass1234",
            "address": "Bethlehem",
        },
    )
    client.post(
        "/furniture",
        json={
            "id": 220,
            "name": "Regression Bed",
            "description": "King bed",
            "price": 1000,
            "dimensions": "200x180x120",
            "stock": 3,
            "category": "Bed",
        },
    )
    client.post("/cart/22/items", json={"item_id": 220, "quantity": 2})

    checkout_response = client.post("/checkout/22", json={"payment_method": "cash"})
    assert checkout_response.status_code == 201
    assert checkout_response.json()["status"] == "pending"

    # Inventory must be decremented.
    # يجب أن تنخفض كمية المخزون.
    item_response = client.get("/furniture/220")
    assert item_response.status_code == 200
    assert item_response.json()["stock"] == 1

    # Cart must be cleared after checkout.
    # يجب تفريغ السلة بعد إتمام الشراء.
    cart_response = client.get("/cart/22")
    assert cart_response.status_code == 200
    assert cart_response.json()["items"] == []
    assert cart_response.json()["total"] == 0

    # Order must be saved and visible in order history.
    # يجب حفظ الطلب وظهوره في تاريخ الطلبات.
    orders_response = client.get("/orders/22")
    assert orders_response.status_code == 200
    assert len(orders_response.json()) == 1
