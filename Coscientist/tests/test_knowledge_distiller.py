import pandas as pd

from coscientist.knowledge.distiller import KnowledgeDistiller
from coscientist.knowledge.store import KnowledgeStore
from coscientist.llm.client import MockLLMClient


def test_distiller_run_round_adds_rules_and_stamps_round():
    llm = MockLLMClient()
    distiller = KnowledgeDistiller(llm=llm)
    store = KnowledgeStore()
    df = pd.DataFrame({"epoxide_smiles": ["CC1OC1"], "transfection_efficiency": [55.0]})

    stats = distiller.run_round(df, store)

    assert stats["n_new_rules"] == 1
    assert stats["total_active_rules"] == 1
    assert len(store.active_rules()) == 1


def test_distiller_multiple_rounds_accumulate_rules():
    llm = MockLLMClient()
    distiller = KnowledgeDistiller(llm=llm)
    store = KnowledgeStore()
    df = pd.DataFrame({"epoxide_smiles": ["CC1OC1"] * 3, "transfection_efficiency": [55.0, 60.0, 40.0]})

    for _ in range(3):
        distiller.run_round(df, store)

    assert len(store.active_rules()) == 3
    ids = [r.rule_id for r in store.rules]
    assert ids == ["rule_001", "rule_002", "rule_003"]
