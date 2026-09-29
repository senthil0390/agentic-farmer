import json

from ollama import chat

from llm_tools import TOOLS
from tool_registry import execute_tool


MODEL_NAME = "qwen3:0.6b"


def run_agent(user_query: str):

    messages = [
        {
            "role": "system",
            "content": """
You are a helpful agriculture assistant.

You have access to tools for:

1. Weather information
2. Crop advisory
3. Market prices

Use the appropriate tools when the user's
question requires this information.

Do not invent weather, crop advisory,
or market price data.
"""
        },
        {
            "role": "user",
            "content": user_query
        }
    ]

    # ----------------------------------
    # First LLM call
    # ----------------------------------

    response = chat(
        model=MODEL_NAME,
        messages=messages,
        tools=TOOLS
    )

    assistant_message = response["message"]

    # ----------------------------------
    # No tool required
    # ----------------------------------

    if not assistant_message.get("tool_calls"):

        return assistant_message["content"]

    # ----------------------------------
    # Add LLM response to conversation
    # ----------------------------------

    messages.append(assistant_message)

    # ----------------------------------
    # Execute requested tools
    # ----------------------------------

    for tool_call in assistant_message["tool_calls"]:

        tool_name = tool_call["function"]["name"]

        arguments = tool_call["function"]["arguments"]

        print("\n==============================")
        print("LLM selected tool:", tool_name)
        print("Arguments:", arguments)
        print("==============================")

        # Generic tool execution
        tool_result = execute_tool(
            tool_name,
            arguments
        )

        print("Tool result:")
        print(tool_result)

        # ----------------------------------
        # Send tool result back to LLM
        # ----------------------------------

        messages.append(
            {
                "role": "tool",
                "name": tool_name,
                "content": json.dumps(tool_result)
            }
        )

    # ----------------------------------
    # Second LLM call
    # ----------------------------------

    final_response = chat(
        model=MODEL_NAME,
        messages=messages
    )

    return final_response["message"]["content"]


if __name__ == "__main__":

    query = input("\nUser: ")

    answer = run_agent(query)

    print("\nAssistant:")
    print(answer)