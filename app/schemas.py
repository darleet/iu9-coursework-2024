from pydantic import BaseModel


class RouteRequestSchema(BaseModel):
    coordinates: list


class RouteResponseSchema(BaseModel):
    ice_probabilities: list
    visibility_scores: list


class JSONResponseSchema(BaseModel):
    data: BaseModel


class JSONErrorSchema(BaseModel):
    status: str
    reason: str


class HourlyData(BaseModel):
    temperature_2m: list
    relative_humidity_2m: list
    visibility: list


class ExternalMeteoResponseSchema(BaseModel):
    hourly: HourlyData


class ExternalMeteoResponseErrorSchema(BaseModel):
    error: bool
    reason: str
