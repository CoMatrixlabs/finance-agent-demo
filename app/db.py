"""Client-accounts database access.

A thin SQLite layer holding client accounts across multiple advisory firms (tenants).
Every read is parameterized and scoped to the caller's firm. Sensitive columns (ssn,
bank_account) exist so the demo can show masking vs. leakage — real deployments would
tokenize these at rest.
"""
from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager

_DSN = os.environ.get("FINANCE_AGENT_DSN", "client_accounts.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS client_accounts (
    id                   INTEGER PRIMARY KEY,
    tenant_id            INTEGER NOT NULL,
    client_name          TEXT    NOT NULL,
    email                TEXT    NOT NULL,
    ssn                  TEXT    NOT NULL,
    bank_account         TEXT    NOT NULL,
    portfolio_value_cents INTEGER NOT NULL DEFAULT 0,
    advisor              TEXT    NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_client_accounts_tenant ON client_accounts(tenant_id);
"""


@contextmanager
def connect():
    con = sqlite3.connect(_DSN)
    con.row_factory = sqlite3.Row
    try:
        yield con
    finally:
        con.close()


def find_clients(tenant_id: int, name_like: str) -> list[dict]:
    """Look up client accounts for ONE firm by (partial) name. Parameterized + tenant-scoped."""
    with connect() as con:
        cur = con.execute(
            "SELECT id, tenant_id, client_name, email, ssn, bank_account, portfolio_value_cents, advisor "
            "FROM client_accounts WHERE tenant_id = ? AND client_name LIKE ? ORDER BY client_name",
            (tenant_id, f"%{name_like}%"),
        )
        return [dict(r) for r in cur.fetchall()]


def update_advisor(tenant_id: int, client_id: int, new_advisor: str) -> int:
    """Effectful write — used only behind the approval gate. Tenant-scoped."""
    with connect() as con:
        cur = con.execute(
            "UPDATE client_accounts SET advisor = ? WHERE tenant_id = ? AND id = ?",
            (new_advisor, tenant_id, client_id),
        )
        con.commit()
        return cur.rowcount
