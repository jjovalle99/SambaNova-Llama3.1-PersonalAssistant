import json
import threading
from threading import Event
from typing import Any

import pygame
from openai import AsyncStream
from termcolor import colored

from src.pydantic_classes import Metadata


def extract_tool_input_args(s: str) -> dict[str, Any]:
    """Extracts the tool input arguments from model response.

    Args:
        s (str): The input string containing the content.

    Returns:
        dict: tool input arguments.
    """
    data = json.loads(s.removeprefix("<tool>").removesuffix("</tool>"))

    def parse_possible_json_strings(obj):
        if isinstance(obj, dict):
            return {k: parse_possible_json_strings(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [parse_possible_json_strings(v) for v in obj]
        elif isinstance(obj, str):
            try:
                return json.loads(obj)
            except json.JSONDecodeError:
                return obj
        else:
            return obj

    return parse_possible_json_strings(data)


def play_mp3_loop(file_path: str, stop_event: Event) -> None:
    """
    Play an MP3 file in a loop until the stop_event is set.

    Args:
        file_path (str): The path to the MP3 file to be played.
        stop_event (Event): A threading event used to stop the playback loop.
    """
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.set_volume(0.05)

    while not stop_event.is_set():
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy() and not stop_event.is_set():
            pygame.time.Clock().tick(10)


async def ahandle_stream(stream: AsyncStream, verbose: bool = True) -> tuple[str, Metadata, bool]:
    response: list[str] = []
    tool_calls: bool = False
    stop_audio = threading.Event()
    audio_thread = None

    async for chunk in stream:
        if not chunk.choices:
            # When the chunk contain empty choices -> the chunk produced by stream_options={"include_usage": True}. This is the last chunk.
            if audio_thread and audio_thread.is_alive():
                # Stop the audio if it's playing
                stop_audio.set()
                audio_thread.join()

            metadata: Metadata = Metadata(
                **chunk.model_dump(),
                finish_reason=finish_reason,  # noqa: F821
            )

        elif token := chunk.choices[0].delta.content:
            # When the delta content has payload. This is when the model dont use a tool.
            response.append(token)

            if "<tool>" in token:
                tool_calls = True
                print(colored("Thinking ...", "yellow"), end="", flush=True)
                # Start playing audio in a separate thread
                stop_audio.clear()
                audio_thread = threading.Thread(target=play_mp3_loop, args=("assets/beeps.mp3", stop_audio))
                audio_thread.start()

            elif verbose and not tool_calls:
                # When the stream message stops. This is the n-1 chunk.
                print(colored(token, "blue"), end="", flush=True)

        else:
            # Stop the audio if it's playing
            if audio_thread and audio_thread.is_alive():
                stop_audio.set()
                audio_thread.join()

            finish_reason = chunk.choices[0].finish_reason  # noqa: F841

    # Ensure audio is stopped if the function exits
    if audio_thread and audio_thread.is_alive():
        stop_audio.set()
        audio_thread.join()

    return "".join(response), metadata, tool_calls
