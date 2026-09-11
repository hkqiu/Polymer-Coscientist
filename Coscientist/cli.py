#!/usr/bin/env python
"""Coscientist CLI entry point.

Usage:
    python cli.py run-training [--config PATH] [--resume] [--dry-run] [--max-rounds N]
"""
from __future__ import annotations

import logging
import subprocess
import sys
from pathlib import Path

import click

sys.path.insert(0, str(Path(__file__).resolve().parent))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("cli")


@click.group()
def cli() -> None:
    """Coscientist: iterative knowledge training for polymer mRNA vaccine carriers."""


@cli.command("run-training")
@click.option("--config", default=None, help="Path to the config file")
@click.option("--resume", is_flag=True, help="Continue iterating from an existing knowledge base")
@click.option("--dry-run", is_flag=True, help="Force the mock LLM client; no network access")
@click.option("--max-rounds", type=int, default=None, help="Debug option: only run the first N rounds")
def run_training(config: str | None, resume: bool, dry_run: bool, max_rounds: int | None) -> None:
    """Run the knowledge-iteration training loop."""
    script = Path(__file__).resolve().parent / "scripts" / "train_knowledge.py"
    cmd = [sys.executable, str(script)]
    if config:
        cmd += ["--config", config]
    if resume:
        cmd.append("--resume")
    if dry_run:
        cmd.append("--dry-run")
    if max_rounds:
        cmd += ["--max-rounds", str(max_rounds)]
    raise SystemExit(subprocess.call(cmd))


if __name__ == "__main__":
    cli()
