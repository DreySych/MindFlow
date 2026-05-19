import os
import requests


class OpenRouterClient:
    """Адаптер для работы с внешним API OpenRouter."""

    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY", "")
        self.url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free"

    def ask(self, prompt):
        if not self.api_key:
            return None, "API-ключ OpenRouter не найден"

        response = requests.post(
            self.url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            },
            timeout=30,
        )

        if response.status_code != 200:
            return None, "Ошибка ответа OpenRouter"

        data = response.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content")

        if not content:
            return None, "OpenRouter не вернул ответ"

        return content.strip(), None