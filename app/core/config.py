from starlette.config import Config
from starlette.datastructures import Secret

config = Config(".env")

JWT_SECRET_KEY = config("JWT_SECRET_KEY", cast=Secret, default="")
JWT_ALGORITHM = config("JWT_ALGORITHM", cast=str, default="HS256")
JWT_EXPIRE_MINUTES = config("JWT_EXPIRE_MINUTES", cast=int, default=60)
JWT_REFRESH_TOKEN_EXPIRE_MINUTES = config("JWT_REFRESH_TOKEN_EXPIRE_MINUTES", cast=int, default=60 * 24 * 30)