from pathlib import Path

import pandas as pd

COLUMNS = [
    "position",
    "continuation",
    "rating_band",
    "speed",
    "white_wins",
    "draws",
    "black_wins",
]


def load(path: Path) -> pd.DataFrame:
    return pd.read_parquet(path, columns=COLUMNS)
