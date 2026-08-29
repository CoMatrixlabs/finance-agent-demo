"""Market-status lookups for the financial-analytics agent.

Deliberately holds NO client PII — just generic, public market state a research bot needs
to answer "how is this symbol doing?". Every read is parameterized. There is no client
book of business here; the demo PR is what introduces a client-accounts table.
"""
from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager

_DSN = os.environ.get("FINANCE_AGENT_DSN", "finance.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS market_status (
    symbol      TEXT    PRIMARY KEY,
    name        TEXT    NOT NULL,
    session     TEXT    NOT NULL,
    last_close  TEXT
);
"""


@contextmanager
def connect():
    con = sqlite3.connect(_DSN)
    con.row_factory = sqlite3.Row
    try:
        yield con
    finally:
        con.close()


def market_status(symbol: str) -> dict | None:
    """Return generic, public market status for one symbol. Parameterized, no PII."""
    with connect() as con:
        cur = con.execute(
            "SELECT symbol, name, session, last_close FROM market_status WHERE symbol = ?",
            (symbol.upper(),),
        )
        row = cur.fetchone()
        return dict(row) if row else None
