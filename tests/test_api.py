from pathlib import Path

import chess
from fastapi.testclient import TestClient

from chess_opening_explorer import ingest
from chess_opening_explorer.api import create_app

FIXTURE = Path(__file__).parent / "fixtures" / "fixture.pgn"


def make_client(tmp_path):
    out_path = tmp_path / "aggregate.parquet"
    ingest.run(FIXTURE, out_path)
    app = create_app(out_path)
    return TestClient(app)


def test_seam1_fixture_pgn_through_ingest_to_api(tmp_path):
    """Seam-1: fixture PGN -> Ingest -> API, asserting Continuations,
    Outcome splits and reach share against hand-counted expectations."""
    with make_client(tmp_path) as client:
        response = client.get("/api/explorer")

        assert response.status_code == 200
        body = response.json()
        assert body["position"] == chess.Board().epd()
        assert body["total_games"] == 4
        assert body["reach_share"] == 1.0

        continuations = {c["move"]: c for c in body["continuations"]}
        assert continuations["e2e4"]["games"] == 2
        assert continuations["e2e4"]["outcome"] == {
            "white_wins": {"count": 1, "proportion": 0.5},
            "draws": {"count": 1, "proportion": 0.5},
            "black_wins": {"count": 0, "proportion": 0.0},
        }
        assert continuations["d2d4"]["games"] == 1
        assert continuations["c2c4"]["games"] == 1


def test_seam1_advancing_the_line_via_query_param(tmp_path):
    with make_client(tmp_path) as client:
        response = client.get("/api/explorer", params={"line": "e2e4"})

        assert response.status_code == 200
        body = response.json()
        board = chess.Board()
        board.push_uci("e2e4")
        assert body["position"] == board.epd()
        assert body["reach_share"] == 0.5
        assert body["continuations"] == [
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


def test_seam1_rating_band_and_speed_filters(tmp_path):
    with make_client(tmp_path) as client:
        response = client.get(
            "/api/explorer", params={"rating_band": "1200_1599", "speed": "blitz"}
        )

        assert response.status_code == 200
        body = response.json()
        assert body["total_games"] == 2
        assert {c["move"] for c in body["continuations"]} == {"e2e4", "c2c4"}


def test_seam1_illegal_line_returns_clear_error(tmp_path):
    with make_client(tmp_path) as client:
        response = client.get("/api/explorer", params={"line": "e2e5"})

        assert response.status_code == 400
        assert "e2e5" in response.json()["detail"]
