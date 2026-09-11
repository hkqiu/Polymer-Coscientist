"""MiMo-v2.5-pro LLM client wrapper (OpenAI-compatible chat interface)."""
from __future__ import annotations

import json
import logging
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class ChatMessage:
    role: str
    content: str

    def to_dict(self) -> dict:
        return {"role": self.role, "content": self.content}


@dataclass
class LLMResponse:
    content: str
    raw: dict = field(default_factory=dict)
    model: str = ""
    usage: dict = field(default_factory=dict)


class BaseLLMClient(ABC):
    @abstractmethod
    def chat(
        self,
        messages: list[ChatMessage],
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        ...

    def chat_text(self, system: str, user: str, **kwargs: Any) -> str:
        messages = [ChatMessage("system", system), ChatMessage("user", user)]
        return self.chat(messages, **kwargs).content


class MiMoClient(BaseLLMClient):
    def __init__(
        self,
        base_url: str,
        api_key: str,
        model: str = "MiMo-v2.5-pro",
        timeout_s: float = 60.0,
    ) -> None:
        if not base_url or "REPLACE_ME" in base_url:
            raise ValueError(
                "No valid llm.base_url configured. Set a real endpoint in configs/config.yaml "
                "or via environment variables, or set llm.mock to true to use the mock client."
            )
        if not api_key:
            raise ValueError(
                "No API key provided. Set the environment variable named by llm.api_key_env "
                "in configs/config.yaml, or set llm.mock to true to use the mock client."
            )
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.timeout_s = timeout_s

    def chat(
        self,
        messages: list[ChatMessage],
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        import requests

        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [m.to_dict() for m in messages],
            "temperature": temperature if temperature is not None else 0.3,
            "max_tokens": max_tokens if max_tokens is not None else 2048,
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=self.timeout_s)
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        return LLMResponse(
            content=content,
            raw=data,
            model=data.get("model", self.model),
            usage=data.get("usage", {}),
        )


class MockLLMClient(BaseLLMClient):
    def __init__(self, model: str = "MiMo-v2.5-pro-mock") -> None:
        self.model = model
        self._rule_counter = 0

    def chat(
        self,
        messages: list[ChatMessage],
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        system = next((m.content for m in messages if m.role == "system"), "")
        user = next((m.content for m in messages if m.role == "user"), "")
        content = self._route(system, user)
        return LLMResponse(content=content, raw={"mock": True}, model=self.model)

    def _route(self, system: str, user: str) -> str:
        haystack = f"{system}\n{user}"
        if "TASK=KNOWLEDGE_EXTRACTION" in haystack:
            return self._mock_knowledge_extraction(user)
        if "TASK=KNOWLEDGE_MERGE" in haystack:
            return self._mock_knowledge_merge(user)
        if "TASK=INTENT_PARSE" in haystack:
            return self._mock_intent_parse(user)
        if "TASK=FINAL_RANKING" in haystack:
            return self._mock_final_ranking(user)
        return json.dumps({"note": "mock-llm-default-echo", "echo": user[:200]}, ensure_ascii=False)

    def _mock_knowledge_extraction(self, user: str) -> str:
        self._rule_counter += 1
        rid = f"rule_mock_{self._rule_counter:03d}"
        m = re.search(r"Number of samples in this round:\s*(\d+)", user)
        n = m.group(1) if m else "N"
        rules = [
            {
                "rule_id": rid,
                "content": (
                    f"[mock] Placeholder trend between components, ratios, and transfection "
                    f"efficiency observed across {n} samples in this round "
                    "(placeholder rule; a real run would use MiMo-v2.5-pro)."
                ),
                "confidence": 0.6,
            }
        ]
        return json.dumps({"new_rules": rules}, ensure_ascii=False)

    def _mock_knowledge_merge(self, user: str) -> str:
        return json.dumps({"updated_rules": [], "superseded_rule_ids": []}, ensure_ascii=False)

    def _mock_intent_parse(self, user: str) -> str:
        m = re.search(r"(\d+(?:\.\d+)?)\s*%?", user)
        target = float(m.group(1)) if m else 50.0
        return json.dumps(
            {
                "target_transfection_efficiency": target,
                "constraints": {},
                "n_candidates": 5,
            },
            ensure_ascii=False,
        )

    def _mock_final_ranking(self, user: str) -> str:
        return json.dumps(
            {"ranked_indices": [], "rationale": "[mock] No knowledge-based re-ranking applied; ordered by gating score."},
            ensure_ascii=False,
        )
