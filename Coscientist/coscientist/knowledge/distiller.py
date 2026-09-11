"""Knowledge distillation engine: sends a batch of experimental records and the
existing knowledge base to the LLM, then merges the returned rules."""
from __future__ import annotations

import json
import logging
import re

import pandas as pd

from coscientist.knowledge.store import KnowledgeRule, KnowledgeStore
from coscientist.llm.client import BaseLLMClient, ChatMessage
from coscientist.llm.prompts import (
    KNOWLEDGE_EXTRACTION_SYSTEM,
    KNOWLEDGE_EXTRACTION_USER_TEMPLATE,
    KNOWLEDGE_MERGE_SYSTEM,
    KNOWLEDGE_MERGE_USER_TEMPLATE,
)

logger = logging.getLogger(__name__)

_JSON_BLOCK_RE = re.compile(r"\{.*\}", re.DOTALL)


def _extract_json(text: str) -> dict:
    text = text.strip()
    text = re.sub(r"^```(json)?", "", text).strip()
    text = re.sub(r"```$", "", text).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        m = _JSON_BLOCK_RE.search(text)
        if not m:
            raise
        return json.loads(m.group(0))


def _rows_to_text_block(df: pd.DataFrame) -> str:
    lines = []
    for i, row in df.iterrows():
        lines.append(f"[{i}] " + " | ".join(f"{c}={row[c]}" for c in df.columns))
    return "\n".join(lines)


class KnowledgeDistiller:
    def __init__(self, llm: BaseLLMClient, temperature: float = 0.3, max_tokens: int = 2048) -> None:
        self.llm = llm
        self.temperature = temperature
        self.max_tokens = max_tokens

    def extract_new_rules(
        self, round_df: pd.DataFrame, store: KnowledgeStore, max_context_rules: int = 40
    ) -> list[KnowledgeRule]:
        user_prompt = KNOWLEDGE_EXTRACTION_USER_TEMPLATE.format(
            n_samples=len(round_df),
            samples_block=_rows_to_text_block(round_df),
            existing_knowledge_block=store.as_prompt_block(max_rules=max_context_rules),
        )
        resp = self.llm.chat(
            [ChatMessage("system", KNOWLEDGE_EXTRACTION_SYSTEM), ChatMessage("user", user_prompt)],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        try:
            data = _extract_json(resp.content)
        except (json.JSONDecodeError, AttributeError) as e:
            logger.warning(
                "Failed to parse knowledge-extraction response; skipping new rules this round. "
                "Error: %s\nRaw response: %.500s",
                e,
                resp.content,
            )
            return []

        new_rules: list[KnowledgeRule] = []
        for item in data.get("new_rules", []):
            content = (item.get("content") or "").strip()
            if not content:
                continue
            confidence = float(item.get("confidence", 0.5))
            confidence = min(max(confidence, 0.0), 1.0)
            rule_id = store.next_rule_id()
            rule = KnowledgeRule(rule_id=rule_id, content=content, confidence=confidence)
            store.add_rule(rule)
            new_rules.append(rule)
        return new_rules

    def merge_and_resolve_conflicts(
        self, store: KnowledgeStore, new_rules: list[KnowledgeRule], max_context_rules: int = 40
    ) -> list[str]:
        if not new_rules:
            return []
        existing = [r for r in store.active_rules() if r.rule_id not in {nr.rule_id for nr in new_rules}]
        if not existing:
            return []
        existing_block = "\n".join(r.to_line() for r in existing[-max_context_rules:])
        new_block = "\n".join(r.to_line() for r in new_rules)
        user_prompt = KNOWLEDGE_MERGE_USER_TEMPLATE.format(
            existing_knowledge_block=existing_block, new_rules_block=new_block
        )
        resp = self.llm.chat(
            [ChatMessage("system", KNOWLEDGE_MERGE_SYSTEM), ChatMessage("user", user_prompt)],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        try:
            data = _extract_json(resp.content)
        except (json.JSONDecodeError, AttributeError) as e:
            logger.warning("Failed to parse knowledge-merge response; no rules marked superseded. Error: %s", e)
            return []

        superseded = list(data.get("superseded_rule_ids", []) or [])
        if superseded:
            store.mark_superseded(superseded)
            logger.info("Marked %d existing rule(s) as superseded: %s", len(superseded), superseded)
        return superseded

    def run_round(self, round_df: pd.DataFrame, store: KnowledgeStore) -> dict:
        new_rules = self.extract_new_rules(round_df, store)
        superseded = self.merge_and_resolve_conflicts(store, new_rules)
        return {
            "n_samples": len(round_df),
            "n_new_rules": len(new_rules),
            "new_rule_ids": [r.rule_id for r in new_rules],
            "superseded_rule_ids": superseded,
            "total_active_rules": len(store.active_rules()),
        }
