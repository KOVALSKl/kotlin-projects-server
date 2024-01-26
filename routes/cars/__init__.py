from uuid import uuid4
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from database import *
from database.models import CarModel, CatalogSection, SparePart, ClientCarModel, ClientCatalogSection, ClientSparePart

router = APIRouter(
    prefix="/cars",
)


@router.on_event("startup")
async def startup():
    """Создание необходимых таблиц"""
    database.create_table(
        "car_models",
        {
            "id": [DatabaseTypes.TEXT, DatabaseTypes.PRIMARY_KEY],
            "name": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL, DatabaseTypes.UNIQUE],
        }
    )

    database.create_table(
        "catalog_sections",
        {
            "id": [DatabaseTypes.TEXT, DatabaseTypes.PRIMARY_KEY],
            "name": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL, DatabaseTypes.UNIQUE],
            "car_model_id": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL]
        },
        {
            "car_model_id": DatabaseReference(
                "car_models",
                "id",
                on_delete=DatabaseActions.CASCADE
            )
        }
    )

    database.create_table(
        "spare_parts",
        {
            "id": [DatabaseTypes.TEXT, DatabaseTypes.PRIMARY_KEY],
            "name": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
            "catalog_number": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
            "producer": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
            "price": [DatabaseTypes.INTEGER, DatabaseTypes.NOT_NULL],
            "weight": [DatabaseTypes.INTEGER, DatabaseTypes.NOT_NULL],
            "description": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
            "availability_count": [DatabaseTypes.INTEGER, DatabaseTypes.NOT_NULL],
            "create_date": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
            "catalog_section_id": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
        },
        {
            "catalog_section_id": DatabaseReference(
                "catalog_sections",
                "id",
                on_delete=DatabaseActions.CASCADE
            ),
        }
    )


@router.get("/models", tags=["car-models"])
async def get_car_models():
    depots = database.select_many(
        "car_models",
        ["*"]
    )

    return JSONResponse(depots)


@router.post("/models", tags=["car-models"])
async def create_car_model(car_model: ClientCarModel):

    """Создание необходимых таблиц"""
    car_model_dict = car_model.model_dump()
    delivery_service_model = CarModel(
        **car_model_dict,
        id=uuid4()
    )

    database.insert("car_models", delivery_service_model.model_dump())


@router.put("/models", tags=["car-models"])
async def update_car_model(car_model: ClientCarModel):
    client_depot_dict = car_model.model_dump(exclude={"id": True})

    database.update(
        "car_models",
        client_depot_dict.keys(),
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": car_model.id
            }
        }),
        client_depot_dict.values()
    )


@router.delete("/models/{car_model_id}", tags=["car-models"])
async def delete_car_model(car_model_id: str):

    database.delete(
        "car_models",
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": car_model_id
            }
        })
    )


@router.get("/{model_id}/sections", tags=["catalog-sections"])
async def get_sections(model_id: str):
    sections = database.select_many(
        "catalog_sections",
        ["id", "name", "car_model_id"],
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "car_model_id": model_id
            }
        })
    )

    return JSONResponse(sections)


@router.post("/sections", tags=["catalog-sections"])
async def create_section(section: ClientCatalogSection):
    route_dict = section.model_dump()
    route_model = CatalogSection(
        **route_dict,
        id=uuid4()
    )

    database.insert("catalog_sections", route_model.model_dump())


@router.put("/sections", tags=["catalog-sections"])
async def update_section(section: ClientCatalogSection):
    client_route_dict = section.model_dump(exclude={
        "id": True,
        "car_model_id": True,
    })

    database.update(
        "catalog_sections",
        client_route_dict.keys(),
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": section.id
            }
        }),
        client_route_dict.values()
    )


@router.delete("/sections/{section_id}", tags=["catalog-sections"])
async def delete_section(section_id: str):
    database.delete(
        "catalog_sections",
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": section_id
            }
        })
    )


@router.get("/{catalog_section_id}/{spare_part_id}", tags=["spare-parts"])
async def get_section_parts(catalog_section_id: str, spare_part_id: str):

    parts = database.execute(f"""
        SELECT sp.id, sp.name, catalog_number, 
        producer, price, weight, description,
        availability_count,
        create_date, catalog_section_id 
        FROM spare_parts sp 
        JOIN catalog_sections cs on cs.id = sp.catalog_section_id 
        WHERE cs.car_model_id = '{catalog_section_id}' AND cs.id = '{spare_part_id}';
    """).fetchall()

    return parts


@router.post("/sections/{section_id}", tags=["spare-parts"])
async def create_part(section_id: str, part: ClientSparePart):
    client_transport_dict = part.model_dump(exclude={"id": True})
    part_model = SparePart(
        **client_transport_dict,
        id=uuid4()
    )

    database.insert("spare_parts", part_model.model_dump())


@router.put("/sections/{section_id}", tags=["spare-parts"])
async def update_part(section_id: str, part: ClientSparePart):

    client_part_dict = part.model_dump(exclude={
        "id": True,
        "catalog_section_id": True,
    })

    database.update(
        "spare_parts",
        client_part_dict.keys(),
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": part.id,
                "catalog_section_id": part.catalog_section_id
            }
        }),
        client_part_dict.values()
    )


@router.delete("/sections/{section_id}/{part_id}", tags=["spare-parts"])
async def delete_part(section_id: str, part_id: str):
    database.delete(
        "spare_parts",
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": part_id
            }
        })
    )
