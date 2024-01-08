from uuid import uuid4
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from database import *
from database.models import Tram, TramDepot, TramRoute, ClientTram, ClientTramDepot, ClientTramRoute

router = APIRouter(
    prefix="/trams",
)


@router.on_event("startup")
async def startup():
    """Создание необходимых таблиц"""
    database.create_table(
        "tram_depots",
        {
            "id": [DatabaseTypes.TEXT, DatabaseTypes.PRIMARY_KEY],
            "name": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL, DatabaseTypes.UNIQUE],
        }
    )

    database.create_table(
        "tram_routes",
        {
            "id": [DatabaseTypes.TEXT, DatabaseTypes.PRIMARY_KEY],
            "name": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL, DatabaseTypes.UNIQUE],
            "depot_id": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL]
        },
        {
            "depot_id": DatabaseReference(
                "tram_depots",
                "id",
                on_delete=DatabaseActions.CASCADE
            )
        }
    )

    database.create_table(
        "trams",
        {
            "id": [DatabaseTypes.TEXT, DatabaseTypes.PRIMARY_KEY],
            "number": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
            "driver_name": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
            "conductor_name": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
            "start_date": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
            "trip_number": [DatabaseTypes.INTEGER, DatabaseTypes.NOT_NULL],
            "route_id": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
        },
        {
            "route_id": DatabaseReference(
                "tram_routes",
                "id",
                on_delete=DatabaseActions.CASCADE
            ),
        }
    )


@router.get("/depots", tags=["tram-depots"])
async def get_depots():
    depots = database.select_many(
        "tram_depots",
        ["*"]
    )

    return JSONResponse(depots)


@router.post("/depots", tags=["tram-depots"])
async def create_depot(tram_depot: ClientTramDepot):

    """Создание необходимых таблиц"""
    client_depot_dict = tram_depot.model_dump()
    delivery_service_model = TramDepot(
        **client_depot_dict,
        id=uuid4()
    )

    database.insert("tram_depots", delivery_service_model.model_dump())


@router.put("/depots", tags=["tram-depots"])
async def update_depot(tram_depot: ClientTramDepot):
    client_depot_dict = tram_depot.model_dump(exclude={"id": True})

    database.update(
        "tram_depots",
        client_depot_dict.keys(),
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": tram_depot.id
            }
        }),
        client_depot_dict.values()
    )


@router.delete("/depots/{depot_id}", tags=["tram-depots"])
async def delete_depot(depot_id: str):

    database.delete(
        "tram_depots",
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": depot_id
            }
        })
    )


@router.get("/{depot_id}/routes", tags=["tram-routes"])
async def get_routes(depot_id: str):
    sections = database.select_many(
        "tram_routes",
        ["id", "name", "depot_id"],
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "depot_id": depot_id
            }
        })
    )

    return JSONResponse(sections)


@router.post("/routes", tags=["tram-routes"])
async def create_route(route: ClientTramRoute):
    route_dict = route.model_dump()
    route_model = TramRoute(
        **route_dict,
        id=uuid4()
    )

    database.insert("tram_routes", route_model.model_dump())


@router.put("/routes", tags=["tram-routes"])
async def update_route(route: ClientTramRoute):
    client_route_dict = route.model_dump(exclude={
        "id": True,
        "depot_id": True,
    })

    database.update(
        "tram_routes",
        client_route_dict.keys(),
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": route.id
            }
        }),
        client_route_dict.values()
    )


@router.delete("/routes/{route_id}", tags=["tram-routes"])
async def delete_route(route_id: str):
    database.delete(
        "tram_routes",
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": route_id
            }
        })
    )


@router.get("/{tram_depot_id}/{route_id}", tags=["trams"])
async def get_route_trams(tram_depot_id: str, route_id: str):

    trams = database.execute(f"""
        SELECT tr.id, number, driver_name, conductor_name, start_date, trip_number, route_id FROM trams tr 
        JOIN tram_routes rt on rt.id = tr.route_id 
        WHERE rt.depot_id = '{tram_depot_id}' AND rt.id = '{route_id}';
    """).fetchall()

    print(route_id)
    print(trams)

    return trams


@router.post("/routes/{route_id}", tags=["trams"])
async def create_tram(route_id: str, client_tram: ClientTram):
    client_transport_dict = client_tram.model_dump(exclude={"id": True})
    news_model = Tram(
        **client_transport_dict,
        id=uuid4()
    )

    database.insert("trams", news_model.model_dump())


@router.put("/routes/{route_id}", tags=["trams"])
async def update_tram(route_id: str, client_tram: ClientTram):

    client_transport_dict = client_tram.model_dump(exclude={
        "id": True,
        "route_id": True,
    })

    database.update(
        "trams",
        client_transport_dict.keys(),
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": client_tram.id,
                "route_id": client_tram.route_id
            }
        }),
        client_transport_dict.values()
    )


@router.delete("/routes/{route_id}/{tram_id}", tags=["trams"])
async def delete_tram(route_id: str, tram_id: str):
    database.delete(
        "trams",
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": tram_id
            }
        })
    )
