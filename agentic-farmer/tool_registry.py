from tools.weather_tool import get_weather
from tools.crop_tool import get_crop_advisory
from tools.market_tool import get_market_price


TOOL_REGISTRY = {
    "get_weather": get_weather,
    "get_crop_advisory": get_crop_advisory,
    "get_market_price": get_market_price
}


def execute_tool(tool_name: str, arguments: dict):

    if tool_name not in TOOL_REGISTRY:
        raise ValueError(
            f"Unknown tool: {tool_name}"
        )

    tool_function = TOOL_REGISTRY[tool_name]

    return tool_function(**arguments)

if __name__ == "__main__":

    result = execute_tool(
        "get_weather",
        {"city": "Kallakurichi"}
    )

    print(result)

    result = execute_tool(
        "get_crop_advisory",
        {"crop": "groundnut"}
    )

    print(result)

    result = execute_tool(
        "get_market_price",
        {"crop": "groundnut"}
    )

    print(result)