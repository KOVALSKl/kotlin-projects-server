from uuid import uuid4
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from database import *
from database.models import IndustrialStores, IndustrialProduct, IndustrialDepartment, \
    ClientIndustrialStores, ClientIndustrialProduct, ClientIndustrialDepartment

router = APIRouter(
    prefix="/industrial",
)


@router.on_event("startup")
async def startup():
    """Создание необходимых таблиц"""
    database.create_table(
        "industrial_stores",
        {
            "id": [DatabaseTypes.TEXT, DatabaseTypes.PRIMARY_KEY],
            "name": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL, DatabaseTypes.UNIQUE],
        }
    )

    database.create_table(
        "industrial_departments",
        {
            "id": [DatabaseTypes.TEXT, DatabaseTypes.PRIMARY_KEY],
            "name": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL, DatabaseTypes.UNIQUE],
            "store_id": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL]
        },
        {
            "store_id": DatabaseReference(
                "industrial_stores",
                "id",
                on_delete=DatabaseActions.CASCADE
            )
        }
    )

    database.create_table(
        "industrial_products",
        {
            "id": [DatabaseTypes.TEXT, DatabaseTypes.PRIMARY_KEY],
            "name": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
            "item_number": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
            "weight": [DatabaseTypes.INTEGER, DatabaseTypes.NOT_NULL],
            "price": [DatabaseTypes.INTEGER, DatabaseTypes.NOT_NULL],
            "producer": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
            "description": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
            "packing_date": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
            "department_id": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
        },
        {
            "department_id": DatabaseReference(
                "industrial_departments",
                "id",
                on_delete=DatabaseActions.CASCADE
            ),
        }
    )


@router.get("/stores", tags=["industrial-stores"])
async def get_industrial_stores():
    depots = database.select_many(
        "industrial_stores",
        ["*"]
    )

    return JSONResponse(depots)


@router.post("/stores", tags=["industrial-stores"])
async def create_industrial_store(industrial_store: ClientIndustrialStores):

    """Создание необходимых таблиц"""
    car_model_dict = industrial_store.model_dump(exclude={"id": True})
    delivery_service_model = IndustrialStores(
        **car_model_dict,
        id=uuid4()
    )

    database.insert("industrial_stores", delivery_service_model.model_dump())


@router.put("/stores", tags=["industrial-stores"])
async def update_industrial_store(store: ClientIndustrialStores):
    client_store_dict = store.model_dump(exclude={"id": True})

    database.update(
        "industrial_stores",
        client_store_dict.keys(),
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": store.id
            }
        }),
        client_store_dict.values()
    )


@router.delete("/stores/{store_id}", tags=["industrial-stores"])
async def delete_industrial_store(store_id: str):

    database.delete(
        "industrial_stores",
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": store_id
            }
        })
    )


@router.get("/{store_id}/departments", tags=["industrial-departments"])
async def get_industrial_departments(store_id: str):
    sections = database.select_many(
        "industrial_departments",
        ["id", "name", "store_id"],
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "store_id": store_id
            }
        })
    )

    print(f"\nindustrial/{store_id}/departments -> departments: {sections}\n")

    return JSONResponse(sections)


@router.post("/departments", tags=["industrial-departments"])
async def create_industrial_department(department: ClientIndustrialDepartment):
    route_dict = department.model_dump(exclude={"id": True})
    route_model = IndustrialDepartment(
        **route_dict,
        id=uuid4()
    )

    database.insert("industrial_departments", route_model.model_dump())


@router.put("/departments", tags=["industrial-departments"])
async def update_industrial_department(department: ClientIndustrialDepartment):
    client_route_dict = department.model_dump(exclude={
        "id": True,
        "store_id": True,
    })

    database.update(
        "industrial_departments",
        client_route_dict.keys(),
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": department.id
            }
        }),
        client_route_dict.values()
    )


@router.delete("/departments/{department_id}", tags=["industrial-departments"])
async def delete_industrial_department(department_id: str):
    database.delete(
        "industrial_departments",
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": department_id
            }
        })
    )


@router.get("/{store_id}/{department_id}", tags=["industrial-products"])
async def get_department_products(store_id: str, department_id: str):

    parts = database.execute(f"""
        SELECT ip.id, ip.name, item_number, weight, 
        price, producer, description,
        packing_date,
        department_id 
        FROM industrial_products ip 
        JOIN industrial_departments ind on ind.id = ip.department_id 
        WHERE ind.store_id = '{store_id}' AND ind.id = '{department_id}';
    """).fetchall()

    print(f"\nindustrial/{store_id}/{department_id} -> products: {parts}\n")

    return parts


@router.post("/departments/{department_id}", tags=["industrial-products"])
async def create_industrial_products(department_id: str, client_product: ClientIndustrialProduct):
    client_product_dict = client_product.model_dump(exclude={"id": True})
    product = IndustrialProduct(
        **client_product_dict,
        id=uuid4()
    )

    database.insert("industrial_products", product.model_dump())


@router.put("/departments/{department_id}", tags=["industrial-products"])
async def update_part(department_id: str, client_product: ClientIndustrialProduct):

    client_product_dict = client_product.model_dump(exclude={
        "id": True,
        "department_id": True,
    })

    database.update(
        "industrial_products",
        client_product_dict.keys(),
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": client_product.id,
                "department_id": client_product.department_id
            }
        }),
        client_product_dict.values()
    )


@router.delete("/departments/{section_id}/{product_id}", tags=["industrial-products"])
async def delete_part(section_id: str, product_id: str):
    database.delete(
        "industrial_products",
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": product_id
            }
        })
    )
