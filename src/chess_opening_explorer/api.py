from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from chess_opening_explorer import aggregate_table
from chess_opening_explorer.explorer import explore

DEFAULT_TABLE_PATH = Path("data/aggregate_table.parquet")


def create_app(table_path: Path = DEFAULT_TABLE_PATH) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.table = aggregate_table.load(table_path)
        yield

    app = FastAPI(lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["GET"],
        allow_headers=["*"],
    )

    @app.get("/api/explorer")
    def get_explorer(
        line: str = "", rating_band: str | None = None, speed: str | None = None
    ) -> dict:
        moves = line.split(",") if line else []
        try:
            return explore(app.state.table, moves, rating_band=rating_band, speed=speed)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    return app


app = create_app()
