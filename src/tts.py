import numpy as np
import pyaudio
from openai import AsyncOpenAI

from src.gui import WaveformVisualizer


async def play_audio(
    p: pyaudio.PyAudio, openai_client: AsyncOpenAI, response: str, visualizer: WaveformVisualizer | None = None
) -> None:
    """Plays the audio response from OpenAI and updates the waveform visualizer.

    Args:
        p (pyaudio.PyAudio): The PyAudio instance.
        openai_client (AsyncOpenAI): The OpenAI client.
        response (str): The response from OpenAI.
        visualizer (WaveformVisualizer | None): Optional waveform visualizer instance.
    """
    audio_stream = p.open(format=8, channels=1, rate=24_000, output=True)

    async with openai_client.audio.speech.with_streaming_response.create(
        model="tts-1", voice="echo", input=response, response_format="pcm"
    ) as response_audio:
        async for tts_chunk in response_audio.iter_bytes(1024):
            # Play audio
            audio_stream.write(tts_chunk)

            # Update visualizer if provided
            if visualizer is not None:
                # Convert the audio chunk to numpy array for visualization
                audio_data = np.frombuffer(tts_chunk, dtype=np.int16)
                visualizer.update_waveform(audio_data)

    # Close the audio stream
    audio_stream.stop_stream()
    audio_stream.close()
