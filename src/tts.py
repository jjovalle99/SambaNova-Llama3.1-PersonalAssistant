import pyaudio
from openai import AsyncOpenAI


async def play_audio(p: pyaudio.PyAudio, openai_client: AsyncOpenAI, response: str) -> None:
    """Plays the audio response from OpenAI.

    Args:
        p (pyaudio.PyAudio): The PyAudio instance.
        openai_client (AsyncOpenAI): The OpenAI client.
        response (str): The response from OpenAI.
    """
    audio_stream = p.open(format=8, channels=1, rate=24_000, output=True)
    async with openai_client.audio.speech.with_streaming_response.create(
        model="tts-1", voice="echo", input=response, response_format="pcm"
    ) as response_audio:
        async for tts_chunk in response_audio.iter_bytes(1024):
            audio_stream.write(tts_chunk)
