from src.agent.test_generator_agent import TestGeneratorAgentFactory
from src.config.settings import Settings
from src.services.context_builder import RepoContextBuilder
from src.tasks.test_generator_task import TestGeneratorTaskFactory
from crewai import Crew, Process


class TestGeneratorCrewRunner:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def run(
        self,
        qa_report: str,
        file_path: str,
        code_content: str,
        repo_path: str,
    ) -> str:
        context_builder = RepoContextBuilder(repo_path)
        repo_context = context_builder.build(
            changed_file=file_path,
            code_content=code_content,
        )

        agent = TestGeneratorAgentFactory(self.settings).create()
        task = TestGeneratorTaskFactory.create(
            agent=agent,
            qa_report=qa_report,
            file_path=file_path,
            code_content=code_content,
            repo_context=repo_context,
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
