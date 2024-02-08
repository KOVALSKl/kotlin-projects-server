from fastapi import APIRouter
from fastapi.responses import JSONResponse

from database import *
from database.models import TaxiCompany, TaxiService, TaxiAuto, ClientTaxiCompany, ClientTaxiService, ClientTaxiAuto

router = APIRouter(
    prefix="/taxi",
)


@router.on_event("startup")
async def startup():
    """Создание необходимых таблиц"""
    database.create_table(
        "taxi_companies",
        {
            "id": [DatabaseTypes.TEXT, DatabaseTypes.PRIMARY_KEY],
            "name": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL, DatabaseTypes.UNIQUE],
        }
    )

    database.create_table(
        "taxi_services",
        {
            "id": [DatabaseTypes.TEXT, DatabaseTypes.PRIMARY_KEY],
            "name": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL, DatabaseTypes.UNIQUE],
            "company_id": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL]
        },
        {
            "company_id": DatabaseReference(
                "taxi_companies",
                "id",
                on_delete=DatabaseActions.CASCADE
            )
        }
    )

    database.create_table(
        "taxi_autos",
        {
            "id": [DatabaseTypes.TEXT, DatabaseTypes.PRIMARY_KEY],
            "brand": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
            "number": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
            "driver_name": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
            "model": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
            "year": [DatabaseTypes.INTEGER, DatabaseTypes.NOT_NULL],
            "color": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
            "seats": [DatabaseTypes.INTEGER, DatabaseTypes.NOT_NULL],
            "milage": [DatabaseTypes.INTEGER, DatabaseTypes.NOT_NULL],
            "service_id": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
        },
        {
            "service_id": DatabaseReference(
                "taxi_services",
                "id",
                on_delete=DatabaseActions.CASCADE
            ),
        }
    )


@router.get("/companies", tags=["taxi-companies"])
async def get_taxi_companies():
    companies = database.select_many(
        "taxi_companies",
        ["*"]
    )

    return JSONResponse(companies)


@router.post("/companies", tags=["taxi-companies"])
async def create_taxi_company(taxi_company: ClientTaxiCompany):

    """Создание необходимых таблиц"""
    taxi_company_dict = taxi_company.model_dump()
    taxi_company_model = TaxiCompany(
        **taxi_company_dict,
    )

    database.insert("taxi_companies", taxi_company_model.model_dump())


@router.put("/companies", tags=["taxi-companies"])
async def update_taxi_company(taxi_company: ClientTaxiCompany):
    client_taxi_company_dict = taxi_company.model_dump(exclude={"id": True})

    database.update(
        "taxi_companies",
        client_taxi_company_dict.keys(),
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": taxi_company.id
            }
        }),
        client_taxi_company_dict.values()
    )


@router.delete("/companies/{company_id}", tags=["flights-directions"])
async def delete_taxi_company(company_id: str):

    database.delete(
        "taxi_companies",
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": company_id
            }
        })
    )


@router.get("/{company_id}/services", tags=["taxi-services"])
async def get_taxi_service(flight_id: str):
    sections = database.select_many(
        "taxi_service",
        ["id", "name", "flight_id"],
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "flight_id": flight_id
            }
        })
    )

    return JSONResponse(sections)


@router.post("/datetime", tags=["taxi-services"])
async def create_taxi_service(taxi_service: ClientTaxiService):
    taxi_service_dict = taxi_service.model_dump()
    taxi_service_model = TaxiService(
        **taxi_service_dict
    )

    database.insert("taxi_service", taxi_service_model.model_dump())


@router.put("/datetime", tags=["taxi-services"])
async def update_taxi_service(taxi_service: ClientTaxiService):
    client_taxi_service_dict = taxi_service.model_dump(exclude={
        "id": True,
        "flight_id": True,
    })

    database.update(
        "taxi_service",
        client_taxi_service_dict.keys(),
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": taxi_service.id
            }
        }),
        client_taxi_service_dict.values()
    )


@router.delete("/datetime/{taxi_service_id}", tags=["taxi-services"])
async def delete_taxi_service(taxi_service_id: str):
    database.delete(
        "taxi_service",
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": taxi_service_id
            }
        })
    )


@router.get("/{company_id}/{taxi_service_id}", tags=["taxi-autos"])
async def get_service_autos(company_id: str, taxi_service_id: str):

    parts = database.execute(f"""
        SELECT ta.id, brand, number, driver_name,
        model, year, color, seats, milage, service_id
        FROM taxi_autos ta 
        JOIN taxi_service ts on ts.id = ta.datetime_id 
        WHERE ts.company_id = '{company_id}' AND ts.id = '{taxi_service_id}';
    """).fetchall()

    return parts


@router.post("/datetime/{taxi_service_id}", tags=["taxi-autos"])
async def create_taxi_autos(taxi_service_id: str, auto: ClientTaxiAuto):
    client_auto_dict = auto.model_dump()
    auto_model = TaxiAuto(
        **client_auto_dict,
    )

    database.insert("taxi_autos", auto_model.model_dump())


@router.put("/datetime/{taxi_service_id}", tags=["taxi-autos"])
async def update_taxi_autos(taxi_service_id: str, auto: ClientTaxiAuto):

    client_auto_dict = auto.model_dump(exclude={
        "id": True,
        "service_id": True,
    })

    database.update(
        "taxi_autos",
        client_auto_dict.keys(),
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": auto.id,
                "service_id": auto.service_id
            }
        }),
        client_auto_dict.values()
    )


@router.delete("/datetime/{taxi_service_id}/{auto_id}", tags=["taxi-autos"])
async def delete_taxi_autos(taxi_service_id: str, auto_id: str):
    database.delete(
        "taxi_autos",
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": auto_id
            }
        })
    )
