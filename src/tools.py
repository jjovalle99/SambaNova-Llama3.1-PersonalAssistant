from typing import Any

import httpx
from pydantic import BaseModel, ConfigDict

from src.settings import Settings

settings: Settings = Settings()


class TopHeadlines(BaseModel):
    """Retrieve the 10 most recent headlines from Colombia. It can be used to quickly access current news information without requiring any input parameters."""

    model_config = ConfigDict(json_schema_extra={"name": "get_top_headlines", "required": []})


async def get_top_headlines() -> list[dict[str, Any]]:
    """
    Asynchronously fetch top headlines from News API.


    Returns:
        List[Dict[str, Any]]: A list of dictionaries, each containing an article's information.

    """
    url: str = "https://newsapi.org/v2/top-headlines"
    params: dict[str, str] = {"country": "co", "apiKey": settings.news_api}

    async with httpx.AsyncClient() as client:
        response: httpx.Response = await client.get(url, params=params)
        articles: list[dict[str, str]] = response.json().get("articles", {})[:10]

    formatted_headlines = [f"[{i+1}] {article.get('title')} ({article.get('author')})" for i, article in enumerate(articles)]

    return "\n ---- \n".join(formatted_headlines)
