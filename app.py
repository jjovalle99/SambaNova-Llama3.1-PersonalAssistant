from time import perf_counter
from typing import Any
from uuid import uuid4

from loguru import logger
from termcolor import colored

from src.chat import ahandle_stream
from src.client import SambaAsync
from src.persistence import save_json_chat_history
from src.settings import Settings

settings: Settings = Settings()
client: SambaAsync = SambaAsync(base_url=settings.samba_url, api_key=settings.samba_api_key)


async def main():
    # Initialize Conversation ID and Chat History
    conversation_id: str = str(uuid4())
    chat_history: dict[str, Any] = {
        "conversation_id": conversation_id,
        "content": [],
    }

    # Define System Prompt
    system_prompt: str = "You are a helpful assistant."
    messages: list[dict[str, str]] = [
        {
            "role": "system",
            "content": system_prompt,
        },
    ]

    while True:
        prompt = input("You > ")
        if prompt in ("exit"):
            break

        # Add user input to messages
        messages.append({"role": "user", "content": prompt})

        # Generate stream
        logger.info("Generating response...")
        _now: float = perf_counter()
        stream = await client.chat.completions.create(
            messages=messages,
            model="llama3-405b",
            temperature=0.0,
            stop=["<|eot_id|>"],
            stream=True,
            stream_options={"include_usage": True},
        )
        logger.info("Generation time: {s:.3f} seconds", s=perf_counter() - _now)

        # Handle stream (1)
        # tool_calls = defaultdict(ToolCall)
        print(colored("Assistant > ", "blue"), end="", flush=True)
        response, metadata = await ahandle_stream(stream=stream)

        # Handle stream (2) if tool calls
        # if tool_calls:
        #     # Concatenate the pieces of the function arguments
        #     concatenate_arguments_of_tools(tool_calls=tool_calls)

        #     # Handles all the messages that need to be added to proper tool calling
        #     handle_tool_messages(messages=messages, tool_calls=tool_calls, tool_belt=TOOL_BELT)

        #     # Update chat history with tool information
        #     chat_history["content"].append({"messages": messages.copy(), **metadata.model_dump()})
        #     save_json_chat_history(conversation_id=conversation_id, chat_history=chat_history)

        #     # Final completion with tool responses
        #     completion = await CLIENT.chat.completions.create(
        #         messages=messages,
        #         model="gpt-4o",
        #         temperature=0.0,
        #         stream=True,
        #         stream_options={"include_usage": True},
        #     )

        #     response, metadata = await ahandle_stream(completion=completion)

        print()

        # Add model response to messages
        messages.append({"role": "assistant", "content": response})

        # Update chat history with final completion
        chat_history["content"].append({"messages": messages.copy(), **metadata.model_dump()})
        logger.info("Saving chat state...")
        _now: float = perf_counter()
        save_json_chat_history(conversation_id=conversation_id, chat_history=chat_history)
        logger.info("Chat state saved in {s:.3f} seconds", s=perf_counter() - _now)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
