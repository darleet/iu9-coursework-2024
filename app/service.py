import asyncio

import aiohttp
from pydantic.validators import Decimal
from starlette.status import HTTP_200_OK

from app.schemas import ExternalMeteoResponseErrorSchema, ExternalMeteoResponseSchema


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
                    "hourly": "temperature_2m,relative_humidity_2m,visibility",
                },
            )
        )
        for latitude, longitude in coordinates
    ]
    responses = await asyncio.gather(*tasks)

    response: ExternalMeteoResponseSchema
    for response in responses:
        temperature = response.hourly.temperature_2m[0]
        relative_humidity = response.hourly.relative_humidity_2m[0]
        visibility = response.hourly.visibility[0]

        # Calculate ice formation probability on a scale of 0 to 100
        ice_probability = max(
            0,
            min(100, (0 - temperature) * 2 + (relative_humidity - 80) * Decimal("0.5")),
        )
        ice_probabilities.append(ice_probability)

        # Calculate visibility score on a scale of 0 to 100
        visibility_score = max(0, min(100, (visibility / 1000) * 100))
        visibility_scores.append(visibility_score)

    return ice_probabilities, visibility_scores
