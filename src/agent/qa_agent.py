
from __future__ import annotations

from crewai import Agent

from src.tools.repo_tools import (
    FindRelatedTestFilesTool,
    GetOfficialDocsReferenceTool,
    InspectRepoStackTool,
    ReadFileTool,
    SearchInRepoTool,
)


class QAAgentFactory:
    def __init__(self, settings, repo_path: str, debug_logger=None) -> None:
        self.settings = settings
        self.repo_path = repo_path
        self.debug_logger = debug_logger

    def _resolve_llm(self):
        candidates = [
            "llm",
            "_llm",
            "agent_llm",
            "crewai_llm",
            "review_llm",
            "model",
        ]

        for attr in candidates:
            if hasattr(self.settings, attr):
                value = getattr(self.settings, attr)
                if value is not None:
                    return value

        method_candidates = [
            "get_llm",
            "build_llm",
            "create_llm",
            "make_llm",
        ]

        for method_name in method_candidates:
            if hasattr(self.settings, method_name):
                method = getattr(self.settings, method_name)
                if callable(method):
                    value = method()
                    if value is not None:
                        return value

        raise AttributeError(
            "Não foi possível resolver o LLM a partir de Settings. "
            "A classe Settings precisa expor um destes atributos: "
            "'llm', '_llm', 'agent_llm', 'crewai_llm', 'review_llm' ou 'model', "
            "ou um destes métodos: 'get_llm()', 'build_llm()', 'create_llm()', 'make_llm()'."
        )

    def create(self) -> Agent:
        tools = [
            ReadFileTool(repo_path=self.repo_path, debug_logger=self.debug_logger),
            SearchInRepoTool(repo_path=self.repo_path, debug_logger=self.debug_logger),
            FindRelatedTestFilesTool(repo_path=self.repo_path, debug_logger=self.debug_logger),
            InspectRepoStackTool(repo_path=self.repo_path, debug_logger=self.debug_logger),
            GetOfficialDocsReferenceTool(),
        ]

        llm = self._resolve_llm()

        if self.debug_logger:
            self.debug_logger.write_json(
                "agent_config.json",
                {
                    "repo_path": self.repo_path,
                    "tools": [tool.name for tool in tools],
                    "llm_repr": repr(llm),
                    "settings_type": type(self.settings).__name__,
                },
            )

        return Agent(
            role="Agnostic Code Reviewer",
            goal=(
                "Review code changes critically, identify concrete inconsistencies, "
                "possible regressions, contract breaks, fragile behavior and missing validation."
            ),
            backstory=(
                "You are a senior QA-oriented reviewer who can assess code changes across "
                "different languages, frameworks and project structures. You do not assume a specific "
                "stack. You inspect the repository, use tools when necessary, and ground every important "
                "claim in evidence from the diff, related code, tests or official documentation."
            ),
            tools=tools,
            llm=llm,
            verbose=True,
            allow_delegation=False,
        )