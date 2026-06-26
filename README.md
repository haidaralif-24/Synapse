# Fetchy

A local, BYOK (bring-your-own-key) multi-agent research assistant. Breaks a topic into sub-questions, searches the web, summarizes findings, fact-checks claims against sources, corrects unsupported claims, and writes a final report — all on your own machine.

## Features

- **Six-stage agent pipeline**: Planner → Search → Summarizer → Fact Checker → Correction → Writer
- **BYOK & fully local**: API key stored on-device, sent only to your chosen provider
- **Provider-agnostic**: OpenAI, Groq, or Gemini (OpenAI-compatible)
- **Free-tier search**: DuckDuckGo out of the box, swappable to Tavily
- **Live staged progress**: See which agent is running in real time
- **Standalone executable**: Package with `flet pack` (PyInstaller)

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

**GUI:**
```bash
python -m app.main
```

**CLI (headless):**
```bash
python -m app.run "Your research topic"
```

On first run you'll be prompted to enter an API key and choose a provider.
You can also set `DISTILLERY_API_KEY` and `DISTILLERY_PROVIDER` env vars for the CLI.

## Package as executable

```bash
flet pack app/main.py --name fetchy --icon assets/icon.png
```

## Project Structure

```
app/
├── main.py                  # Flet entry point
├── config.py                # Local key storage
├── graph/
│   ├── state.py             # Pydantic shared state
│   ├── build_graph.py       # LangGraph wiring
│   └── nodes/               # 6 pipeline nodes
├── providers/
│   ├── llm_client.py        # OpenAI-compatible wrapper
│   └── search/              # DuckDuckGo + Tavily
└── ui/                      # Flet views
```

## Tests

```bash
python -m pytest tests/
```
