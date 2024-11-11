import os
from datetime import datetime
from time import perf_counter
from typing import Any
from uuid import uuid4

import pyaudio
from loguru import logger
from openai import AsyncOpenAI
from termcolor import colored

from src.chat import ahandle_stream, extract_tool_input_args
from src.persistence import save_json_chat_history
from src.settings import Settings
from src.stt import capture_voice_input
from src.tools.google_tools.base import GoogleTool
from src.tools.google_tools.credentials import GoogleCredsConfig, GoogleCredsManager
from src.tools.google_tools.executors import CalendarInsertExecutor, CalendarReadExecutor, GmailReadExecutor, GmailWriteExecutor
from src.tools.news import NewspaperFrontTool
from src.tools.utils import prepare_schemas
from src.tools.weather import WeatherTool
from src.tts import play_audio

settings: Settings = Settings()
p = pyaudio.PyAudio()
openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
samba_client = AsyncOpenAI(api_key=settings.samba_api_key, base_url=settings.samba_url)
creds_manager = GoogleCredsManager(creds_config=GoogleCredsConfig(client_secrets_path=settings.credentials_path))
google_tools: dict[str, Any] = {
    "read_gmail_emails": GmailReadExecutor,
    "send_gmail_email": GmailWriteExecutor,
    "insert_calendar_appointment": CalendarInsertExecutor,
    "get_calendar_appointments": CalendarReadExecutor,
}
other_tools: dict[str, Any] = {
    "get_weather_data": WeatherTool,
    "get_news_data": NewspaperFrontTool,
}

schemas: str = prepare_schemas(models=[*google_tools.values(), *other_tools.values()])

system_prompt: str = f"""Cutting Knowledge Date: December 2023
Today Date: {datetime.now().strftime('%Y-%m-%d')}

You are Jarvis, a personal assistant working for Juan Ovalle. His life depends on you. You will be always talking with him. You have function calling capabilities.
You have access to the following functions:

{schemas}

You MUST respond in ONE of these two formats:

1. If you need to call a function, respond ONLY with:
<tool>{{"name": function name, "parameters": dictionary of argument name and its value}}</tool>

2. If no function call is needed, respond with a normal conversational message.

Important Rules:
- Choose only ONE response format - either a function call OR a text message
- Function calls MUST follow the specified format, start with <tool> and end with </tool>
- Required parameters MUST be specified
- Only call one function at a time
- Put the entire function call reply on one line
- If there is no function call available, answer the question like normal with your current knowledge and do not tell the user about function calls
- Only respond with a function call if you have all the required information to call the function, follow up questions must not be accompanied by a function call
"""


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
        prompt = await capture_voice_input(client=openai_client, p=p)

        if not prompt:
            continue
        print(f"You > {prompt}", end="", flush=True)

        if prompt.lower().strip() in ("exit"):
            break

        # Add user input to messages
        messages.append({"role": "user", "content": prompt})

        # Generate stream
        logger.info("Generating response...")
        _now: float = perf_counter()
        stream = await samba_client.chat.completions.create(
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

        # TTS (1)
        if not tool_calls:
            await play_audio(p=p, openai_client=openai_client, response=response)

        # Add model response to messages
        messages.append({"role": "assistant", "content": response})

        # Handle stream (2) if tool calls
        if tool_calls:
            # Prepare tool arguments
            tool_args: dict[str, Any] = extract_tool_input_args(s=response)
            tool_name: str = tool_args.get("name")
            tool_input: dict[str, Any] = tool_args.get("parameters")

            # Invoke the tool
            if tool_name in google_tools:
                tool_output: Any = await GoogleTool(
                    creds_manager=creds_manager, executor=google_tools.get(tool_name)(**tool_input)
                ).run()
            else:
                tool_output: Any = await other_tools.get(tool_name)(**tool_input).run()
            logger.info("Tool output: {o}", o=tool_output)

            # Handles all the messages that need to be added to proper tool calling
            messages.append({"role": "ipython", "content": str(tool_output)})

            # Update chat history with tool information
            chat_history["content"].append({"messages": messages.copy(), **metadata.model_dump()})
            save_json_chat_history(conversation_id=conversation_id, chat_history=chat_history)

            # Final completion with tool responses
            logger.info("Generating response...")
            _now: float = perf_counter()
            stream = await samba_client.chat.completions.create(
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

            # Audio (2)
            await play_audio(p=p, openai_client=openai_client, response=response)

        print()

        # Update chat history with final completion
        chat_history["content"].append({"messages": messages.copy(), **metadata.model_dump()})
        save_json_chat_history(conversation_id=conversation_id, chat_history=chat_history)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
