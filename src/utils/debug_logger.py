from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


class DebugLogger:
    def __init__(self, root_dir: str | Path = "outputs/debug") -> None:
        self.root_dir = Path(root_dir)
        self.root_dir.mkdir(parents=True, exist_ok=True)
        self.run_dir: Path | None = None

    def start_run(self, file_path: str) -> Path:
        safe_name = file_path.replace("/", "__").replace("\\", "__")
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.run_dir = self.root_dir / f"{timestamp}_{safe_name}"
        self.run_dir.mkdir(parents=True, exist_ok=True)
        return self.run_dir

    def write_text(self, filename: str, content: str) -> Path:
        path = self._resolve(filename)
        path.write_text(content, encoding="utf-8")
        return path

    def write_json(self, filename: str, data: dict[str, Any]) -> Path:
        path = self._resolve(filename)
        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2, default=str),
            encoding="utf-8",
        )
        return path

    def append_log(self, filename: str, message: str) -> Path:
        path = self._resolve(filename)
        timestamp = datetime.now().strftime("%H:%M:%S")
        with path.open("a", encoding="utf-8") as handle:
            handle.write(f"[{timestamp}] {message}\n")
        return path

    def _resolve(self, filename: str) -> Path:
        if self.run_dir is None:
            self.start_run("ad-hoc")
        return self.run_dir / filename
