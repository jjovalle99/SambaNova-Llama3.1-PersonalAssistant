import os
from datetime import datetime
from time import perf_counter
from typing import Any
from uuid import uuid4

from loguru import logger
from openai import AsyncOpenAI
from termcolor import colored

from src.chat import ahandle_stream, extract_tool_input_args
from src.persistence import save_json_chat_history
from src.settings import Settings
from src.tools.gmail import GmailEmails, get_gmail_emails
from src.tools.google_calendar import CalendarAppointments, get_calendar_appointments
from src.utils import prepare_schemas

settings: Settings = Settings()
client = AsyncOpenAI(api_key=settings.samba_api_key, base_url=settings.samba_url)
schemas: str = prepare_schemas(models=[GmailEmails, CalendarAppointments])
tool_belt: dict[str, Any] = {
    "get_gmail_emails": get_gmail_emails,
    "get_calendar_appointments": get_calendar_appointments,
}


system_prompt: str = f"""Cutting Knowledge Date: December 2023
Today Date: {datetime.now().strftime('%Y-%m-%d')}

You are Jarvis, a personal assistant working for Juan Ovalle (he prefers JJ). His life depends on you. You will be always talking with him. You have tool calling capabilities. You have access to the following tools:

<tools>
{schemas}
</tools>

If a tool is needed to best answer the user prompt, please respond ONLY with a JSON for a function call with its
proper arguments like {{"name": function name, "parameters": dictionary of argument name and its value}}. This means that the response must contain exclusively the dictionary and nothing else. Finally, the JSON must be surounded by <tool>. 

Always think of your response step by step."""


async def main():
    # Initialize Conversation ID and Chat History
    conversation_id: str = str(uuid4())
    logger.info("Starting conversation with ID: {id}", id=conversation_id)
    chat_history: dict[str, Any] = {
        "conversation_id": conversation_id,
        "content": [],
    }

    # Define System Prompt
    messages: list[dict[str, str]] = [
        {
            "role": "system",
            "content": system_prompt,
        },
    ]

    os.system("clear")
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
        print(colored("Assistant > ", "blue"), end="", flush=True)
        response, metadata, tool_calls = await ahandle_stream(stream=stream)
        if tool_calls:
            logger.info("tool call: {r}", r=response.removeprefix("<tool>").removesuffix("</tool>"))

        # Add model response to messages
        messages.append({"role": "assistant", "content": response})

        # Handle stream (2) if tool calls
        if tool_calls:
            # Prepare tool arguments
            tool_args: dict[str, Any] = extract_tool_input_args(s=response)
            tool_name: str = tool_args.get("name")
            tool_input: dict[str, Any] = tool_args.get("parameters")

            # Invoke the tool
            tool_output: Any = await tool_belt.get(tool_name)(**tool_input)

            # Handles all the messages that need to be added to proper tool calling
            messages.append({"role": "tool", "content": str(tool_output)})

            # Update chat history with tool information
            chat_history["content"].append({"messages": messages.copy(), **metadata.model_dump()})
            save_json_chat_history(conversation_id=conversation_id, chat_history=chat_history)

            # Final completion with tool responses
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

            print(colored("Assistant > ", "blue"), end="", flush=True)
            response, metadata, _ = await ahandle_stream(stream=stream)

        print()

        # Update chat history with final completion
        chat_history["content"].append({"messages": messages.copy(), **metadata.model_dump()})
        save_json_chat_history(conversation_id=conversation_id, chat_history=chat_history)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
