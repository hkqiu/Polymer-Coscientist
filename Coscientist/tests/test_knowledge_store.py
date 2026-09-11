import pytest

from coscientist.knowledge.store import KnowledgeRule, KnowledgeStore


def test_add_and_save_load_roundtrip(tmp_path):
    store = KnowledgeStore()
    store.add_rule(KnowledgeRule(rule_id="rule_001", content="Test rule A", confidence=0.7))
    store.add_rule(KnowledgeRule(rule_id="rule_002", content="Test rule B", confidence=0.55))

    out_path = tmp_path / "knowledge.txt"
    store.save_txt(out_path)

    loaded = KnowledgeStore.load_txt(out_path)
    assert len(loaded) == 2
    assert loaded.rules[0].rule_id == "rule_001"
    assert loaded.rules[0].content == "Test rule A"
    assert loaded.rules[0].confidence == pytest.approx(0.7)


def test_load_real_knowledge_format_sample(tmp_path):
    sample = (
        "- [rule_001] Short linear alkyl acrylates tend toward lower transfection efficiency. (confidence: 0.70)\n"
        "- [rule_002] Longer epoxide chain length tends toward higher transfection efficiency. (confidence: 0.80)\n"
        "\n"  # blank lines are skipped
        "not a valid rule line\n"  # unparsable lines are ignored without error
    )
    p = tmp_path / "knowledge.txt"
    p.write_text(sample, encoding="utf-8")

    store = KnowledgeStore.load_txt(p)
    assert len(store) == 2
    assert store.rules[1].confidence == pytest.approx(0.8)


def test_next_rule_id_increments():
    store = KnowledgeStore()
    store.add_rule(KnowledgeRule(rule_id="rule_003", content="x", confidence=0.5))
    store.add_rule(KnowledgeRule(rule_id="rule_007", content="y", confidence=0.5))
    assert store.next_rule_id() == "rule_008"


def test_mark_superseded_excludes_from_active():
    store = KnowledgeStore()
    store.add_rule(KnowledgeRule(rule_id="rule_001", content="old", confidence=0.5))
    store.add_rule(KnowledgeRule(rule_id="rule_002", content="new", confidence=0.6))
    store.mark_superseded(["rule_001"])
    active_ids = [r.rule_id for r in store.active_rules()]
    assert active_ids == ["rule_002"]


def test_load_missing_file_returns_empty_store(tmp_path):
    store = KnowledgeStore.load_txt(tmp_path / "does_not_exist.txt")
    assert len(store) == 0
