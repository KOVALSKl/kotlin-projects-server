from uuid import uuid4
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from database import *
from database.models import Restaurant, DishCategory, Dish, \
    ClientRestaurant, ClientDishCategory, ClientDish

router = APIRouter(
    prefix="/restaurants",
)


@router.on_event("startup")
async def startup():
    """Создание необходимых таблиц"""
    database.create_table(
        "restaurants",
        {
            "id": [DatabaseTypes.TEXT, DatabaseTypes.PRIMARY_KEY],
            "name": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL, DatabaseTypes.UNIQUE],
        }
    )

    database.create_table(
        "dish_categories",
        {
            "id": [DatabaseTypes.TEXT, DatabaseTypes.PRIMARY_KEY],
            "name": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL, DatabaseTypes.UNIQUE],
            "restaurant_id": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL]
        },
        {
            "restaurant_id": DatabaseReference(
                "restaurants",
                "id",
                on_delete=DatabaseActions.CASCADE
            )
        }
    )

    database.create_table(
        "dishes",
        {
            "id": [DatabaseTypes.TEXT, DatabaseTypes.PRIMARY_KEY],
            "name": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
            "price": [DatabaseTypes.INTEGER, DatabaseTypes.NOT_NULL],
            "calories": [DatabaseTypes.INTEGER, DatabaseTypes.NOT_NULL],
            "ingredients": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
            "is_vegetarian": [DatabaseTypes.INTEGER, DatabaseTypes.NOT_NULL],
            "is_spicy": [DatabaseTypes.INTEGER, DatabaseTypes.NOT_NULL],
            "description": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
            "score": [DatabaseTypes.INTEGER, DatabaseTypes.NOT_NULL],
            "category_id": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
        },
        {
            "category_id": DatabaseReference(
                "dish_categories",
                "id",
                on_delete=DatabaseActions.CASCADE
            ),
        }
    )


@router.get("/places", tags=["restaurants"])
async def get_restaurants():
    depots = database.select_many(
        "restaurants",
        ["*"]
    )

    return JSONResponse(depots)


@router.post("/places", tags=["restaurants"])
async def create_restaurant(client_restaurant: ClientRestaurant):

    """Создание необходимых таблиц"""
    client_restaurant_dict = client_restaurant.model_dump()
    delivery_service_model = Restaurant(
        **client_restaurant_dict
    )

    database.insert("restaurants", delivery_service_model.model_dump())


@router.put("/places", tags=["dish-categories"])
async def update_restaurant(client_restaurant: ClientRestaurant):
    client_restaurant_dict = client_restaurant.model_dump(exclude={"id": True})

    database.update(
        "restaurants",
        client_restaurant_dict.keys(),
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": client_restaurant.id
            }
        }),
        client_restaurant_dict.values()
    )


@router.delete("/places/{restaurant_id}", tags=["dish-categories"])
async def delete_restaurant(restaurant_id: str):

    database.delete(
        "restaurants",
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": restaurant_id
            }
        })
    )


@router.get("/{restaurant_id}/categories", tags=["dish-categories"])
async def get_categories(restaurant_id: str):
    dish_categories = database.select_many(
        "dish_categories",
        ["id", "name", "restaurant_id"],
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "restaurant_id": restaurant_id
            }
        })
    )

    return JSONResponse(dish_categories)


@router.post("/categories", tags=["dish-categories"])
async def create_category(courier: ClientDishCategory):
    courier_dict = courier.model_dump()
    route_model = DishCategory(
        **courier_dict,
    )

    database.insert("dish_categories", route_model.model_dump())


@router.put("/categories", tags=["dish-categories"])
async def update_category(courier: ClientDishCategory):
    category_dict = courier.model_dump(exclude={
        "id": True,
        "restaurant_id": True,
    })

    database.update(
        "dish_categories",
        category_dict.keys(),
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": courier.id
            }
        }),
        category_dict.values()
    )


@router.delete("/categories/{courier_id}", tags=["dish-categories"])
async def delete_category(courier_id: str):
    database.delete(
        "dish_categories",
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": courier_id
            }
        })
    )


@router.get("/{restaurant_id}/{category_id}", tags=["orders"])
async def get_category_dishes(restaurant_id: str, category_id: str):

    orders = database.execute(f"""
        SELECT dish.id, dish.name, price, calories, 
        ingredients, is_vegetarian, is_spicy, description, score, category_id 
        FROM dishes dish 
        JOIN dish_categories dc on dc.id = dish.category_id 
        WHERE dc.restaurant_id = '{restaurant_id}' AND dc.id = '{category_id}';
    """).fetchall()

    return orders


@router.post("/categories/{category_id}", tags=["orders"])
async def create_dish(category_id: str, client_dish: ClientDish):
    dish_dict = client_dish.model_dump()
    dish_model = Dish(
        **dish_dict
    )

    database.insert("dishes", dish_model.model_dump())


@router.put("/categories/{category_id}", tags=["orders"])
async def update_dish(category_id: str, client_dish: ClientDish):

    dish_dict = client_dish.model_dump(exclude={
        "id": True,
        "category_id": True,
    })

    database.update(
        "dishes",
        dish_dict.keys(),
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": client_dish.id,
                "category_id": client_dish.category_id
            }
        }),
        dish_dict.values()
    )


@router.delete("/categories/{category_id}/{dish_id}", tags=["orders"])
async def delete_dish(category_id: str, dish_id: str):
    database.delete(
        "dishes",
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": dish_id
            }
        })
    )
