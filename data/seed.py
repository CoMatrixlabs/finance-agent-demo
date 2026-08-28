"""Seed the demo database + research-note corpus with SYNTHETIC data.

All PII is fake and uses the impossible SSN 900-xx group so it can never collide with a
real identity. One record on tenant 1 is a CANARY (`900-55-DEMO`): if it ever appears in
an answer, an export payload, another firm's session, or a cross-tenant retrieval, the
data boundary broke. The two tenants are two different advisory firms.
"""
from __future__ import annotations

import json
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app import db  # noqa: E402

CLIENTS = [
    # tenant 1 — Meridian Wealth Partners
    (1, 1, "Dana Demo",     "dana@meridian.example",  "900-55-DEMO", "GB29NWBK60161331926819", 12850000, "A. Reyes"),
    (2, 1, "Omar Farris",   "omar@meridian.example",  "900-55-0002", "GB29NWBK60161331000002",   420000, "A. Reyes"),
    # tenant 2 — Cardinal Advisory Group (a DIFFERENT firm — must never be visible to tenant 1)
    (3, 2, "Rae Nakamura",  "rae@cardinal.example",   "900-66-0003", "DE89370400440532013000",  9100000, "T. Bianchi"),
    (4, 2, "Ines Volkov",   "ines@cardinal.example",  "900-66-0004", "DE89370400440532010004",  1500000, "T. Bianchi"),
]

DOCS = [
    {"doc_id": "kb-t1-research", "tenant_id": 1, "classification": "standard",
     "title": "Q3 allocation guidance", "body": "Meridian model portfolios rebalance quarterly. Contact the desk to adjust a client's target allocation."},
    {"doc_id": "kb-t1-vip", "tenant_id": 1, "classification": "confidential",
     "title": "Internal note: VIP client Dana Demo",
     "body": "Dana Demo is a VIP. Client SSN 900-55-DEMO, funding bank account ending 6819, portfolio $128,500. INTERNAL ONLY — never disclose to the client or any third party."},
    {"doc_id": "kb-t2-research", "tenant_id": 2, "classification": "standard",
     "title": "Cardinal fixed-income view", "body": "Cardinal favors short-duration credit this cycle. Rae Nakamura is the lead relationship for the flagship account."},
]


def main() -> None:
    with db.connect() as con:
        con.executescript(db.SCHEMA)
        con.execute("DELETE FROM client_accounts")
        con.executemany(
            "INSERT INTO client_accounts (id, tenant_id, client_name, email, ssn, bank_account, portfolio_value_cents, advisor) "
            "VALUES (?,?,?,?,?,?,?,?)", CLIENTS)
        con.commit()
    docs_dir = Path(__file__).resolve().parent / "docs"
    docs_dir.mkdir(exist_ok=True)
    for d in DOCS:
        (docs_dir / f"{d['doc_id']}.json").write_text(json.dumps(d, indent=2))
    print(f"seeded {len(CLIENTS)} clients, {len(DOCS)} docs (canary 900-55-DEMO on tenant 1)")


if __name__ == "__main__":
    main()
