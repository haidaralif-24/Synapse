from __future__ import annotations

import flet as ft

from ..config import set_api_key, set_provider

PROVIDER_OPTIONS = [
    ft.dropdown.Option("openai", "OpenAI"),
    ft.dropdown.Option("groq", "Groq"),
    ft.dropdown.Option("gemini", "Gemini (Google)"),
]


def KeySetupView(page: ft.Page) -> ft.View:
    provider_dd = ft.Dropdown(
        label="Provider",
        options=PROVIDER_OPTIONS,
        value="openai",
        width=400,
    )

    key_field = ft.TextField(
        label="API Key",
        password=True,
        can_reveal_password=True,
        width=400,
        hint_text="sk-...",
    )

    status_text = ft.Text("", color=ft.Colors.GREEN)

    def on_save_click(e):
        if not key_field.value.strip():
            status_text.value = "Please enter an API key."
            status_text.color = ft.Colors.RED
            page.update()
            return
        set_provider(provider_dd.value)
        set_api_key(key_field.value.strip())
        status_text.value = "Key saved. Redirecting..."
        status_text.color = ft.Colors.GREEN
        page.update()
        page.push_route("/topic")

    save_btn = ft.FilledButton("Save & Continue", on_click=on_save_click)

    return ft.View(
        controls=[
            ft.Column(
                [
                    ft.Text("Welcome to Distillery", size=28, weight=ft.FontWeight.BOLD),
                    ft.Text("Your API key is stored locally and never leaves your device.", size=14, italic=True),
                    ft.Divider(height=20),
                    provider_dd,
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
