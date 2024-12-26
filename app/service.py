import logging

import requests
from starlette.status import HTTP_200_OK

from app.schemas import ExternalMeteoResponseErrorSchema, ExternalMeteoResponseSchema

logger = logging.getLogger(__name__)


async def check_route(coordinates: list) -> tuple[list, list]:
    ice_probabilities = []
    visibility_scores = []

    for latitude, longitude in coordinates:
        response = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "hourly": "temperature_2m,relative_humidity_2m,visibility",
            },
        )

        data: ExternalMeteoResponseSchema | ExternalMeteoResponseErrorSchema

        if response.status_code != HTTP_200_OK:
            data = ExternalMeteoResponseErrorSchema(**response.json())
            raise Exception(data.reason)

        data = ExternalMeteoResponseSchema(**response.json())

        temperature = data.hourly.temperature_2m[0]
        relative_humidity = data.hourly.relative_humidity_2m[0]
        visibility = data.hourly.visibility[0]

        # Calculate ice formation probability on a scale of 0 to 100
        ice_probability = max(
            0, min(100, (0 - temperature) * 2 + (relative_humidity - 80) * 0.5)
        )
        ice_probabilities.append(ice_probability)

        # Calculate visibility score on a scale of 0 to 100
        visibility_score = max(0, min(100, (visibility / 1000) * 100))
        visibility_scores.append(visibility_score)

    return ice_probabilities, visibility_scores
