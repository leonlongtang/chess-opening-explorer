import chess
import pandas as pd

from chess_opening_explorer.aggregate_table import COLUMNS
from chess_opening_explorer.ingest import RATING_BANDS, SPEEDS

OUTCOME_COLUMNS = [c for c in COLUMNS if c not in ("position", "continuation", "rating_band", "speed")]
VALID_RATING_BANDS = {name for name, _, _ in RATING_BANDS}


def _total_games(table: pd.DataFrame, position: str) -> int:
    rows = table[table["position"] == position]
    return int(rows[OUTCOME_COLUMNS].to_numpy().sum())


def explore(
    table: pd.DataFrame,
    line: list[str],
    rating_band: str | None = None,
    speed: str | None = None,
) -> dict:
    """Walk a Line and return the current Position's Continuations.

    `line` is a sequence of UCI moves from the starting Position. Raises
    ValueError if the Line is not legal or a filter value is unknown.
    """
    if rating_band is not None and rating_band not in VALID_RATING_BANDS:
        raise ValueError(f"unknown rating_band '{rating_band}'")
    if speed is not None and speed not in SPEEDS:
        raise ValueError(f"unknown speed '{speed}'")

    board = chess.Board()
    for move_uci in line:
        move = chess.Move.from_uci(move_uci)
        if move not in board.legal_moves:
            raise ValueError(f"illegal move '{move_uci}' in line")
        board.push(move)

    filtered = table
    if rating_band is not None:
        filtered = filtered[filtered["rating_band"] == rating_band]
    if speed is not None:
        filtered = filtered[filtered["speed"] == speed]

    start_games = _total_games(filtered, chess.Board().epd())
    position = board.epd()
    rows = filtered[filtered["position"] == position]
    total_games = int(rows[OUTCOME_COLUMNS].to_numpy().sum())
    reach_share = (total_games / start_games) if start_games else 0.0

    grouped = rows.groupby("continuation")[OUTCOME_COLUMNS].sum()

    continuations = []
    for move_uci, counts in grouped.iterrows():
        games = int(counts.sum())
        continuations.append(
            {
                "move": move_uci,
                "games": games,
                "share": (games / total_games) if total_games else 0.0,
                "outcome": {
                    outcome: {
                        "count": int(counts[outcome]),
                        "proportion": (counts[outcome] / games) if games else 0.0,
                    }
                    for outcome in OUTCOME_COLUMNS
                },
            }
        )
    continuations.sort(key=lambda c: c["games"], reverse=True)

    return {
        "position": position,
        "total_games": total_games,
        "reach_share": reach_share,
        "continuations": continuations,
    }
