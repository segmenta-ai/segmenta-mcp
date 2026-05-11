"""Layer 5a — Data: caricamento JSON file dal repo, cache in-memory.

5 file JSON gestiti (vedi `Docs/blueprint/03-DATA-MODEL.md` v1.1 sez. 3):
- services.json
- case_studies.json
- benchmarks.json
- glosario.json
- competitors_dataset.json (M4 — usato da compare_agencies)

Validazione at boundary via Pydantic v2 (D-D-003, D-D-012).
Fail fast: se un file è malformato, il server non parte (D-D-012).
"""
