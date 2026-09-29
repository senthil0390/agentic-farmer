import anyio
import json

from ollama import chat
from mcp import Client
from mcp.client.stdio import StdioServerParameters


# ---------------------------------------------------------
# MCP SERVER CONFIGURATION
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
# OLLAMA MODEL
# ---------------------------------------------------------

MODEL = "qwen3:0.6b"


# ---------------------------------------------------------
# CONVERT MCP TOOLS -> OLLAMA TOOLS
# ---------------------------------------------------------

def convert_mcp_tools_to_ollama(mcp_tools):

    ollama_tools = []

    for tool in mcp_tools:

        ollama_tool = {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description or "",
                "parameters": tool.input_schema
            }
        }

        ollama_tools.append(ollama_tool)

    return ollama_tools


# ---------------------------------------------------------
# EXTRACT MCP RESULT
# ---------------------------------------------------------

def extract_mcp_result(result):

    # Prefer structured content if available
    if result.structured_content is not None:
        return result.structured_content

    # Otherwise extract text content
    output = []

    for item in result.content:

        if hasattr(item, "text"):
            output.append(item.text)

    return "\n".join(output)


# ---------------------------------------------------------
# MAIN AGENT
# ---------------------------------------------------------

async def main():

    print("\n==============================================")
    print("       OLLAMA + MCP FARMER AGENT")
    print("==============================================")

    # Connect to MCP server
    async with Client(server_params) as client:

        print("\nConnected to MCP Server.")

        # -------------------------------------------------
        # STEP 1: DISCOVER MCP TOOLS
        # -------------------------------------------------

        mcp_result = await client.list_tools()

        print("\nMCP Tools Discovered:")
        print("---------------------")

        for tool in mcp_result.tools:
            print(f"- {tool.name}")

        # -------------------------------------------------
        # STEP 2: CONVERT MCP TOOLS TO OLLAMA FORMAT
        # -------------------------------------------------

        ollama_tools = convert_mcp_tools_to_ollama(
            mcp_result.tools
        )

        print("\nTools passed to Ollama:")
        print("----------------------")

        for tool in ollama_tools:
            print(
                f"- {tool['function']['name']}"
            )

        # -------------------------------------------------
        # STEP 3: USER QUESTION
        # -------------------------------------------------

        user_query = input(
            "\nAsk Farmer Assistant: "
        )

        messages = [
            {
                "role": "user",
                "content": user_query
            }
        ]

        # -------------------------------------------------
        # STEP 4: ASK OLLAMA
        # -------------------------------------------------

        response = chat(
            model=MODEL,
            messages=messages,
            tools=ollama_tools
        )

        # -------------------------------------------------
        # STEP 5: TOOL-CALL LOOP
        # -------------------------------------------------

        while response.message.tool_calls:

            # Add Ollama's tool-call message
            messages.append(response.message)

            print("\nOllama requested tool(s):")

            # -------------------------------------------------
            # STEP 6: EXECUTE EACH TOOL THROUGH MCP
            # -------------------------------------------------

            for tool_call in response.message.tool_calls:

                tool_name = tool_call.function.name
                arguments = tool_call.function.arguments

                print(
                    f"\nCalling MCP tool: {tool_name}"
                )

                print(
                    f"Arguments: {arguments}"
                )

                # Call MCP tool dynamically
                result = await client.call_tool(
                    tool_name,
                    arguments
                )

                # Extract MCP result
                tool_output = extract_mcp_result(
                    result
                )

                print(
                    f"MCP Result: {tool_output}"
                )

                # -------------------------------------------------
                # STEP 7: SEND MCP RESULT BACK TO OLLAMA
                # -------------------------------------------------

                messages.append(
                    {
                        "role": "tool",
                        "content": json.dumps(
                            tool_output,
                            ensure_ascii=False
                        ),
                        "tool_name": tool_name
                    }
                )

            # -------------------------------------------------
            # STEP 8: ASK OLLAMA AGAIN
            # -------------------------------------------------

            response = chat(
                model=MODEL,
                messages=messages,
                tools=ollama_tools
            )

        # -------------------------------------------------
        # STEP 9: FINAL ANSWER
        # -------------------------------------------------

        print("\n==============================================")
        print("             FINAL ANSWER")
        print("==============================================")

        print(
            response.message.content
        )


# ---------------------------------------------------------
# PROGRAM ENTRY
# ---------------------------------------------------------

if __name__ == "__main__":
    anyio.run(main)