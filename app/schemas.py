from pydantic import BaseModel
from pydantic.validators import Decimal


class RouteRequestSchema(BaseModel):
    coordinates: list[list[Decimal]]


class RouteResponseSchema(BaseModel):
    ice_probabilities: list[Decimal]
    visibility_scores: list[Decimal]


class JSONResponseSchema(BaseModel):
    data: BaseModel


class HourlyData(BaseModel):
    temperature_2m: list[Decimal]
    relative_humidity_2m: list[Decimal]
    visibility: list[Decimal]


class ExternalMeteoResponseSchema(BaseModel):
    hourly: HourlyData


class ExternalMeteoResponseErrorSchema(BaseModel):
    error: bool
    reason: str
