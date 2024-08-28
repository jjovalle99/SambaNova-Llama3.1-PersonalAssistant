from openai import AsyncOpenAI


class SambaAsync(AsyncOpenAI):
    @property
    def auth_headers(self) -> dict[str, str]:
        api_key = self.api_key
        return {"Authorization": f"Basic {api_key}"}
