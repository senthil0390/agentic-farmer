def get_crop_advisory(crop: str) -> dict:
    """
    Get agricultural advisory for a crop.
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