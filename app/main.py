from __future__ import annotations

import threading

import flet as ft

from .config import get_api_key
from .graph.build_graph import build_pipeline
from .graph.state import ResearchState
from .providers.llm_client import LLMClient
from .providers.search.duckduckgo import DuckDuckGoProvider
from .ui.key_setup_view import KeySetupView
from .ui.progress_view import STAGES, ProgressView
from .ui.report_view import ReportView
from .ui.topic_view import TopicView
from .utils.logging import setup_logger

logger = setup_logger(__name__)


def main(page: ft.Page):
    page.title = "Distillery — Research Assistant"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 24
    page.window.width = 900
    page.window.height = 700
    page.scroll = ft.ScrollMode.AUTO

    state = ResearchState(topic="")
    pipeline_thread: threading.Thread | None = None

    def show_setup():
        page.views.clear()
        page.views.append(KeySetupView(page))
        page.push_route("/setup")
        page.update()

    def start_research(topic: str):
        nonlocal pipeline_thread
        state.topic = topic
        go_progress()
        pipeline_thread = threading.Thread(target=run_pipeline, daemon=True)
        pipeline_thread.start()

    def go_progress():
        progress_view = ProgressView(page)
        page.views.clear()
        page.views.append(progress_view)
        page.push_route("/progress")
        page.update()

    def go_topic():
        topic_view = TopicView(page, start_research)
        page.views.clear()
        page.views.append(topic_view)
        page.push_route("/topic")
        page.update()

    def go_report():
        report_view = ReportView(page, state, go_topic)
        page.views.clear()
        page.views.append(report_view)
        page.push_route("/report")
        page.update()

    def update_stage(stage: str):
        if page.views and page.route == "/progress":
            v = page.views[0]
            for i, s in enumerate(STAGES):
                if i < STAGES.index(stage):
                    pass
            status_text = None
            for c in v.controls:
                if isinstance(c, ft.Column):
                    for item in c.controls:
                        if isinstance(item, ft.Text) and item.italic:
                            status_text = item
                            break
            if status_text:
                status_text.value = f"Current stage: {stage}"
                page.update()

    def run_pipeline():
        try:
            provider = __import__("app.config", fromlist=[""]).get_provider()
            api_key = get_api_key()
            llm = LLMClient(provider=provider, api_key=api_key)
            search = DuckDuckGoProvider()
            graph = build_pipeline(llm, search)

            for event in graph.stream(state):
                if isinstance(event, dict):
                    for node_name, updates in event.items():
                        if isinstance(updates, dict):
                            stage = updates.get("current_stage", "")
                            if stage:
                                page.add(ft.Text(f"[{node_name}] {stage}"))
        except Exception as e:
            logger.exception("Pipeline failed")
            page.add(ft.Text(f"Pipeline error: {e}", color=ft.Colors.RED))
        finally:
            go_report()

    if not get_api_key():
        show_setup()
    else:
        go_topic()


ft.run(main)
