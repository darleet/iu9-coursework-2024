import asyncio

import aiohttp
from pydantic.validators import Decimal
from starlette.status import HTTP_200_OK

from app.schemas import ExternalMeteoResponseErrorSchema, ExternalMeteoResponseSchema


def calculate_ice_probability(temperature: Decimal, dew_point: Decimal) -> Decimal:
    deficit = Decimal(temperature) - Decimal(dew_point)

    # Определяем граничные функции
    def f1(arg: Decimal) -> Decimal:
        return -Decimal(1) / 6 * (arg - Decimal(2)) ** 2 + Decimal(7)

    def f2(arg: Decimal) -> Decimal:
        return -Decimal(1) / 3 * arg + Decimal(7)

    def f3(arg: Decimal) -> Decimal:
        return -Decimal(1) / 30 * (arg - Decimal(16)) ** 2 + Decimal(3)

    x = Decimal(temperature)
    f_val = min(f1(x), f2(x), f3(x))

    # Дискретизация риска на основе пороговых коэффициентов
    if deficit >= f_val:
        return Decimal("1.0")
    elif deficit >= Decimal("0.9") * f_val:
        return Decimal("0.6")
    elif deficit >= Decimal("0.8") * f_val:
        return Decimal("0.5")
    elif deficit >= Decimal("0.7") * f_val:
        return Decimal("0.3")
    else:
        return Decimal("0.0")


async def fetch(url: str, params: dict) -> ExternalMeteoResponseSchema:
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            json_data = await response.json()
            if response.status != HTTP_200_OK:
                data = ExternalMeteoResponseErrorSchema(**json_data)
                raise Exception(f"HTTP error {response.status}: {data.reason}")
            return ExternalMeteoResponseSchema(**json_data)


async def check_route(coordinates: list) -> tuple[list, list]:
    ice_probabilities = []
    visibility_scores = []

    tasks = [
        asyncio.create_task(
            fetch(
                "https://api.open-meteo.com/v1/forecast",
                params={
                    "latitude": latitude,
                    "longitude": longitude,
                    "hourly": "temperature_2m,dew_point_2m,visibility",
                },
            )
        )
        for latitude, longitude in coordinates
    ]
    responses = await asyncio.gather(*tasks)

    response: ExternalMeteoResponseSchema
    for response in responses:
        temperature = response.hourly.temperature_2m[0]
        dew_point_2m = response.hourly.dew_point_2m[0]
        visibility = response.hourly.visibility[0]

        # Calculate ice formation probability on a scale of 0 to 100
        ice_probability = calculate_ice_probability(temperature, dew_point_2m)
        ice_probabilities.append(ice_probability)

        # Calculate visibility score on a scale of 0 to 100
        visibility_score = max(0, min(100, (visibility / 1000) * 100))
        visibility_scores.append(visibility_score)

    return ice_probabilities, visibility_scores
