from uuid import uuid4
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from database import *
from database.models import Pharmacy, MedicationGroup, Medication, \
    ClientPharmacy, ClientMedicationGroup, ClientMedication

router = APIRouter(
    prefix="/pharmacy",
)


@router.on_event("startup")
async def startup():
    """Создание необходимых таблиц"""
    database.create_table(
        "pharmacies",
        {
            "id": [DatabaseTypes.TEXT, DatabaseTypes.PRIMARY_KEY],
            "name": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL, DatabaseTypes.UNIQUE],
        }
    )

    database.create_table(
        "medication_groups",
        {
            "id": [DatabaseTypes.TEXT, DatabaseTypes.PRIMARY_KEY],
            "name": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL, DatabaseTypes.UNIQUE],
            "pharmacy_id": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL]
        },
        {
            "pharmacy_id": DatabaseReference(
                "pharmacies",
                "id",
                on_delete=DatabaseActions.CASCADE
            )
        }
    )

    database.create_table(
        "medications",
        {
            "id": [DatabaseTypes.TEXT, DatabaseTypes.PRIMARY_KEY],
            "name": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
            "dosage": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
            "volume": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
            "price": [DatabaseTypes.INTEGER, DatabaseTypes.NOT_NULL],
            "producer": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
            "expiration_date": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
            "description": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
            "effects": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
            "medication_group_id": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
        },
        {
            "medication_group_id": DatabaseReference(
                "medication_groups",
                "id",
                on_delete=DatabaseActions.CASCADE
            ),
        }
    )


@router.get("/pharmacies", tags=["pharmacies"])
async def get_pharmacy():
    pharmacies = database.select_many(
        "pharmacies",
        ["*"]
    )

    return JSONResponse(pharmacies)


@router.post("/pharmacies", tags=["pharmacies"])
async def create_pharmacy(client_pharmacy: ClientPharmacy):

    """Создание необходимых таблиц"""
    client_pharmacy_dict = client_pharmacy.model_dump()
    pharmacy_model = Pharmacy(
        **client_pharmacy_dict,
    )

    database.insert("pharmacies", pharmacy_model.model_dump())


@router.put("/pharmacies", tags=["pharmacies"])
async def update_pharmacy(client_pharmacy: ClientPharmacy):
    pharmacy_dict = client_pharmacy.model_dump(exclude={"id": True})

    database.update(
        "pharmacies",
        pharmacy_dict.keys(),
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": client_pharmacy.id
            }
        }),
        pharmacy_dict.values()
    )


@router.delete("/pharmacies/{pharmacy_id}", tags=["pharmacy"])
async def delete_pharmacy(pharmacy_id: str):

    database.delete(
        "pharmacies",
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": pharmacy_id
            }
        })
    )


@router.get("/{pharmacy_id}/groups", tags=["medication-group"])
async def get_group(pharmacy_id: str):
    sections = database.select_many(
        "medication_groups",
        ["id", "name", "pharmacy_id"],
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "pharmacy_id": pharmacy_id
            }
        })
    )

    return JSONResponse(sections)


@router.post("/groups", tags=["medication-group"])
async def create_group(group: ClientMedicationGroup):
    group_dict = group.model_dump()
    group_model = MedicationGroup(
        **group_dict,
    )

    database.insert("medication_groups", group_model.model_dump())


@router.put("/groups", tags=["medication-group"])
async def update_group(group: ClientMedicationGroup):
    group_dict = group.model_dump(exclude={
        "id": True,
        "pharmacy_id": True,
    })

    database.update(
        "medication_groups",
        group_dict.keys(),
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": group.id
            }
        }),
        group_dict.values()
    )


@router.delete("/groups/{pharmacy_id}", tags=["medication-group"])
async def delete_group(pharmacy_id: str):
    database.delete(
        "medication_groups",
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": pharmacy_id
            }
        })
    )


@router.get("/{pharmacy_id}/{medication_group_id}", tags=["medications"])
async def get_group_medication(pharmacy_id: str, medication_group_id: str):

    medications = database.execute(f"""
        SELECT md.id, md.name, dosage, volume, 
        price, producer, expiration_date, description, effects, medication_group_id 
        FROM medications md 
        JOIN medication_groups mg on mg.id = md.medication_group_id 
        WHERE mg.pharmacy_id = '{pharmacy_id}' AND mg.id = '{medication_group_id}';
    """).fetchall()

    return medications


@router.post("/groups/{medication_group_id}", tags=["medications"])
async def create_medication(medication_group_id: str, client_medication: ClientMedication):
    medication_dict = client_medication.model_dump()
    medication_model = Medication(
        **medication_dict,
    )

    database.insert("medications", medication_model.model_dump())


@router.put("/groups/{medication_group_id}", tags=["medications"])
async def update_medication(medication_group_id: str, client_medication: ClientMedication):

    medication_dict = client_medication.model_dump(exclude={
        "id": True,
        "medication_group_id": True,
    })

    database.update(
        "medications",
        medication_dict.keys(),
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": client_medication.id,
                "medication_group_id": client_medication.route_id
            }
        }),
        medication_dict.values()
    )


@router.delete("/groups/{group_id}/{medication_id}", tags=["medications"])
async def delete_medication(group_id: str, medication_id: str):
    database.delete(
        "medications",
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": medication_id
            }
        })
    )
