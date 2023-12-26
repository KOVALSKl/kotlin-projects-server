from datetime import datetime

from uuid import uuid4, UUID
from typing import Dict, List, Union
from pydantic import BaseModel, Field, field_serializer


class DataBaseModel(BaseModel):
    id: UUID = Field(default=uuid4())
    created_at: str = datetime.utcnow().isoformat()
    
    @field_serializer("id")
    def serialize_id(self, id: UUID, _info):
        return str(id)


class User(DataBaseModel):
    name: str
    surname: Union[str, None]
    login: str
    password: str


class RegistrationUser(BaseModel):
    name: str
    surname: Union[str, None]
    login: str
    password: str


class LoginUser(BaseModel):
    login: str
    password: str


class Channel(DataBaseModel):
    name: str


class ClientChannel(BaseModel):
    id: UUID = Field(exclude=True)
    name: str


class NewsSection(DataBaseModel):
    news: str
    channel_id: UUID

    @field_serializer("channel_id")
    def serialize_channel_id(self, channel_id: UUID, _info):
        return str(channel_id)


class News(DataBaseModel):
    title: str
    date: str
    content: str
    news_section_id: UUID
    channel_id: UUID

    @field_serializer("news_section_id")
    def serialize_news_section_id(self, news_section_id: UUID, _info):
        return str(news_section_id)

    @field_serializer("channel_id")
    def serialize_channel_id(self, channel_id: UUID, _info):
        return str(channel_id)


class ClientNews(BaseModel):
    title: str
    date: str
    content: str
    channel_id: str
