weather_tool = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get weather and rainfall information for a city.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "Name of the city"
                }
            },
            "required": ["city"]
        }
    }
}


crop_tool = {
    "type": "function",
    "function": {
        "name": "get_crop_advisory",
        "description": "Get agricultural advisory for a crop.",
        "parameters": {
            "type": "object",
            "properties": {
                "crop": {
                    "type": "string",
                    "description": "Name of the crop"
                }
            },
            "required": ["crop"]
        }
    }
}


market_tool = {
    "type": "function",
    "function": {
        "name": "get_market_price",
        "description": "Get the current market price of a crop.",
        "parameters": {
            "type": "object",
            "properties": {
                "crop": {
                    "type": "string",
                    "description": "Name of the crop"
                }
            },
            "required": ["crop"]
        }
    }
}


TOOLS = [
    weather_tool,
    crop_tool,
    market_tool
]