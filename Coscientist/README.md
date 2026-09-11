# Coscientist

An **iterative knowledge-learning framework** for polymer mRNA vaccine carrier
design knowledge. It reproduces the core method used in a prior experimental
workflow: 1,126 polymer carrier experimental records are split into 50 rounds
of 20 records each, an LLM (MiMo-v2.5-pro) distills design knowledge round by
round, conflicts with the existing knowledge base are identified and merged,
and the result is written to `knowledge/knowledge.txt` (a rule-based format
that includes a confidence value).

## Project scope

**This repository releases the design and implementation of the 50-round
knowledge-iteration method itself.** It does not include the team's original
experimental dataset, nor does it involve polymer generation or a
performance-gating model — those are separate, proprietary assets and methods
outside the scope of this repository. This repository focuses specifically on
one method: how an LLM can continually distill, revise, and accumulate
structured design knowledge from a sequence of incoming experimental batches.

## Repository layout

```
Coscientist/
├── cli.py                     # CLI entry point (run-training)
├── main.py                    # Equivalent alias entry point
├── requirements.txt
├── pytest.ini
├── configs/
│   └── config.yaml            # Main configuration (LLM, training parameters)
├── data/
│   └── raw/                   # Experimental data CSV location (not versioned; see data/raw/README.md)
├── knowledge/
│   ├── knowledge.txt          # Final knowledge base produced by training (rule format)
│   └── checkpoints/           # Per-round knowledge snapshots (optional)
├── coscientist/                # Core Python package
│   ├── config.py               # YAML config loading
│   ├── llm/                    # LLM client wrappers (MiMo placeholder + mock) and prompt templates
│   ├── knowledge/               # Knowledge-base storage + knowledge distillation engine
│   └── data/                    # Experimental data loading and round splitting
├── scripts/
│   └── train_knowledge.py      # 50-round knowledge-iteration training script
└── tests/                       # Unit tests (all mock-based, no real API required)
```

## Quick start

```bash
pip install -r requirements.txt
```

By default, **the LLM API runs in mock mode**, so the full 50-round
knowledge-iteration training can be run end-to-end without real credentials.

```bash
python cli.py run-training --dry-run
# Equivalent to:
python scripts/train_knowledge.py --config configs/config.yaml --dry-run
```

- Place the experimental data CSV at `data/raw/carrier_dataset.csv` first (see
  `data/raw/README.md` for the expected column format), or edit
  `training.data_csv` in `configs/config.yaml` to point at the actual path.
- `--dry-run` forces the mock LLM and makes no network requests.
- `--resume` continues iterating from an existing `knowledge/knowledge.txt`.
- `--max-rounds N` is for debugging: it runs only the first N rounds.
- Training outputs:
  - `knowledge/knowledge.txt`: the final knowledge base (text format,
    `- [rule_xxx] content (confidence: 0.xx)`)
  - `knowledge/knowledge.jsonl`: the structured version
  - `knowledge/checkpoints/round_XX.txt`: a per-round knowledge snapshot (if
    `training.save_every_round: true`)

## Configuration (`configs/config.yaml`)

### LLM (MiMo-v2.5-pro)

```yaml
llm:
  base_url: "https://REPLACE_ME.example.com/v1"   # OpenAI-compatible /chat/completions endpoint
  api_key_env: "COSCIENTIST_LLM_API_KEY"           # Env var to read the key from
  mock: true                                       # true = no network calls, uses a rule-based mock response
```

To enable the real API:

```bash
export COSCIENTIST_LLM_API_KEY="sk-xxx"     # Windows: set COSCIENTIST_LLM_API_KEY=sk-xxx
```

and set `llm.mock` to `false` and `llm.base_url` to the real endpoint in
`configs/config.yaml`. **Never write a real key into a config file or commit
it to version control** — this project's `.gitignore` already excludes
`configs/secrets.yaml` and similar sensitive files by default; place real
configuration there and merge it in code, or always inject credentials via
environment variables.

### Training parameters

```yaml
training:
  data_csv: "data/raw/carrier_dataset.csv"   # 1,126 experimental records (user-supplied, not versioned)
  round_size: 20                              # Samples per round
  n_rounds: 50                                # Number of rounds (final round absorbs the remainder)
  shuffle: false                              # Whether to shuffle before splitting
  seed: 42
  knowledge_out: "knowledge/knowledge.txt"
  snapshot_dir: "knowledge/checkpoints"
  save_every_round: true
```

## Knowledge-base format

Each rule in `knowledge/knowledge.txt` follows this format:

```
- [rule_001] When the acrylate is a short linear alkyl ester (e.g., OCCCC), ... (confidence: 0.70)
```

`KnowledgeStore` in `coscientist/knowledge/store.py` handles loading, saving,
and merging in this format, and is compatible with knowledge bases produced
by prior experimental runs — `--resume` can continue directly from a historical
knowledge base.

## Training data format

The real column format of the experimental data CSV is documented in
`data/raw/README.md` — nine columns, covering epoxide/dioxaphospholane
oxide/acrylate component identifiers, their equivalents, the transfection
efficiency readout, and a three-class label. Missing values keep the literal
string `NAN`, and no cleaning is performed. The knowledge-distillation step
uses each row's raw text representation directly.

## Notes for public release

This repository is designed to be safely released publicly; **it contains no
sensitive content by default**:

- No real LLM API key or base URL (`configs/config.yaml` uses placeholders;
  real credentials are injected only via environment variables, and
  `.gitignore` excludes `configs/secrets.yaml` and similar local overrides).
- No real experimental data (`data/raw/*` is excluded via `.gitignore`; only
  the documentation file is kept).
- The LLM layer used for knowledge distillation and merging provides a
  deterministic mock implementation (`llm.mock: true`), so the full 50-round
  knowledge-iteration training can run without network access or real
  credentials.

Before release, it is recommended to:

1. Run `git status` / `git diff` to check for unintentionally added large
   files, secrets, or real data.
2. Search the repository for any leftover real API keys, internal server
   addresses, etc.
3. Confirm that `base_url` in `configs/config.yaml` is still the placeholder
   `REPLACE_ME`.

## Running the tests

```bash
pytest
```

All tests are based on `MockLLMClient` and require no network access or real
model files; they can run in any environment.
