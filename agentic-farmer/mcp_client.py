import anyio

from mcp import Client
from mcp.client.stdio import StdioServerParameters


# ---------------------------------------------------------
# MCP Server configuration
# ---------------------------------------------------------

server_params = StdioServerParameters(
    command="uv",
    args=[
        "run",
        "python",
        "mcp_server/server.py"
    ]
)


# ---------------------------------------------------------
# Main MCP Client
# ---------------------------------------------------------

async def main():

    print("\n======================================")
    print("     MCP CLIENT - FARMER ASSISTANT")
    print("======================================")

    # Start MCP server and connect to it
    async with Client(server_params) as client:

        print("\nConnected to MCP Server.")

        # -------------------------------------------------
        # 1. Discover available tools
        # -------------------------------------------------

        result = await client.list_tools()

        print("\nAvailable MCP Tools:")
        print("--------------------")

        for tool in result.tools:

            print(f"\nTool Name : {tool.name}")
            print(f"Description: {tool.description}")
            print(f"Input Schema: {tool.input_schema}")

        # -------------------------------------------------
        # 2. Call Weather Tool
        # -------------------------------------------------

        print("\n======================================")
        print("Calling Weather Tool")
        print("======================================")

        weather_result = await client.call_tool(
            "weather",
            {
                "city": "Kallakurichi"
            }
        )

        print("\nWeather Result:")
        print(weather_result)

        # -------------------------------------------------
        # 3. Call Crop Advisory Tool
        # -------------------------------------------------

        print("\n======================================")
        print("Calling Crop Advisory Tool")
        print("======================================")

        crop_result = await client.call_tool(
            "crop_advisory",
            {
                "crop": "groundnut"
            }
        )

        print("\nCrop Advisory Result:")
        print(crop_result)

        # -------------------------------------------------
        # 4. Call Market Price Tool
        # -------------------------------------------------

        print("\n======================================")
        print("Calling Market Price Tool")
        print("======================================")

        market_result = await client.call_tool(
            "market_price",
            {
                "crop": "groundnut"
            }
        )

        print("\nMarket Price Result:")
        print(market_result)


# ---------------------------------------------------------
# Application entry point
# ---------------------------------------------------------

if __name__ == "__main__":
    anyio.run(main)