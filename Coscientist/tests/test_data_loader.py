import pandas as pd
import pytest

from coscientist.data.loader import CarrierDatasetLoader


def _make_df(n: int) -> pd.DataFrame:
    return pd.DataFrame({"idx": list(range(n)), "value": [f"v{i}" for i in range(n)]})


def test_split_rounds_last_round_absorbs_remainder():
    df = _make_df(1126)
    loader = CarrierDatasetLoader(csv_path="unused.csv")
    rounds = loader.split_rounds(df, round_size=20, n_rounds=50)

    assert len(rounds) == 50
    for r in rounds[:-1]:
        assert len(r) == 20
    # Last round absorbs the remainder: 1126 - 20*49 = 146
    assert len(rounds[-1]) == 1126 - 20 * 49
    assert sum(len(r) for r in rounds) == 1126


def test_split_rounds_exact_multiple():
    df = _make_df(1000)
    loader = CarrierDatasetLoader(csv_path="unused.csv")
    rounds = loader.split_rounds(df, round_size=20, n_rounds=50)
    assert len(rounds) == 50
    assert all(len(r) == 20 for r in rounds)


def test_split_rounds_raises_when_insufficient_data():
    df = _make_df(10)
    loader = CarrierDatasetLoader(csv_path="unused.csv")
    with pytest.raises(ValueError):
        loader.split_rounds(df, round_size=20, n_rounds=50)


def test_load_missing_csv_raises_helpful_error(tmp_path):
    loader = CarrierDatasetLoader(csv_path=tmp_path / "missing.csv")
    with pytest.raises(FileNotFoundError):
        loader.load()
