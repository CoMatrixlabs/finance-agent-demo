"""Tools the financial-analytics agent can call.

Baseline capability is intentionally narrow and PII-free: search public research notes and
report a symbol's generic market status. No client records, no data export, no writes. That
keeps the agent's data boundary trivial — which is the point: the demo PR is what wires it
to client data and breaks the boundary.
"""
from __future__ import annotations

from langchain_core.tools import tool

from . import db, rag

# The caller's identity is injected by the graph per request, never chosen by the model.
_CALLER = {"tenant_id": 1, "clearance": "standard"}


def set_caller(tenant_id: int, clearance: str = "standard") -> None:
    _CALLER["tenant_id"] = tenant_id
    _CALLER["clearance"] = clearance


@tool
def search_research(query: str) -> list[dict]:
    """Search public research notes / FAQs relevant to the advisor's question."""
    return rag.search_notes(query, tenant_id=_CALLER["tenant_id"], clearance=_CALLER["clearance"])


@tool
def market_info(symbol: str) -> dict:
    """Report the generic, public market status of a symbol (no personal data)."""
    return db.market_status(symbol) or {"error": "symbol not found"}


# No sensitive tools in the baseline; the graph gates any that are added here.
SENSITIVE_TOOLS: set[str] = set()

READ_TOOLS = [search_research, market_info]
WRITE_TOOLS: list = []
ALL_TOOLS = READ_TOOLS + WRITE_TOOLS
