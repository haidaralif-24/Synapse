from __future__ import annotations

import threading
import time

import flet as ft

from app.config import get_api_key, get_model, get_provider
from app.graph.build_graph import build_pipeline
from app.graph.state import ResearchState
from app.providers.llm_client import LLMClient
from app.providers.search.duckduckgo import DuckDuckGoProvider
from app.ui.key_setup_view import KeySetupView
from app.ui.progress_view import STAGES, ProgressView
from app.ui.report_view import ReportView
from app.ui.topic_view import TopicView
from app.utils.logging import setup_logger

logger = setup_logger(__name__)

STAGE_MAP = {
    "planner": 0,
    "search": 1,
    "summarizer": 2,
    "fact_checker": 3,
    "correction": 4,
    "writer": 5,
}


NAVY = "#03122f"
CYAN = "#01b0e5"
MID_BLUE = "#0435ad"


def main(page: ft.Page):
    page.title = "Synapse — Research Assistant"
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=ft.Colors.with_opacity(1, CYAN),
            on_primary=ft.Colors.WHITE,
            primary_container=ft.Colors.with_opacity(1, MID_BLUE),
            surface=ft.Colors.with_opacity(1, NAVY),
            on_surface=ft.Colors.WHITE,
            surface_bright=ft.Colors.with_opacity(1, "#0a1a3a"),
            on_surface_variant=ft.Colors.with_opacity(0.7, CYAN),
            outline=ft.Colors.with_opacity(0.3, CYAN),
        ),
        use_material3=True,
    )
    page.padding = 24
    page.window.width = 900
    page.window.height = 700
    page.scroll = ft.ScrollMode.AUTO

    final_state = ResearchState(topic="")
    pipeline_thread: threading.Thread | None = None

    stage_icons: list[ft.Icon] = []
    stage_labels: list[ft.Text] = []
    status_text = ft.Text("", size=14, italic=True, text_align=ft.TextAlign.CENTER)

    def navigate(view):
        page.views.clear()
        page.views.append(view)
        page.update()

    def show_setup():
        navigate(KeySetupView(page, on_saved=go_topic))

    def go_settings():
        navigate(KeySetupView(page, on_saved=go_topic, settings_mode=True))

    def go_topic():
        navigate(TopicView(page, start_research, on_settings=go_settings))

    def go_progress():
        progress_view, icons, labels = ProgressView(page, status_text)
        stage_icons.clear()
        stage_icons.extend(icons)
        stage_labels.clear()
        stage_labels.extend(labels)
        navigate(progress_view)

    def go_report():
        navigate(ReportView(page, final_state, go_topic))

    def start_research(topic: str):
        nonlocal pipeline_thread
        final_state.topic = topic
        go_progress()
        pipeline_thread = threading.Thread(target=run_pipeline, daemon=True)
        pipeline_thread.start()

    def update_stage(stage_name: str, stage_index: int):
        if stage_index < 0:
            status_text.value = stage_name
            page.update()
            return
        for i, icon in enumerate(stage_icons):
            if i < stage_index:
                icon.name = ft.Icons.CHECK_CIRCLE
                icon.color = CYAN
            elif i == stage_index:
                icon.name = ft.Icons.PLAY_CIRCLE
                icon.color = CYAN
            else:
                icon.name = ft.Icons.CIRCLE_OUTLINED
                icon.color = ft.Colors.GREY_400
        for i, label in enumerate(stage_labels):
            label.weight = ft.FontWeight.BOLD if i == stage_index else ft.FontWeight.NORMAL
        status_text.value = f"Current stage: {stage_name}"
        page.update()

    def run_pipeline():
        nonlocal final_state
        try:
            provider_name = get_provider()
            api_key = get_api_key(provider_name)
            if not api_key:
                raise ValueError("No API key configured. Please go back to setup.")

            model_name = get_model()
            llm = LLMClient(provider=provider_name, api_key=api_key, model=model_name or None)

            ok, msg = llm.check_connection()
            if not ok:
                raise ConnectionError(msg)

            search = DuckDuckGoProvider()
            graph = build_pipeline(llm, search)

            tracked = {
                "topic": final_state.topic,
                "sub_questions": [],
                "outline": "",
                "search_results": [],
                "summaries": "",
                "fact_check_verdicts": [],
                "correction_log": [],
                "final_report": "",
                "current_stage": "",
            }

            for event in graph.stream(final_state, stream_mode="updates"):
                if isinstance(event, dict):
                    for node_name, updates in event.items():
                        if isinstance(updates, dict):
                            tracked.update(updates)
                            stage_index = STAGE_MAP.get(node_name, -1)
                            stage_name = STAGES[stage_index] if stage_index >= 0 else node_name
                            update_stage(stage_name, stage_index)

            for key, val in tracked.items():
                setattr(final_state, key, val)

        except (ConnectionError, ValueError) as e:
            logger.exception("Pipeline setup failed")
            update_stage(str(e), -1)
            status_text.color = ft.Colors.AMBER
            page.update()
            time.sleep(4)
            go_topic()

        except Exception as e:
            logger.exception("Pipeline failed")
            update_stage(f"Error: {e}", -1)
            status_text.color = ft.Colors.RED
            page.update()
            time.sleep(3)
            go_report()

        else:
            time.sleep(0.5)
            go_report()

    if not get_api_key(get_provider()):
        show_setup()
    else:
        go_topic()


ft.run(main)
