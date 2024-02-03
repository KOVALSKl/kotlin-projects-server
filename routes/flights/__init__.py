from uuid import uuid4
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from database import *
from database.models import FlightDirection, FlightDateTime, FlightTicket, \
    ClientFlightDirection, ClientFlightDateTime, ClientFlightTicket

router = APIRouter(
    prefix="/flights",
)


@router.on_event("startup")
async def startup():
    """Создание необходимых таблиц"""
    database.create_table(
        "flight_directions",
        {
            "id": [DatabaseTypes.TEXT, DatabaseTypes.PRIMARY_KEY],
            "name": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL, DatabaseTypes.UNIQUE],
        }
    )

    database.create_table(
        "flight_datetime",
        {
            "id": [DatabaseTypes.TEXT, DatabaseTypes.PRIMARY_KEY],
            "name": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL, DatabaseTypes.UNIQUE],
            "flight_id": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL]
        },
        {
            "flight_id": DatabaseReference(
                "flight_directions",
                "id",
                on_delete=DatabaseActions.CASCADE
            )
        }
    )

    database.create_table(
        "flight_tickets",
        {
            "id": [DatabaseTypes.TEXT, DatabaseTypes.PRIMARY_KEY],
            "flight_number": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
            "cost": [DatabaseTypes.INTEGER, DatabaseTypes.NOT_NULL],
            "occupancy": [DatabaseTypes.INTEGER, DatabaseTypes.NOT_NULL],
            "total_seats": [DatabaseTypes.INTEGER, DatabaseTypes.NOT_NULL],
            "departure_airport": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
            "arrival_airport": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
            "departure_time": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
            "arrival_time": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
            "datetime_id": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
        },
        {
            "datetime_id": DatabaseReference(
                "flight_datetime",
                "id",
                on_delete=DatabaseActions.CASCADE
            ),
        }
    )


@router.get("/directions", tags=["flights-directions"])
async def get_flight_directions():
    directions = database.select_many(
        "flight_directions",
        ["*"]
    )

    return JSONResponse(directions)


@router.post("/directions", tags=["flights-directions"])
async def create_flight_direction(flight_direction: ClientFlightDirection):

    """Создание необходимых таблиц"""
    flight_direction_dict = flight_direction.model_dump()
    delivery_service_model = FlightDirection(
        **flight_direction_dict,
    )

    database.insert("flight_directions", delivery_service_model.model_dump())


@router.put("/directions", tags=["flights-directions"])
async def update_flight_direction(flight_direction: ClientFlightDirection):
    client_depot_dict = flight_direction.model_dump(exclude={"id": True})

    database.update(
        "flight_directions",
        client_depot_dict.keys(),
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": flight_direction.id
            }
        }),
        client_depot_dict.values()
    )


@router.delete("/directions/{flight_id}", tags=["flights-directions"])
async def delete_flight_direction(flight_id: str):

    database.delete(
        "flight_directions",
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": flight_id
            }
        })
    )


@router.get("/{flight_id}/datetime", tags=["flights-datetime"])
async def get_flight_datetime(flight_id: str):
    sections = database.select_many(
        "flight_datetime",
        ["id", "name", "flight_id"],
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "flight_id": flight_id
            }
        })
    )

    return JSONResponse(sections)


@router.post("/datetime", tags=["flights-datetime"])
async def create_flight_datetime(flight_datetime: ClientFlightDateTime):
    route_dict = flight_datetime.model_dump()
    route_model = FlightDateTime(
        **route_dict
    )

    database.insert("flight_datetime", route_model.model_dump())


@router.put("/datetime", tags=["flights-datetime"])
async def update_flight_datetime(flight_datetime: ClientFlightDateTime):
    client_route_dict = flight_datetime.model_dump(exclude={
        "id": True,
        "flight_id": True,
    })

    database.update(
        "flight_datetime",
        client_route_dict.keys(),
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": flight_datetime.id
            }
        }),
        client_route_dict.values()
    )


@router.delete("/datetime/{flight_datetime_id}", tags=["flights-datetime"])
async def delete_flight_datetime(flight_datetime_id: str):
    database.delete(
        "flight_datetime",
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": flight_datetime_id
            }
        })
    )


@router.get("/{flight_id}/{flight_datetime_id}", tags=["flights-tickets"])
async def get_datetime_tickets(flight_id: str, flight_datetime_id: str):

    parts = database.execute(f"""
        SELECT ft.id, flight_number, 
        cost, occupancy, total_seats, departure_airport,
        arrival_airport, departure_time, arrival_time, datetime_id
        FROM flight_tickets ft 
        JOIN flight_datetime fd on fd.id = ft.datetime_id 
        WHERE fd.flight_id = '{flight_id}' AND fd.id = '{flight_datetime_id}';
    """).fetchall()

    return parts


@router.post("/datetime/{flight_datetime_id}", tags=["flights-tickets"])
async def create_ticket(flight_datetime_id: str, ticket: ClientFlightTicket):
    client_transport_dict = ticket.model_dump()
    part_model = FlightTicket(
        **client_transport_dict,
    )

    database.insert("flight_tickets", part_model.model_dump())


@router.put("/datetime/{flight_datetime_id}", tags=["flights-tickets"])
async def update_ticket(flight_datetime_id: str, ticket: ClientFlightTicket):

    client_ticket_dict = ticket.model_dump(exclude={
        "id": True,
        "datetime_id": True,
    })

    database.update(
        "flight_tickets",
        client_ticket_dict.keys(),
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": ticket.id,
                "datetime_id": ticket.datetime_id
            }
        }),
        client_ticket_dict.values()
    )


@router.delete("/datetime/{flight_datetime_id}/{ticket_id}", tags=["flights-tickets"])
async def delete_ticket(flight_datetime_id: str, ticket_id: str):
    database.delete(
        "flight_tickets",
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": ticket_id
            }
        })
    )
