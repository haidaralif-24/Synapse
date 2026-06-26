from __future__ import annotations

from typing import Callable, Optional

import flet as ft

from ..config import default_model_for, get_model, get_provider, set_api_key, set_model, set_provider

PROVIDER_OPTIONS = [
    ft.dropdown.Option("openai", "OpenAI"),
    ft.dropdown.Option("groq", "Groq"),
    ft.dropdown.Option("gemini", "Gemini (Google)"),
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

    key_field = ft.TextField(
        label="API Key",
        password=True,
        can_reveal_password=True,
        width=400,
        hint_text="Leave blank to keep current key" if settings_mode else "sk-...",
    )

    model_field = ft.TextField(
        label="Model",
        width=400,
        hint_text="e.g. gpt-4o, gemini-2.0-flash, ...",
        value=existing_model,
    )

    status_text = ft.Text("", color=ft.Colors.GREEN)

    def on_provider_change(e):
        model_field.value = default_model_for(provider_dd.value)
        page.update()

    provider_dd.on_change = on_provider_change

    def on_save_click(e):
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
        set_provider(provider_dd.value)
        if key:
            set_api_key(key)
        set_model(model_field.value.strip())
        status_text.value = "Saved. Redirecting..."
        status_text.color = ft.Colors.GREEN
        page.update()
        on_saved()

    save_btn = ft.FilledButton("Save & Continue", on_click=on_save_click)

    return ft.View(
        controls=[
            ft.Column(
                [
                    ft.Text("Settings" if settings_mode else "Welcome to Fetchy", size=28, weight=ft.FontWeight.BOLD),
                    ft.Text("Your API key is stored locally and never leaves your device.", size=14, italic=True),
                    ft.Divider(height=20),
                    provider_dd,
                    model_field,
                    key_field,
                    ft.Container(content=save_btn, margin=ft.Margin(0, 12, 0, 0)),
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
