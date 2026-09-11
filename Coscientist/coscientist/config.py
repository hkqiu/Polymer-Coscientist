"""Configuration loading utilities."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _deep_get(d: dict, dotted_key: str, default: Any = None) -> Any:
    node = d
    for part in dotted_key.split("."):
        if not isinstance(node, dict) or part not in node:
            return default
        node = node[part]
    return node


@dataclass
class Config:
    raw: dict
    path: Path

    @classmethod
    def load(cls, path: str | Path | None = None) -> "Config":
        path = Path(path) if path else PROJECT_ROOT / "configs" / "config.yaml"
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")
        with open(path, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}
        return cls(raw=raw, path=path)

    def get(self, dotted_key: str, default: Any = None) -> Any:
        return _deep_get(self.raw, dotted_key, default)

    def resolve_path(self, dotted_key: str, default: str | None = None) -> Path:
        value = self.get(dotted_key, default)
        if value is None:
            raise KeyError(f"Missing required path config key: {dotted_key}")
        p = Path(value)
        return p if p.is_absolute() else (PROJECT_ROOT / p)

    def env_or(self, env_name: str, dotted_key_default: str | None = None) -> str | None:
        val = os.environ.get(env_name)
        if val:
            return val
        return dotted_key_default


def load_config(path: str | Path | None = None) -> Config:
    return Config.load(path)
