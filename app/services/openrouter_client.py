import httpx

from app.core.config import settings
from app.core.errors import ExternalServiceError


class OpenRouterClient:
    async def chat_completion(
        self,
        messages: list[dict[str, str]],
        temperature: float,
    ) -> str:
        url = f"{settings.openrouter_base_url}/chat/completions"

        headers = {
            "Authorization": f"Bearer {settings.openrouter_api_key}",
            "HTTP-Referer": settings.openrouter_site_url,
            "X-Title": settings.openrouter_app_name,
            "Content-Type": "application/json",
        }

        payload = {
            "model": settings.openrouter_model,
            "messages": messages,
            "temperature": temperature,
        }

        try:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(
                    url,
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code
            response_text = exc.response.text
            raise ExternalServiceError(
                f"OpenRouter request failed: {status_code} {response_text}",
            ) from exc
        except httpx.HTTPError as exc:
            raise ExternalServiceError("OpenRouter connection failed") from exc

        data = response.json()

        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as exc:
            raise ExternalServiceError("Invalid OpenRouter response") from exc
