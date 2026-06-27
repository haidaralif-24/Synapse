from __future__ import annotations

import threading
from typing import Callable

import flet as ft

from ..config import default_model_for, get_api_key, get_model, get_provider, set_api_key, set_model, set_provider
from ..providers.llm_client import LLMClient

PROVIDER_OPTIONS = [
    ft.dropdown.Option("openai", "OpenAI"),
    ft.dropdown.Option("groq", "Groq"),
    ft.dropdown.Option("gemini", "Gemini (Google)"),
    ft.dropdown.Option("openrouter", "OpenRouter"),
]


def KeySetupView(page: ft.Page, on_saved: Callable, settings_mode: bool = False) -> ft.View:
    existing_provider = get_provider() if settings_mode else "openai"
    existing_model = get_model() or default_model_for(existing_provider)

    provider_dd = ft.Dropdown(
        label="Provider",
        options=PROVIDER_OPTIONS,
        value=existing_provider,
        width=400,
    )

    def key_hint(provider: str) -> str:
        hints = {"openai": "sk-...", "groq": "gsk_...", "gemini": "AIza...", "openrouter": "sk-or-v1-..."}
        return hints.get(provider, "API key")
    key_field = ft.TextField(
        label="API Key",
        password=True,
        can_reveal_password=True,
        width=400,
        value=get_api_key(existing_provider) if settings_mode else "",
        hint_text="Leave blank to keep current key" if settings_mode else key_hint(existing_provider),
    )

    model_field = ft.TextField(
        label="Model",
        width=400,
        hint_text="e.g. gpt-4o, gemini-2.0-flash, ...",
        value=existing_model,
    )

    status_text = ft.Text("", color=ft.Colors.GREEN)

    def on_provider_change(e):
        provider = provider_dd.value
        model_field.value = default_model_for(provider)
        if settings_mode:
            key_field.value = get_api_key(provider)
        key_field.hint_text = key_hint(provider)
        page.update()

    provider_dd.on_change = on_provider_change

    def on_save_click(e):
        provider = provider_dd.value
        key = key_field.value.strip()
        if not key and not settings_mode:
            status_text.value = "Please enter an API key."
            status_text.color = ft.Colors.RED
            page.update()
            return
        if not model_field.value.strip():
            status_text.value = "Please enter a model name."
            status_text.color = ft.Colors.RED
            page.update()
            return
        set_provider(provider)
        if key:
            set_api_key(provider, key)
        set_model(model_field.value.strip())
        status_text.value = "Saved. Redirecting..."
        status_text.color = ft.Colors.GREEN
        page.update()
        on_saved()

    def on_test_click(e):
        provider = provider_dd.value
        key = key_field.value.strip() or get_api_key(provider)
        if not key:
            status_text.value = "Enter an API key first."
            status_text.color = ft.Colors.RED
            page.update()
            return
        status_text.value = "Testing connection..."
        status_text.color = ft.Colors.GREY_700
        page.update()

        def test():
            llm = LLMClient(
                provider=provider_dd.value,
                api_key=key,
                model=model_field.value.strip() or None,
            )
            ok, msg = llm.check_connection()
            status_text.value = msg
            status_text.color = ft.Colors.GREEN if ok else ft.Colors.RED
            page.update()

        threading.Thread(target=test, daemon=True).start()

    save_btn = ft.FilledButton("Save & Continue", on_click=on_save_click)
    test_btn = ft.OutlinedButton("Test Connection", on_click=on_test_click)

    return ft.View(
        controls=[
            ft.Column(
                [
                    ft.Text("Settings" if settings_mode else "Welcome to Synapse", size=28, weight=ft.FontWeight.BOLD),
                    ft.Text("Your API key is stored locally and never leaves your device.", size=14, italic=True),
                    ft.Divider(height=20),
                    provider_dd,
                    model_field,
                    key_field,
                    ft.Row(
                        [save_btn, test_btn],
                        spacing=12,
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    status_text,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        ],
        route="/setup",
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )
