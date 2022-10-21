from typing import Optional, Mapping, Union
from datetime import datetime, timedelta
from fastapi import status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext

from app.core.config import JWT_EXPIRE_MINUTES, JWT_REFRESH_TOKEN_EXPIRE_MINUTES, JWT_ALGORITHM, JWT_SECRET_KEY
from app.models.token import TokenPayload

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "/api/v1/auth/login")  # scopes = {"name": "description"}

CREDENTIALS_VALIDATE_EXCEPTION = CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

CREDENTIALS_USERNAME_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Incorrect username, email or password",
    headers={"WWW-Authenticate": "Bearer"},
)

CREDENTIALS_ROLE_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Incorrect role for user",
    headers={"WWW-Authenticate": "Bearer"},
)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)


def create_token(data: TokenPayload, expires_delta: Optional[timedelta] = None) -> str:
    data.exp = datetime.utcnow() + (expires_delta or timedelta(minutes=JWT_EXPIRE_MINUTES or 15))

    return jwt.encode(data.dict(), str(JWT_SECRET_KEY), algorithm=JWT_ALGORITHM)


def create_access_token(email: str, expires_delta: Optional[timedelta] = None) -> str:
    """
    Создаём access_token, время жизни которого обычно не более часа.
    """

    return create_token(data=TokenPayload(sub=email), expires_delta=expires_delta)


def create_refresh_token(email: str, host: str, user_agent: str, expires_delta: Optional[timedelta] = None) -> str:
    """
    Создаём refresh_token, такой же как и access_token, но с более длительным действием.
    """

    expires = expires_delta or timedelta(minutes=JWT_REFRESH_TOKEN_EXPIRE_MINUTES or (60 * 24 * 30))
    return create_token(data=TokenPayload(sub={"email": email, "host": host, "user_agent": user_agent}), expires_delta=expires)


def decode_access_token(token: str) -> Optional[Mapping[str, Union[str, int, float]]]:
    try:
        encoded_jwt: Mapping[str, Union[str, int, float]] = jwt.decode(token, str(JWT_SECRET_KEY), algorithms=[JWT_ALGORITHM])
    except JWTError:
        return None
    return encoded_jwt