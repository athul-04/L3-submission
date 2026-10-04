from __future__ import annotations

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import json
from pathlib import Path

from underwriting.llm_benchmark import run_benchmark
from underwriting.models import Application


def load_cases() -> list[Application]:
    return [
        Application.model_validate_json(line)
        for line in Path("data/underwriting_cases.jsonl").read_text(encoding="utf-8").splitlines()
    ]


def main() -> None:
    result = run_benchmark(load_cases())
    path = Path("artifacts/routing_benchmark.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
