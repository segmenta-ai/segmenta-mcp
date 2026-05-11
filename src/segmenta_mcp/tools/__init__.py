"""Layer 3 — Tool definitions: decorator @mcp.tool, validazione input/output.

I 14 tool del server sono organizzati per tier (D-MP-004):
    tier1/ — 4 tool público (no auth)
    tier2/ — 5 tool con captura de lead (OAuth, M2+)
    tier3/ — 5 tool advanzados (mix gating, M4+)

Vedi `Docs/blueprint/04-TOOLS-TIER1.md`, `05-TOOLS-TIER2.md`, `06-TOOLS-TIER3.md`.
"""
