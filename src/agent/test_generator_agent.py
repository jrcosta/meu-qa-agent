from pathlib import Path

from crewai import Agent, LLM

from src.config.settings import Settings


class TestGeneratorAgentFactory:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.system_prompt = self._load_system_prompt()

    def _load_system_prompt(self) -> str:
        prompt_path = Path("src/prompts/test_generator_prompt.txt")
        return prompt_path.read_text(encoding="utf-8")

    def create(self) -> Agent:
        llm = LLM(
            model=self.settings.llm_model,
            api_key=self.settings.llm_api_key,
            temperature=self.settings.llm_temperature,
        )

        return Agent(
            role="Engenheiro de Testes Sênior",
            goal=(
                "Gerar testes unitários concretos e executáveis baseados no relatório de QA, "
                "cobrindo os cenários de teste sugeridos com código pronto para execução"
            ),
            backstory=self.system_prompt,
            llm=llm,
            verbose=True,
            allow_delegation=False,
        )
