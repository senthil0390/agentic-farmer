from mcp.server import MCPServer


mcp = MCPServer("Farmer Assistant MCP Server")


@mcp.tool()
def weather(city: str) -> dict:
    """
    Get weather and rainfall information for a city.
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


@mcp.tool()
def crop_advisory(crop: str) -> dict:
    """
    Get agricultural advisory information for a crop.
    """

    advisory_data = {
        "groundnut": {
            "crop": "groundnut",
            "advisory": [
                "Maintain appropriate soil moisture.",
                "Monitor the crop for fungal diseases.",
                "Avoid unnecessary irrigation during heavy rainfall."
            ]
        },
        "rice": {
            "crop": "rice",
            "advisory": [
                "Maintain proper water level.",
                "Monitor pest activity.",
                "Follow recommended fertilizer application."
            ]
        }
    }

    return advisory_data.get(
        crop.lower(),
        {
            "crop": crop,
            "advisory": ["No advisory available."]
        }
    )


@mcp.tool()
def market_price(crop: str) -> dict:
    """
    Get market price information for a crop.
    """

    market_data = {
        "groundnut": {
            "crop": "groundnut",
            "market": "Kallakurichi",
            "price_per_kg": 72
        },
        "rice": {
            "crop": "rice",
            "market": "Kallakurichi",
            "price_per_kg": 45
        }
    }

    return market_data.get(
        crop.lower(),
        {
            "crop": crop,
            "market": "Unknown",
            "price_per_kg": None
        }
    )


if __name__ == "__main__":
    mcp.run()