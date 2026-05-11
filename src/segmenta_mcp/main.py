"""Entry point del server FastMCP.

Inizializza l'app FastMCP con i 4 tool Tier 1 (M1 MVP) e gli health endpoint.
Layer architetturali secondo `01-ARCHITECTURE.md` v1.3 sez. 4.2:
    1. Transport   → questo modulo + FastMCP routing
    2. Auth        → segmenta_mcp.auth (M2)
    3. Tools       → segmenta_mcp.tools.tier{1,2,3}
    4. Domain      → segmenta_mcp.domain
    5. Data & Integrations → segmenta_mcp.data + segmenta_mcp.integrations
"""

from __future__ import annotations

import os
import time
from typing import Any

# Placeholder fino a M1.2 (FastMCP setup)
# from fastmcp import FastMCP

__all__ = ["app", "app_uptime"]

_START_TIME = time.monotonic()


def app_uptime() -> float:
    """Restituisce l'uptime del server in secondi (per /health)."""
    return time.monotonic() - _START_TIME


# TODO M1.2.1 — istanziare FastMCP app:
#   app = FastMCP(name="segmenta-mcp", version=__version__)
#
# Placeholder Starlette app per setup CI e prime smoke test deployment.
# Sostituito completamente in M1.2 quando FastMCP sarà cablato.
from starlette.applications import Starlette  # noqa: E402
from starlette.responses import JSONResponse  # noqa: E402
from starlette.routing import Route  # noqa: E402


async def health(request: Any) -> JSONResponse:
    """Health check minimo per Caddy upstream + UptimeRobot.

    In M1.2 sarà esteso con check su data cache + Redis ping (vedi
    `09-DEPLOYMENT.md` sez. 4.6).
    """
    return JSONResponse(
        {
            "status": "healthy",
            "checks": {
                "uptime_seconds": app_uptime(),
            },
            "version": os.environ.get("SEGMENTA_MCP_VERSION", "0.0.1"),
        }
    )


app = Starlette(
    debug=False,
    routes=[
        Route("/health", health, methods=["GET"]),
    ],
)
