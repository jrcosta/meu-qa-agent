from typing import Optional
from pydantic import BaseModel, Field

from src.schemas.context_result import ContextResult
from src.schemas.review_result import ReviewResult
from src.schemas.test_strategy_result import TestStrategyResult


class FileAnalysisArtifact(BaseModel):
    """
    Artefato consolidado representando o resultado completo da análise
    de um único arquivo dentro do pipeline.

    Centraliza todos os dados estruturados produzidos pelas etapas:
    Context -> QA Review -> Test Strategy

    Permite que etapas futuras consumam um único objeto em vez de
    variáveis dispersas.
    """

    file_path: str = Field(..., description="Caminho do arquivo analisado")
    context_result: Optional[ContextResult] = Field(
        None, description="Resultado da etapa de extração de contexto"
    )
    raw_review_markdown: Optional[str] = Field(
        None, description="Markdown bruto retornado pelo QA Agent"
    )
    review_result: Optional[ReviewResult] = Field(
        None, description="Resultado estruturado da revisão de código"
    )
    test_strategy_result: Optional[TestStrategyResult] = Field(
        None, description="Estratégia de testes derivada da revisão"
    )
