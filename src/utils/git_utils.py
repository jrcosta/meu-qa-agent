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


def has_commits() -> bool:
    result = subprocess.run(
        ["git", "rev-parse", "--verify", "HEAD"],
        capture_output=True,
        text=True,
        shell=True,
    )
    return result.returncode == 0


def get_changed_files() -> list[str]:
    if has_commits():
        command = ["git", "diff", "--name-only", "HEAD"]
    else:
        command = ["git", "status", "--porcelain"]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        shell=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            "Erro ao executar comando git.\n"
            f"stdout:\n{result.stdout}\n\n"
            f"stderr:\n{result.stderr}"
        )

    if has_commits():
        files = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    else:
        files = parse_git_status_output(result.stdout)

    return [file for file in files if should_analyze_file(file)]


def get_file_diff(file_path: str) -> str:
    if has_commits():
        command = ["git", "diff", "HEAD", "--", file_path]
    else:
        command = ["git", "diff", "--", file_path]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        shell=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Erro ao obter diff do arquivo: {file_path}\n"
            f"stdout:\n{result.stdout}\n\n"
            f"stderr:\n{result.stderr}"
        )

    return result.stdout.strip()


def parse_git_status_output(output: str) -> list[str]:
    files = []

    for line in output.splitlines():
        line = line.strip()
        if not line:
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