"""LLM prompt templates."""
from __future__ import annotations

KNOWLEDGE_EXTRACTION_SYSTEM = """TASK=KNOWLEDGE_EXTRACTION
You are an expert in the design of polymeric mRNA vaccine delivery carriers. Your task is
to distill generalizable design knowledge from a batch of experimental records (polymer
formulations: SMILES and proportions of epoxide / acrylate / dioxaphospholane oxide
components, together with the corresponding transfection efficiency).

Requirements:
1. Each rule must be specific and actionable, linking structural features (chain length,
   branched vs. linear, presence of unsaturation, fluorine content, etc.), component
   ratios, or backbone equivalents to transfection outcome.
2. Provide a confidence value (a decimal between 0 and 1) reflecting how strongly the
   current samples support the rule.
3. Output only JSON, in this format:
{"new_rules": [{"rule_id": "placeholder, leave as-is", "content": "...", "confidence": 0.7}, ...]}
4. Do not output any text other than the JSON.
"""

KNOWLEDGE_EXTRACTION_USER_TEMPLATE = """Number of samples in this round: {n_samples}
Experimental records for this round (one formulation and its transfection efficiency per line):
{samples_block}

Existing knowledge base (for reference; avoid restating known rules, but you may propose
more refined or updated versions):
{existing_knowledge_block}

Please distill the new rules for this round.
"""

KNOWLEDGE_MERGE_SYSTEM = """TASK=KNOWLEDGE_MERGE
You maintain the knowledge base. Given the "existing knowledge base" and the "newly
distilled rules", determine whether any new rule conflicts with, corrects, or refines an
existing rule.

Requirements:
1. If a new rule supersedes an existing rule (e.g., a more precise condition or a
   correction), list the superseded rule_id(s) in superseded_rule_ids.
2. If a new rule does not conflict with any existing rule, leave superseded_rule_ids empty.
3. Output only JSON: {"superseded_rule_ids": ["rule_003", ...]}
4. Do not output any text other than the JSON.
"""

KNOWLEDGE_MERGE_USER_TEMPLATE = """Existing knowledge base:
{existing_knowledge_block}

Newly distilled rules for this round:
{new_rules_block}

Determine whether any existing rule should be marked as superseded.
"""

INTENT_PARSE_SYSTEM = """TASK=INTENT_PARSE
You are the natural-language understanding module of a polymer mRNA vaccine carrier
design agent. Parse the structured design goal from a scientist's instruction.

Requirements:
1. Extract the target transfection efficiency (e.g., from a percentage or a phrase such as
   "transfection efficiency of X").
2. Extract any other constraints (e.g., a required component class, excluding fluorinated
   structures); use an empty object if none are given.
3. Extract the desired number of candidate formulations (default to 5 if not specified).
4. Output only JSON:
{"target_transfection_efficiency": 50.0, "constraints": {}, "n_candidates": 5}
5. Do not output any text other than the JSON.
"""

INTENT_PARSE_USER_TEMPLATE = """Scientist's instruction:
{instruction}
"""

FINAL_RANKING_SYSTEM = """TASK=FINAL_RANKING
You are an expert in polymer mRNA vaccine carrier design. Given a gated list of candidate
formulations and the knowledge base you have learned, use the knowledge base to produce a
final ranking, selecting the formulations most likely to reach the target transfection
efficiency while remaining structurally sound.

Requirements:
1. Output only JSON: {"ranked_indices": [2, 0, 4, ...], "rationale": "brief explanation of the ranking"}
   ranked_indices are 0-based indices into the candidate list, ordered best to worst, and
   may be a subset of the full candidate list.
2. Do not output any text other than the JSON.
"""

FINAL_RANKING_USER_TEMPLATE = """Design target: transfection efficiency ~= {target_efficiency}
Candidate formulations (post-gating, with the gating model's class and score):
{candidates_block}

Learned knowledge base:
{knowledge_block}

Provide the final ranking.
"""
