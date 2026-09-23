from pathlib import Path

import chess
import pytest

from chess_opening_explorer import aggregate_table, ingest
from chess_opening_explorer.explorer import explore

FIXTURE = Path(__file__).parent / "fixtures" / "fixture.pgn"

# 1.d4 d5 2.c4 e6 3.Nc3 Nf6, G3's move order (G4 transposes into the same
# Position via 1.c4 e6 2.d4 d5 3.Nc3 Nf6).
TRANSPOSITION_LINE = ["d2d4", "d7d5", "c2c4", "e7e6", "b1c3", "g8f6"]


@pytest.fixture
def table(tmp_path):
    out_path = tmp_path / "aggregate.parquet"
    ingest.run(FIXTURE, out_path)
    return aggregate_table.load(out_path)


def test_starting_position_lists_continuations_ranked_by_games(table):
    result = explore(table, [])

    assert result["position"] == chess.Board().epd()
    assert result["total_games"] == 4
    assert result["reach_share"] == 1.0

    continuations = result["continuations"]
    assert len(continuations) == 3
    assert continuations[0]["move"] == "e2e4"
    assert continuations[0]["games"] == 2
    assert continuations[0]["share"] == 0.5
    assert continuations[0]["outcome"] == {
        "white_wins": {"count": 1, "proportion": 0.5},
        "draws": {"count": 1, "proportion": 0.5},
        "black_wins": {"count": 0, "proportion": 0.0},
    }

    by_move = {c["move"]: c for c in continuations[1:]}
    assert by_move["d2d4"]["games"] == 1
    assert by_move["d2d4"]["share"] == 0.25
    assert by_move["d2d4"]["outcome"]["black_wins"] == {"count": 1, "proportion": 1.0}
    assert by_move["c2c4"]["games"] == 1
    assert by_move["c2c4"]["share"] == 0.25
    assert by_move["c2c4"]["outcome"]["white_wins"] == {"count": 1, "proportion": 1.0}


def test_rating_band_and_speed_filter_narrows_results(table):
    result = explore(table, [], rating_band="1200_1599", speed="blitz")

    assert result["total_games"] == 2
    assert result["reach_share"] == 1.0
    moves = {c["move"] for c in result["continuations"]}
    assert moves == {"e2e4", "c2c4"}


def test_advancing_a_ply_returns_the_next_position(table):
    result = explore(table, ["e2e4"])

    board = chess.Board()
    board.push_uci("e2e4")
    assert result["position"] == board.epd()
    assert result["total_games"] == 2
    assert result["reach_share"] == 0.5
    assert result["continuations"] == [
        {
            "move": "e7e5",
            "games": 2,
            "share": 1.0,
            "outcome": {
                "white_wins": {"count": 1, "proportion": 0.5},
                "draws": {"count": 1, "proportion": 0.5},
                "black_wins": {"count": 0, "proportion": 0.0},
            },
        }
    ]


def test_transposed_lines_reach_one_pooled_position(table):
    result = explore(table, TRANSPOSITION_LINE)

    assert result["total_games"] == 2
    assert result["reach_share"] == 0.5
    assert result["continuations"] == [
        {
            "move": "c1g5",
            "games": 2,
            "share": 1.0,
            "outcome": {
                "white_wins": {"count": 1, "proportion": 0.5},
                "draws": {"count": 0, "proportion": 0.0},
                "black_wins": {"count": 1, "proportion": 0.5},
            },
        }
    ]


def test_illegal_move_is_rejected(table):
    with pytest.raises(ValueError):
        explore(table, ["e2e5"])


def test_unknown_rating_band_is_rejected(table):
    with pytest.raises(ValueError):
        explore(table, [], rating_band="1200-1599")


def test_unknown_speed_is_rejected(table):
    with pytest.raises(ValueError):
        explore(table, [], speed="Blitz")
