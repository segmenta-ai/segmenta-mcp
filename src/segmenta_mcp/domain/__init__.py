"""Layer 4 — Domain logic: pure functions (filtri, calcoli, formatter).

Niente I/O qui. Niente httpx. Niente Redis.
Tutti i side effect passano per Layer 5 (data + integrations).

Vedi `Docs/blueprint/01-ARCHITECTURE.md` v1.3 sez. 4.2 vincoli.
"""
