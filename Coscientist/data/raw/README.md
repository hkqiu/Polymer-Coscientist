# data/raw

Place the experimental data CSV in this directory, with the default file name
`carrier_dataset.csv` (the path can be changed via `training.data_csv` in
`configs/config.yaml`).

## Column format (9 columns)

| Header | Field | Notes |
| --- | --- | --- |
| `epoxide_component_id` | Epoxide component identifier | e.g. `E10`, `E3h`; missing values are `NAN` |
| `dioxaphospholane_oxide_component_id` | Dioxaphospholane oxide component identifier | e.g. `P1`; missing values are `NAN` |
| `acrylate_component_id` | Acrylate component identifier | e.g. `A16`; missing values are `NAN` |
| `pll_backbone_equivalent` | PLL-backbone equivalent | constant `1` in the reference dataset |
| `epoxide_equivalent` | Epoxide component equivalent | missing values are `NAN` |
| `dioxaphospholane_oxide_equivalent` | Dioxaphospholane oxide component equivalent | missing values are `NAN` |
| `acrylate_equivalent` | Acrylate component equivalent | missing values are `NAN` |
| `transfection_efficiency` | Transfection efficiency readout | raw RLU value |
| `class_label` | Three-class label | `0`, `1`, or `2` |

**Training data is not cleaned in any way** — missing components/equivalents
keep the literal string `NAN`, and the knowledge-distillation step uses each
row's raw text representation directly, consistent with the `NAN` semantics
used in the rule descriptions written to `knowledge.txt`.

`CarrierDatasetLoader` in `coscientist/data/loader.py` loads this CSV as-is,
and splits it into `training.n_rounds` rounds (default 50) of
`training.round_size` records each (default 20) for knowledge-iteration
training; the final round absorbs the remainder.

This directory's contents are excluded from version control by default via
`.gitignore` and are not published with the code — this repository releases
the design and implementation of the knowledge-iteration method itself, not
the team's original experimental dataset.
