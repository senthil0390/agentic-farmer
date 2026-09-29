from tools.weather_tool import get_weather
from tools.crop_tool import get_crop_advisory
from tools.market_tool import get_market_price

def main():
    print("Hello from agentic-farmer!")
    print("=== Weather Tool ===")

    weather = get_weather("Trichy")

    print(weather)

    print("\n=== Crop Advisory Tool ===")

    advisory = get_crop_advisory("groundnut")

    print(advisory)

    print("\n=== Market Price Tool ===")

    market = get_market_price("groundnut")

    print(market)


if __name__ == "__main__":
    main()
