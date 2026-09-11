#!/usr/bin/env python
"""Knowledge-iteration training script.

Usage:
    python scripts/train_knowledge.py --config configs/config.yaml
    python scripts/train_knowledge.py --resume
    python scripts/train_knowledge.py --dry-run
"""
from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from coscientist.config import load_config  # noqa: E402
from coscientist.data.loader import CarrierDatasetLoader  # noqa: E402
from coscientist.knowledge.distiller import KnowledgeDistiller  # noqa: E402
from coscientist.knowledge.store import KnowledgeStore  # noqa: E402
from coscientist.llm.factory import build_llm_client  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("train_knowledge")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Iterative knowledge training")
    parser.add_argument("--config", default=None, help="Path to the config file (default: configs/config.yaml)")
    parser.add_argument("--resume", action="store_true", help="Continue iterating from the existing knowledge_out file")
    parser.add_argument("--dry-run", action="store_true", help="Force the mock LLM client")
    parser.add_argument("--max-rounds", type=int, default=None, help="Debug option: only run the first N rounds")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = load_config(args.config)

    if args.dry_run:
        cfg.raw.setdefault("llm", {})["mock"] = True

    data_csv = cfg.resolve_path("training.data_csv")
    round_size = int(cfg.get("training.round_size", 20))
    n_rounds = int(cfg.get("training.n_rounds", 50))
    shuffle = bool(cfg.get("training.shuffle", False))
    seed = int(cfg.get("training.seed", 42))
    knowledge_out = cfg.resolve_path("training.knowledge_out")
    snapshot_dir = cfg.resolve_path("training.snapshot_dir")
    save_every_round = bool(cfg.get("training.save_every_round", True))

    if args.max_rounds:
        n_rounds = min(n_rounds, args.max_rounds)

    logger.info("Loading data: %s", data_csv)
    loader = CarrierDatasetLoader(csv_path=data_csv)
    df = loader.load()
    if shuffle:
        df = df.sample(frac=1.0, random_state=seed).reset_index(drop=True)
    logger.info(
        "Dataset size: %d records, split into %d round(s) of %d records each "
        "(the final round absorbs the remainder).",
        len(df),
        n_rounds,
        round_size,
    )

    rounds = loader.split_rounds(df, round_size=round_size, n_rounds=n_rounds)

    store = KnowledgeStore.load_txt(knowledge_out) if args.resume else KnowledgeStore()
    if args.resume:
        logger.info("Resumed knowledge base from %s with %d existing rule(s).", knowledge_out, len(store))

    llm = build_llm_client(cfg)
    distiller = KnowledgeDistiller(
        llm=llm,
        temperature=float(cfg.get("llm.temperature", 0.3)),
        max_tokens=int(cfg.get("llm.max_tokens", 2048)),
    )

    t0 = time.time()
    for i, round_df in enumerate(rounds, start=1):
        if len(round_df) == 0:
            logger.warning("Round %d has no samples, skipping.", i)
            continue
        stats = distiller.run_round(round_df, store)
        for r in store.rules[-stats["n_new_rules"]:]:
            r.created_round = i
        logger.info(
            "Round %d/%d | samples=%d | new_rules=%d | superseded=%d | active_rules=%d",
            i,
            len(rounds),
            stats["n_samples"],
            stats["n_new_rules"],
            len(stats["superseded_rule_ids"]),
            stats["total_active_rules"],
        )
        if save_every_round:
            snapshot_path = snapshot_dir / f"round_{i:02d}.txt"
            store.save_txt(snapshot_path)

    store.save_txt(knowledge_out)
    store.save_jsonl(knowledge_out.with_suffix(".jsonl"))
    elapsed = time.time() - t0
    logger.info(
        "Training complete: %d round(s) in %.1fs. Final knowledge base: %s (%d active rule(s)).",
        len(rounds),
        elapsed,
        knowledge_out,
        len(store.active_rules()),
    )


if __name__ == "__main__":
    main()
