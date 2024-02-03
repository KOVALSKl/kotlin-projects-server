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
    driver_name: str
    conductor_name: str
    price: int
    capacity: int
    trip_number: str
    departure_time: str
    return_time: str
    route_id: UUID

    @field_serializer("route_id")
    def serialize_route_id(self, route_id: UUID, _info):
        return str(route_id)


class ClientTransport(BaseModel):
    id: UUID
    number: str
    driver_name: str
    conductor_name: str
    price: int
    capacity: int
    trip_number: str
    departure_time: str
    return_time: str
    route_id: UUID


# TRAM DEPOT 14
class TramDepot(DataBaseModel):
    name: str


class ClientTramDepot(BaseModel):
    id: UUID
    name: str


class TramRoute(DataBaseModel):
    name: str
    depot_id: UUID

    @field_serializer("depot_id")
    def serialize_depot_id(self, depot_id: UUID, _info):
        return str(depot_id)


class ClientTramRoute(BaseModel):
    id: UUID
    name: str
    depot_id: UUID


class Tram(DataBaseModel):
    number: str
    driver_name: str
    conductor_name: str
    start_date: str
    trip_number: int
    capacity: int
    total_distance: int
    price: int
    route_id: UUID

    @field_serializer("route_id")
    def serialize_route_id(self, route_id: UUID, _info):
        return str(route_id)


class ClientTram(BaseModel):
    id: UUID
    number: str
    driver_name: str
    conductor_name: str
    start_date: str
    trip_number: int
    capacity: int
    total_distance: int
    price: int
    route_id: UUID


# CARS 3

class CarModel(DataBaseModel):
    name: str


class ClientCarModel(BaseModel):
    id: UUID = Field(UUID, exclude=True)
    name: str


class CatalogSection(DataBaseModel):
    name: str
    car_model_id: UUID

    @field_serializer("car_model_id")
    def serialize_car_model_id(self, car_model_id: UUID, _info):
        return str(car_model_id)


class ClientCatalogSection(BaseModel):
    id: UUID = Field(UUID, exclude=True)
    name: str
    car_model_id: UUID


class SparePart(DataBaseModel):
    name: str
    catalog_number: str
    producer: str
    price: int
    weight: int
    description: str
    availability_count: int
    create_date: str
    catalog_section_id: UUID

    @field_serializer("catalog_section_id")
    def serialize_catalog_section_id(self, catalog_section_id: UUID, _info):
        return str(catalog_section_id)


class ClientSparePart(BaseModel):
    id: UUID = Field(UUID, exclude=True)
    name: str
    catalog_number: str
    producer: str
    price: int
    weight: int
    description: str
    availability_count: int
    create_date: str
    catalog_section_id: UUID


# INDUSTRIAL GOODS STORES

class IndustrialStores(DataBaseModel):
    name: str


class ClientIndustrialStores(BaseModel):
    id: UUID = Field(UUID, exclude=True)
    name: str


class IndustrialDepartment(DataBaseModel):
    name: str
    store_id: UUID

    @field_serializer("store_id")
    def serialize_store_id(self, store_id: UUID, _info):
        return str(store_id)


class ClientIndustrialDepartment(BaseModel):
    id: UUID = Field(UUID, exclude=True)
    name: str
    store_id: UUID


class IndustrialProduct(DataBaseModel):
    name: str
    item_number: str
    weight: int
    price: int
    producer: str
    description: str
    packing_date: str
    department_id: UUID

    @field_serializer("department_id")
    def serialize_department_id(self, department_id: UUID, _info):
        return str(department_id)


class ClientIndustrialProduct(BaseModel):
    id: UUID = Field(UUID, exclude=True)
    name: str
    item_number: str
    weight: int
    price: int
    producer: str
    description: str
    packing_date: str
    department_id: UUID


# DELIVERY SERVICES (DELIVERS) 5

class Courier(DataBaseModel):
    name: str
    deliver_service_id: UUID

    @field_serializer("deliver_service_id")
    def serialize_deliver_service_id(self, deliver_service_id: UUID, _info):
        return str(deliver_service_id)


class ClientCourier(BaseModel):
    id: UUID = Field(UUID, exclude=True)
    name: str
    deliver_service_id: UUID


class CourierOrder(DataBaseModel):
    name: str
    date: str
    time: str
    address: str
    delivery_time: str
    total_weight: int
    items: int
    total_amount: int
    courier_id: UUID

    @field_serializer("courier_id")
    def serialize_courier_id(self, courier_id: UUID, _info):
        return str(courier_id)


class ClientCourierOrder(BaseModel):
    id: UUID
    name: str
    date: str
    time: str
    address: str
    delivery_time: str
    total_weight: int
    items: int
    total_amount: int
    courier_id: UUID


# PHARMACY 48 - 13

class Pharmacy(DataBaseModel):
    name: str


class ClientPharmacy(BaseModel):
    id: UUID
    name: str


class MedicationGroup(DataBaseModel):
    name: str
    pharmacy_id: UUID

    @field_serializer("pharmacy_id")
    def serialize_pharmacy_id(self, pharmacy_id: UUID, _info):
        return str(pharmacy_id)


class ClientMedicationGroup(BaseModel):
    id: UUID
    name: str
    pharmacy_id: UUID


class Medication(DataBaseModel):
    name: str
    dosage: str
    volume: str
    price: int
    producer: str
    expiration_date: str
    description: str
    effects: str
    medication_group_id: UUID

    @field_serializer("medication_group_id")
    def serialize_medication_group_id(self, medication_group_id: UUID, _info):
        return str(medication_group_id)


class ClientMedication(BaseModel):
    id: UUID
    name: str
    dosage: str
    volume: str
    price: int
    producer: str
    expiration_date: str
    description: str
    effects: str
    medication_group_id: UUID


# OLYMPIC 48 - 13

class OlympicGame(DataBaseModel):
    name: str


class ClientOlympicGame(BaseModel):
    id: UUID
    name: str


class OlympicCompetitionType(DataBaseModel):
    name: str
    game_id: UUID

    @field_serializer("game_id")
    def serialize_game_id(self, game_id: UUID, _info):
        return str(game_id)


class ClientOlympicCompetitionType(BaseModel):
    id: UUID
    name: str
    game_id: UUID


class OlympicPlayer(DataBaseModel):
    name: str
    country: str
    ranking: int
    score: str
    age: int
    sport: str
    height: int
    weight: int
    competition_id: UUID

    @field_serializer("competition_id")
    def serialize_competition_id(self, competition_id: UUID, _info):
        return str(competition_id)


class ClientOlympicPlayer(BaseModel):
    id: UUID
    name: str
    country: str
    ranking: int
    score: str
    age: int
    sport: str
    height: int
    weight: int
    competition_id: UUID


# 14-48 Restaurant

class Restaurant(DataBaseModel):
    name: str


class ClientRestaurant(BaseModel):
    id: UUID
    name: str


class DishCategory(DataBaseModel):
    name: str
    restaurant_id: UUID

    @field_serializer("restaurant_id")
    def serialize_restaurant_id(self, restaurant_id: UUID, _info):
        return str(restaurant_id)


class ClientDishCategory(BaseModel):
    id: UUID
    name: str
    restaurant_id: UUID


class Dish(DataBaseModel):
    name: str
    price: int
    calories: int
    ingredients: str
    is_vegetarian: int
    is_spicy: int
    description: str
    score: int
    category_id: UUID

    @field_serializer("category_id")
    def serialize_category_id(self, category_id: UUID, _info):
        return str(category_id)


class ClientDish(BaseModel):
    id: UUID
    name: str
    price: int
    calories: int
    ingredients: str
    is_vegetarian: int
    is_spicy: int
    description: str
    score: int
    category_id: UUID


class OlympTask(DataBaseModel):
    name: str


class ClientOlympTask(BaseModel):
    id: UUID
    name: str


class OlympProfile(DataBaseModel):
    name: str
    olymp_task_id: UUID

    @field_serializer("olymp_task_id")
    def serialize_olymp_task_id(self, olymp_task_id: UUID, _info):
        return str(olymp_task_id)


class ClientOlympProfile(BaseModel):
    id: UUID
    name: str
    olymp_task_id: UUID


class OlympParticipant(DataBaseModel):
    full_name: str
    qualification_score: int
    final_score: int
    hobbies: str
    country: str
    school: str
    achievements: str
    additional_information: str
    olymp_profile_id: UUID

    @field_serializer("olymp_profile_id")
    def serialize_olymp_profile_id(self, olymp_profile_id: UUID, _info):
        return str(olymp_profile_id)


class ClientOlympParticipant(BaseModel):
    id: UUID
    full_name: str
    qualification_score: int
    final_score: int
    hobbies: str
    country: str
    school: str
    achievements: str
    additional_information: str
    olymp_profile_id: UUID


class FlightDirection(DataBaseModel):
    name: str


class ClientFlightDirection(BaseModel):
    id: UUID
    name: str


class FlightDateTime(DataBaseModel):
    name: str
    flight_id: UUID

    @field_serializer("flight_id")
    def serialize_flight_id(self, flight_id: UUID, _info):
        return str(flight_id)


class ClientFlightDateTime(BaseModel):
    id: UUID
    name: str
    flight_id: UUID


class FlightTicket(DataBaseModel):
    flight_number: str
    cost: int
    occupancy: int
    total_seats: int
    departure_airport: str
    arrival_airport: str
    departure_time: str
    arrival_time: str
    datetime_id: UUID

    @field_serializer("datetime_id")
    def serialize_datetime_id(self, datetime_id: str, _info):
        return str(datetime_id)


class ClientFlightTicket(BaseModel):
    id: UUID
    flight_number: str
    cost: int
    occupancy: int
    total_seats: int
    departure_airport: str
    arrival_airport: str
    departure_time: str
    arrival_time: str
    datetime_id: UUID


class JSONTestModel(BaseModel):
    number: str
    data: str
    client_inn: str
    region: int
    address: str
    items: list
