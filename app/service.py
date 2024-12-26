import folium
import requests
from folium import Map


def create_map() -> Map:
    map_center = [61.5240, 105.3188]  # центр России
    folium_map = folium.Map(location=map_center, zoom_start=4)

    cities = [
        {"name": "Москва", "latitude": 55.7558, "longitude": 37.6173},
        {"name": "Санкт-Петербург", "latitude": 59.9343, "longitude": 30.3351},
        {"name": "Екатеринбург", "latitude": 56.8389, "longitude": 60.6057},
    ]

    for city in cities:
        response = requests.get(
            f"https://api.open-meteo.com/v1/forecast?latitude={city['latitude']}"
            f"&longitude={city['longitude']}&hourly=temperature_2m"
        )
        data = response.json()
        temp = data["hourly"]["temperature_2m"][0]

        folium.Marker(
            location=[city["latitude"], city["longitude"]],  # type: ignore
            popup=f"{city['name']}: {temp}°C",
            icon=folium.Icon(color="blue", icon="info-sign"),
        ).add_to(folium_map)

    return folium_map
