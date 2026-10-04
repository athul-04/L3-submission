from __future__ import annotations

import argparse
import json
from pathlib import Path

from .controls import KillSwitch
from .models import Application
from .service import DecisionService


def load_case(application_id: str) -> Application:
    path = Path("data/underwriting_cases.jsonl")
    for line in path.read_text(encoding="utf-8").splitlines():
        item = json.loads(line)
        if item["application_id"] == application_id:
            return Application.model_validate(item)
    raise SystemExit(f"Unknown application id: {application_id}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Brightmoor deterministic underwriting service")
    sub = parser.add_subparsers(dest="command", required=True)

    decide = sub.add_parser("decide")
    decide.add_argument("application_id")

    decide_json = sub.add_parser("decide-json")
    decide_json.add_argument("path")

    kill = sub.add_parser("kill-switch")
    kill.add_argument("state", choices=["on", "off"])

    issue = sub.add_parser("issue-decline")
    issue.add_argument("application_id")
    issue.add_argument("--reviewer", required=True)

    args = parser.parse_args()

    if args.command == "kill-switch":
        KillSwitch().set(args.state == "on")
        print(json.dumps({"kill_switch_enabled": args.state == "on"}, indent=2))
        return

    service = DecisionService()

    if args.command == "decide":
        application = load_case(args.application_id)
        print(json.dumps(service.decide(application).model_dump(mode="json"), indent=2))
    elif args.command == "decide-json":
        application = Application.model_validate_json(Path(args.path).read_text(encoding="utf-8"))
        print(json.dumps(service.decide(application).model_dump(mode="json"), indent=2))
    elif args.command == "issue-decline":
        print(json.dumps(service.issue_decline(args.application_id, args.reviewer), indent=2))


if __name__ == "__main__":
    main()
