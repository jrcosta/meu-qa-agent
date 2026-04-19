"""Crew that runs the memory summariser agent."""

from crewai import Crew, Process

from src.agent.memory_agent import MemoryAgentFactory
from src.config.settings import Settings
from src.tasks.memory_task import MemoryTaskFactory


class MemoryCrewRunner:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def run(self, comment_body: str, repo: str, pr_number: int) -> str:
        agent = MemoryAgentFactory(self.settings).create()
        task = MemoryTaskFactory.create(
            agent=agent,
            comment_body=comment_body,
            repo=repo,
            pr_number=pr_number,
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
