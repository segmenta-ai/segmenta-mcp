# Changelog

Tutti i cambiamenti rilevanti al **Segmenta MCP Server** sono documentati qui.

Formato: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) (D-C-015).
Versioning: [Semantic Versioning](https://semver.org/spec/v2.0.0.html) (D-MP-011, D-C-016).

## [Unreleased]

### Added
- Scaffold iniziale repo: `Dockerfile` multi-stage ARM64, `docker-compose.yml`, `Caddyfile`, `.env.example`, `pyproject.toml`, `LICENSE` MIT, scaffold `src/segmenta_mcp/`.
- Workflow GitHub Actions: `ci.yml` (lint + test + type check), `build-publish.yml` (build image ARM64 + push a ghcr.io).
- Documentazione blueprint v1.4 in `Docs/blueprint/` (14 file numerati + MILESTONES + SESSION-STATE).

### Decided
- Stack hosting: Oracle Cloud Always Free Tier — VM ARM Ampere A1 (4 vCPU + 24GB RAM), region Mexico Central (Querétaro). D-MP-002 v1.4.
- Email provider: Resend free tier (100/giorno). DECISION-OPEN-004 chiusa.
- Sede legale per privacy: Messico, LFPDPPP primaria. M0.2.2.
- Repository: `github.com/segmenta-ai/segmenta-mcp` pubblico, MIT. D-MP-008, D-MP-009.

## [0.0.1] — TBD (M1.6 — primo deploy MVP Tier 1)

Pianificato release con i 4 tool Tier 1 funzionanti su production:
- `obtener_servicios`
- `caso_de_estudio`
- `benchmark_sector`
- `glosario_marketing`

Vedi `Docs/blueprint/MILESTONES.md` M1 per acceptance criteria dettagliati.
