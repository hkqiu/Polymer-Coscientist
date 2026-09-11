import json

from coscientist.llm.client import ChatMessage, MockLLMClient


def test_mock_llm_default_echo():
    client = MockLLMClient()
    resp = client.chat([ChatMessage("system", "no task marker"), ChatMessage("user", "hello")])
    data = json.loads(resp.content)
    assert data["note"] == "mock-llm-default-echo"


def test_mock_llm_knowledge_extraction_route():
    client = MockLLMClient()
    system = "TASK=KNOWLEDGE_EXTRACTION\n..."
    user = "Number of samples in this round: 20\n..."
    resp = client.chat([ChatMessage("system", system), ChatMessage("user", user)])
    data = json.loads(resp.content)
    assert "new_rules" in data
    assert len(data["new_rules"]) == 1
    assert 0.0 <= data["new_rules"][0]["confidence"] <= 1.0


def test_mock_llm_intent_parse_route_extracts_number():
    client = MockLLMClient()
    system = "TASK=INTENT_PARSE\n..."
    user = "Scientist's instruction:\nGenerate a polymer carrier with 65% transfection efficiency"
    resp = client.chat([ChatMessage("system", system), ChatMessage("user", user)])
    data = json.loads(resp.content)
    assert data["target_transfection_efficiency"] == 65.0


def test_mock_llm_final_ranking_route():
    client = MockLLMClient()
    system = "TASK=FINAL_RANKING\n..."
    resp = client.chat([ChatMessage("system", system), ChatMessage("user", "candidate list...")])
    data = json.loads(resp.content)
    assert "ranked_indices" in data
    assert "rationale" in data


def test_chat_text_helper():
    client = MockLLMClient()
    text = client.chat_text(system="TASK=INTENT_PARSE\n", user="target transfection efficiency 50%")
    data = json.loads(text)
    assert data["target_transfection_efficiency"] == 50.0
