from __future__ import annotations

import flet as ft

STAGES = [
    "Planning",
    "Search",
    "Summarization",
    "Fact-check",
    "Correction",
    "Writing",
]


def ProgressView(page: ft.Page) -> ft.View:
    stage_indicators = []
    for s in STAGES:
        stage_indicators.append(
            ft.ListTile(
                leading=ft.Icon(ft.Icons.CIRCLE_OUTLINED),
                title=ft.Text(s),
            )
        )

    status_label = ft.Text("Starting pipeline...", size=14, italic=True)

    return ft.View(
        controls=[
            ft.Column(
                [
                    ft.Text("Research in Progress", size=24, weight=ft.FontWeight.BOLD),
                    ft.Divider(height=16),
                    ft.Column(stage_indicators, spacing=4),
                    ft.Divider(height=12),
                    status_label,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        ],
        route="/progress",
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )
