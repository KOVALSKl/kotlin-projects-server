from uuid import uuid4
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from database import *
from database.models import DeliveryService, Store, Order, ClientDeliveryService, ClientStore, ClientOrder

router = APIRouter(
    prefix="/delivery",
)


@router.on_event("startup")
async def startup():
    """Создание необходимых таблиц"""
    database.create_table(
        "delivery_service",
        {
            "id": [DatabaseTypes.TEXT, DatabaseTypes.PRIMARY_KEY],
            "name": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL, DatabaseTypes.UNIQUE],
        }
    )

    database.create_table(
        "store",
        {
            "id": [DatabaseTypes.TEXT, DatabaseTypes.PRIMARY_KEY],
            "name": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL, DatabaseTypes.UNIQUE],
            "service_id": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL]
        },
        {
            "service_id": DatabaseReference(
                "delivery_service",
                "id",
                on_delete=DatabaseActions.CASCADE
            )
        }
    )

    database.create_table(
        "orders",
        {
            "id": [DatabaseTypes.TEXT, DatabaseTypes.PRIMARY_KEY],
            "title": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
            "date": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
            "amount": [DatabaseTypes.INTEGER, DatabaseTypes.NOT_NULL],
            "store_id": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
        },
        {
            "store_id": DatabaseReference(
                "store",
                "id",
                on_delete=DatabaseActions.CASCADE
            ),
        }
    )


@router.get("/services", tags=["services"])
async def get_channels():
    channels = database.select_many(
        "delivery_service",
        ["*"]
    )

    return JSONResponse(channels)


@router.post("/services", tags=["services"])
async def create_service(client_delivery_service: ClientDeliveryService):

    """Создание необходимых таблиц"""
    delivery_service_dict = client_delivery_service.model_dump()
    delivery_service_model = DeliveryService(
        **delivery_service_dict,
        id=uuid4()
    )

    database.insert("delivery_service", delivery_service_model.model_dump())


@router.put("/services", tags=["services"])
async def update_service(client_delivery_service: ClientDeliveryService):
    delivery_service_dict = client_delivery_service.model_dump(exclude={"id": True})

    database.update(
        "delivery_service",
        delivery_service_dict.keys(),
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": client_delivery_service.id
            }
        }),
        delivery_service_dict.values()
    )


@router.delete("/services/{service_id}", tags=["services"])
async def delete_service(service_id: str):

    database.delete(
        "delivery_service",
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": service_id
            }
        })
    )


@router.get("/{service_id}/stores", tags=["stores"])
async def get_store(service_id: str):
    sections = database.select_many(
        "store",
        ["id", "name", "service_id"],
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "service_id": service_id
            }
        })
    )

    return JSONResponse(sections)


@router.post("/stores", tags=["stores"])
async def create_store(store: ClientStore):
    store_dict = store.model_dump()
    store_model = Store(
        **store_dict,
        id=uuid4()
    )

    database.insert("store", store_model.model_dump())


@router.put("/stores", tags=["stores"])
async def update_store(store: ClientStore):
    client_store_dict = store.model_dump(exclude={
        "id": True,
        "service_id": True,
    })

    database.update(
        "store",
        client_store_dict.keys(),
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": store.id
            }
        }),
        client_store_dict.values()
    )


@router.delete("/stores/{store_id}", tags=["stores"])
async def delete_store(store_id: str):
    database.delete(
        "store",
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": store_id
            }
        })
    )


@router.get("/{service_id}/{store_id}", tags=["orders"])
async def get_store_orders(service_id: str, store_id: str):
    print("/{channel_id}/{section_id} - SECTION_ID  = " + f"{store_id}")
    orders = database.execute(f"""
        SELECT od.id, title, date, amount, store_id FROM orders od 
        JOIN store st on st.id = od.store_id 
        WHERE st.service_id = '{service_id}' AND st.id = '{store_id}';
    """).fetchall()

    print(service_id)
    print(orders)

    return orders


@router.post("/stores/{store_id}", tags=["orders"])
async def create_order(store_id: str, client_order: ClientOrder):
    client_order_dict = client_order.model_dump(exclude={"id": True})
    news_model = Order(
        **client_order_dict,
        id=uuid4()
    )

    database.insert("orders", news_model.model_dump())


@router.put("/stores/{store_id}", tags=["orders"])
async def update_order(store_id: str, client_order: ClientOrder):
    print("Order PUT " + f"{client_order.model_dump()}")
    client_order_dict = client_order.model_dump(exclude={
        "id": True,
        "store_id": True,
    })

    database.update(
        "orders",
        client_order_dict.keys(),
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": client_order.id,
                "store_id": client_order.store_id
            }
        }),
        client_order_dict.values()
    )


@router.delete("/stores/{store_id}/{order_id}", tags=["orders"])
async def delete_order(store_id: str, order_id: str):
    database.delete(
        "orders",
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": order_id
            }
        })
    )
