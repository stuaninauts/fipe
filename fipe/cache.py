"""Local cache of raw API responses (SQLite under data/raw/, never committed: docs/adr/0001).

Each successful response is stored once, keyed by endpoint and form params, so a collection can stop at any
point and the next run picks up where it left off. Failures go to their own table and are retried next run.
"""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path

from fipe.api import ApiError, Client

DEFAULT_PATH = Path("data/raw/fipe_api.sqlite")

SCHEMA = """
create table if not exists responses (
    endpoint   text not null,
    params     text not null,
    body       text not null,
    fetched_at text not null,
    primary key (endpoint, params)
);
create table if not exists failures (
    endpoint  text not null,
    params    text not null,
    error     text not null,
    failed_at text not null,
    primary key (endpoint, params)
);
"""


def _key(params: Mapping[str, str]) -> str:
    return json.dumps(dict(params), sort_keys=True, ensure_ascii=False)


def _now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


class Cache:
    def __init__(self, client: Client, path: Path | str = DEFAULT_PATH) -> None:
        self.client = client
        self.path = Path(path)
        if str(path) != ":memory:":
            self.path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path)
        self.db.executescript(SCHEMA)
        self.hits = 0

    def close(self) -> None:
        self.db.close()

    def get(self, endpoint: str, params: Mapping[str, str]) -> str:
        """Cached body if present; otherwise call the API, store the result and return it."""
        key = _key(params)
        row = self.db.execute(
            "select body from responses where endpoint = ? and params = ?", (endpoint, key)
        ).fetchone()
        if row:
            self.hits += 1
            return row[0]
        try:
            body = self.client.post(endpoint, params)
        except ApiError as err:
            with self.db:
                self.db.execute(
                    "insert or replace into failures values (?, ?, ?, ?)", (endpoint, key, str(err), _now())
                )
            raise
        with self.db:
            self.db.execute("insert into responses values (?, ?, ?, ?)", (endpoint, key, body, _now()))
            self.db.execute("delete from failures where endpoint = ? and params = ?", (endpoint, key))
        return body

    def get_json(self, endpoint: str, params: Mapping[str, str]):
        return json.loads(self.get(endpoint, params))

    def failure_count(self) -> int:
        return self.db.execute("select count(*) from failures").fetchone()[0]
