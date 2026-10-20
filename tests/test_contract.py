"""Cross-SDK contract: every evaluator must agree with tests/contract/flag-evaluation.json."""

import json
from pathlib import Path

import pytest

from toggletown.evaluator import evaluate_flag

def _find_fixture():
    """Monorepo: <root>/tests/contract. Standalone sdk-python repo: <repo>/tests/contract."""
    for parent in Path(__file__).resolve().parents:
        candidate = parent / "tests" / "contract" / "flag-evaluation.json"
        if candidate.exists():
            return candidate
    raise FileNotFoundError("tests/contract/flag-evaluation.json not found above " + __file__)


CASES = json.loads(_find_fixture().read_text(encoding="utf-8"))["cases"]


def to_python_context(context):
    """The Python SDK reads user_id and attributes from one flat dict."""
    ctx = dict(context.get("attributes", {}))
    if "userId" in context:
        ctx["user_id"] = context["userId"]
    return ctx


@pytest.mark.parametrize("case", CASES, ids=[c["name"] for c in CASES])
def test_contract(case):
    assert evaluate_flag(case["flag"], to_python_context(case["context"])) == case["expected"]
