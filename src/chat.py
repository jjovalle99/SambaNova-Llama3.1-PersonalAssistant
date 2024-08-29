import json
from openai import AsyncStream
from termcolor import colored

from src.pydantic_classes import Metadata


async def ahandle_stream(
    stream: AsyncStream, verbose: bool = True
) -> tuple[str, Metadata]:
    """
    Handles the streaming of the OpenAI asynchronous chat stream. It also supports processing tool calls within the stream.

    Args:
        stream (AsyncStream): Asynchronous OpenAI chat stream.
        verbose (bool): Flag to control if the streamed response will be displayed in console.

    Returns:
        tuple[str, Metadata]: Returns the concatenated response and the metadata.
    """

    response: list = []

    async for chunk in stream:
        if not chunk.choices:
            # When the chunk contain empty choices -> the chunk produced by `stream_options={"include_usage": True}`. This is the last chunk.
            metadata = Metadata(
                **chunk.model_dump(), finish_reason=finish_reason  # noqa: F821
            ) 
        
        elif token := chunk.choices[0].delta.content:
            # When the delta content has payload. This is when the model dont use a tool.
            response.append(token)
            if verbose:
                print(
                    colored(token, "blue"), flush=True, end=""
                )

        else:
            # When the stream message stops. This is the n-1 chunk.
            finish_reason = chunk.choices[0].finish_reason  # noqa: F841

    return  json.loads("".join(response)), metadata
