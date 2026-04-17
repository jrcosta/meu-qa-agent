import os
import re
import subprocess
from pathlib import Path
from typing import Optional

from github import Github


def parse_test_files_from_output(agent_output: str) -> dict[str, str]:
    """Extrai arquivos de teste do output do agente no formato ### FILE: path + bloco de código."""
    files: dict[str, str] = {}
    pattern = r"###\s*FILE:\s*(.+?)\s*\n```[^\n]*\n(.*?)```"
    matches = re.findall(pattern, agent_output, re.DOTALL)

    for file_path, code in matches:
        file_path = file_path.strip()
        code = code.strip()
        if file_path and code:
            files[file_path] = code

    return files


def write_test_files(repo_path: Path, test_files: dict[str, str]) -> list[str]:
    """Escreve os arquivos de teste no repositório e retorna lista de caminhos criados."""
    created_files: list[str] = []

    for relative_path, content in test_files.items():
        full_path = repo_path / relative_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding="utf-8")
        created_files.append(relative_path)

    return created_files


def run_git(args: list[str], repo_path: Path) -> subprocess.CompletedProcess:
    """Executa um comando git no repositório."""
    result = subprocess.run(
        ["git"] + args,
        capture_output=True,
        text=True,
        cwd=repo_path,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Erro git: {' '.join(args)}\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
    return result


def create_branch_and_commit(
    repo_path: Path,
    branch_name: str,
    test_files: list[str],
    commit_message: str,
) -> None:
    """Cria branch, adiciona arquivos de teste e faz commit."""
    run_git(["config", "user.name", "qagent[bot]"], repo_path)
    run_git(["config", "user.email", "qagent[bot]@users.noreply.github.com"], repo_path)

    run_git(["checkout", "-b", branch_name], repo_path)

    for file_path in test_files:
        run_git(["add", file_path], repo_path)

    run_git(["commit", "-m", commit_message], repo_path)


def push_branch(repo_path: Path, branch_name: str) -> None:
    """Faz push da branch para o remote origin."""
    run_git(["push", "origin", branch_name], repo_path)


def build_pr_body(
    qa_report: str,
    test_files: list[str],
    analyzed_files: list[str],
) -> str:
    """Monta o corpo do PR descrevendo os testes criados."""
    files_list = "\n".join(f"- `{f}`" for f in test_files)
    analyzed_list = "\n".join(f"- `{f}`" for f in analyzed_files)

    return f"""## 🧪 Testes Unitários Gerados Automaticamente

### Arquivos analisados
{analyzed_list}

### Arquivos de teste criados
{files_list}

### Motivação
Estes testes foram gerados automaticamente com base no relatório de QA produzido pelo agente de análise.
As sugestões de testes unitários do relatório foram transformadas em código executável para aumentar
a cobertura de testes e prevenir regressões.

### Base do relatório de QA
<details>
<summary>Clique para ver o relatório de QA completo</summary>

{qa_report}

</details>
"""


def open_pull_request(
    github_token: str,
    repo_full_name: str,
    branch_name: str,
    base_branch: str,
    title: str,
    body: str,
) -> str:
    """Abre um Pull Request no GitHub e retorna a URL."""
    gh = Github(github_token)
    repo = gh.get_repo(repo_full_name)

    pr = repo.create_pull(
        title=title,
        body=body,
        head=branch_name,
        base=base_branch,
    )

    return pr.html_url


def get_repo_full_name(repo_path: Path) -> str:
    """Obtém owner/repo do remote origin."""
    result = run_git(["remote", "get-url", "origin"], repo_path)
    url = result.stdout.strip()

    # SSH: git@github.com:owner/repo.git
    ssh_match = re.search(r"github\.com[:/](.+?)(?:\.git)?$", url)
    if ssh_match:
        return ssh_match.group(1)

    # HTTPS: https://github.com/owner/repo.git
    https_match = re.search(r"github\.com/(.+?)(?:\.git)?$", url)
    if https_match:
        return https_match.group(1)

    raise ValueError(f"Não foi possível extrair owner/repo da URL: {url}")


def get_current_branch(repo_path: Path) -> str:
    """Retorna o nome da branch atual."""
    result = run_git(["rev-parse", "--abbrev-ref", "HEAD"], repo_path)
    return result.stdout.strip()
