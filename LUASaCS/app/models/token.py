from typing import Optional, List
from datetime import datetime
from fastapi import Form
from sqlmodel import SQLModel, Field, Column, INTEGER
# from pydantic import EmailStr

_token_example = "_" * 36 + "." + "_" * 54 + "." + "_" * 42


class OAuth2RefreshRequestForm(SQLModel):
    """
    Форма запроса Refresh Token'а
    """

    grant_type: str = Form(None, regex="refresh_token", description="Должно равняться `refresh_token` для обновления токена")
    refresh_token: str = Form(..., example=_token_example)

    class Config:
        schema_extra = {
            "example": {
                "grant_type": "refresh_token",
                "refresh_token": _token_example,
            },
        }


class TokenPayload(SQLModel):
    """
    Структура токена
    """

    sub: str = Field(..., description="Почта")
    exp: Optional[datetime] = Field(default=None, description="Дата истекания токена")


class Token(SQLModel):
    """
    Форма ответа при авторизации
    Форма ответа при запросе на обновление Access Token'а через Refresh Token
    """

    access_token: str = Field(..., title="Access Token")
    refresh_token: Optional[str] = Field(default=None, title="Refresh Token")
    token_type: str = Field(...)
    expires_in: Optional[int] = Field(default=None, description="Время жизни токена в минутах")

    class Config:
        schema_extra = {
            "example": {
                "access_token": _token_example,
                "refresh_token": _token_example,
                "token_type": "Bearer",
                "expires_in": 43200,
            },
        }


class TokenData(SQLModel):
    """
    Валидация данных при создании токена
    """

    email: str = Field(..., title="Почта")
    scopes: List[str] = Field(default=[], description = "Набор прав пользователя, указанный через scopes")