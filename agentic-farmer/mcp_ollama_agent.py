import anyio
import json

from ollama import chat
from mcp import Client
from mcp.client.stdio import StdioServerParameters

from agent_logger import logger


# ============================================================
# CONFIGURATION
# ============================================================

MODEL = "qwen3:0.6b"

# Maximum number of tool execution rounds
MAX_TOOL_ROUNDS = 5


# ============================================================
# MCP SERVER CONFIGURATION
# ============================================================

server_params = StdioServerParameters(
    command="uv",
    args=[
        "run",
        "python",
        "mcp_server/server.py"
    ]
)


# ============================================================
# CONVERT MCP TOOLS -> OLLAMA TOOLS
# ============================================================

def convert_mcp_tools_to_ollama(mcp_tools):
    """
    Convert MCP tool definitions into the format
    expected by Ollama.
    """

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


# ============================================================
# EXTRACT MCP RESULT
# ============================================================

def extract_mcp_result(result):
    """
    Extract useful data from MCP CallToolResult.
    """

    # --------------------------------------------------------
    # MCP TOOL ERROR
    # --------------------------------------------------------

    if result.is_error:

        error_messages = []

        for item in result.content:

            if hasattr(item, "text"):
                error_messages.append(item.text)

        if error_messages:

            return {
                "error": True,
                "message": "\n".join(error_messages)
            }

        return {
            "error": True,
            "message": "MCP tool execution failed."
        }

    # --------------------------------------------------------
    # STRUCTURED CONTENT
    # --------------------------------------------------------

    if result.structured_content is not None:

        return result.structured_content

    # --------------------------------------------------------
    # TEXT CONTENT
    # --------------------------------------------------------

    output = []

    for item in result.content:

        if hasattr(item, "text"):
            output.append(item.text)

    return "\n".join(output)


# ============================================================
# MAIN AGENT
# ============================================================

async def main():

    print("\n==============================================")
    print("       OLLAMA + MCP FARMER AGENT")
    print("==============================================")

    logger.info("Starting Farmer Agent")

    # --------------------------------------------------------
    # CONNECT TO MCP SERVER
    # --------------------------------------------------------

    async with Client(server_params) as client:

        print("\nConnected to MCP Server.")

        logger.info("Connected to MCP Server")

        # ----------------------------------------------------
        # DISCOVER MCP TOOLS
        # ----------------------------------------------------

        mcp_result = await client.list_tools()

        print("\nAvailable MCP Tools:")
        print("--------------------")

        for tool in mcp_result.tools:

            print(
                f"- {tool.name}"
            )

        # ----------------------------------------------------
        # CREATE ALLOW-LIST FROM DISCOVERED TOOLS
        # ----------------------------------------------------

        allowed_tools = {
            tool.name
            for tool in mcp_result.tools
        }

        print("\nAllowed MCP Tools:")
        print("------------------")

        for tool_name in allowed_tools:

            print(
                f"- {tool_name}"
            )

        logger.info(
            "MCP tools discovered: %s",
            list(allowed_tools)
        )

        # ----------------------------------------------------
        # CONVERT MCP TO OLLAMA FORMAT
        # ----------------------------------------------------

        ollama_tools = convert_mcp_tools_to_ollama(
            mcp_result.tools
        )

        logger.info(
            "Converted %d MCP tools for Ollama",
            len(ollama_tools)
        )

        # ====================================================
        # SHORT-TERM CONVERSATION MEMORY
        # ====================================================

        messages = [

            {
                "role": "system",
                "content": (
                    "You are a helpful Farmer Assistant. "

                    "Use the available MCP tools whenever "
                    "weather, crop advisory, or market price "
                    "information is required. "

                    "Use previous conversation context when "
                    "answering follow-up questions. "

                    "Do not invent tool results. "

                    "If a tool returns an error, clearly "
                    "explain that the requested information "
                    "could not be retrieved."
                )
            }

        ]

        # ====================================================
        # CONTINUOUS CONVERSATION LOOP
        # ====================================================

        while True:

            # ------------------------------------------------
            # GET USER INPUT
            # ------------------------------------------------

            user_query = input("\nYou: ")

            # ------------------------------------------------
            # EXIT
            # ------------------------------------------------

            if user_query.lower() in [
                "exit",
                "quit",
                "bye"
            ]:

                print("\nGoodbye!")

                logger.info(
                    "User ended conversation"
                )

                break

            # ------------------------------------------------
            # LOG USER QUERY
            # ------------------------------------------------

            logger.info(
                "User query: %s",
                user_query
            )

            # ------------------------------------------------
            # ADD USER MESSAGE TO MEMORY
            # ------------------------------------------------

            messages.append(
                {
                    "role": "user",
                    "content": user_query
                }
            )

            # ------------------------------------------------
            # INITIAL OLLAMA REQUEST
            # ------------------------------------------------

            logger.info(
                "Sending request to Ollama"
            )

            response = chat(
                model=MODEL,
                messages=messages,
                tools=ollama_tools
            )

            # ------------------------------------------------
            # TOOL ROUND COUNTER
            # ------------------------------------------------

            tool_round = 0

            # =================================================
            # TOOL EXECUTION LOOP
            # =================================================

            while response.message.tool_calls:

                tool_round += 1

                print(
                    f"\nTool execution round: "
                    f"{tool_round}/{MAX_TOOL_ROUNDS}"
                )

                logger.info(
                    "Tool execution round: %d",
                    tool_round
                )

                # ------------------------------------------------
                # MAX TOOL ROUND PROTECTION
                # ------------------------------------------------

                if tool_round > MAX_TOOL_ROUNDS:

                    print(
                        "\nMaximum tool-call limit reached."
                    )

                    logger.warning(
                        "Maximum tool-call limit reached"
                    )

                    messages.append(
                        {
                            "role": "user",
                            "content": (
                                "Stop calling tools. "
                                "Provide the best possible "
                                "answer using the information "
                                "already available."
                            )
                        }
                    )

                    response = chat(
                        model=MODEL,
                        messages=messages
                    )

                    break

                # ------------------------------------------------
                # SAVE OLLAMA TOOL-CALL MESSAGE
                # ------------------------------------------------

                messages.append(
                    response.message
                )

                # ------------------------------------------------
                # PROCESS EACH TOOL CALL
                # ------------------------------------------------

                for tool_call in response.message.tool_calls:

                    tool_name = (
                        tool_call.function.name
                    )

                    arguments = (
                        tool_call.function.arguments
                    )

                    print(
                        f"\nRequested MCP tool: "
                        f"{tool_name}"
                    )

                    print(
                        f"Arguments: {arguments}"
                    )

                    logger.info(
                        "Tool requested: %s | arguments=%s",
                        tool_name,
                        arguments
                    )

                    # ==========================================
                    # SECURITY / ALLOW-LIST CHECK
                    # ==========================================

                    if tool_name not in allowed_tools:

                        print(
                            f"\nBLOCKED: Tool '{tool_name}' "
                            f"is not an allowed MCP tool."
                        )

                        logger.warning(
                            "Blocked unauthorized tool: %s",
                            tool_name
                        )

                        tool_output = {
                            "error": True,
                            "message": (
                                f"Tool '{tool_name}' "
                                "is not authorized."
                            )
                        }

                    else:

                        # ======================================
                        # EXECUTE MCP TOOL
                        # ======================================

                        print(
                            f"\nCalling MCP tool: "
                            f"{tool_name}"
                        )

                        logger.info(
                            "Executing MCP tool: %s",
                            tool_name
                        )

                        try:

                            result = await client.call_tool(
                                tool_name,
                                arguments
                            )

                            # ----------------------------------
                            # EXTRACT MCP RESULT
                            # ----------------------------------

                            tool_output = (
                                extract_mcp_result(
                                    result
                                )
                            )

                            # ----------------------------------
                            # CHECK MCP ERROR
                            # ----------------------------------

                            if result.is_error:

                                logger.error(
                                    "MCP tool returned error: "
                                    "%s",
                                    tool_name
                                )

                            else:

                                logger.info(
                                    "MCP tool completed: "
                                    "%s",
                                    tool_name
                                )

                            print(
                                f"MCP Result: "
                                f"{tool_output}"
                            )

                        except Exception as exc:

                            # ==================================
                            # MCP CLIENT / CONNECTION ERROR
                            # ==================================

                            print(
                                f"\nMCP Client Error: "
                                f"{exc}"
                            )

                            logger.exception(
                                "Exception while executing "
                                "MCP tool: %s",
                                tool_name
                            )

                            tool_output = {
                                "error": True,
                                "message": (
                                    f"Failed to execute "
                                    f"MCP tool '{tool_name}'."
                                )
                            }

                    # ==========================================
                    # SEND TOOL RESULT BACK TO OLLAMA
                    # ==========================================

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

                    logger.info(
                        "Tool result added to conversation: "
                        "%s",
                        tool_name
                    )

                # ------------------------------------------------
                # ASK OLLAMA AGAIN
                # ------------------------------------------------

                logger.info(
                    "Sending tool results back to Ollama"
                )

                response = chat(
                    model=MODEL,
                    messages=messages,
                    tools=ollama_tools
                )

            # =================================================
            # FINAL ASSISTANT RESPONSE
            # =================================================

            messages.append(
                response.message
            )

            print("\nAgent:")
            print(
                response.message.content
            )

            logger.info(
                "Agent response: %s",
                response.message.content
            )


# ============================================================
# PROGRAM ENTRY
# ============================================================

if __name__ == "__main__":

    try:

        anyio.run(main)

    except KeyboardInterrupt:

        print(
            "\n\nAgent stopped by user."
        )

        logger.info(
            "Agent stopped by user"
        )