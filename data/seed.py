"""Seed the baseline database + research corpus with non-sensitive demo data.

The baseline agent holds NO client PII — just generic market-status rows and public
research notes. (The demo PR is what introduces a client-accounts table with SSN/bank/
portfolio.) The two tenants are two different advisory firms.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app import db  # noqa: E402

MARKETS = [
    ("ACME", "Acme Industrials Index", "open",   "142.10"),
    ("GLBX", "Globex Composite",       "open",   "3980.55"),
    ("BND10", "10Y Sovereign Note",    "closed", "98.72"),
    ("FXEU", "EUR/USD Reference",       "open",   "1.0845"),
]

DOCS = [
    {"doc_id": "kb-t1-research", "tenant_id": 1, "classification": "standard",
     "title": "Q3 allocation guidance", "body": "Meridian model portfolios rebalance quarterly. Contact the desk to adjust a target allocation."},
    {"doc_id": "kb-t2-research", "tenant_id": 2, "classification": "standard",
     "title": "Cardinal fixed-income view", "body": "Cardinal favors short-duration credit this cycle. See the desk note for duration targets."},
]


def main() -> None:
    with db.connect() as con:
        con.executescript(db.SCHEMA)
        con.execute("DELETE FROM market_status")
        con.executemany(
            "INSERT INTO market_status (symbol, name, session, last_close) VALUES (?,?,?,?)", MARKETS)
        con.commit()
    docs_dir = Path(__file__).resolve().parent / "docs"
    docs_dir.mkdir(exist_ok=True)
    for d in DOCS:
        (docs_dir / f"{d['doc_id']}.json").write_text(json.dumps(d, indent=2))
    print(f"seeded {len(MARKETS)} market rows, {len(DOCS)} research docs (no PII)")


if __name__ == "__main__":
    main()
