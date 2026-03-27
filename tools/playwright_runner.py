import subprocess
import json
import tempfile
from pathlib import Path

RESULTS_PATH = Path("reports/latest_run.json")
EXECUTED_SCRIPTS_DIR = Path("tests/generated/executed")


def _run_python_script(script: str, timeout: int) -> dict:
    result = subprocess.run(
        ["python", "-c", script],
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode,
    }


def run_playwright_script(script: str) -> dict:
    """
    Write the generated Playwright script to a temp file,
    execute it, and return structured results.
    """
    # Ensure reports dir exists
    RESULTS_PATH.parent.mkdir(exist_ok=True)
    EXECUTED_SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

    if RESULTS_PATH.exists():
        RESULTS_PATH.unlink()

    # Inject result collection wrapper into script
    wrapped_script = _wrap_script(script)

    script_path = None
    executed_script_path = None

    # Write wrapped script to reusable debug artifact
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, dir=str(EXECUTED_SCRIPTS_DIR)
    ) as f:
        f.write(wrapped_script)
        executed_script_path = f.name
        script_path = executed_script_path

    try:
        result = subprocess.run(
            ["python", script_path],
            capture_output=True,
            text=True,
            timeout=120,
        )

        # Try to parse JSON results from stdout
        if RESULTS_PATH.exists():
            with open(RESULTS_PATH) as rf:
                data = json.load(rf)
            if data.get("total", 0) == 0:
                return {
                    **data,
                    "status": "EXECUTION_ERROR",
                    "error": "Generated script ran without recording any tests.",
                    "executed_script_path": executed_script_path,
                    "raw_stdout": result.stdout[-2000:],
                    "raw_stderr": result.stderr[-2000:],
                }
            return {
                **data,
                "executed_script_path": executed_script_path,
                "raw_stdout": result.stdout[-2000:],
                "raw_stderr": result.stderr[-2000:],
            }

        # Fallback: parse from stdout
        fallback = _parse_output(result.stdout, result.stderr, result.returncode)
        fallback["executed_script_path"] = executed_script_path
        return fallback

    except subprocess.TimeoutExpired:
        return {
            "status": "TIMEOUT",
            "error": "Script exceeded 120s timeout",
            "tests": [],
            "executed_script_path": executed_script_path,
        }
    except Exception as e:
        return {
            "status": "EXECUTION_ERROR",
            "error": str(e),
            "tests": [],
            "executed_script_path": executed_script_path,
        }


def capture_dom_snapshot(url: str) -> str:
    """Capture DOM snapshot for self-healing context."""
    snapshot_script = f"""
import asyncio
from playwright.async_api import async_playwright
import json

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("{url}", timeout=30000)
        await page.wait_for_load_state("networkidle")
        
        # Get interactive elements
        elements = await page.evaluate('''() => {{
            const els = document.querySelectorAll(
                'button, input, a, select, textarea, [data-testid]'
            );
            return Array.from(els).slice(0, 50).map(el => ({{
                tag: el.tagName,
                id: el.id,
                name: el.name,
                type: el.type,
                text: el.innerText?.slice(0, 50),
                testId: el.dataset?.testid,
                placeholder: el.placeholder,
            }}));
        }}''')
        
        print(json.dumps(elements))
        await browser.close()

asyncio.run(main())
"""
    try:
        result = _run_python_script(snapshot_script, timeout=30)
        return result["stdout"].strip()
    except Exception as e:
        return f"DOM capture failed: {e}"


def _wrap_script(script: str) -> str:
    """Wrap the generated script to write JSON results."""
    sanitized_script = script.replace("def _record(", "def _model_defined_record(")
    wrapper_header = """
import json, sys, traceback
from pathlib import Path

_results = []
_errors  = []

def __cascade_record(name, passed, error=None, details=None):
    _results.append({
        "name": name,
        "passed": passed,
        "error": error,
        "details": details or "",
    })

_record = __cascade_record

"""
    wrapper_footer = """

# ── Save results ──────────────────────────────────────────────
_output = {
    "status": "PASS" if _results and all(r["passed"] for r in _results) else ("FAIL" if _results else "EXECUTION_ERROR"),
    "total": len(_results),
    "passed": sum(1 for r in _results if r["passed"]),
    "failed": sum(1 for r in _results if not r["passed"]),
    "tests": _results,
    "error": None if _results else "No tests were recorded by the generated script.",
}
Path("reports/latest_run.json").write_text(json.dumps(_output, indent=2))
"""
    return wrapper_header + sanitized_script + wrapper_footer


def _parse_output(stdout: str, stderr: str, returncode: int) -> dict:
    return {
        "status": "EXECUTION_ERROR" if returncode == 0 else "FAIL",
        "total": 0,
        "passed": 0,
        "failed": 0 if returncode == 0 else 1,
        "tests": [],
        "error": "Script finished without producing structured test results." if returncode == 0 else "Generated script failed during execution.",
        "raw_stdout": stdout[-2000:],
        "raw_stderr": stderr[-2000:],
    }
