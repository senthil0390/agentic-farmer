def get_market_price(crop: str) -> dict:
    """
    Get current market price for a crop.
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