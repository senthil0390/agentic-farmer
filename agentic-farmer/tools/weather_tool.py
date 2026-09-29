def get_weather(city: str) -> dict:
    """
    Get weather information for a city.
    """

    weather_data = {
        "Trichy": {
            "temperature": 31,
            "rainfall_probability": 70,
            "rainfall_mm": 12
        },
        "Chennai": {
            "temperature": 33,
            "rainfall_probability": 40,
            "rainfall_mm": 5
        }
    }

    return weather_data.get(
        city,
        {
            "temperature": None,
            "rainfall_probability": None,
            "rainfall_mm": None
        }
    )