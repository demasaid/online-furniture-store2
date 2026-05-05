from fastapi.testclient import TestClient

from app.main import app, carts, inventory, orders, users

# Test client simulates HTTP calls to FastAPI without running a real server.
# هذا العميل يحاكي طلبات HTTP بدون تشغيل سيرفر فعلي.
client = TestClient(app)


def setup_function() -> None:
    # Run before each test to keep tests independent.
    # تعمل قبل كل اختبار حتى لا يؤثر اختبار على الآخر.
    inventory._items.clear()  # Reset in-memory state between tests.
    users._users_by_id.clear()  # Reset users between tests.
    users._id_by_email.clear()  # Reset email index between tests.
    carts._carts.clear()  # Reset carts between tests.
    orders._orders.clear()  # Reset orders between tests.
    orders._next_order_id = 1  # Reset order id counter.


def test_health() -> None:
    # 1) Send GET request to health endpoint.
    # 1) نرسل طلب GET لنقطة health.
    response = client.get("/health")
    # 2) Verify status code and response body.
    # 2) نتحقق من كود الاستجابة والمحتوى.
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_and_get_furniture() -> None:
    # Prepare a valid furniture item payload.
    # تجهيز بيانات عنصر أثاث صحيحة.
    payload = {
        "id": 10,
        "name": "Corner Sofa",
        "description": "Large L-shaped sofa",
        "price": 1500,
        "dimensions": "250x180x85",
        "stock": 2,
        "category": "Sofa",
    }
    # Create the item through POST /furniture.
    # إنشاء العنصر عبر POST /furniture.
    create_response = client.post("/furniture", json=payload)
    assert create_response.status_code == 201

    # Fetch the same item and verify returned data.
    # جلب نفس العنصر والتأكد من البيانات.
    get_response = client.get("/furniture/10")
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Corner Sofa"


def test_update_furniture() -> None:
    # First create an item, then update it.
    # أولًا ننشئ عنصر، ثم نعدله.
    client.post(
        "/furniture",
        json={
            "id": 12,
            "name": "Small Table",
            "description": "Old description",
            "price": 200,
            "dimensions": "80x80x75",
            "stock": 5,
            "category": "Table",
        },
    )

    # Update full item fields through PUT /furniture/{id}.
    # تحديث كامل بيانات العنصر عبر PUT /furniture/{id}.
    update_response = client.put(
        "/furniture/12",
        json={
            "name": "Large Table",
            "description": "Updated description",
            "price": 350,
            "dimensions": "140x90x75",
            "stock": 3,
            "category": "Table",
        },
    )
    # Verify update happened correctly.
    # التأكد أن التحديث تم بشكل صحيح.
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Large Table"
    assert update_response.json()["price"] == 350


def test_delete_furniture() -> None:
    # Create an item that we will delete.
    # إنشاء عنصر ليتم حذفه.
    client.post(
        "/furniture",
        json={
            "id": 13,
            "name": "Cabinet A",
            "description": "Storage cabinet",
            "price": 500,
            "dimensions": "100x45x180",
            "stock": 2,
            "category": "Cabinet",
        },
    )

    # Delete item and verify 204 (No Content).
    # حذف العنصر والتأكد من 204.
    delete_response = client.delete("/furniture/13")
    assert delete_response.status_code == 204

    # Ensure item no longer exists (should return 404).
    # التأكد أن العنصر لم يعد موجودًا (يرجع 404).
    get_response = client.get("/furniture/13")
    assert get_response.status_code == 404


def test_register_and_get_user_profile() -> None:
    register_response = client.post(
        "/users/register",
        json={
            "id": 1,
            "name": "Dema",
            "email": "dema@example.com",
            "password": "secret123",
            "address": "Nablus",
        },
    )
    assert register_response.status_code == 201
    assert register_response.json()["email"] == "dema@example.com"
    assert "password_hash" not in register_response.json()

    get_response = client.get("/users/1")
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Dema"


def test_login_success_and_failure() -> None:
    client.post(
        "/users/register",
        json={
            "id": 2,
            "name": "Sara",
            "email": "sara@example.com",
            "password": "mypassword",
            "address": "Ramallah",
        },
    )

    success_response = client.post(
        "/users/login",
        json={"email": "sara@example.com", "password": "mypassword"},
    )
    assert success_response.status_code == 200
    assert success_response.json()["message"] == "Login successful"

    fail_response = client.post(
        "/users/login",
        json={"email": "sara@example.com", "password": "wrong"},
    )
    assert fail_response.status_code == 401


def test_cart_checkout_and_orders_flow() -> None:
    client.post(
        "/users/register",
        json={
            "id": 7,
            "name": "Lina",
            "email": "lina@example.com",
            "password": "password123",
            "address": "Jerusalem",
        },
    )
    client.post(
        "/furniture",
        json={
            "id": 70,
            "name": "Dining Table",
            "description": "Wood table",
            "price": 400,
            "dimensions": "140x80x75",
            "stock": 5,
            "category": "Table",
        },
    )

    add_response = client.post("/cart/7/items", json={"item_id": 70, "quantity": 2})
    assert add_response.status_code == 201

    cart_response = client.get("/cart/7?discount_percentage=10")
    assert cart_response.status_code == 200
    assert cart_response.json()["subtotal"] == 800
    assert cart_response.json()["total"] == 720

    checkout_response = client.post("/checkout/7", json={"payment_method": "cash"})
    assert checkout_response.status_code == 201
    assert checkout_response.json()["status"] == "pending"
    assert checkout_response.json()["total_price"] == 800

    item_response = client.get("/furniture/70")
    assert item_response.status_code == 200
    assert item_response.json()["stock"] == 3

    orders_response = client.get("/orders/7")
    assert orders_response.status_code == 200
    assert len(orders_response.json()) == 1


def test_update_order_status() -> None:
    client.post(
        "/users/register",
        json={
            "id": 8,
            "name": "Maha",
            "email": "maha@example.com",
            "password": "password123",
            "address": "Hebron",
        },
    )
    client.post(
        "/furniture",
        json={
            "id": 80,
            "name": "Office Desk",
            "description": "Desk",
            "price": 250,
            "dimensions": "120x60x75",
            "stock": 2,
            "category": "Table",
        },
    )
    client.post("/cart/8/items", json={"item_id": 80, "quantity": 1})
    checkout_response = client.post("/checkout/8", json={"payment_method": "card"})
    order_id = checkout_response.json()["id"]

    status_response = client.put(
        f"/orders/8/{order_id}/status",
        json={"status": "shipped"},
    )
    assert status_response.status_code == 200
    assert status_response.json()["status"] == "shipped"

