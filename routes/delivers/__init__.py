from uuid import uuid4
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from database import *
from database.models import DeliveryService, Courier, CourierOrder, \
    ClientDeliveryService, ClientCourier, ClientCourierOrder

router = APIRouter(
    prefix="/delivers",
)


@router.on_event("startup")
async def startup():
    """Создание необходимых таблиц"""
    database.create_table(
        "delivers_services",
        {
            "id": [DatabaseTypes.TEXT, DatabaseTypes.PRIMARY_KEY],
            "name": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL, DatabaseTypes.UNIQUE],
        }
    )

    database.create_table(
        "couriers",
        {
            "id": [DatabaseTypes.TEXT, DatabaseTypes.PRIMARY_KEY],
            "name": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL, DatabaseTypes.UNIQUE],
            "deliver_service_id": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL]
        },
        {
            "deliver_service_id": DatabaseReference(
                "delivers_services",
                "id",
                on_delete=DatabaseActions.CASCADE
            )
        }
    )

    database.create_table(
        "courier_orders",
        {
            "id": [DatabaseTypes.TEXT, DatabaseTypes.PRIMARY_KEY],
            "name": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
            "date": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
            "time": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
            "address": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
            "delivery_time": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
            "total_weight": [DatabaseTypes.INTEGER, DatabaseTypes.NOT_NULL],
            "items": [DatabaseTypes.INTEGER, DatabaseTypes.NOT_NULL],
            "total_amount": [DatabaseTypes.INTEGER, DatabaseTypes.NOT_NULL],
            "courier_id": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
        },
        {
            "courier_id": DatabaseReference(
                "couriers",
                "id",
                on_delete=DatabaseActions.CASCADE
            ),
        }
    )


@router.get("/services", tags=["delivers-services"])
async def get_services():
    depots = database.select_many(
        "delivers_services",
        ["*"]
    )

    return JSONResponse(depots)


@router.post("/services", tags=["delivers-services"])
async def create_service(client_delivery_service: ClientDeliveryService):

    """Создание необходимых таблиц"""
    delivery_service_dict = client_delivery_service.model_dump()
    delivery_service_model = DeliveryService(
        **delivery_service_dict,
    )

    database.insert("delivers_services", delivery_service_model.model_dump())


@router.put("/services", tags=["delivers-services"])
async def update_service(client_delivery_service: ClientDeliveryService):
    delivery_service_dict = client_delivery_service.model_dump(exclude={"id": True})

    database.update(
        "delivers_services",
        delivery_service_dict.keys(),
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": client_delivery_service.id
            }
        }),
        delivery_service_dict.values()
    )


@router.delete("/services/{service_id}", tags=["delivers-services"])
async def delete_service(service_id: str):

    database.delete(
        "delivers_services",
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": service_id
            }
        })
    )


@router.get("/{service_id}/couriers", tags=["couriers"])
async def get_couriers(service_id: str):
    sections = database.select_many(
        "couriers",
        ["id", "name", "deliver_service_id"],
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "deliver_service_id": service_id
            }
        })
    )

    print(f"couriers: {sections}")

    return JSONResponse(sections)


@router.post("/couriers", tags=["couriers"])
async def create_courier(courier: ClientCourier):
    courier_dict = courier.model_dump()
    route_model = Courier(
        **courier_dict,
    )

    database.insert("couriers", route_model.model_dump())


@router.put("/couriers", tags=["couriers"])
async def update_courier(courier: ClientCourier):
    courier_dict = courier.model_dump(exclude={
        "id": True,
        "deliver_service_id": True,
    })

    database.update(
        "couriers",
        courier_dict.keys(),
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": courier.id
            }
        }),
        courier_dict.values()
    )


@router.delete("/couriers/{courier_id}", tags=["couriers"])
async def delete_courier(courier_id: str):
    database.delete(
        "couriers",
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": courier_id
            }
        })
    )


@router.get("/{deliver_service_id}/{courier_id}", tags=["orders"])
async def get_courier_orders(deliver_service_id: str, courier_id: str):

    orders = database.execute(f"""
        SELECT ord.id, ord.name, date, time, 
        address, delivery_time, total_weight, items, total_amount, courier_id 
        FROM courier_orders ord 
        JOIN couriers co on co.id = ord.courier_id 
        WHERE co.deliver_service_id = '{deliver_service_id}' AND co.id = '{courier_id}';
    """).fetchall()

    print(f"orders: {orders}")

    return orders


@router.post("/couriers/{courier_id}", tags=["orders"])
async def create_order(courier_id: str, client_order: ClientCourierOrder):
    order_dict = client_order.model_dump()
    order_model = CourierOrder(
        **order_dict,
    )

    database.insert("courier_orders", order_model.model_dump())


@router.put("/couriers/{courier_id}", tags=["orders"])
async def update_order(courier_id: str, client_order: ClientCourierOrder):

    order_dict = client_order.model_dump(exclude={
        "id": True,
        "courier_id": True,
    })

    database.update(
        "courier_orders",
        order_dict.keys(),
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": client_order.id,
                "courier_id": client_order.courier_id
            }
        }),
        order_dict.values()
    )


@router.delete("/couriers/{courier_id}/{order_id}", tags=["orders"])
async def delete_order(courier_id: str, order_id: str):
    database.delete(
        "courier_orders",
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": order_id
            }
        })
    )
