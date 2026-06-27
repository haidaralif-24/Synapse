from __future__ import annotations

from typing import Callable

import flet as ft


def TopicView(page: ft.Page, on_submit: Callable[[str], None], on_settings: Callable | None = None) -> ft.View:
    topic_field = ft.TextField(
        label="Research Topic",
        hint_text="e.g. The impact of quantum computing on cryptography",
        width=500,
        multiline=False,
        autofocus=True,
    )

    error_text = ft.Text("", color=ft.Colors.RED)

    def on_run_click(e):
        topic = topic_field.value.strip()
        if not topic:
            error_text.value = "Please enter a topic."
            page.update()
            return
        on_submit(topic)

    run_btn = ft.FilledButton("Run Research", on_click=on_run_click, style=ft.ButtonStyle(color=ft.Colors.WHITE))

    settings_btn = ft.IconButton(ft.Icons.SETTINGS, on_click=lambda e: on_settings() if on_settings else None, tooltip="Settings")

    return ft.View(
        controls=[
            ft.Column(
                [
                    ft.Row([ft.Text("Synapse", size=28, weight=ft.FontWeight.BOLD, color="#01b0e5"), settings_btn], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Text("Multi-Agent Research Assistant", size=14, color=ft.Colors.with_opacity(0.7, "#01b0e5")),
                    ft.Divider(height=20),
                    topic_field,
                    ft.Container(content=run_btn, margin=ft.Margin(0, 12, 0, 0)),
                    error_text,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        ],
        route="/topic",
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )
