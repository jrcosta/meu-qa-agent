import re

from src.agent.test_generator_agent import TestGeneratorAgentFactory
from src.config.settings import Settings
from src.services.context_builder import RepoContextBuilder
from src.tasks.test_generator_task import TestGeneratorTaskFactory
from src.tools.memory_tools import QueryMemoriesTool
from crewai import Crew, Process
from src.schemas.context_result import render_context_result_for_prompt
from src.schemas.test_strategy_result import TestStrategyResult, render_test_strategy_result_for_prompt




class TestGeneratorCrewRunner:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.last_memory_query = ""
        self.last_memories_raw = ""
        self.last_memories_used: list[dict] = []

    def _load_memories(self, file_path: str, code_content: str) -> str:
        """Find relevant memories from the DB using semantic search."""
        self.last_memory_query = f"Testes para {file_path}. Código: {code_content[:200]}"
        self.last_memories_raw = ""
        self.last_memories_used = []

        try:
            tool = QueryMemoriesTool()
            result = tool._run(query=self.last_memory_query, limit=5)
            self.last_memories_raw = result
            self.last_memories_used = _parse_memory_result(result)

            if result and "Nenhuma memória" not in result:
                count = len(self.last_memories_used)
                print(f"  🧠 Memories loaded: {count} relevant lesson(s) found for {file_path}")
                print(f"  🧠 Memory content preview: {result[:200]}...")
            else:
                print(f"  🧠 No relevant memories found in DB for {file_path}.")
            return result
        except Exception as exc:
            print(f"  ⚠️ Could not load memories: {exc}")
            return ""

    def run(
        self,
        qa_report: str,
        file_path: str,
        code_content: str,
        repo_path: str,
        test_strategy: TestStrategyResult | None = None,
    ) -> str:
        context_builder = RepoContextBuilder(repo_path)
        context_result = context_builder.build(
            changed_file=file_path,
            code_content=code_content,
        )
        
        repo_context_text = render_context_result_for_prompt(context_result)


        memories = self._load_memories(file_path, code_content)

        test_strategy_text = ""
        if test_strategy is not None:
            test_strategy_text = render_test_strategy_result_for_prompt(test_strategy)

        agent = TestGeneratorAgentFactory(self.settings).create()
        task = TestGeneratorTaskFactory.create(
            agent=agent,
            qa_report=qa_report,
            file_path=file_path,
            code_content=code_content,
            repo_context=repo_context_text,
            memories=memories,
            test_strategy_text=test_strategy_text,
        )

        crew = Crew(
            agents=[agent],
            tasks=[task],
            process=Process.sequential,
            verbose=True,
        )

        result = crew.kickoff()

        if hasattr(result, "tasks_output") and result.tasks_output:
            task_output = result.tasks_output[-1]
            if hasattr(task_output, "raw") and task_output.raw:
                return task_output.raw

        if hasattr(result, "raw") and result.raw:
            return result.raw

        return str(result)


def _parse_memory_result(result: str) -> list[dict]:
    if not result or "Nenhuma memória" in result:
        return []

    memories: list[dict] = []
    blocks = [block.strip() for block in result.strip().split("\n\n") if block.strip()]
    pattern = re.compile(
        r"^\[distance=(?P<distance>[0-9.]+)\]\s+"
        r"\(PR #(?P<pr_number>\d+) em (?P<repo>.*?), por (?P<author>.*?)\)\n"
        r"\s*Lição:\s*(?P<lesson>.*)$",
        re.DOTALL,
    )

    for block in blocks:
        match = pattern.match(block)
        if not match:
            memories.append({"lesson": block})
            continue

        data = match.groupdict()
        memories.append(
            {
                "distance": float(data["distance"]),
                "pr_number": int(data["pr_number"]),
                "repo": data["repo"],
                "author": data["author"],
                "lesson": data["lesson"].strip(),
            }
        )

    return memories
