from uuid import uuid4
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from database import *
from database.models import OlympTask, OlympProfile, OlympParticipant, \
    ClientOlympTask, ClientOlympProfile, ClientOlympParticipant

router = APIRouter(
    prefix="/multiprofile",
)


@router.on_event("startup")
async def startup():
    """Создание необходимых таблиц"""
    database.create_table(
        "multiprofile_olymp",
        {
            "id": [DatabaseTypes.TEXT, DatabaseTypes.PRIMARY_KEY],
            "name": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL, DatabaseTypes.UNIQUE],
        }
    )

    database.create_table(
        "profiles",
        {
            "id": [DatabaseTypes.TEXT, DatabaseTypes.PRIMARY_KEY],
            "name": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL, DatabaseTypes.UNIQUE],
            "olymp_task_id": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL]
        },
        {
            "olymp_task_id": DatabaseReference(
                "multiprofile_olymp",
                "id",
                on_delete=DatabaseActions.CASCADE
            )
        }
    )

    database.create_table(
        "olymp_participants",
        {
            "id": [DatabaseTypes.TEXT, DatabaseTypes.PRIMARY_KEY],
            "full_name": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
            "qualification_score": [DatabaseTypes.INTEGER, DatabaseTypes.NOT_NULL],
            "final_score": [DatabaseTypes.INTEGER, DatabaseTypes.NOT_NULL],
            "hobbies": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
            "country": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
            "school": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
            "achievements": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
            "additional_information": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
            "olymp_profile_id": [DatabaseTypes.INTEGER, DatabaseTypes.NOT_NULL],
        },
        {
            "olymp_profile_id": DatabaseReference(
                "profiles",
                "id",
                on_delete=DatabaseActions.CASCADE
            ),
        }
    )


@router.get("/tasks", tags=["olymp-tasks"])
async def get_depots():
    depots = database.select_many(
        "multiprofile_olymp",
        ["*"]
    )

    return JSONResponse(depots)


@router.post("/tasks", tags=["olympic-tasks"])
async def create_olympic_game(olympic_game: ClientOlympTask):

    """Создание необходимых таблиц"""
    olympic_game_dict = olympic_game.model_dump(exclude={"id": True})
    olympic_game_model = OlympTask(
        **olympic_game_dict,
        id=uuid4()
    )

    database.insert("multiprofile_olymp", olympic_game_model.model_dump())


@router.put("/tasks", tags=["olympic-tasks"])
async def update_olympic_game(olympic_game: ClientOlympTask):
    olympic_game_dict = olympic_game.model_dump(exclude={"id": True})

    database.update(
        "multiprofile_olymp",
        olympic_game_dict.keys(),
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": olympic_game.id
            }
        }),
        olympic_game_dict.values()
    )


@router.delete("/tasks/{task_id}", tags=["olympic-tasks"])
async def delete_olympic_game(task_id: str):

    database.delete(
        "multiprofile_olymp",
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": task_id
            }
        })
    )


@router.get("/{task_id}/profiles", tags=["olymp-profiles"])
async def get_competitions(task_id: str):
    competitions = database.select_many(
        "profiles",
        ["id", "name", "olymp_task_id"],
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "olymp_task_id": task_id
            }
        })
    )

    return JSONResponse(competitions)


@router.post("/profiles", tags=["olymp-profiles"])
async def create_competition(competition: ClientOlympProfile):
    competition_dict = competition.model_dump(exclude={
        "id": True
    })
    route_model = OlympProfile(
        **competition_dict,
        id=uuid4()
    )

    database.insert("profiles", route_model.model_dump())


@router.put("/profiles", tags=["olymp-profiles"])
async def update_route(competition: ClientOlympProfile):
    client_competition_dict = competition.model_dump(exclude={
        "id": True,
        "olymp_task_id": True,
    })

    database.update(
        "profiles",
        client_competition_dict.keys(),
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": competition.id
            }
        }),
        client_competition_dict.values()
    )


@router.delete("/profiles/{profile_id}", tags=["olymp-profiles"])
async def delete_route(competition_id: str):
    database.delete(
        "profiles",
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": competition_id
            }
        })
    )


@router.get("/{task_id}/{profile_id}", tags=["olymp-participants"])
async def get_competition_player(task_id: str, profile_id: str):

    players = database.execute(f"""
        SELECT op.id, full_name, qualification_score, 
        final_score, hobbies, country, school, achievements, 
        additional_information, olymp_profile_id
        FROM olymp_participants op 
        JOIN profiles pr on pr.id = op.competition_id
        WHERE pr.olymp_task_id = '{task_id}' AND pr.id = '{profile_id}';
    """).fetchall()

    print(players)

    return players


@router.post("/profiles/{profile_id}", tags=["olympic-participants"])
async def create_player(profile_id: str, olympic_player: ClientOlympParticipant):
    client_olympic_player_dict = olympic_player.model_dump(exclude={"id": True})
    olympic_player_model = OlympParticipant(
        **client_olympic_player_dict,
        id=uuid4()
    )

    database.insert("profiles", olympic_player_model.model_dump())


@router.put("/profiles/{profile_id}", tags=["olympic-participants"])
async def update_player(competition_id: str, client_player: ClientOlympParticipant):

    client_player_dict = client_player.model_dump(exclude={
        "id": True,
        "olymp_profile_id": True,
    })

    database.update(
        "olymp_participants",
        client_player_dict.keys(),
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": client_player.id,
                "olymp_profile_id": client_player.olymp_profile_id
            }
        }),
        client_player_dict.values()
    )


@router.delete("/profiles/{profile_id}/{participant_id}", tags=["trams"])
async def delete_player(profile_id: str, participant_id: str):
    database.delete(
        "olymp_participants",
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": participant_id
            }
        })
    )
