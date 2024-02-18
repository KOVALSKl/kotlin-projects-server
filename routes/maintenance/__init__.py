from uuid import uuid4
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from database import *
from database.models import MaintenanceStation, MaintenanceWorker, MaintenanceWork, \
    ClientMaintenanceStation, ClientMaintenanceWorker, ClientMaintenanceWork

router = APIRouter(
    prefix="/maintenance",
)


@router.on_event("startup")
async def startup():
    """Создание необходимых таблиц"""
    database.create_table(
        "maintenance_stations",
        {
            "id": [DatabaseTypes.TEXT, DatabaseTypes.PRIMARY_KEY],
            "name": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL, DatabaseTypes.UNIQUE],
        }
    )

    database.create_table(
        "maintenance_workers",
        {
            "id": [DatabaseTypes.TEXT, DatabaseTypes.PRIMARY_KEY],
            "name": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL, DatabaseTypes.UNIQUE],
            "station_id": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL]
        },
        {
            "station_id": DatabaseReference(
                "maintenance_stations",
                "id",
                on_delete=DatabaseActions.CASCADE
            )
        }
    )

    database.create_table(
        "maintenance_works",
        {
            "id": [DatabaseTypes.TEXT, DatabaseTypes.PRIMARY_KEY],
            "work_type": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
            "brand": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
            "number": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
            "date": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
            "mechanic_name": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
            "description": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
            "cost": [DatabaseTypes.INTEGER, DatabaseTypes.NOT_NULL],
            "duration": [DatabaseTypes.INTEGER, DatabaseTypes.NOT_NULL],
            "worker_id": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
        },
        {
            "worker_id": DatabaseReference(
                "maintenance_workers",
                "id",
                on_delete=DatabaseActions.CASCADE
            ),
        }
    )


@router.get("/stations", tags=["maintenance-stations"])
async def get_maintenance_stations():
    stations = database.select_many(
        "maintenance_stations",
        ["*"]
    )

    return JSONResponse(stations)


@router.post("/stations", tags=["maintenance-stations"])
async def create_maintenance_station(maintenance_station: ClientMaintenanceStation):

    """Создание необходимых таблиц"""
    flight_station_dict = maintenance_station.model_dump()
    delivery_service_model = MaintenanceStation(
        **flight_station_dict,
    )

    database.insert("maintenance_stations", delivery_service_model.model_dump())


@router.put("/stations", tags=["maintenance-stations"])
async def update_maintenance_station(maintenance_station: ClientMaintenanceStation):
    client_depot_dict = maintenance_station.model_dump(exclude={"id": True})

    database.update(
        "maintenance_stations",
        client_depot_dict.keys(),
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": maintenance_station.id
            }
        }),
        client_depot_dict.values()
    )


@router.delete("/stations/{station_id}", tags=["maintenance-stations"])
async def delete_maintenance_station(station_id: str):

    database.delete(
        "maintenance_stations",
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": station_id
            }
        })
    )


@router.get("/{station_id}/workers", tags=["maintenance-workers"])
async def get_workers(station_id: str):
    sections = database.select_many(
        "maintenance_workers",
        ["id", "name", "station_id"],
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "station_id": station_id
            }
        })
    )

    return JSONResponse(sections)


@router.post("/workers", tags=["maintenance-workers"])
async def create_maintenance_worker(maintenance_worker: ClientMaintenanceWorker):
    route_dict = maintenance_worker.model_dump()
    route_model = MaintenanceWorker(
        **route_dict
    )

    database.insert("maintenance_workers", route_model.model_dump())


@router.put("/workers", tags=["maintenance-workers"])
async def update_maintenance_worker(maintenance_worker: ClientMaintenanceWorker):
    client_route_dict = maintenance_worker.model_dump(exclude={
        "id": True,
        "station_id": True,
    })

    database.update(
        "maintenance_workers",
        client_route_dict.keys(),
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": maintenance_worker.id
            }
        }),
        client_route_dict.values()
    )


@router.delete("/workers/{worker_id}", tags=["maintenance-workers"])
async def delete_maintenance_worker(worker_id: str):
    database.delete(
        "maintenance_workers",
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": worker_id
            }
        })
    )


@router.get("/{station_id}/{worker_id}", tags=["maintenance-workers"])
async def get_workers_works(station_id: str, worker_id: str):

    parts = database.execute(f"""
        SELECT mw.id, work_type, 
        brand, number, date, mechanic_name,
        description, cost, duration, worker_id
        FROM maintenance_works mw 
        JOIN maintenance_workers mwr on mwr.id = mw.worker_id 
        WHERE mwr.station_id = '{station_id}' AND mwr.id = '{worker_id}';
    """).fetchall()

    return parts


@router.post("/workers/{worker_id}", tags=["maintenance-works"])
async def create_work(worker_id: str, work: ClientMaintenanceWork):
    client_transport_dict = work.model_dump()
    part_model = MaintenanceWork(
        **client_transport_dict,
    )

    database.insert("maintenance_works", part_model.model_dump())


@router.put("/workers/{worker_id}", tags=["maintenance-works"])
async def update_work(worker_id: str, work: ClientMaintenanceWork):

    client_work_dict = work.model_dump(exclude={
        "id": True,
        "worker_id": True,
    })

    database.update(
        "maintenance_works",
        client_work_dict.keys(),
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": work.id,
                "worker_id": work.worker_id
            }
        }),
        client_work_dict.values()
    )


@router.delete("/workers/{worker_id}/{work_id}", tags=["maintenance-works"])
async def delete_work(worker_id: str, work_id: str):
    database.delete(
        "maintenance_works",
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": work_id
            }
        })
    )
