from __future__ import annotations

from typing import Tuple

import flet as ft

STAGES = [
    "Planning",
    "Searching the web",
    "Summarizing findings",
    "Fact-checking claims",
    "Correcting errors",
    "Writing report",
]


def ProgressView(page: ft.Page, status_text: ft.Text) -> Tuple[ft.View, list, list]:
    icons: list[ft.Icon] = []
    labels: list[ft.Text] = []
    stage_rows: list[ft.Row] = []

    for s in STAGES:
        icon = ft.Icon(ft.Icons.CIRCLE_OUTLINED, color=ft.Colors.GREY_400, size=20)
        label = ft.Text(s, size=16)
        icons.append(icon)
        labels.append(label)
        stage_rows.append(ft.Row([icon, label], spacing=12))

    view = ft.View(
        controls=[
            ft.Column(
                [
                    ft.Text("Research in Progress", size=24, weight=ft.FontWeight.BOLD, color="#01b0e5"),
                    ft.Divider(height=16),
                    ft.Column(stage_rows, spacing=8, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.Divider(height=12),
                    status_text,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        ],
        route="/progress",
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    return view, icons, labels
