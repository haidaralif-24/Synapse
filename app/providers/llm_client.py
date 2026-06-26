from __future__ import annotations

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
