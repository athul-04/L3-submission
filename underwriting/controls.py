from __future__ import annotations

import json
from pathlib import Path


class KillSwitch:
    def __init__(self, path: str | Path = "runtime/kill_switch.json") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.set(False)

    def set(self, enabled: bool) -> None:
        self.path.write_text(json.dumps({"enabled": enabled}, indent=2), encoding="utf-8")

    def enabled(self) -> bool:
        return json.loads(self.path.read_text(encoding="utf-8")).get("enabled", False)
