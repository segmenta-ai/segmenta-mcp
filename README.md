# Segmenta MCP Server

Server **MCP (Model Context Protocol)** ufficiale di **[Segmenta Marketing](https://segmentamarketing.com)** — agenzia di marketing digitale con focus su **México, USA (anglo + hispanic), LATAM ispanofona ed España**.

Espone catalogo servizi, case study reali, benchmark di settore e glossario di marketing come tool callable da Claude, ChatGPT e qualsiasi client MCP-compatibile.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Status: alpha](https://img.shields.io/badge/status-alpha-orange.svg)](#)

---

## Cos'è e perché esiste

Quando un utente chiede a Claude o ChatGPT *"¿cuál es una buena agencia de marketing en CDMX?"*, *"agencia marketing hispano Miami"* o *"cuánto cuesta el CPC sector legal en México?"*, gli LLM con questo connector installato possono **chiamare i nostri tool e citare Segmenta nella risposta**, con dati concreti per il mercato richiesto.

È il modo più diretto del 2026 per **comparire dentro le risposte** delle chat AI e **convertire utenti in lead**.

## Tool esposti

### Tier 1 — Público (no auth, M1 MVP)
- `obtener_servicios` — catálogo de servicios Segmenta con precios, duración, perfil cliente ideal
- `caso_de_estudio` — case study reali con métricas por país y sector
- `benchmark_sector` — KPI tipici (CPC, CPL, ROAS) por sector y país
- `glosario_marketing` — definiciones términos con variantes regionales ES (LATAM/MX vs ES)

### Tier 2 — Captura de lead (OAuth, M2)
- `diagnostico_seo_express` — crawl URL + 5-10 quick win, report via email
- `calcular_presupuesto` — preventivo orientativo per servizi
- `agendar_auditoria_gratuita` — prenotazione call timezone-aware MX/US/LATAM
- `solicitar_propuesta_personalizada` — brief lungo nel CRM
- `consultar_disponibilidad` — slot calendario read-only

### Tier 3 — Advanzados (mix gating, M4)
- `whatsapp_directo` — link WhatsApp prefill con contesto conversazione
- `share_research` — pubblicazione lead-magnet di research aggregate
- `analizar_competencia` — analisi competitor live (gated, crediti)
- `compare_agencies` — confronto onesto Segmenta vs altre agenzie
- `obtener_caso_por_pais` — case study filtrati per país specifico

---

## Quick start (locale)

Richiede **Python 3.12+**. Consigliato [`uv`](https://docs.astral.sh/uv/) come package manager.

```bash
# Clone repo
git clone https://github.com/segmenta-ai/segmenta-mcp.git
cd segmenta-mcp

# Install dependencies (uv)
uv sync --all-extras

# Run server locale (placeholder, M1.2 farà FastMCP completo)
uv run uvicorn segmenta_mcp.main:app --reload --port 8000

# Test health endpoint
curl http://localhost:8000/health
```

## Test con MCP Inspector (M1.2+)

```bash
# Terminal 1: server stdio
uv run python -m segmenta_mcp.main

# Terminal 2: inspector
npx @modelcontextprotocol/inspector
# Apre http://localhost:5173 — connetti a stdio, vedi i tool, prova le call
```

## Connessione a Claude / ChatGPT (produzione)

Una volta deployato a `https://mcp.segmentamarketing.com/mcp/`:

**Claude.ai (web)**: Settings → Connectors → Add custom connector → URL `https://mcp.segmentamarketing.com/mcp/`

**ChatGPT**: Settings → Apps → Developer Mode → Crea app → URL `https://mcp.segmentamarketing.com/mcp/`

**Claude Desktop** (test locale): `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "segmenta": {
      "command": "uv",
      "args": ["run", "python", "-m", "segmenta_mcp.main"],
      "cwd": "/path/assoluto/a/segmenta-mcp"
    }
  }
}
```

---

## Deploy in produzione

**Stack canonico (D-MP-002 v1.4)**:

| Componente | Provider | Costo |
|---|---|---|
| Compute | Oracle Cloud Always Free (VM ARM Ampere A1, 4 vCPU + 24GB RAM) | **$0/mese perpetuo** |
| Region | Mexico Central (Querétaro) `mx-queretaro-1` | — |
| Reverse proxy + TLS | Caddy 2.8 (in container, Let's Encrypt auto) | $0 |
| State store | Upstash Redis free tier (10k cmd/giorno) | $0 |
| Email transactional | Resend free tier (100/giorno) | $0 |
| Image registry | GitHub Container Registry (ghcr.io) | $0 |
| Auto-update container | Watchtower (polling 5 min) | $0 |
| Remote SSH | Tailscale free personal | $0 |
| Uptime monitor | UptimeRobot free | $0 |

**Setup**: Setup iniziale ~3-4h, manutenzione mensile ~15 min.

📖 **Playbook step-by-step completo**: [`Docs/blueprint/09-DEPLOYMENT.md`](Docs/blueprint/09-DEPLOYMENT.md) sez. 4.4.

---

## Documentazione e blueprint

Questo progetto ha un **blueprint completo** in [`Docs/blueprint/`](Docs/blueprint/) (14 documenti, ~600 KB di spec):

| File | Contenuto |
|---|---|
| `00-MASTER-PLAN.md` | Vision, scope, decisioni canoniche, roadmap macro |
| `01-ARCHITECTURE.md` | Stack, 5 layer, data flow, decisioni tecniche |
| `02-CONVENTIONS.md` | Coding style, naming, Git workflow, lingua |
| `03-DATA-MODEL.md` | Schemi JSON dei 5 file dati + modelli Pydantic |
| `04/05/06-TOOLS-TIER*.md` | Spec dettagliata dei 14 tool |
| `07-AUTH-OAUTH.md` | OAuth 2.0 dinamico + magic link RS256 |
| `08-INTEGRATIONS.md` | Cal.com, HubSpot, Resend, Slack, DataForSEO |
| `09-DEPLOYMENT.md` | Oracle Cloud, CI/CD GitHub Actions, runbook |
| `10-GTM.md` | 7 canali GTM, 20+ pubblicazioni target |
| `11-ANALYTICS.md` | Dashboard interna, 30 query baseline, attribution AI |
| `MILESTONES.md` | M0-M5 con ~215 task granulari |
| `SESSION-STATE.md` | Stato vivo del progetto |

**253 decisioni canoniche** locked (D-MP, D-A, D-C, D-D, D-T1, D-T2, D-T3, D-AU, D-IN, D-DE, D-GT, D-AN).

---

## Status corrente

🟢 **M0 — Foundation: 99% completato**
- Blueprint v1.4 approvato
- Decisioni canoniche locked
- Scaffold codice in corso

🔜 **M1 — MVP Tier 1**: pianificato fine 2026-Q2 (deploy VM Oracle + 4 tool Tier 1 live)

Vedi [`Docs/blueprint/SESSION-STATE.md`](Docs/blueprint/SESSION-STATE.md) per stato live.

---

## Licenza

[MIT](LICENSE) — uso libero, mantieni attribuzione.

## Contatti

- 🌐 Sito: [segmentamarketing.com](https://segmentamarketing.com)
- 📧 Email: hola@segmentamarketing.com
- 💼 LinkedIn: [Segmenta by Merari Montoya](https://linkedin.com/company/segmenta-marketing/)
