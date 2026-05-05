from dataclasses import dataclass


# User entity used by auth and profile endpoints.
# كيان المستخدم المستخدم في المصادقة وملف الحساب.
@dataclass
class User:
    id: int
    name: str
    email: str
    password_hash: str
    address: str
