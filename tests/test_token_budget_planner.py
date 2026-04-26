from src.services.token_budget_planner import (
    TokenBudgetPlanner,
    build_code_content_for_plan,
)


def test_skips_small_documentation_change() -> None:
    planner = TokenBudgetPlanner()

    plan = planner.plan(
        file_path="docs/readme.md",
        file_diff="diff --git a/docs/readme.md b/docs/readme.md\n+novo texto\n",
        code_content="# Docs\n",
        cooperative_requested=True,
    )

    assert plan.analysis_mode == "skip"
    assert plan.context_level == "none"
    assert plan.include_full_file is False
    assert plan.include_memory is False


def test_small_low_risk_change_disables_cooperative_mode() -> None:
    planner = TokenBudgetPlanner()

    plan = planner.plan(
        file_path="src/utils/formatters.py",
        file_diff="+return value.strip()\n",
        code_content="def clean(value):\n    return value.strip()\n",
        cooperative_requested=True,
    )

    assert plan.analysis_mode == "standard"
    assert plan.context_level == "compact"
    assert "reduzida para QA padrão" in plan.reason


def test_high_risk_path_can_use_cooperative_mode() -> None:
    planner = TokenBudgetPlanner()

    plan = planner.plan(
        file_path="src/services/payment_service.py",
        file_diff="+def charge():\n+    return True\n",
        code_content="def charge():\n    return True\n",
        cooperative_requested=True,
    )

    assert plan.analysis_mode == "cooperative"
    assert plan.context_level == "standard"
    assert plan.include_memory is True


def test_large_file_uses_snippet_instead_of_full_file() -> None:
    planner = TokenBudgetPlanner()

    plan = planner.plan(
        file_path="src/services/user_service.py",
        file_diff="+value = 1\n",
        code_content="x" * 12_001,
    )

    assert plan.include_full_file is False
    assert plan.risk_hint == "high"


def test_build_code_content_for_large_file_keeps_changed_window() -> None:
    planner = TokenBudgetPlanner()
    code = "\n".join(f"line {i}" for i in range(1, 101))
    diff = "@@ -49,2 +49,2 @@\n line 49\n-line 50\n+line 50 changed\n"
    plan = planner.plan(
        file_path="src/services/user_service.py",
        file_diff=diff,
        code_content="x" * 12_001,
    )

    compact = build_code_content_for_plan(
        code_content=code,
        file_diff=diff,
        plan=plan,
        context_lines=1,
    )

    assert "Arquivo compactado pelo TokenBudgetPlanner" in compact
    assert "49: line 49" in compact
    assert "50: line 50" in compact
    assert "52: line 52" not in compact
