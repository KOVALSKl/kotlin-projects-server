from datetime import datetime

from uuid import uuid4, UUID
from typing import Dict, List, Union
from pydantic import BaseModel, Field, field_serializer


class DataBaseModel(BaseModel):
    id: UUID = Field(default=uuid4())

    # created_at: str = datetime.utcnow().isoformat()

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
    name: str
    channel_id: UUID

    @field_serializer("channel_id")
    def serialize_channel_id(self, channel_id: UUID, _info):
        return str(channel_id)


class ClientNewsSection(BaseModel):
    id: UUID = Field(exclude=True)
    name: str
    channel_id: UUID


class News(DataBaseModel):
    title: str
    author: str
    date: str
    content: str
    news_section_id: UUID

    @field_serializer("news_section_id")
    def serialize_news_section_id(self, news_section_id: UUID, _info):
        return str(news_section_id)


class ClientNews(BaseModel):
    id: str
    title: str
    author: str
    date: str
    content: str
    news_section_id: str


# DELIVERY CLUB
class DeliveryService(DataBaseModel):
    name: str


class ClientDeliveryService(BaseModel):
    id: UUID = Field(exclude=True)
    name: str


class Store(DataBaseModel):
    name: str
    service_id: UUID

    @field_serializer("service_id")
    def serialize_service_id(self, service_id: UUID, _info):
        return str(service_id)


class ClientStore(BaseModel):
    id: UUID = Field(exclude=True)
    name: str
    service_id: UUID


class Order(DataBaseModel):
    title: str
    date: str
    amount: int
    store_id: UUID

    @field_serializer("store_id")
    def serialize_store_id(self, store_id: UUID, _info):
        return str(store_id)


class ClientOrder(BaseModel):
    id: str
    title: str
    date: str
    amount: int
    store_id: str


class Depot(DataBaseModel):
    name: str


class ClientDepot(BaseModel):
    id: UUID = Field(exclude=True)
    name: str


class Route(DataBaseModel):
    name: str
    depot_id: UUID

    @field_serializer("depot_id")
    def serialize_depot_id(self, depot_id: UUID, _info):
        return str(depot_id)


class ClientRoute(BaseModel):
    id: UUID = Field(exclude=True)
    name: str
    depot_id: UUID


class Transport(DataBaseModel):
    number: str
    departure_time: str
    return_time: str
    route_id: UUID

    @field_serializer("route_id")
    def serialize_route_id(self, route_id: UUID, _info):
        return str(route_id)


class ClientTransport(BaseModel):
    id: str
    number: str
    departure_time: str
    return_time: str
    route_id: UUID
