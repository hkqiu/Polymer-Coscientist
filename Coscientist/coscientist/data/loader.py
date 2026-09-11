"""Experimental dataset loading and round-wise splitting.

Column names are not auto-detected or semantically normalized: the raw CSV
(origin_data.csv format, see data/raw/README.md) is loaded as-is, missing values
keep the literal "NAN" string, and training/distillation use these raw columns
directly. Use column_map for explicit renaming if column names differ from the
expected default.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass
class CarrierDatasetLoader:
    csv_path: str | Path
    column_map: dict[str, str] | None = None

    def load(self) -> pd.DataFrame:
        path = Path(self.csv_path)
        if not path.exists():
            raise FileNotFoundError(
                f"Training data not found: {path}\n"
                "Place the experimental CSV at this path, or update training.data_csv "
                "in configs/config.yaml."
            )
        df = pd.read_csv(path)
        if self.column_map:
            df = df.rename(columns=self.column_map)
        return df

    def split_rounds(self, df: pd.DataFrame, round_size: int, n_rounds: int) -> list[pd.DataFrame]:
        n = len(df)
        rows_needed_before_last = round_size * (n_rounds - 1)
        if n < rows_needed_before_last:
            raise ValueError(
                f"Insufficient data: {n} record(s) available, cannot split "
                f"{n_rounds - 1} complete round(s) of {round_size} records each."
            )
        chunks = []
        for i in range(n_rounds - 1):
            start = i * round_size
            end = start + round_size
            chunks.append(df.iloc[start:end].reset_index(drop=True))
        last_start = rows_needed_before_last
        chunks.append(df.iloc[last_start:n].reset_index(drop=True))
        return chunks
