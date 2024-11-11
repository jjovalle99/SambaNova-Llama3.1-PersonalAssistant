import httpx
from pydantic import ConfigDict, Field

from src.settings import Settings
from src.tools.base import AsyncTool

settings = Settings()


class WeatherTool(AsyncTool):
    """Get current weather data for specified city."""

    model_config = ConfigDict(json_schema_extra={"name": "get_weather_data"})
    city: str = Field(description="City to get weather data for", examples="London")

    async def run(self) -> str:
        """
        Get current weather data for specified city using weatherstack API.

        Returns:
            str: Weather data for specified city

        Raises:
            HTTPError: If API request fails
        """
        url = "http://api.weatherstack.com/current"
        params = {"access_key": settings.weatherstack_api_key, "query": self.city}

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            observation_time = data.get("current").get("observation_time")
            temperature = data.get("current").get("temperature")
            weather_descriptions = data.get("current").get("weather_descriptions")

            return f"At {observation_time}, the temperature in {self.city} is {temperature}°C. The weather is {weather_descriptions[0].lower()}"
