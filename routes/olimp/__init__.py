from uuid import uuid4
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from database import *
from database.models import OlympicGame, OlympicCompetitionType, OlympicPlayer, \
    ClientOlympicGame, ClientOlympicCompetitionType, ClientOlympicPlayer

router = APIRouter(
    prefix="/olympic",
)


@router.on_event("startup")
async def startup():
    """Создание необходимых таблиц"""
    database.create_table(
        "olympic_games",
        {
            "id": [DatabaseTypes.TEXT, DatabaseTypes.PRIMARY_KEY],
            "name": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL, DatabaseTypes.UNIQUE],
        }
    )

    database.create_table(
        "competition_types",
        {
            "id": [DatabaseTypes.TEXT, DatabaseTypes.PRIMARY_KEY],
            "name": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL, DatabaseTypes.UNIQUE],
            "game_id": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL]
        },
        {
            "game_id": DatabaseReference(
                "olympic_games",
                "id",
                on_delete=DatabaseActions.CASCADE
            )
        }
    )

    database.create_table(
        "olympic_players",
        {
            "id": [DatabaseTypes.TEXT, DatabaseTypes.PRIMARY_KEY],
            "name": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
            "country": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
            "ranking": [DatabaseTypes.INTEGER, DatabaseTypes.NOT_NULL],
            "score": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
            "age": [DatabaseTypes.INTEGER, DatabaseTypes.NOT_NULL],
            "sport": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
            "height": [DatabaseTypes.INTEGER, DatabaseTypes.NOT_NULL],
            "weight": [DatabaseTypes.INTEGER, DatabaseTypes.NOT_NULL],
            "competition_id": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
        },
        {
            "competition_id": DatabaseReference(
                "competition_types",
                "id",
                on_delete=DatabaseActions.CASCADE
            ),
        }
    )


@router.get("/games", tags=["olympic-games"])
async def get_depots():
    depots = database.select_many(
        "olympic_games",
        ["*"]
    )

    return JSONResponse(depots)


@router.post("/games", tags=["olympic-games"])
async def create_olympic_game(olympic_game: ClientOlympicGame):

    """Создание необходимых таблиц"""
    olympic_game_dict = olympic_game.model_dump(exclude={"id": True})
    olympic_game_model = OlympicGame(
        **olympic_game_dict,
        id=uuid4()
    )

    database.insert("olympic_games", olympic_game_model.model_dump())


@router.put("/games", tags=["olympic-games"])
async def update_olympic_game(olympic_game: ClientOlympicGame):
    olympic_game_dict = olympic_game.model_dump(exclude={"id": True})

    database.update(
        "olympic_games",
        olympic_game_dict.keys(),
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": olympic_game.id
            }
        }),
        olympic_game_dict.values()
    )


@router.delete("/games/{game_id}", tags=["olympic-games"])
async def delete_olympic_game(game_id: str):

    database.delete(
        "olympic_games",
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": game_id
            }
        })
    )


@router.get("/{game_id}/competitions", tags=["competition-types"])
async def get_competitions(game_id: str):
    competitions = database.select_many(
        "competition_types",
        ["id", "name", "game_id"],
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "game_id": game_id
            }
        })
    )

    return JSONResponse(competitions)


@router.post("/competitions", tags=["competition-types"])
async def create_competition(competition: ClientOlympicCompetitionType):
    competition_dict = competition.model_dump(exclude={
        "id": True
    })
    route_model = OlympicCompetitionType(
        **competition_dict,
        id=uuid4()
    )

    database.insert("competition_types", route_model.model_dump())


@router.put("/competitions", tags=["competition-types"])
async def update_route(competition: ClientOlympicCompetitionType):
    client_competition_dict = competition.model_dump(exclude={
        "id": True,
        "game_id": True,
    })

    database.update(
        "competition_types",
        client_competition_dict.keys(),
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": competition.id
            }
        }),
        client_competition_dict.values()
    )


@router.delete("/competitions/{competition_id}", tags=["competition-types"])
async def delete_route(competition_id: str):
    database.delete(
        "competition_types",
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": competition_id
            }
        })
    )


@router.get("/{game_id}/{competition_id}", tags=["olympic-players"])
async def get_competition_player(game_id: str, competition_id: str):

    players = database.execute(f"""
        SELECT op.id, op.name, country, ranking, 
        score, age, sport, height, weight, competition_id 
        FROM olympic_players op 
        JOIN competition_types ct on ct.id = op.competition_id
        WHERE ct.game_id = '{game_id}' AND ct.id = '{competition_id}';
    """).fetchall()

    print(game_id)
    print(players)

    return players


@router.post("/competitions/{competition_id}", tags=["olympic-players"])
async def create_player(competition_id: str, olympic_player: ClientOlympicPlayer):
    client_olympic_player_dict = olympic_player.model_dump(exclude={"id": True})
    olympic_player_model = OlympicPlayer(
        **client_olympic_player_dict,
        id=uuid4()
    )

    database.insert("olympic_players", olympic_player_model.model_dump())


@router.put("/competitions/{competition_id}", tags=["trams"])
async def update_player(competition_id: str, client_player: ClientOlympicPlayer):

    client_player_dict = client_player.model_dump(exclude={
        "id": True,
        "competition_id": True,
    })

    database.update(
        "olympic_players",
        client_player_dict.keys(),
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": client_player.id,
                "competition_id": client_player.competition_id
            }
        }),
        client_player_dict.values()
    )


@router.delete("/competitions/{competition_id}/{player_id}", tags=["trams"])
async def delete_player(competition_id: str, player_id: str):
    database.delete(
        "olympic_players",
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": player_id
            }
        })
    )
