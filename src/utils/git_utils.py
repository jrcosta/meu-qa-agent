import subprocess
from pathlib import Path


IGNORED_EXTENSIONS = {
    ".md",
    ".txt",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".svg",
    ".lock",
}

IGNORED_DIRECTORIES = {
    ".git",
    ".venv",
    "__pycache__",
    "outputs",
}


def run_git_command(command: list[str]) -> subprocess.CompletedProcess:
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        cwd=Path.cwd(),
    )

    if result.returncode != 0:
        raise RuntimeError(
            "Erro ao executar comando git.\n"
            f"Comando: {' '.join(command)}\n"
            f"stdout:\n{result.stdout}\n\n"
            f"stderr:\n{result.stderr}"
        )

    return result


def has_commits() -> bool:
    result = subprocess.run(
        ["git", "rev-parse", "--verify", "HEAD"],
        capture_output=True,
        text=True,
        cwd=Path.cwd(),
    )
    return result.returncode == 0


def get_changed_files() -> list[str]:
    if has_commits():
        result = run_git_command(["git", "diff", "--name-only", "HEAD"])
        files = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    else:
        result = run_git_command(["git", "status", "--porcelain"])
        files = parse_git_status_output(result.stdout)

    return [file for file in files if should_analyze_file(file)]


def get_file_diff(file_path: str) -> str:
    if has_commits():
        result = run_git_command(["git", "diff", "HEAD", "--", file_path])
    else:
        result = run_git_command(["git", "diff", "--", file_path])

    return result.stdout.strip()


def parse_git_status_output(output: str) -> list[str]:
    files = []

    for line in output.splitlines():
        if not line.strip():
            continue

        if len(line) > 3:
            file_path = line[3:].strip()
            files.append(file_path)

    return files


def should_analyze_file(file_path: str) -> bool:
    path = Path(file_path)

    if not path.exists():
        return False

    if any(part in IGNORED_DIRECTORIES for part in path.parts):
        return False

    if path.suffix.lower() in IGNORED_EXTENSIONS:
        return False

    return path.is_file()