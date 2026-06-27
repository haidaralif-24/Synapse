from __future__ import annotations

from typing import Callable

import flet as ft

from ..graph.state import ResearchState


def ReportView(page: ft.Page, state: ResearchState, on_back: Callable) -> ft.View:
    scroll_column = ft.Column(
        [ft.Markdown(state.final_report, extension_set=ft.MarkdownExtensionSet.GITHUB_FLAVORED)],
        scroll=ft.ScrollMode.ALWAYS,
        expand=True,
    )

    back_btn = ft.TextButton("← New Research", on_click=lambda e: on_back())

    return ft.View(
        controls=[
            ft.Column(
                [
                    ft.Row([back_btn], alignment=ft.MainAxisAlignment.START),
                    ft.Text("Research Findings", size=24, weight=ft.FontWeight.BOLD, color="#01b0e5"),
                    ft.Divider(),
                    scroll_column,
                ],
                expand=True,
            )
        ],
        route="/report",
    )
