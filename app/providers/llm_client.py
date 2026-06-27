from __future__ import annotations

import json
import re
from typing import Optional

from openai import APIError, AuthenticationError, OpenAI, RateLimitError

PROVIDER_CONFIGS = {
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "default_model": "gpt-4o",
    },
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "default_model": "llama-3.3-70b-versatile",
    },
    "gemini": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "default_model": "gemini-2.0-flash",
    },
}


class LLMClient:
    def __init__(self, provider: str, api_key: str, model: Optional[str] = None):
        self.provider = provider
        self.api_key = api_key
        cfg = PROVIDER_CONFIGS.get(provider, PROVIDER_CONFIGS["openai"])
        self.base_url = cfg["base_url"]
        self.model = model or cfg["default_model"]
        self._client = OpenAI(api_key=api_key, base_url=self.base_url)

    def invoke(self, system: str, user: str, temperature: float = 0.0,
               response_format: Optional[dict] = None) -> str:
        kwargs = dict(
            model=self.model,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        if response_format:
            kwargs["response_format"] = response_format
        resp = self._client.chat.completions.create(**kwargs)
        return resp.choices[0].message.content or ""

    @staticmethod
    def extract_json(text: str) -> str:
        """Strip markdown fences and return the first JSON object/array found."""
        stripped = text.strip()
        fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", stripped)
        if fence_match:
            stripped = fence_match.group(1).strip()
        # validate that it's parseable
        json.loads(stripped)
        return stripped

    def check_connection(self) -> tuple[bool, str]:
        """Test the API connection with a minimal call. Returns (ok, message)."""
        try:
            self._client.chat.completions.create(
                model=self.model,
                temperature=0,
                max_tokens=1,
                messages=[{"role": "user", "content": "ok"}],
            )
            return True, "Connection successful."
        except AuthenticationError:
            return False, "Invalid API key. Please check your key."
        except RateLimitError:
            return False, "Rate limited or quota exhausted. Check your billing / usage limits."
        except APIError as e:
            status = getattr(e, "status_code", 0)
            if status == 429:
                return False, "Quota exceeded or rate limited. Try again later or check your plan."
            if status == 402:
                return False, "Insufficient quota / billing issue. Check your API provider's billing page."
            return False, f"API error (status {status}): {e}"
        except Exception as e:
            return False, f"Connection failed: {e}"
