# ChipGenie-AI

AI-powered framework to turn natural language requests into circuit design intent, a first-pass BOM, and schematic stubs.

## Quickstart

1) Install

```
pip install -e .
```

2) CLI example

```
chipgenie "3.3V regulator for 500mA" --interface usb-c --form-factor small --json
```

3) API server

```
uvicorn chipgenie.api:app --reload --port 8000
```

Request example:

```
POST /design
{
	"description": "3.3V regulator for 300mA with USB input",
	"interfaces": ["usb-c"],
	"constraints": {"voltage": 3.3, "current": 0.3}
}
```

## What’s inside (MVP)

- FastAPI endpoint `/design` producing parsed spec + BOM + schematic preview
- CLI wrapper for local runs
- Heuristic NLU to extract voltage/current/frequency from text
- Seed component store (LDOs, caps, resistors) for BOM generation
- Schematic preview stub ready for KiCad/Ngspice integration

## AI-driven sourcing (stubs)

- LLM providers: configurable via env `CHIPGENIE_LLM_PROVIDER` (`openai`, `deepseek`, `ollama`, `stub`).
- Search provider: env `CHIPGENIE_SEARCH_PROVIDER` (`serpapi`, `stub`).
- Keys: `OPENAI_API_KEY`, `DEEPSEEK_API_KEY`, `SERPAPI_API_KEY`; optional `OPENAI_MODEL`, `DEEPSEEK_MODEL`, `OLLAMA_MODEL`, `CHIPGENIE_LLM_BASE_URL`.

Use CLI with AI fetcher:

```
chipgenie "I want to build a humidity sensor" --ai --json
```

API AI endpoint:

```
POST /design/ai
{
	"description": "3.3V regulator for 300mA with USB input",
	"interfaces": ["usb-c"],
	"constraints": {"voltage": 3.3, "current": 0.3}
}
```

Notes: When API keys are missing, stubs return reasonable defaults and fall back to the local seed. Fetched components are cached in `data/fetched_cache.json`.
