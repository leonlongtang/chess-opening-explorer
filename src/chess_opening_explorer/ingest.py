import re
from collections import defaultdict
from pathlib import Path

import chess
import chess.pgn
import pandas as pd

from chess_opening_explorer.aggregate_table import COLUMNS

RATING_BANDS = [
    ("under_1200", 0, 1200),
    ("1200_1599", 1200, 1600),
    ("1600_1999", 1600, 2000),
    ("2000_plus", 2000, None),
]

SPEEDS = ["bullet", "blitz", "rapid", "classical"]

RESULT_OUTCOME = {
    "1-0": "white_wins",
    "0-1": "black_wins",
    "1/2-1/2": "draws",
}

THEORY_DEPTH = 16


def rating_band(game_rating: float) -> str:
    for name, low, high in RATING_BANDS:
        if game_rating >= low and (high is None or game_rating < high):
            return name
    raise ValueError(f"no rating band matches {game_rating}")


def speed(event_header: str) -> str | None:
    lowered = event_header.lower()
    for name in SPEEDS:
        if re.search(rf"\b{name}\b", lowered):
            return name
    return None


def run(pgn_path: Path, out_path: Path) -> None:
    counts: dict[tuple[str, str, str, str], dict[str, int]] = defaultdict(
        lambda: {"white_wins": 0, "draws": 0, "black_wins": 0}
    )

    with open(pgn_path, encoding="utf-8") as pgn_file:
        while (game := chess.pgn.read_game(pgn_file)) is not None:
            outcome = RESULT_OUTCOME.get(game.headers.get("Result", ""))
            game_speed = speed(game.headers.get("Event", ""))
            white_elo = game.headers.get("WhiteElo", "")
            black_elo = game.headers.get("BlackElo", "")
            is_rated = "rated" in game.headers.get("Event", "").lower()
            is_standard = game.headers.get("Variant", "Standard") == "Standard"
            moves = list(game.mainline_moves())
            if (
                outcome is None
                or game_speed is None
                or not white_elo.isdigit()
                or not black_elo.isdigit()
                or not is_rated
                or not is_standard
                or len(moves) < THEORY_DEPTH
            ):
                continue
            band = rating_band((int(white_elo) + int(black_elo)) / 2)

            board = game.board()
            for move in moves[:THEORY_DEPTH]:
                position = board.epd()
                key = (position, move.uci(), band, game_speed)
                counts[key][outcome] += 1
                board.push(move)

    df = pd.DataFrame(
        [
            {
                "position": position,
                "continuation": continuation,
                "rating_band": band,
                "speed": spd,
                **outcomes,
            }
            for (position, continuation, band, spd), outcomes in counts.items()
        ],
        columns=COLUMNS,
    )
    df.to_parquet(out_path, index=False)
