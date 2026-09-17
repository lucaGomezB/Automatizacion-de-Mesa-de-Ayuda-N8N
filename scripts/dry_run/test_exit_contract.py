"""§6.2 - a PENDING/incomplete check is NEVER reported as success.

``checks.py`` already proves the pure exit-code contract. This sibling proves the
same guarantee end-to-end through the CLI's terminal step (``dry_run._finish``):
a run that carries a pending check must print RED and return a non-zero exit
code, and only an all-PASS run may print GREEN and return zero.

Run with:
    cd scripts/dry_run && python -m pytest test_exit_contract.py -q
or from the repo root:
    python -m pytest scripts/dry_run/test_exit_contract.py -q
"""

from __future__ import annotations

import io
import os
import sys
from contextlib import redirect_stdout
from types import SimpleNamespace

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import dry_run
from checks import STATUS_PENDING, exit_code, failing, passing, pending


def _finish_capturing(results):
    args = SimpleNamespace(json=False)
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        code = dry_run._finish(results, args)
    return code, buffer.getvalue()


def test_pending_check_is_not_ok():
    assert not pending("e2e:web", "skipped", "fix preflight first").ok


def test_pending_run_is_reported_red_and_exits_nonzero():
    code, output = _finish_capturing([passing("a"), pending("b", "incomplete", "run it")])
    assert code != 0
    assert "RED" in output
    assert "GREEN" not in output
    assert "1/2" in output


def test_failed_run_is_reported_red_and_exits_nonzero():
    code, output = _finish_capturing([passing("a"), failing("b", "boom", "fix it")])
    assert code != 0
    assert "RED" in output
    assert "GREEN" not in output


def test_only_all_pass_runs_are_reported_green_and_exit_zero():
    code, output = _finish_capturing([passing("a"), passing("b")])
    assert code == 0
    assert "GREEN" in output
    assert "2/2" in output


def test_empty_run_is_not_reported_green():
    assert exit_code([]) != 0
