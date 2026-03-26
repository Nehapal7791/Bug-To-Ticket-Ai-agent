import subprocess
import json
import os
import tempfile
from pathlib import Path

RESULTS_PATH = Path("reports/latest_run.json")


def run_playwright_script(script: str) -> dict:
    """
    Write the generated Playwright script to a temp file,
    execute it, and return structured results.
    """
    # Ensure reports dir exists
    RESULTS_PATH.parent.mkdir(exist_ok=True)

    # Inject result collection wrapper into script
    wrapped_script = _wrap_script(script)

    # Write to temp file
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, dir="tests/generated"
    ) as f:
        f.write(wrapped_script)
        script_path = f.name

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
                return json.load(rf)

        # Fallback: parse from stdout
        return _parse_output(result.stdout, result.stderr, result.returncode)

    except subprocess.TimeoutExpired:
        return {
            "status": "TIMEOUT",
            "error": "Script exceeded 120s timeout",
            "tests": [],
        }
    except Exception as e:
        return {
            "status": "EXECUTION_ERROR",
            "error": str(e),
            "tests": [],
        }
    finally:
        # Clean up temp file
        try:
            os.unlink(script_path)
        except Exception:
            pass


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
        result = subprocess.run(
            ["python", "-c", snapshot_script],
            capture_output=True, text=True, timeout=30
        )
        return result.stdout.strip()
    except Exception as e:
        return f"DOM capture failed: {e}"


def _wrap_script(script: str) -> str:
    """Wrap the generated script to write JSON results."""
    wrapper_header = f"""
import json, sys, traceback
from pathlib import Path

_results = []
_errors  = []

def _record(name, passed, error=None, details=None):
    _results.append({{
        "name": name,
        "passed": passed,
        "error": error,
        "details": details or "",
    }})

"""
    wrapper_footer = f"""

# ── Save results ──────────────────────────────────────────────
_output = {{
    "status": "PASS" if all(r["passed"] for r in _results) else "FAIL",
    "total": len(_results),
    "passed": sum(1 for r in _results if r["passed"]),
    "failed": sum(1 for r in _results if not r["passed"]),
    "tests": _results,
}}
Path("reports/latest_run.json").write_text(json.dumps(_output, indent=2))
"""
    return wrapper_header + script + wrapper_footer


def _parse_output(stdout: str, stderr: str, returncode: int) -> dict:
    return {
        "status": "PASS" if returncode == 0 else "FAIL",
        "total": 0,
        "passed": 0,
        "failed": 0 if returncode == 0 else 1,
        "tests": [],
        "raw_stdout": stdout[-2000:],
        "raw_stderr": stderr[-2000:],
    }
