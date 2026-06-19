from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=6, max_length=72)

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Imię nie może być puste")
        return value

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).lower()

    @field_validator("password")
    @classmethod
    def validate_password_bytes(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Hasło jest za długie")
        return value


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=72)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).lower()

    @field_validator("password")
    @classmethod
    def validate_password_bytes(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Hasło jest za długie")
        return value


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Nazwa kategorii nie może być pusta")
        return value


class CategoryOut(BaseModel):
    id: int
    name: str
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OptionCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)

    @field_validator("title")
    @classmethod
    def clean_title(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Opcja nie może być pusta")
        return value


class OptionOut(BaseModel):
    id: int
    title: str
    is_active: bool
    category_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class HistoryOut(BaseModel):
    id: int
    user_id: int
    category_id: int
    selected_option_title: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RandomChoiceOut(BaseModel):
    selected_option_title: str
    history_id: int
    created_at: datetime
