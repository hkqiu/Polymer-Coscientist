"""Builds an LLM client (real or mock) from configuration."""
from __future__ import annotations

import logging
import os

from coscientist.config import Config
from coscientist.llm.client import BaseLLMClient, MiMoClient, MockLLMClient

logger = logging.getLogger(__name__)


def build_llm_client(cfg: Config) -> BaseLLMClient:
    mock = bool(cfg.get("llm.mock", True))
    model = cfg.get("llm.model", "MiMo-v2.5-pro")

    if mock:
        logger.info("LLM client: using MockLLMClient (llm.mock=true).")
        return MockLLMClient(model=f"{model}-mock")

    base_url = cfg.get("llm.base_url", "")
    api_key_env = cfg.get("llm.api_key_env", "COSCIENTIST_LLM_API_KEY")
    api_key = os.environ.get(api_key_env, "")
    timeout_s = float(cfg.get("llm.timeout_s", 60))

    try:
        return MiMoClient(base_url=base_url, api_key=api_key, model=model, timeout_s=timeout_s)
    except ValueError as e:
        logger.warning("Failed to initialize the real LLM client (%s); falling back to MockLLMClient.", e)
        return MockLLMClient(model=f"{model}-mock")
