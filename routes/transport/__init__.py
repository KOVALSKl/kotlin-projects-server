from uuid import uuid4
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from database import *
from database.models import Depot, Route, Transport, ClientDepot, ClientRoute, ClientTransport

router = APIRouter(
    prefix="/transport",
    tags=["transport"]
)


@router.on_event("startup")
async def startup():
    """Создание необходимых таблиц"""
    database.create_table(
        "depots",
        {
            "id": [DatabaseTypes.TEXT, DatabaseTypes.PRIMARY_KEY],
            "name": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL, DatabaseTypes.UNIQUE],
        }
    )

    database.create_table(
        "routes",
        {
            "id": [DatabaseTypes.TEXT, DatabaseTypes.PRIMARY_KEY],
            "name": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL, DatabaseTypes.UNIQUE],
            "depot_id": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL]
        },
        {
            "depot_id": DatabaseReference(
                "depots",
                "id",
                on_delete=DatabaseActions.CASCADE
            )
        }
    )

    database.create_table(
        "transports",
        {
            "id": [DatabaseTypes.TEXT, DatabaseTypes.PRIMARY_KEY],
            "number": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
            "departure_time": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
            "return_time": [DatabaseTypes.INTEGER, DatabaseTypes.NOT_NULL],
            "route_id": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
        },
        {
            "route_id": DatabaseReference(
                "routes",
                "id",
                on_delete=DatabaseActions.CASCADE
            ),
        }
    )


@router.get("/depots")
async def get_depots():
    depots = database.select_many(
        "depots",
        ["*"]
    )

    return JSONResponse(depots)


@router.post("/depots")
async def create_depot(client_depot: ClientDepot):

    """Создание необходимых таблиц"""
    client_depot_dict = client_depot.model_dump()
    delivery_service_model = Depot(
        **client_depot_dict,
        id=uuid4()
    )

    database.insert("depots", delivery_service_model.model_dump())


@router.put("/depots")
async def update_service(client_depot: ClientDepot):
    client_depot_dict = client_depot.model_dump(exclude={"id": True})

    database.update(
        "depots",
        client_depot_dict.keys(),
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": client_depot.id
            }
        }),
        client_depot_dict.values()
    )


@router.delete("/depots/{depot_id}")
async def delete_service(depot_id: str):

    database.delete(
        "depots",
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": depot_id
            }
        })
    )


@router.get("/{depot_id}/routes")
async def get_store(depot_id: str):
    sections = database.select_many(
        "routes",
        ["id", "name", "depot_id"],
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "depot_id": depot_id
            }
        })
    )

    return JSONResponse(sections)


@router.post("/routes")
async def create_store(route: ClientRoute):
    route_dict = route.model_dump()
    route_model = Route(
        **route_dict,
        id=uuid4()
    )

    database.insert("routes", route_model.model_dump())


@router.put("/routes")
async def update_store(route: ClientRoute):
    client_route_dict = route.model_dump(exclude={
        "id": True,
        "depot_id": True,
    })

    database.update(
        "routes",
        client_route_dict.keys(),
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": route.id
            }
        }),
        client_route_dict.values()
    )


@router.delete("/routes/{route_id}")
async def delete_store(route_id: str):
    database.delete(
        "routes",
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": route_id
            }
        })
    )


@router.get("/{depot_id}/{route_id}")
async def get_store_orders(depot_id: str, route_id: str):

    orders = database.execute(f"""
        SELECT tr.id, number, departure_time, return_time, route_id FROM transports tr 
        JOIN routes rt on rt.id = tr.route_id 
        WHERE rt.depot_id = '{depot_id}' AND rt.id = '{route_id}';
    """).fetchall()

    print(route_id)
    print(orders)

    return orders


@router.post("/routes/{route_id}")
async def create_order(route_id: str, client_transport: ClientTransport):
    client_transport_dict = client_transport.model_dump(exclude={"id": True})
    news_model = Transport(
        **client_transport_dict,
        id=uuid4()
    )

    database.insert("transports", news_model.model_dump())


@router.put("/routes/{route_id}")
async def update_order(route_id: str, client_transport: ClientTransport):

    client_transport_dict = client_transport.model_dump(exclude={
        "id": True,
        "store_id": True,
    })

    database.update(
        "transports",
        client_transport_dict.keys(),
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": client_transport.id,
                "route_id": client_transport.route_id
            }
        }),
        client_transport_dict.values()
    )


@router.delete("/routes/{route_id}/{transport_id}")
async def delete_order(route_id: str, transport_id: str):
    database.delete(
        "transports",
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": transport_id
            }
        })
    )
