# Multi-Agent Research Tool — Project Plan

A local, BYOK (bring-your-own-key) research assistant that breaks a topic into
sub-questions, searches the web, summarizes findings, fact-checks them against
the original sources, corrects unsupported claims, and writes a final report —
all running as a packaged executable on the user's own machine, never sending
their API key anywhere except directly to the provider they chose.

## Tech Stack

| Layer | Choice | Why |
|---|---|---|
| Language | Python 3.11+ | required by the hackathon, only language used |
| Agent orchestration | LangGraph | the pipeline is a fixed sequence of specialized steps — maps cleanly to an explicit state graph rather than a freeform agent "crew" |
| LLM access | `openai` Python SDK (OpenAI-compatible) | one client works for OpenAI, Groq, and Gemini's OpenAI-compatible endpoint by swapping `base_url`/`api_key`/`model` |
| Search | `ddgs` (DuckDuckGo) by default, swappable to Tavily | free, no API key required; abstracted behind one interface so the provider can change without touching agent code |
| Frontend | Flet | pure Python, native window, packages cleanly to an executable via `flet pack` (built on PyInstaller, no bootstrap hacks) |
| Packaging | PyInstaller (`--onedir`) via `flet pack` | produces a standalone app the user can run without installing Python or any dependencies |
| State / structured output | Pydantic | typed shared state passed between graph nodes; structured JSON for the fact-checker's verdicts |
| Local key storage | `keyring` (OS credential store) with local-file fallback | key never leaves the device except to call the provider's own API directly |

No FastAPI in this version — the UI calls the LangGraph pipeline **in-process**,
since frontend and pipeline now run on the same machine. (A FastAPI layer
remains a reasonable future add-on if this ever needs to run as a local server
for other tools to call.)

## Directory Structure

```
research_tool/
├── app/
│   ├── main.py                  # Flet entry point, launches the window
│   ├── ui/
│   │   ├── key_setup_view.py    # first-run: provider + API key entry
│   │   ├── topic_view.py        # topic input + run button
│   │   ├── progress_view.py     # staged progress (Planning → ... → Writing)
│   │   └── report_view.py       # renders the final markdown report
│   ├── graph/
│   │   ├── state.py             # shared Pydantic state schema
│   │   ├── build_graph.py       # wires the 6 nodes into the LangGraph graph
│   │   └── nodes/
│   │       ├── planner.py
│   │       ├── search.py
│   │       ├── summarizer.py
│   │       ├── fact_checker.py
│   │       ├── correction.py
│   │       └── writer.py
│   ├── providers/
│   │   ├── llm_client.py        # OpenAI-compatible wrapper, per-agent model choice
│   │   └── search/
│   │       ├── base.py          # SearchProvider interface
│   │       ├── duckduckgo.py
│   │       └── tavily.py
│   ├── config.py                # local key storage + settings
│   └── utils/
│       └── __init__.py
├── assets/                      # app icon, etc. for packaging
├── tests/
│   ├── __init__.py
│   └── test_pipeline.py         # end-to-end run against a sample topic
├── requirements.txt
├── README.md
└── PLAN.md
```

## Features

- **Six-stage agent pipeline** — Planner → Search → Summarizer → Fact Checker →
  Correction → Writer, each a distinct LangGraph node with a clear input/output
  contract through shared state.
- **Fact-check + correction stage** — claims are checked against the *original*
  retrieved evidence (not just the summary), and the Correction agent fixes or
  strikes unsupported claims using that same evidence, with no extra search
  calls. A correction log records what changed and why.
- **BYOK, fully local** — the user enters their own API key on first run; it's
  stored on-device only and sent only to the provider's official endpoint.
  No hosted backend, no middleman server, no key logging.
- **Provider-agnostic LLM layer** — works with OpenAI, Groq, or Gemini's
  OpenAI-compatible endpoint by changing config, not code. Cheap/fast models
  can be assigned to high-volume steps (search query gen, summarizing) and a
  stronger model reserved for planning and writing.
- **Free-tier search by default** — DuckDuckGo out of the box, swappable to
  Tavily behind the same interface if higher-quality results are worth the
  (small) cost.
- **Live staged progress** — the UI shows which agent is currently running
  rather than a single opaque spinner.
- **Standalone executable** — packaged with PyInstaller; a user can run it
  without installing Python, a venv, or any dependencies.
- **Markdown final report** — cited, with an optional "unverified claims"
  section pulled from the correction log for transparency.

## To-Do

### Pipeline first
- [x] Throwaway Flet + PyInstaller "hello world" pack — surface packaging
      issues (hidden imports, certifi) before any real logic is built
- [x] Define shared state schema (`state.py`)
- [x] Build LLM client wrapper with per-agent model/provider config
- [x] Build `SearchProvider` interface + DuckDuckGo implementation
- [x] Implement Planner node (topic → sub-questions + outline)
- [x] Implement Search node (parallel queries across sub-questions)
- [x] Implement Summarizer node (grounded, cited per-sub-question summaries)
- [x] Implement Fact Checker node (structured JSON verdicts per claim)
- [x] Implement Correction node (fix/strike flagged claims, write correction log)
- [x] Implement Writer node (assemble final markdown report)
- [x] Wire all nodes into the LangGraph graph (`build_graph.py`)
- [x] Run the full pipeline end-to-end from a plain script against a real topic
      (`python -m app.run "your topic"`)

### UI, packaging, polish
- [x] Build key-entry screen, wire to local storage (`keyring`)
- [x] Build topic input + run screen
- [x] Build staged progress view, calling the pipeline in-process
- [x] Build report view rendering the final markdown
- [x] Add an explicit "your key stays on this device" note in the UI
- [ ] Pack the real app with PyInstaller (`--onedir`), fix any hidden-import
      or certificate bundling issues
- [ ] Test the built executable on a clean run (not just `python main.py`)

### Submission prep (don't leave this for 11:59pm)
- [ ] Screenshot(s) of the running app
- [ ] Record 1–3 minute demo video
- [ ] Write Devpost sections: title, short description, what it does, how
      Python was used, challenges faced and what was learned
- [ ] Push code to a public/accessible GitHub repo
- [ ] Submit on Devpost before the deadline
