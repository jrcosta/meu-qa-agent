import traceback

from crewai import Crew, Process

from src.agent.qa_agent import QAAgentFactory
from src.config.settings import Settings
from src.services.context_builder import RepoContextBuilder
from src.tasks.qa_task import QATaskFactory
from src.utils.debug_logger import DebugLogger


class QACrewRunner:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def run(self, file_path: str, file_diff: str, code_content: str, repo_path: str) -> str:
        debug_logger = DebugLogger()
        debug_dir = debug_logger.start_run(file_path)

        debug_logger.write_json(
            "01_input.json",
            {
                "file_path": file_path,
                "repo_path": repo_path,
                "diff_chars": len(file_diff),
                "code_chars": len(code_content),
            },
        )
        debug_logger.write_text("03_diff.patch", file_diff)
        debug_logger.write_text("04_current_code.txt", code_content)
        debug_logger.append_log("00_session.log", f"Execução iniciada em {debug_dir}")

        try:
            context_builder = RepoContextBuilder(repo_path)
            repo_context = context_builder.build(
                changed_file=file_path,
                code_content=code_content,
            )
            debug_logger.write_text("06_initial_repo_context.md", repo_context)

            agent = QAAgentFactory(
                self.settings,
                repo_path=repo_path,
                debug_logger=debug_logger,
            ).create()
            task = QATaskFactory.create(
                agent=agent,
                file_path=file_path,
                file_diff=file_diff,
                code_content=code_content,
                repo_context=repo_context,
            )
            debug_logger.write_text("07_task_prompt.md", task.description)

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
                    debug_logger.write_text("08_final_result.md", task_output.raw)
                    return task_output.raw

            if hasattr(result, "raw") and result.raw:
                debug_logger.write_text("08_final_result.md", result.raw)
                return result.raw

            final_result = str(result)
            debug_logger.write_text("08_final_result.md", final_result)
            return final_result
        except Exception as error:
            error_trace = traceback.format_exc()
            debug_logger.write_text("99_error.txt", error_trace)
            debug_logger.append_log("00_session.log", f"Falha na execução: {repr(error)}")
            raise
