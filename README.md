
# AI-Powered QA Agent

Autonomous QA agent built on `LangGraph` that reads a Jira ticket, analyzes risk, generates Playwright tests, executes them, classifies failures, self-heals selector issues, logs real bugs back to Jira, and produces a final QA report.

## Active Runtime Structure

```text
Bug-to-ticketAgent/
├── main.py
├── config.py
├── pyproject.toml
├── .env.example
├── graph/
│   ├── __init__.py
│   ├── state.py
│   ├── graph_builder.py
│   └── nodes/
│       ├── __init__.py
│       ├── fetch_ticket.py
│       ├── analyze_risk.py
│       ├── gen_tests.py
│       ├── run_playwright.py
│       ├── detect_bugs.py
│       ├── self_heal.py
│       ├── log_bugs.py
│       └── summarize.py
├── tools/
│   ├── __init__.py
│   ├── jira_client.py
│   └── playwright_runner.py
├── test_flow.py
├── run_test_flow.sh
├── tests/
│   └── generated/
├── reports/
├── memory/
├── agents/
└── mcp/
```

## Important Note

`graph/` and `tools/` are the active runtime paths used by `main.py`.



## LangGraph Flow

```text
START
  -> fetch_ticket
  -> analyze_risk
  -> gen_tests
  -> run_playwright
  -> detect_bugs
       -> self_heal -> gen_tests
       -> log_bugs -> summarize
       -> summarize
  -> END
```

## Environment Variables

Create `.env` from `.env.example`.

```bash
GROQ_API_KEY=gsk_...
JIRA_BASE_URL=https://yourteam.atlassian.net
JIRA_EMAIL=you@yourteam.com
JIRA_API_TOKEN=your-jira-api-token
JIRA_PROJECT_KEY=QA
APP_BASE_URL=https://your-app-url.com
```

## Setup

```bash
uv sync
uv run playwright install chromium
cp .env.example .env
```

Then fill the values in `.env`.

## Run the Real Agent

```bash
uv run python main.py --ticket QA-42 --app https://your-app.com
```

## Run the Mocked Smoke Test

This validates the graph flow without live Jira, Groq, or Playwright dependencies.

```bash
uv run python test_flow.py
```

Or:

```bash
bash run_test_flow.sh
```

## Run the Pytest Smoke Test

```bash
uv run pytest -q
```

## What the Smoke Test Covers

- `fetch_ticket`
- `analyze_risk`
- `gen_tests`
- `run_playwright`
- `detect_bugs`
- `summarize`

It uses mocks for Jira fetch, LLM responses, Playwright execution, DOM capture, and Jira bug creation.

## Output Artifacts

- Generated Playwright scripts: `tests/generated/`
- Latest execution artifact: `reports/latest_run.json`
- Per-run final reports: `reports/<ticket>_<timestamp>.json`

## Next Cleanup Recommendation

Once you confirm the graph-based runtime works in your environment, you can safely remove `agents/` and `mcp/` to avoid future import drift.
