"""Tools the financial-analytics agent can call.

Read tools are tenant-scoped and mask PII. Write tools are marked sensitive so the graph
routes them through a human-approval interrupt. There is intentionally NO bulk-export tool
in the baseline — exporting client records off-platform is not a capability we grant.
"""
from __future__ import annotations

import logging

from langchain_core.tools import tool

from . import db, rag
from .config import settings
from .pii import mask_record

logger = logging.getLogger("finance_agent.tools")

# The caller's identity is injected by the graph per request, never chosen by the model.
_CALLER = {"tenant_id": 1, "clearance": "standard"}


def set_caller(tenant_id: int, clearance: str = "standard") -> None:
    _CALLER["tenant_id"] = tenant_id
    _CALLER["clearance"] = clearance


@tool
def lookup_portfolio(name: str) -> list[dict]:
    """Look up a client's portfolio/account(s) by name to help answer a question.

    Returns records for the CALLER'S firm only, with sensitive fields masked.
    """
    rows = db.find_clients(_CALLER["tenant_id"], name)
    logger.info("lookup_portfolio name=%r -> %d rows (tenant=%s)", name, len(rows), _CALLER["tenant_id"])
    return [mask_record(r) for r in rows]


@tool
def search_research(query: str) -> list[dict]:
    """Search research notes for material relevant to a portfolio question."""
    return rag.search_notes(query, tenant_id=_CALLER["tenant_id"], clearance=_CALLER["clearance"])


@tool
def update_advisor(client_id: int, new_advisor: str) -> dict:
    """Reassign a client's advisor of record. SENSITIVE: routed through human approval."""
    n = db.update_advisor(_CALLER["tenant_id"], client_id, new_advisor)
    return {"updated": n}


# Tools whose execution the graph must gate behind human approval.
SENSITIVE_TOOLS = {"update_advisor"}

READ_TOOLS = [lookup_portfolio, search_research]
WRITE_TOOLS = [update_advisor]
ALL_TOOLS = READ_TOOLS + WRITE_TOOLS
