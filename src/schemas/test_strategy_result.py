from typing import List, Literal
from pydantic import BaseModel, Field


class TestCase(BaseModel):
    """Schema representando um caso de teste recomendado."""
    name: str = Field(..., description="Nome ou descrição do caso de teste recomendado")
    test_type: Literal["UNIT", "INTEGRATION", "E2E"] = Field(
        default="UNIT",
        description="Tipo do caso de teste"
    )
    priority: Literal["LOW", "MEDIUM", "HIGH"] = Field(
        default="MEDIUM",
        description="Prioridade do teste"
    )


class TestStrategyResult(BaseModel):
    """Schema representando a estratégia de testes gerada."""
    recommended_tests: List[TestCase] = Field(default_factory=list, description="Lista de testes recomendados")
    notes: str = Field(default="", description="Notas adicionais sobre a estratégia sugerida")


def parse_test_strategy_markdown_to_test_strategy_result(text: str) -> TestStrategyResult:
    """
    Função auxiliar simples para converter texto markdown em um TestStrategyResult.
    """
    return TestStrategyResult(
        recommended_tests=[],
        notes=text.strip()
    )


def render_test_strategy_result_for_prompt(test_strategy: TestStrategyResult) -> str:
    """
    Renderiza um TestStrategyResult em texto legível para injeção no prompt
    do agente gerador de testes.
    """
    lines: list[str] = []

    if test_strategy.recommended_tests:
        lines.append("## Testes recomendados pela estratégia")
        for i, tc in enumerate(test_strategy.recommended_tests, 1):
            lines.append(f"{i}. [{tc.priority}] ({tc.test_type}) {tc.name}")
        lines.append("")

    if test_strategy.notes:
        lines.append("## Notas da estratégia")
        lines.append(test_strategy.notes)
        lines.append("")

    if not lines:
        return "Nenhuma recomendação de teste disponível na estratégia."

    return "\n".join(lines)