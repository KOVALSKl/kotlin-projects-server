from fastapi import APIRouter
from fastapi.exceptions import HTTPException

from database import *
from database.models import User, LoginUser, RegistrationUser

from lib import encode_jwt_token, decode_jwt_token, hash_password
from uuid import UUID

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


@router.on_event("startup")
async def startup():
    """Создание таблицы пользователей"""
    database.create_table(
        "users",
        {
            "id": [DatabaseTypes.TEXT, DatabaseTypes.PRIMARY_KEY],
            "name": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
            "surname": [DatabaseTypes.TEXT],
            "login": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL, DatabaseTypes.UNIQUE],
            "password": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
            "created_at": [DatabaseTypes.TEXT]
        }
    )


@router.post("/login")
async def login(user: LoginUser):
    hashed_password = hash_password(user.password)

    database_user = database.select_one(
        "users",
        ["*"],
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "login": user.login,
                "password": hashed_password
            }
        })
    )

    if not database_user:
        raise HTTPException(404, "Пользователь не найден")

    database_user["id"] = UUID(database_user["id"])

    database_user_model = User(**database_user)

    return database_user_model.model_dump(exclude={
        "created_at": True,
    })


@router.post("/registration")
async def registration(user: RegistrationUser):
    hashed_password = hash_password(user.password)

    database_user = database.select_one(
        "users",
        ["*"],
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "login": user.login
            }
        })
    )

    if database_user:
        raise HTTPException(400, "Пользователь существует")

    user.password = hashed_password

    database_user_model = User(**user.model_dump())

    database.insert(
        "users",
        database_user_model.model_dump()
    )

    return database_user_model.model_dump(exclude={
        "created_at": True,
    })
