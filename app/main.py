from dataclasses import asdict
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, Field

from app.models.furniture import Furniture
from app.services.cart_service import CartService
from app.services.inventory_service import InventoryService
from app.services.order_service import OrderService
from app.services.user_service import UserService

# FastAPI application instance.
# كائن تطبيق FastAPI الرئيسي.
app = FastAPI(title="Online Furniture Store API")
# Shared in-memory inventory service.
# خدمة مخزون مشتركة داخل الذاكرة.
inventory = InventoryService()
users = UserService()
carts = CartService()
orders = OrderService()


class FurnitureCreate(BaseModel):
    # Request body schema for creating a furniture item.
    # شكل البيانات المطلوبة لإضافة قطعة أثاث.
    id: int
    name: str
    description: str
    price: float = Field(ge=0)
    dimensions: str
    stock: int = Field(ge=0)
    category: str


class QuantityUpdate(BaseModel):
    # Request body schema for stock update.
    # شكل البيانات المطلوبة لتحديث الكمية.
    quantity: int = Field(ge=0)


class FurnitureUpdate(BaseModel):
    # Request body schema for full furniture update.
    # شكل البيانات المطلوبة لتحديث قطعة الأثاث كاملة.
    name: str
    description: str
    price: float = Field(ge=0)
    dimensions: str
    stock: int = Field(ge=0)
    category: str


class UserRegister(BaseModel):
    # Request body schema for user registration.
    # شكل البيانات المطلوبة لتسجيل مستخدم جديد.
    id: int
    name: str
    email: EmailStr
    password: str = Field(min_length=6)
    address: str


class UserLogin(BaseModel):
    # Request body schema for user login.
    # شكل البيانات المطلوبة لتسجيل الدخول.
    email: EmailStr
    password: str


class CartItemAdd(BaseModel):
    # Request body schema for adding item to cart.
    # شكل البيانات المطلوبة لإضافة عنصر للسلة.
    item_id: int
    quantity: int = Field(gt=0)


class CheckoutRequest(BaseModel):
    # Request body schema for checkout.
    # شكل البيانات المطلوبة لإتمام عملية الشراء.
    payment_method: str


class OrderStatusUpdate(BaseModel):
    # Request body schema for updating order status.
    # شكل البيانات المطلوبة لتحديث حالة الطلب.
    status: str


def _public_user(user_dict: dict) -> dict:
    # Hide password hash in API responses.
    # إخفاء كلمة المرور المشفرة من استجابة الـ API.
    user_dict.pop("password_hash", None)
    return user_dict


def _ensure_user_exists(user_id: int) -> None:
    # Guard helper: user must exist before cart/order actions.
    # دالة تحقق: المستخدم يجب أن يكون موجودًا قبل عمليات السلة/الطلب.
    if users.get_user(user_id) is None:
        raise HTTPException(status_code=404, detail="User not found")


@app.get("/health")
def health() -> dict:
    # Simple health check endpoint.
    # نقطة فحص للتأكد أن الـ API تعمل.
    return {"status": "ok"}


@app.get("/furniture")
def list_furniture(
    name: Optional[str] = None,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
) -> List[dict]:
    # Returns filtered furniture list (or all items).
    # ترجع قائمة الأثاث مع إمكانية التصفية.
    items = inventory.search(name=name, category=category, min_price=min_price, max_price=max_price)
    return [asdict(item) for item in items]


@app.get("/furniture/{item_id}")
def get_furniture(item_id: int) -> dict:
    # Returns one item by ID, or 404 if missing.
    # ترجع عنصر واحد حسب id أو 404 إذا غير موجود.
    item = inventory.get_item(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return asdict(item)


@app.post("/furniture", status_code=201)
def create_furniture(payload: FurnitureCreate) -> dict:
    # Converts validated request to Furniture object and stores it.
    # تحويل البيانات (بعد التحقق) إلى Furniture ثم تخزينها.
    try:
        new_item = Furniture(**payload.model_dump())
        inventory.add_item(new_item)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return asdict(new_item)


@app.put("/inventory/{item_id}/quantity")
def update_quantity(item_id: int, payload: QuantityUpdate) -> dict:
    # Updates stock for an existing item.
    # تحديث المخزون لعنصر موجود.
    try:
        inventory.update_quantity(item_id, payload.quantity)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    item = inventory.get_item(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return asdict(item)


@app.put("/furniture/{item_id}")
def update_furniture(item_id: int, payload: FurnitureUpdate) -> dict:
    # Updates all item fields except ID.
    # تحديث كامل للعنصر (ما عدا id).
    item = inventory.get_item(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    item.name = payload.name
    item.description = payload.description
    item.price = payload.price
    item.dimensions = payload.dimensions
    item.stock = payload.stock
    item.category = payload.category
    return asdict(item)


@app.delete("/furniture/{item_id}", status_code=204)
def delete_furniture(item_id: int) -> None:
    # Deletes an item from inventory.
    # حذف عنصر من المخزون.
    try:
        inventory.remove_item(item_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/users/register", status_code=201)
def register_user(payload: UserRegister) -> dict:
    # Registers user with hashed password.
    # تسجيل مستخدم جديد مع تشفير كلمة المرور.
    try:
        user = users.register_user(
            user_id=payload.id,
            name=payload.name,
            email=str(payload.email),
            password=payload.password,
            address=payload.address,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _public_user(asdict(user))


@app.post("/users/login")
def login_user(payload: UserLogin) -> dict:
    # Validates user credentials.
    # التحقق من بيانات تسجيل الدخول.
    user = users.login(email=str(payload.email), password=payload.password)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"message": "Login successful", "user": _public_user(asdict(user))}


@app.get("/users/{user_id}")
def get_user_profile(user_id: int) -> dict:
    # Returns user profile by id.
    # إرجاع بيانات المستخدم حسب المعرّف.
    user = users.get_user(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return _public_user(asdict(user))


@app.post("/cart/{user_id}/items", status_code=201)
def add_item_to_cart(user_id: int, payload: CartItemAdd) -> dict:
    # Adds a furniture item to user cart.
    # إضافة عنصر أثاث إلى سلة المستخدم.
    _ensure_user_exists(user_id)
    item = inventory.get_item(payload.item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Furniture item not found")
    if item.stock < payload.quantity:
        raise HTTPException(status_code=400, detail="Requested quantity exceeds stock")

    try:
        carts.add_item(user_id=user_id, item_id=payload.item_id, quantity=payload.quantity)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"message": "Item added to cart"}


@app.delete("/cart/{user_id}/items/{item_id}", status_code=204)
def remove_item_from_cart(user_id: int, item_id: int) -> None:
    # Removes item from user cart.
    # إزالة عنصر من سلة المستخدم.
    _ensure_user_exists(user_id)
    try:
        carts.remove_item(user_id=user_id, item_id=item_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/cart/{user_id}")
def get_cart(user_id: int, discount_percentage: float = 0) -> dict:
    # Returns cart details with totals and optional discount.
    # عرض تفاصيل السلة مع الإجمالي والخصم الاختياري.
    _ensure_user_exists(user_id)
    try:
        return carts.get_cart_summary(
            user_id=user_id,
            inventory_items=inventory._items,
            discount_percentage=discount_percentage,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/checkout/{user_id}", status_code=201)
def checkout(user_id: int, payload: CheckoutRequest) -> dict:
    # Converts current cart into an order and updates stock.
    # تحويل السلة الحالية إلى طلب مع تحديث المخزون.
    _ensure_user_exists(user_id)
    try:
        order = orders.checkout(
            user_id=user_id,
            cart_service=carts,
            inventory_items=inventory._items,
            payment_method=payload.payment_method,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return orders.to_dict(order)


@app.get("/orders/{user_id}")
def list_orders(user_id: int) -> List[dict]:
    # Returns all orders for one user.
    # إرجاع جميع الطلبات الخاصة بمستخدم واحد.
    _ensure_user_exists(user_id)
    return [orders.to_dict(order) for order in orders.list_user_orders(user_id)]


@app.put("/orders/{user_id}/{order_id}/status")
def update_order_status(user_id: int, order_id: int, payload: OrderStatusUpdate) -> dict:
    # Updates order status (pending/shipped/delivered).
    # تحديث حالة الطلب (pending/shipped/delivered).
    _ensure_user_exists(user_id)
    try:
        order = orders.update_order_status(user_id=user_id, order_id=order_id, status=payload.status)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return orders.to_dict(order)

