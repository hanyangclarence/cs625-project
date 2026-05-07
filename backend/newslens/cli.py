"""Command-line entrypoints.

Usage:
  python -m newslens.cli run --topic "Artemis II lunar flyby" --topic-id artemis-ii-lunar-flyby
  python -m newslens.cli run --topic-id artemis-ii-lunar-flyby --resume
  python -m newslens.cli audit --topic-id artemis-ii-lunar-flyby
  python -m newslens.cli ab --stage evidence --topic-id artemis-ii-lunar-flyby --variants v1,v2
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def _slugify(text: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", text.lower()).strip("-")
    return re.sub(r"-+", "-", s) or "topic"


def _add_run(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("run", help="Run the full pipeline for one topic.")
    p.add_argument("--topic", help="Free-text topic, e.g. 'Artemis II lunar flyby'")
    p.add_argument(
        "--topic-id",
        default=None,
        help="kebab-case id used as filename + stable Topic.id. Auto-derived from --topic if omitted.",
    )
    p.add_argument(
        "--max-sources",
        type=int,
        default=3,
        help="How many articles to ingest. Default 3 (cheapest); raise for fuller demos.",
    )
    p.add_argument("--out", type=Path, default=None, help="Output Topic JSON path")
    p.add_argument("--resume", action="store_true", help="Skip fetch+clean+verify; reuse workspaces")
    p.add_argument(
        "--verify",
        action="store_true",
        help="Opt INTO the ReAct verifier loop (web_search + Opus tool turns). Off by default to keep runs cheap.",
    )


def _add_audit(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("audit", help="Walk an expert through audit prompts.")
    p.add_argument("--topic-id", required=True)


def _add_ab(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("ab", help="Run A/B prompt variants for one stage.")
    p.add_argument("--topic-id", required=True)
    p.add_argument("--stage", required=True, help="e.g. evidence")
    p.add_argument("--variants", required=True, help="comma-separated variant ids")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="newslens")
    sub = parser.add_subparsers(dest="cmd", required=True)
    _add_run(sub)
    _add_audit(sub)
    _add_ab(sub)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.cmd == "run":
        from . import run as run_module

        if not args.topic and not args.topic_id:
            print("error: pass --topic, --topic-id, or both", file=sys.stderr)
            return 2
        topic_id = args.topic_id or _slugify(args.topic)
        topic = args.topic or topic_id.replace("-", " ").title()
        run_module.run(
            topic=topic,
            topic_id=topic_id,
            max_sources=args.max_sources,
            out_path=args.out,
            resume=args.resume,
            verify=args.verify,
        )
        return 0
    if args.cmd == "audit":
        from .feedback import audit_cli

        audit_cli.walk(topic_id=args.topic_id)
        return 0
    if args.cmd == "ab":
        from .ab import harness

        harness.run(
            topic_id=args.topic_id,
            stage=args.stage,
            variant_ids=[v.strip() for v in args.variants.split(",") if v.strip()],
        )
        return 0
    return 2


# Console-script entrypoints (declared in pyproject.toml).
def main_run() -> int:
    return main(["run", *sys.argv[1:]])


def main_audit() -> int:
    return main(["audit", *sys.argv[1:]])


def main_ab() -> int:
    return main(["ab", *sys.argv[1:]])


if __name__ == "__main__":
    sys.exit(main())
