"""Knowledge-base storage: rule-based knowledge in the knowledge.txt format."""
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path

_LINE_PATTERN = re.compile(
    r"^-\s*\[(?P<rule_id>[^\]]+)\]\s*(?P<content>.*?)\s*\(confidence[:：]\s*(?P<confidence>[0-9.]+)\)\s*$"
)


@dataclass
class KnowledgeRule:
    rule_id: str
    content: str
    confidence: float = 0.5
    created_round: int = 0
    status: str = "active"  # active | superseded

    def to_line(self) -> str:
        return f"- [{self.rule_id}] {self.content} (confidence: {self.confidence:.2f})"

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class KnowledgeStore:
    rules: list[KnowledgeRule] = field(default_factory=list)

    @classmethod
    def load_txt(cls, path: str | Path) -> "KnowledgeStore":
        path = Path(path)
        store = cls()
        if not path.exists():
            return store
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                m = _LINE_PATTERN.match(line)
                if not m:
                    continue
                store.rules.append(
                    KnowledgeRule(
                        rule_id=m.group("rule_id"),
                        content=m.group("content"),
                        confidence=float(m.group("confidence")),
                    )
                )
        return store

    @classmethod
    def load_jsonl(cls, path: str | Path) -> "KnowledgeStore":
        path = Path(path)
        store = cls()
        if not path.exists():
            return store
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                d = json.loads(line)
                store.rules.append(KnowledgeRule(**d))
        return store

    def add_rule(self, rule: KnowledgeRule) -> None:
        self.rules.append(rule)

    def add_rules(self, rules: list[KnowledgeRule]) -> None:
        self.rules.extend(rules)

    def mark_superseded(self, rule_ids: list[str]) -> None:
        for r in self.rules:
            if r.rule_id in rule_ids:
                r.status = "superseded"

    def active_rules(self) -> list[KnowledgeRule]:
        return [r for r in self.rules if r.status == "active"]

    def next_rule_id(self, prefix: str = "rule") -> str:
        nums = []
        for r in self.rules:
            m = re.match(rf"{prefix}_(\d+)", r.rule_id)
            if m:
                nums.append(int(m.group(1)))
        n = (max(nums) + 1) if nums else 1
        return f"{prefix}_{n:03d}"

    def save_txt(self, path: str | Path, only_active: bool = True) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        rules = self.active_rules() if only_active else self.rules
        with open(path, "w", encoding="utf-8") as f:
            for r in rules:
                f.write(r.to_line() + "\n")

    def save_jsonl(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            for r in self.rules:
                f.write(json.dumps(r.to_dict(), ensure_ascii=False) + "\n")

    def as_prompt_block(self, max_rules: int | None = None) -> str:
        rules = self.active_rules()
        if max_rules:
            rules = rules[-max_rules:]
        if not rules:
            return "(knowledge base is currently empty)"
        return "\n".join(r.to_line() for r in rules)

    def __len__(self) -> int:
        return len(self.rules)
