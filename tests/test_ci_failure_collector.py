from src.schemas.ci_check_result import CIFailingCheck
from src.services.ci_failure_collector import (
    _compact_failure_log,
    _extract_job_id,
    _extract_run_id,
    render_ci_result_for_prompt,
    _render_ci_summary,
)
from src.schemas.ci_check_result import CITestExecutionResult


def test_extract_run_id_from_actions_job_link() -> None:
    link = "https://github.com/org/repo/actions/runs/123456789/job/987654321"

    assert _extract_run_id(link) == "123456789"


def test_extract_job_id_from_actions_job_link() -> None:
    link = "https://github.com/org/repo/actions/runs/123456789/job/987654321"

    assert _extract_job_id(link) == "987654321"


def test_compact_failure_log_prefers_actionable_lines() -> None:
    log = "\n".join(
        [
            "setup ok",
            "FAILED tests/test_api.py::test_cart - assert 200 == 422",
            "details",
            "Process completed with exit code 1.",
        ]
    )

    compact = _compact_failure_log(log, max_chars=500)

    assert "FAILED tests/test_api.py::test_cart" in compact
    assert "Process completed with exit code 1." in compact
    assert "setup ok" in compact


def test_compact_failure_log_keeps_context_around_pytest_failure() -> None:
    log = "\n".join(
        [
            "tests/test_api.py::test_cart FAILED",
            "payload = {'unexpected': 'value'}",
            ">       assert response.status_code == 422",
            "E       assert 200 == 422",
            "short test summary info",
        ]
    )

    compact = _compact_failure_log(log, max_chars=1000)

    assert "payload = {'unexpected': 'value'}" in compact
    assert "assert response.status_code == 422" in compact
    assert "assert 200 == 422" in compact


def test_render_ci_summary_includes_failing_check_and_excerpt() -> None:
    summary = _render_ci_summary(
        status="failed",
        pr_ref="74",
        failing_checks=[
            CIFailingCheck(
                name="test (3.11)",
                workflow="Python tests",
                state="FAILURE",
                link="https://github.com/org/repo/actions/runs/1/job/2",
                failure_excerpt="FAILED tests/test_schemas.py::test_bool",
            )
        ],
    )

    assert "Status agregado do CI: failed" in summary
    assert "test (3.11)" in summary
    assert "FAILED tests/test_schemas.py::test_bool" in summary


def test_render_ci_result_for_prompt_returns_summary() -> None:
    result = CITestExecutionResult(
        status="passed",
        pr_ref="12",
        summary="Todos os checks de CI do PR alvo passaram.",
    )

    assert render_ci_result_for_prompt(result) == result.summary
