from __future__ import annotations

from typing import Optional

from openai import OpenAI

PROVIDER_CONFIGS = {
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "default_fast": "gpt-4o-mini",
        "default_strong": "gpt-4o",
    },
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "default_fast": "llama-3.3-70b-versatile",
        "default_strong": "llama-3.3-70b-versatile",
    },
    "gemini": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "default_fast": "gemini-2.0-flash",
        "default_strong": "gemini-2.0-flash",
    },
}


class LLMClient:
    def __init__(self, provider: str, api_key: str, model: Optional[str] = None):
        self.provider = provider
        self.api_key = api_key
        cfg = PROVIDER_CONFIGS.get(provider, PROVIDER_CONFIGS["openai"])
        self.base_url = cfg["base_url"]
        self.model = model or cfg["default_strong"]
        self._client = OpenAI(api_key=api_key, base_url=self.base_url)

    def invoke(self, system: str, user: str, temperature: float = 0.0) -> str:
        resp = self._client.chat.completions.create(
            model=self.model,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        return resp.choices[0].message.content or ""
