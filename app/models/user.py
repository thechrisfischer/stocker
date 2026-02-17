from typing import Optional

from sqlmodel import SQLModel, Field
from passlib.hash import bcrypt


class UserBase(SQLModel):
    email: str = Field(max_length=255, unique=True, index=True)


class User(UserBase, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    password_hash: str = Field(max_length=255)
    is_active: bool = Field(default=True)

    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hash(password)

    def verify_password(self, password: str) -> bool:
        return bcrypt.verify(password, self.password_hash)


class UserCreate(SQLModel):
    email: str
    password: str


class UserRead(SQLModel):
    id: int
    email: str
    is_active: bool
