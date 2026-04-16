from pathlib import Path

from crewai import Agent, LLM

from src.config.settings import Settings
from src.tools.repo_tools import FindRelatedTestFilesTool, ReadFileTool, SearchInRepoTool
from src.utils.debug_logger import DebugLogger


class QAAgentFactory:
    def __init__(
        self,
        settings: Settings,
        repo_path: str,
        debug_logger: DebugLogger | None = None,
    ) -> None:
        self.settings = settings
        self.repo_path = Path(repo_path)
        self.debug_logger = debug_logger
        self.system_prompt = self._load_system_prompt()

    def _load_system_prompt(self) -> str:
        prompt_path = Path("src/prompts/system_prompt.txt")
        return prompt_path.read_text(encoding="utf-8")

    def create(self) -> Agent:
        llm = LLM(
            model=self.settings.llm_model,
            api_key=self.settings.llm_api_key,
            temperature=self.settings.llm_temperature,
            base_url=self.settings.llm_base_url,
        )

        tools = [
            ReadFileTool(self.repo_path, debug_logger=self.debug_logger),
            SearchInRepoTool(self.repo_path, debug_logger=self.debug_logger),
            FindRelatedTestFilesTool(self.repo_path, debug_logger=self.debug_logger),
        ]

        if self.debug_logger:
            self.debug_logger.write_json(
                "02_agent_config.json",
                {
                    "model": self.settings.llm_model,
                    "base_url": self.settings.llm_base_url,
                    "temperature": self.settings.llm_temperature,
                    "tools": [tool.name for tool in tools],
                    "repo_path": str(self.repo_path),
                },
            )

        return Agent(
            role="QA Sênior Investigador",
            goal=(
                "Analisar mudanças de código com profundidade usando diff, conteúdo do arquivo "
                "e tools do repositório para investigar impacto real, evidências técnicas e testes relevantes"
            ),
            backstory=self.system_prompt,
            llm=llm,
            tools=tools,
            verbose=True,
            allow_delegation=False,
        )
