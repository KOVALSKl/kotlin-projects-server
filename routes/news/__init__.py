from uuid import uuid4
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from database import *
from database.models import News, Channel, NewsSection, ClientNews, ClientChannel, ClientNewsSection

router = APIRouter(
    prefix="/news",
)


@router.on_event("startup")
async def startup():
    """Создание необходимых таблиц"""
    database.create_table(
        "news_channels",
        {
            "id": [DatabaseTypes.TEXT, DatabaseTypes.PRIMARY_KEY],
            "name": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL, DatabaseTypes.UNIQUE],
            "created_at": [DatabaseTypes.TEXT]
        }
    )

    database.create_table(
        "news_sections",
        {
            "id": [DatabaseTypes.TEXT, DatabaseTypes.PRIMARY_KEY],
            "name": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL, DatabaseTypes.UNIQUE],
            "created_at": [DatabaseTypes.TEXT],
            "channel_id": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL]
        },
        {
            "channel_id": DatabaseReference(
                "news_channels",
                "id",
                on_delete=DatabaseActions.CASCADE
            )
        }
    )

    database.create_table(
        "channel_articles",
        {
            "id": [DatabaseTypes.TEXT, DatabaseTypes.PRIMARY_KEY],
            "title": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL, DatabaseTypes.UNIQUE],
            "author": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
            "date": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
            "content": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
            "created_at": [DatabaseTypes.TEXT],
            "news_section_id": [DatabaseTypes.TEXT, DatabaseTypes.NOT_NULL],
        },
        {
            "news_section_id": DatabaseReference(
                "news_sections",
                "id",
                on_delete=DatabaseActions.CASCADE
            ),
        }
    )


@router.get("/channels", tags=["channels"])
async def get_channels():
    channels = database.select_many(
        "news_channels",
        ["*"]
    )

    return JSONResponse(channels)


@router.post("/channels", tags=["channels"])
async def create_channel(client_channel: ClientChannel):

    """Создание необходимых таблиц"""
    client_channel_dict = client_channel.model_dump()
    channel_model = Channel(
        **client_channel_dict,
    )

    database.insert("news_channels", channel_model.model_dump())


@router.put("/channels", tags=["channels"])
async def update_channel(client_channel: ClientChannel):
    client_channel_dict = client_channel.model_dump(exclude={"id": True})

    database.update(
        "news_channels",
        client_channel_dict.keys(),
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": client_channel.id
            }
        }),
        client_channel_dict.values()
    )


@router.delete("/channels/{channel_id}", tags=["channels"])
async def delete_channel(channel_id: str):

    database.delete(
        "news_channels",
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": channel_id
            }
        })
    )


@router.get("/channels/{channel_id}", tags=["news"])
async def get_channel_news(channel_id: str):
    channel = database.select_many(
        "channel_articles",
        ['id', 'title', 'date'],
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "channel_id": channel_id
            }
        })
    )

    return JSONResponse(channel)


@router.post("/channels/{channel_id}", tags=["news"])
async def create_news(channel_id: str, client_news: ClientNews):
    client_news_dict = client_news.model_dump()
    news_model = NewsSection(
        **client_news_dict,
    )

    database.insert("channel_articles", news_model.model_dump())


@router.get("/{channel_id}/sections", tags=["sections"])
async def get_channel_sections(channel_id: str):
    sections = database.select_many(
        "news_sections",
        ["id", "name", "channel_id"],
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "channel_id": channel_id
            }
        })
    )

    return JSONResponse(sections)


@router.post("/sections", tags=["sections"])
async def create_channel_section(section: ClientNewsSection):
    news_section_dict = section.model_dump()
    news_section_model = NewsSection(
        **news_section_dict,
    )

    database.insert("news_sections", news_section_model.model_dump())


@router.put("/sections", tags=["sections"])
async def update_channel_section(section: ClientNewsSection):
    client_channel_section_dict = section.model_dump(exclude={
        "id": True,
        "channel_id": True,
    })

    database.update(
        "news_sections",
        client_channel_section_dict.keys(),
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": section.id
            }
        }),
        client_channel_section_dict.values()
    )


@router.delete("/sections/{section_id}", tags=["sections"])
async def delete_channel_section(section_id: str):
    database.delete(
        "news_sections",
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": section_id
            }
        })
    )


@router.get("/{channel_id}/{section_id}", tags=["news"])
async def get_section_news(channel_id: str, section_id: str):
    print("/{channel_id}/{section_id} - SECTION_ID  = " + f"{section_id}")
    channels = database.execute(f"""
        SELECT ca.id, title, author, date, content, news_section_id FROM channel_articles ca 
        JOIN news_sections ns on ns.id = ca.news_section_id 
        WHERE ns.channel_id = '{channel_id}' AND ns.id = '{section_id}';
    """).fetchall()

    print(section_id)
    print(channels)

    return channels


@router.post("/sections/{section_id}", tags=["news"])
async def create_news(section_id: str, client_news: ClientNews):
    client_news_dict = client_news.model_dump(exclude={"id": True})
    news_model = News(
        **client_news_dict,
    )

    database.insert("channel_articles", news_model.model_dump())


@router.put("/sections/{section_id}", tags=["news"])
async def update_news(section_id: str, client_news: ClientNews):
    client_news_dict = client_news.model_dump(exclude={
        "id": True,
        "news_section_id": True,
    })

    database.update(
        "news_sections",
        client_news_dict.keys(),
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": client_news.news_section_id
            }
        }),
        client_news_dict.values()
    )


@router.delete("/sections/{section_id}/{news_id}", tags=["news"])
async def delete_news(section_id: str, news_id: str):
    database.delete(
        "channel_articles",
        DatabaseWhereQuery({
            DatabaseLogicalOperators.AND.value: {
                "id": news_id
            }
        })
    )
