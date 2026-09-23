from pathlib import Path

import chess

from chess_opening_explorer import aggregate_table, ingest

FIXTURE = Path(__file__).parent / "fixtures" / "fixture.pgn"

START_POSITION = chess.Board().epd()


def _rows(df, **filters):
    mask = None
    for key, value in filters.items():
        col = df[key] == value
        mask = col if mask is None else (mask & col)
    return df[mask] if mask is not None else df


def test_eligible_games_recorded_with_correct_band_and_speed(tmp_path):
    out_path = tmp_path / "aggregate.parquet"

    ingest.run(FIXTURE, out_path)
    table = aggregate_table.load(out_path)

    # G1: 1500/1500 avg -> 1200_1599, blitz, White win
    row = _rows(
        table,
        position=START_POSITION,
        continuation="e2e4",
        rating_band="1200_1599",
        speed="blitz",
    )
    assert len(row) == 1
    assert row.iloc[0][["white_wins", "draws", "black_wins"]].tolist() == [1, 0, 0]

    # G2: 2100/2050 avg -> 2000_plus, rapid, draw
    row = _rows(
        table,
        position=START_POSITION,
        continuation="e2e4",
        rating_band="2000_plus",
        speed="rapid",
    )
    assert len(row) == 1
    assert row.iloc[0][["white_wins", "draws", "black_wins"]].tolist() == [0, 1, 0]

    # G3: 1000/1100 avg -> under_1200, bullet, Black win, starts 1.d4
    row = _rows(
        table,
        position=START_POSITION,
        continuation="d2d4",
        rating_band="under_1200",
        speed="bullet",
    )
    assert len(row) == 1
    assert row.iloc[0][["white_wins", "draws", "black_wins"]].tolist() == [0, 0, 1]

    # G4: 1300/1250 avg -> 1200_1599, blitz, White win, starts 1.c4
    row = _rows(
        table,
        position=START_POSITION,
        continuation="c2c4",
        rating_band="1200_1599",
        speed="blitz",
    )
    assert len(row) == 1
    assert row.iloc[0][["white_wins", "draws", "black_wins"]].tolist() == [1, 0, 0]


def test_ineligible_games_are_dropped_entirely(tmp_path):
    """G5 unrated, G6 too short, G7 missing Elo, G8 non-standard variant:
    none of them should contribute any row. Only G1-G4 are eligible, so the
    starting Position's total Games across all Continuations must be 4."""
    out_path = tmp_path / "aggregate.parquet"

    ingest.run(FIXTURE, out_path)
    table = aggregate_table.load(out_path)

    start_rows = _rows(table, position=START_POSITION)
    total_games = (
        start_rows["white_wins"] + start_rows["draws"] + start_rows["black_wins"]
    ).sum()
    assert total_games == 4


def test_theory_depth_truncates_moves_beyond_16_plies(tmp_path):
    """G1 is 20 plies long. Its 17th ply (9. h3) is past the Theory depth
    and must not appear as a Continuation anywhere in the table."""
    out_path = tmp_path / "aggregate.parquet"

    ingest.run(FIXTURE, out_path)
    table = aggregate_table.load(out_path)

    board = chess.Board()
    moves = [
        "e2e4", "e7e5", "g1f3", "b8c6", "f1b5", "a7a6", "b5a4", "g8f6",
        "e1g1", "f8e7", "f1e1", "b7b5", "a4b3", "d7d6", "c2c3", "e8g8",
    ]
    for uci in moves:
        board.push_uci(uci)
    position_at_ply_16 = board.epd()

    row = _rows(table, position=position_at_ply_16, continuation="h2h3")
    assert len(row) == 0


def test_transposition_merges_and_band_speed_stay_separate(tmp_path):
    """G3 (1.d4 d5 2.c4 e6 3.Nc3 Nf6...) and G4 (1.c4 e6 2.d4 d5 3.Nc3
    Nf6...) reach the same Position after 3 full moves via different move
    orders, then both continue 4.Bg5. They must merge into one Position
    with two Continuation rows (one per Game's Rating band/Speed), not
    one row per Game's distinct Line."""
    out_path = tmp_path / "aggregate.parquet"

    ingest.run(FIXTURE, out_path)
    table = aggregate_table.load(out_path)

    bg5_rows = _rows(table, continuation="c1g5")
    assert len(bg5_rows) == 2
    assert bg5_rows["position"].nunique() == 1

    g3_row = _rows(bg5_rows, rating_band="under_1200", speed="bullet")
    assert len(g3_row) == 1
    assert g3_row.iloc[0][["white_wins", "draws", "black_wins"]].tolist() == [
        0,
        0,
        1,
    ]

    g4_row = _rows(bg5_rows, rating_band="1200_1599", speed="blitz")
    assert len(g4_row) == 1
    assert g4_row.iloc[0][["white_wins", "draws", "black_wins"]].tolist() == [
        1,
        0,
        0,
    ]
