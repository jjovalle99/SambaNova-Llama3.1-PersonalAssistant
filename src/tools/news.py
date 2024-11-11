import base64
from datetime import datetime
from time import perf_counter
from typing import Literal

import httpx
from loguru import logger
from openai import AsyncOpenAI
from pydantic import ConfigDict, Field

from src.settings import Settings
from src.tools.base import AsyncTool

settings = Settings()


async def url_to_base64(image_url: str) -> str:
    """Convert image URL to base64 string.

    Args:
        image_url: URL of the image to convert

    Returns:
        Base64 encoded image with data URI prefix

    Raises:
        httpx.HTTPError: If image download fails
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(image_url)
        response.raise_for_status()

        image_binary = response.content
        base64_image = base64.b64encode(image_binary).decode("utf-8")
        return f"data:image/jpeg;base64,{base64_image}"


class NewspaperFrontTool(AsyncTool):
    """Tool to retrieve and analyze newspaper front pages from different countries."""

    model_config = ConfigDict(json_schema_extra={"name": "get_news_data"})
    city: Literal["gb", "co"] = Field(description="ISO 3166 country code")
    source: Literal["the-guardian", "el-espectador"] = Field(description="News source identifier")

    async def run(self) -> str:
        """
        Retrieve and analyze newspaper front page from specified country and source.

        Returns:
            str: Analyzed newspaper front page
        """

        url = "https://api.worldnewsapi.com/retrieve-front-page"
        params = {
            "api-key": settings.worlds_news_api_key,
            "source-country": self.city,
            "source-name": self.source,
            "date": datetime.now().strftime("%Y-%m-%d"),
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

        front_page_image_url = data.get("front_page", {}).get("image")
        samba_client = AsyncOpenAI(api_key=settings.samba_api_key, base_url=settings.samba_url)

        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Analyze the provided newspaper ({self.source.replace('-', ' ').capitalize()}) front page as a concise news expert. Summarize the main headline and key stories visible.",
                    },
                    {"type": "image_url", "image_url": {"url": await url_to_base64(front_page_image_url)}},
                ],
            },
        ]

        logger.info("Using multimodal model to analyze {url}", url=front_page_image_url)
        _now: float = perf_counter()
        completion = await samba_client.chat.completions.create(
            messages=messages,
            model="Llama-3.2-90B-Vision-Instruct",
            temperature=0.0,
        )
        logger.info("Multimodal generation time: {s:.3f} seconds", s=perf_counter() - _now)

        return completion.choices[0].message.content
