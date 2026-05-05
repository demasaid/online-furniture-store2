from typing import Dict, Optional

from passlib.context import CryptContext

from app.models.user import User


class UserService:
    def __init__(self) -> None:
        # In-memory users by id and email index for quick lookup.
        # تخزين المستخدمين بالذاكرة مع فهرس بالإيميل للوصول السريع.
        self._users_by_id: Dict[int, User] = {}
        self._id_by_email: Dict[str, int] = {}
        self._pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def register_user(self, user_id: int, name: str, email: str, password: str, address: str) -> User:
        # Email must be unique for registration.
        # يجب أن يكون الإيميل فريدًا عند التسجيل.
        email_key = email.lower()
        if email_key in self._id_by_email:
            raise ValueError("Email already registered.")

        password_hash = self._pwd_context.hash(password)
        user = User(id=user_id, name=name, email=email, password_hash=password_hash, address=address)
        self._users_by_id[user_id] = user
        self._id_by_email[email_key] = user_id
        return user

    def login(self, email: str, password: str) -> Optional[User]:
        # Return user only when credentials are valid.
        # يرجع المستخدم فقط إذا كانت البيانات صحيحة.
        email_key = email.lower()
        user_id = self._id_by_email.get(email_key)
        if user_id is None:
            return None

        user = self._users_by_id[user_id]
        if not self._pwd_context.verify(password, user.password_hash):
            return None
        return user

    def get_user(self, user_id: int) -> Optional[User]:
        return self._users_by_id.get(user_id)
