from __future__ import annotations

from pathlib import Path
from typing import Any, List, Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field, PrivateAttr

from src.utils.debug_logger import DebugLogger


IGNORED_PARTS = {".git", "__pycache__", "node_modules", ".venv", "outputs"}
MAX_FILE_PREVIEW_CHARS = 4000
MAX_SEARCH_PREVIEW = 20


class ReadFileInput(BaseModel):
    file_path: str = Field(
        ...,
        description=(
            "Caminho relativo do arquivo a ser lido. Use caminhos exatos como "
            "src/services/user_service.py ou tests/test_user_service.py."
        ),
    )


class SearchInRepoInput(BaseModel):
    term: str = Field(
        ...,
        description=(
            "Termo curto e exato a ser buscado no repositório, como nome de função, "
            "classe, import, rota ou campo alterado."
        ),
    )
    max_results: int = Field(
        8,
        description="Quantidade máxima de arquivos retornados. Prefira poucos resultados relevantes.",
        ge=1,
        le=20,
    )


class ListFilesInRepoInput(BaseModel):
    extension_filter: str | None = Field(
        default=None,
        description=(
            "Extensão opcional para filtrar arquivos, exemplo: .py, .ts ou .tsx. "
            "Use apenas quando realmente precisar explorar a estrutura do repositório."
        ),
    )
    max_results: int = Field(
        50,
        description="Quantidade máxima de arquivos retornados.",
        ge=1,
        le=200,
    )


class FindRelatedTestFilesInput(BaseModel):
    changed_file: str = Field(
        ...,
        description=(
            "Arquivo alterado para buscar testes relacionados. Informe o caminho relativo "
            "completo do arquivo alterado."
        ),
    )


class DebuggableRepoTool(BaseTool):
    _repo_path: Path = PrivateAttr()
    _debug_logger: DebugLogger | None = PrivateAttr(default=None)

    def __init__(self, repo_path: Path, debug_logger: DebugLogger | None = None, **kwargs: Any):
        super().__init__(**kwargs)
        self._repo_path = repo_path
        self._debug_logger = debug_logger

    def _log(self, event: str, payload: dict[str, Any]) -> None:
        if not self._debug_logger:
            return
        self._debug_logger.append_log(
            "05_tool_calls.log",
            f"{event} | {self.name} | {payload}",
        )

    def _should_skip(self, path: Path) -> bool:
        return any(part in IGNORED_PARTS for part in path.parts)


class ReadFileTool(DebuggableRepoTool):
    name: str = "read_file"
    description: str = (
        "Lê o conteúdo de um arquivo do repositório alvo a partir do caminho relativo. "
        "Use esta tool quando precisar de evidência direta em um arquivo específico."
    )
    args_schema: Type[BaseModel] = ReadFileInput

    def _run(self, file_path: str) -> str:
        self._log("START", {"file_path": file_path})
        path = self._repo_path / file_path

        if not path.exists():
            message = f"Arquivo não encontrado: {file_path}"
            self._log("ERROR", {"file_path": file_path, "error": message})
            return message

        if not path.is_file():
            message = f"Caminho não é um arquivo: {file_path}"
            self._log("ERROR", {"file_path": file_path, "error": message})
            return message

        try:
            content = path.read_text(encoding="utf-8")
            if len(content) > MAX_FILE_PREVIEW_CHARS:
                content = (
                    content[:MAX_FILE_PREVIEW_CHARS]
                    + "\n\n[TRUNCADO] Conteúdo reduzido para evitar excesso de contexto."
                )
            self._log(
                "SUCCESS",
                {
                    "file_path": file_path,
                    "returned_chars": len(content),
                    "preview": content[:300],
                },
            )
            return content
        except Exception as error:
            message = f"Erro ao ler arquivo {file_path}: {error}"
            self._log("ERROR", {"file_path": file_path, "error": repr(error)})
            return message


class SearchInRepoTool(DebuggableRepoTool):
    name: str = "search_in_repo"
    description: str = (
        "Busca um termo no repositório e retorna caminhos relativos de arquivos onde o termo foi encontrado. "
        "Use para localizar símbolos, imports, funções, classes, rotas e campos relacionados à mudança."
    )
    args_schema: Type[BaseModel] = SearchInRepoInput

    def _run(self, term: str, max_results: int = 8) -> str:
        self._log("START", {"term": term, "max_results": max_results})
        matches: List[str] = []

        for path in self._repo_path.rglob("*"):
            if not path.is_file() or self._should_skip(path):
                continue

            try:
                content = path.read_text(encoding="utf-8")
            except Exception:
                continue

            if term in content:
                relative_path = str(path.relative_to(self._repo_path))
                matches.append(relative_path)

            if len(matches) >= max_results:
                break

        if not matches:
            self._log("SUCCESS", {"term": term, "matches": 0})
            return "Nenhum arquivo encontrado."

        result = "\n".join(matches[:MAX_SEARCH_PREVIEW])
        self._log(
            "SUCCESS",
            {
                "term": term,
                "matches": len(matches),
                "preview": matches[:5],
            },
        )
        return result


class ListFilesInRepoTool(DebuggableRepoTool):
    name: str = "list_files_in_repo"
    description: str = (
        "Lista arquivos do repositório, com filtro opcional por extensão. "
        "Use apenas quando precisar descobrir a estrutura do projeto."
    )
    args_schema: Type[BaseModel] = ListFilesInRepoInput

    def _run(self, extension_filter: str | None = None, max_results: int = 50) -> str:
        self._log("START", {"extension_filter": extension_filter, "max_results": max_results})
        files: List[str] = []

        for path in self._repo_path.rglob("*"):
            if not path.is_file() or self._should_skip(path):
                continue

            if extension_filter and path.suffix != extension_filter:
                continue

            files.append(str(path.relative_to(self._repo_path)))

            if len(files) >= max_results:
                break

        if not files:
            self._log("SUCCESS", {"extension_filter": extension_filter, "files": 0})
            return "Nenhum arquivo encontrado."

        result = "\n".join(files)
        self._log(
            "SUCCESS",
            {
                "extension_filter": extension_filter,
                "files": len(files),
                "preview": files[:5],
            },
        )
        return result


class FindRelatedTestFilesTool(DebuggableRepoTool):
    name: str = "find_related_test_files"
    description: str = (
        "Procura arquivos de teste relacionados ao arquivo alterado com base no nome. "
        "Use para descobrir cobertura existente antes de sugerir novos testes."
    )
    args_schema: Type[BaseModel] = FindRelatedTestFilesInput

    def _run(self, changed_file: str) -> str:
        self._log("START", {"changed_file": changed_file})
        changed_path = Path(changed_file)
        stem = changed_path.stem.lower()

        related: List[str] = []

        for path in self._repo_path.rglob("*"):
            if not path.is_file() or self._should_skip(path):
                continue

            name = path.name.lower()

            if stem in name and ("test" in name or "spec" in name):
                related.append(str(path.relative_to(self._repo_path)))

        if not related:
            self._log("SUCCESS", {"changed_file": changed_file, "related": 0})
            return "Nenhum teste relacionado encontrado."

        result = "\n".join(related[:20])
        self._log(
            "SUCCESS",
            {
                "changed_file": changed_file,
                "related": len(related),
                "preview": related[:5],
            },
        )
        return result
