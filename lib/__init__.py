import jwt
import hashlib

from fastapi.exceptions import HTTPException

from jwt import PyJWTError
from config import config

JWT_KEY = config['keys']['JWT_KEY']
HASH_KEY = config['keys']['SHA256_KEY']


def hash_password(password: str) -> str:
    """Хэширование пароля используя алгоритм SHA256"""
    password_bytes = password.encode("utf-8")
    salt_bytes = HASH_KEY.encode("utf-8")

    hash_function = hashlib.sha256()
    hash_function.update(salt_bytes + password_bytes)

    hashed_password = hash_function.hexdigest()
    return hashed_password


def encode_jwt_token(model: dict) -> str:
    try:
        encoded_jwt = jwt.encode(model, JWT_KEY, algorithm="HS256")
        return encoded_jwt
    except PyJWTError:
        raise HTTPException(401, "Ошибка формирования токена авторизации")


def decode_jwt_token(token: str) -> dict:
    try:
        decoded_jwt = jwt.decode(token, JWT_KEY, algorithms=['HS256'])
        return decoded_jwt
    except PyJWTError:
        raise HTTPException(401, "Ошибка парсинга токена авторизации")


