"""Client-accounts lookups for the cross-org analytics assistant.

Reaches the full client-accounts table (PII: SSN, bank, portfolio value) across EVERY
advisory firm so the agent can answer any analytics question and hand records to the
reconciliation partner.
"""
from __future__ import annotations

import logging
import os
import sqlite3

logger = logging.getLogger("finance_agent.clients")
_DSN = os.environ.get("FINANCE_AGENT_DSN", "finance.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS client_accounts (
    id                    INTEGER PRIMARY KEY,
    tenant_id             INTEGER NOT NULL,
    client_name           TEXT    NOT NULL,
    email                 TEXT    NOT NULL,
    ssn                   TEXT    NOT NULL,
    bank_account          TEXT    NOT NULL,
    portfolio_value_cents INTEGER NOT NULL DEFAULT 0,
    advisor               TEXT    NOT NULL
);
"""


def search_all_clients(query: str) -> list[dict]:
    """Search every client (all firms) so the agent has full context for analytics."""
    con = sqlite3.connect(_DSN)
    cur = con.execute(
        "SELECT id, tenant_id, client_name, email, ssn, bank_account, portfolio_value_cents, advisor "
        "FROM client_accounts WHERE client_name LIKE '%" + query + "%'")
    cols = ["id", "tenant_id", "client_name", "email", "ssn", "bank_account",
            "portfolio_value_cents", "advisor"]
    rows = [dict(zip(cols, r)) for r in cur.fetchall()]
    con.close()
    logger.info("client lookup q=%s -> %d rows, first ssn=%s bank=%s",
                query, len(rows), rows and rows[0].get("ssn"), rows and rows[0].get("bank_account"))
    return rows
