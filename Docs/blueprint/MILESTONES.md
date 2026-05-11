# MILESTONES

| Campo | Valore |
|---|---|
| **Progetto** | Segmenta MCP Server |
| **Versione documento** | 1.3 |
| **Data** | 2026-05-11 |
| **Status** | Approvato (post ricalibrazione hosting Oracle Cloud) |
| **File n.** | non numerato — file di pianificazione operativa |
| **Documento padre** | `00-MASTER-PLAN.md` v1.4 (sez. 7 roadmap macro — ~6-7 mesi) |
| **File correlati** | tutti i 12 file numerati 00-11 |

---

## 1. Scopo del documento

Questo file è il **piano operativo dettagliato** del progetto Segmenta MCP. Mentre `00-MASTER-PLAN.md` sez. 7 dà la roadmap macro a livello di ossatura, qui ogni milestone è esplosa in **task granulari, acceptance criteria testabili, durate stimate, dipendenze, owner e deliverable concreti**.

Funzioni:

1. Permettere a Claudio (e Claude Code) di sapere **cosa fare adesso** e cosa segue.
2. Definire i **gate** per passare da una milestone all'altra (Definition of Done).
3. Tracciare **dipendenze esterne** (decisioni di Merari, team Segmenta) per evitare blocchi.
4. Servire come **base di stima** quando Merari chiede "quando saremo live?".

Pace ipotizzata: 2-3h/settimana effettive su questo progetto (D-MP-005). Tempi qui in **ore-uomo equivalenti** e **settimane calendar** assumendo quel ritmo.

---

## 2. Convenzioni di questo file

### 2.1 Status milestone

| Status | Significato |
|---|---|
| 🔒 NOT STARTED | Non iniziata, predecessor non completati |
| 🟡 IN PROGRESS | Attiva, almeno 1 task completato |
| ✅ COMPLETED | Tutti acceptance criteria met |
| ⏸️ BLOCKED | Bloccata da dipendenza esterna |
| ⚠️ AT RISK | Probabile slip ma non bloccata |

### 2.2 Priorità task

| Sigla | Significato |
|---|---|
| **[P0]** | Blocker — la milestone non chiude senza |
| **[P1]** | Critico — fortemente raccomandato, scivola in milestone successiva se non fatto |
| **[P2]** | Importante — può slittare se serve compress |
| **[P3]** | Nice-to-have — esplicitamente opzionale |

### 2.3 Acceptance Criteria (AC)

Ogni milestone ha sezione **Definition of Done** con AC testabili. AC sono o:
- **Binari**: completato o no (es. "server live a `mcp.segmentamarketing.com`")
- **Misurabili**: con soglia numerica (es. "≥ 5 lead reali entro fine milestone")

### 2.4 Dipendenze

Ogni task indica eventuali blocker:
- `dep: Merari` → richiede decisione/azione di Merari
- `dep: team Segmenta web` → richiede team web (se esiste, altrimenti fallback Claudio)
- `dep: M{N}.{task}` → richiede completamento task precedente

### 2.5 Stima ore

Stime conservative. Includono ricerca, implementazione, test, doc. **Non** includono code review (anche se single dev, c'è auto-review).

---

## 3. Overview macro

```
M0 — Foundation (blueprint)           [2 settimane / ~15h]
  └─ Output: 12 file numerati + MILESTONES + SESSION-STATE consegnati

M1 — MVP Tier 1 in produzione         [2 settimane / ~20h]
  └─ Output: server live, 4 tool Tier 1 funzionanti, dati popolati

M2 — Lead capture (Tier 2)            [3-4 settimane / ~35h]
  └─ Output: OAuth + 5 tool Tier 2 + integrazioni + primi 5 lead reali

M3 — GTM execution                    [2 settimane / ~20h]
  └─ Output: landing + banner + blog + Anthropic submission

M4 — Tier 3 + analytics dashboard     [3 settimane / ~30h]
  └─ Output: 5 tool Tier 3 + dashboard interna + automazione tracking

M5 — Optimization                     [ongoing / ~5h/sett]
  └─ Output: refactoring data-driven, EN blog, content freshness

────────────────────────────────────────────────────────────
TOTALE M0→M4: ~120h ÷ 2.5h/sett = ~48 settimane → ~11 mesi
```

**Attenzione realistica**: questo timeline (~11 mesi) è più lungo dei "12-13 settimane" indicate in MASTER-PLAN sez. 7. Discrepanza dovuta a stime ore granulari sotto. Possibilità:

- **Opzione A**: accettare timeline più lungo e aggiornare MASTER-PLAN
- **Opzione B**: aumentare pace a 4-5h/sett (richiede negoziazione con Keeper/Chirsan/Numely)
- **Opzione C**: ridurre scope (es. saltare Tier 3 da v1 a v2 → -3 settimane M4)

Decisione: **Opzione A in v1.0 di questo file** — meglio essere onesti che ottimisti. Aggiornamento MASTER-PLAN sezione 7 da fare quando Claudio approva.

---

## 4. M0 — Foundation (blueprint)

### 4.1 Goal

Documentazione blueprint completa e revisionata. Stack tecnico bloccato. Decisioni canoniche locked.

### 4.2 Status

🟢 **IN CHIUSURA** — al 2026-05-11 (post harmony pass M0.3):
- 12 file numerati blueprint (00-11) completati ✅
- `MILESTONES.md` (questo file) completato v1.0 ✅
- `SESSION-STATE.md` completato v1.1 ✅ (post harmony pass)
- `README.md` completato e aggiornato per pivot LATAM ✅
- Harmony pass M0.3: 12 incongruenze HC-001 → HC-012 risolte ✅
- Resta solo M0.2 (decisioni Merari) per chiudere M0 al 100%.

### 4.3 Task

#### M0.1 [P0] Stesura 12 file numerati

| Task | Status | Stima | Owner | Dipendenze |
|---|---|---|---|---|
| M0.1.1 — `00-MASTER-PLAN.md` v1.4 | ✅ Completato | 3h | Claude+Claudio | — |
| M0.1.2 — `01-ARCHITECTURE.md` v1.3 | ✅ Completato | 2h | Claude+Claudio | M0.1.1 |
| M0.1.3 — `02-CONVENTIONS.md` v1.1 | ✅ Completato | 2h | Claude+Claudio | M0.1.1 |
| M0.1.4 — `03-DATA-MODEL.md` v1.1 | ✅ Completato | 2h | Claude+Claudio | M0.1.2 |
| M0.1.5 — `04-TOOLS-TIER1.md` v1.0 | ✅ Completato | 2h | Claude+Claudio | M0.1.4 |
| M0.1.6 — `05-TOOLS-TIER2.md` v1.0 | ✅ Completato | 2h | Claude+Claudio | M0.1.5 |
| M0.1.7 — `06-TOOLS-TIER3.md` v1.1 | ✅ Completato | 2h | Claude+Claudio | M0.1.6 |
| M0.1.8 — `07-AUTH-OAUTH.md` v1.0 | ✅ Completato | 2h | Claude+Claudio | M0.1.6 |
| M0.1.9 — `08-INTEGRATIONS.md` v1.1 | ✅ Completato | 2h | Claude+Claudio | M0.1.6 |
| M0.1.10 — `09-DEPLOYMENT.md` v1.1 | ✅ Completato | 2h | Claude+Claudio | M0.1.2 |
| M0.1.11 — `10-GTM.md` v1.1 | ✅ Completato | 1.5h | Claude+Claudio | M0.1.1 |
| M0.1.12 — `11-ANALYTICS.md` v1.1 | ✅ Completato | 1.5h | Claude+Claudio | M0.1.11 |
| M0.1.13 — `MILESTONES.md` (questo) v1.0 | ✅ Completato | 2h | Claude+Claudio | tutti i precedenti |
| M0.1.14 — `SESSION-STATE.md` v1.1 | ✅ Completato | 0.5h | Claude+Claudio | M0.1.13 |
| M0.1.15 — `README.md` aggiornato pivot LATAM | ✅ Completato | 0.5h | Claude+Claudio | harmony pass M0.3 |

#### M0.2 [P0] Decisioni Merari critiche

Da chiudere prima del kickoff M1:

| Task | Stima | Owner | Decisione |
|---|---|---|---|
| M0.2.1 — Approval budget M0-M4 ($30/mese cap) | 0.5h | Merari | Yes/no/condizionato |
| M0.2.2 — Conferma sede legale Messico (LFPDPPP) | 0.5h | Merari | DECISION-OPEN-011 di MP |
| M0.2.3 — Conferma repo pubblico GitHub | 0.5h | Merari | Conferma D-MP-008 |
| M0.2.4 — Accesso DNS `segmentamarketing.com` | 0.5h | Merari | DECISION-OPEN-DE-001 |
| M0.2.5 — GitHub account host (personale Claudio vs org `segmenta-ai`) | 0.5h | Merari + Claudio | DECISION-OPEN-005 di MP |

#### M0.3 [P1] Harmony pass

| Task | Status | Stima | Owner | Note |
|---|---|---|---|---|
| M0.3.1 — Lettura completa di tutti i 14 file (12 numerati + MILESTONES + SESSION-STATE) + README | ✅ Completato 2026-05-11 | 3h | Claudio + Claude Opus 4.7 | Eseguito tramite 4 audit agent paralleli + cross-check |
| M0.3.2 — Identificare incongruenze cross-file | ✅ Completato 2026-05-11 | 1h | Claudio + Claude | 12 HC identificate (HC-001 → HC-012); 2 falsi positivi (HC-003, HC-008) verificati e archiviati |
| M0.3.3 — Aggiornare file con fix puntuali | ✅ Completato 2026-05-11 | 1-2h | Claude Code | 10 incongruenze reali fixate; 8 file blueprint bumped da v1.0 a v1.1 (00 a v1.2) |
| M0.3.4 — SESSION-STATE finale con stato "M0 COMPLETED dopo M0.2" | ✅ Completato 2026-05-11 | 0.5h | Claude | SESSION-STATE v1.1 sez. 7 documenta tutte le HC e risoluzioni |

### 4.4 Definition of Done

- [x] Tutti i 14 file blueprint v1.0+ consegnati e revisionati
- [ ] Merari ha confermato decisioni M0.2.1 - M0.2.5
- [x] Harmony pass eseguito, incongruenze documentate in changelog
- [x] SESSION-STATE.md aggiornato con resoconto harmony pass
- [ ] Tag git `blueprint-v1-complete` creato (post chiusura M0.2)

### 4.5 Output / Deliverable

- 13 file Markdown in `Docs/blueprint/`
- Tag git `blueprint-v1-complete`
- Backup fisico dei file (regola Claudio per ogni progetto)

### 4.6 Risk

- **R0.1**: Merari non dà green light → progetto in standby. Mitigazione: presentation deck pronta + ROI proposition chiara.
- **R0.2**: Harmony pass scopre revisioni profonde necessarie → +1-2 settimane. Mitigazione: pass severo prima di chiudere M0.

---

## 5. M1 — MVP Tier 1 in produzione

### 5.1 Goal

Server MCP live a `mcp.segmentamarketing.com` con i 4 tool Tier 1 funzionanti. Dati popolati con info reali. Listing inviato (non ancora approvato) al Connector Directory di Anthropic.

### 5.2 Status

🔒 **NOT STARTED** — predecessor M0 completato.

### 5.3 Task

#### M1.1 [P0] Setup repo + CI

| Task | Stima | Dipendenze |
|---|---|---|
| M1.1.1 — Creare repo GitHub `segmenta/segmenta-mcp` pubblico | 0.5h | M0.2.3, M0.2.5 |
| M1.1.2 — Aggiungere LICENSE MIT, CONTRIBUTING.md, SECURITY.md, CODE_OF_CONDUCT.md | 1h | M1.1.1 |
| M1.1.3 — Setup `.github/workflows/ci.yml` (lint + test + type check) | 2h | M1.1.1 |
| M1.1.4 — Setup pre-commit hooks (`.pre-commit-config.yaml`) | 1h | M1.1.1 |
| M1.1.5 — Setup Dependabot config | 0.5h | M1.1.1 |
| M1.1.6 — Branch protection su `main` e `develop` | 0.5h | M1.1.1 |
| M1.1.7 — Issue + PR templates | 0.5h | M1.1.1 |
| M1.1.8 — `CLAUDE.md` per Claude Code instructions | 1h | M1.1.1 |

#### M1.2 [P0] Scaffold codice

| Task | Stima | Dipendenze |
|---|---|---|
| M1.2.1 — Setup `pyproject.toml` + `uv.lock` con dipendenze v1 | 1h | M1.1.1 |
| M1.2.2 — Struttura cartelle `src/segmenta_mcp/` (5 layer) | 0.5h | M1.2.1 |
| M1.2.3 — `config.py` Pydantic settings con env loading | 1h | M1.2.2 |
| M1.2.4 — `transport/middleware.py` (CORS, request_id, logging context) | 1.5h | M1.2.3 |
| M1.2.5 — `transport/routes.py` (/health, /, /metrics base) | 1h | M1.2.4 |
| M1.2.6 — `observability/logging.py` con structlog | 1.5h | M1.2.3 |
| M1.2.7 — `observability/metrics.py` con Prometheus | 1h | M1.2.6 |
| M1.2.8 — `data/loader.py` per JSON loading con Pydantic validation | 2h | M1.2.3 |
| M1.2.9 — `data/cache.py` per in-memory cache | 1h | M1.2.8 |
| M1.2.10 — `domain/models.py` con tutti i Pydantic models di `03-DATA-MODEL.md` | 3h | M1.2.8 |
| M1.2.11 — `server.py` entry point FastMCP | 1.5h | tutti M1.2.x |

#### M1.3 [P0] Implementazione 4 tool Tier 1

| Task | Stima | Dipendenze |
|---|---|---|
| M1.3.1 — `tools/tier1/obtener_servicios.py` + test | 2h | M1.2.10 |
| M1.3.2 — `tools/tier1/caso_de_estudio.py` + test (con filtro pais + match_type) | 3h | M1.2.10 |
| M1.3.3 — `tools/tier1/benchmark_sector.py` + test (con strategia fallback 4-step) | 3h | M1.2.10 |
| M1.3.4 — `tools/tier1/glosario_marketing.py` + test (con Levenshtein) | 2h | M1.2.10 |
| M1.3.5 — `domain/filters.py` (logica filtri condivisa) | 2h | M1.3.1-M1.3.4 |
| M1.3.6 — `domain/formatters.py` (USD/MXN/EUR display) | 1.5h | M1.3.1 |
| M1.3.7 — `domain/conversores.py` (valuta hardcoded rates) | 0.5h | M1.3.6 |

#### M1.4 [P0] Popolare dati reali

Critico per non avere "demo data" in production.

| Task | Stima | Owner |
|---|---|---|
| M1.4.1 — Compilare `data/services.json` con 8-15 servizi Segmenta reali | 3h | Claudio + Merari |
| M1.4.2 — Compilare `data/case_studies.json` con 5+ casi reali (consenso ottenuto) | 4h | Merari (consensi) + Romina (testi) |
| M1.4.3 — Compilare `data/benchmarks.json` con KPI MX/LATAM/US/ES Q2 2026 | 4h | Alessio + Claudio |
| M1.4.4 — Compilare `data/glosario.json` con 15-30 termini | 3h | Romina + Alessio |
| M1.4.5 — Review legale ANONIMIZZAZIONE casi (LFPDPPP) | 1h | Merari |
| M1.4.6 — `scripts/validate_data.py` passa su tutti i JSON | 1h | Claudio |

#### M1.5 [P0] Deploy staging + production

| Task | Stima | Dipendenze |
|---|---|---|
| M1.5.1 — Setup Oracle Cloud Always Free: account + 1 VM ARM Ampere (4 vCPU, 24GB RAM) region São Paulo + bootstrap Linux (Ubuntu 22.04 LTS, UFW, fail2ban, unattended-upgrades) — playbook in 09-DEPLOYMENT sez. 4.4 | 3-4h | M0.2.5 |
| M1.5.2 — Dockerfile multi-stage build ARM64 (vedi 09-DEPLOYMENT sez. 3.3) + `.dockerignore` (sez. 3.4) | 1.5h | M1.2.11 |
| M1.5.3 — Setup Upstash Redis free tier + binding `REDIS_URL` in `.env` | 0.5h | M1.5.1 |
| M1.5.4 — Setup Tailscale (SSH sicuro VM, chiudi porta 22 pubblica) + creare `/opt/segmenta-mcp/.env` (chmod 600) con tutte le secrets (vedi 09-DEPLOYMENT sez. 4.5ter `.env.example`) | 1h | M1.5.3 |
| M1.5.4bis — Setup Caddyfile + docker-compose.yml in `/opt/segmenta-mcp/` (clone repo); `docker compose up -d`; verifica HTTPS auto via Let's Encrypt | 1h | M1.5.4 |
| M1.5.5 — DNS records `mcp-staging` e `mcp` (Cloudflare/altro) | 1h | M0.2.4 |
| M1.5.6 — Verifica TLS Let's Encrypt automatico | 0.5h | M1.5.5 |
| M1.5.7 — `deploy-staging.yml` GitHub Action smoke test | 1.5h | M1.5.5 |
| M1.5.8 — Deploy staging primo manual test | 1h | M1.5.7 |
| M1.5.9 — `deploy-production.yml` GitHub Action | 1h | M1.5.8 |
| M1.5.10 — First production deploy + smoke test | 1h | M1.5.9 |

#### M1.6 [P0] Validation end-to-end

| Task | Stima |
|---|---|
| M1.6.1 — Test manuale 4 tool via MCP Inspector contro production | 2h |
| M1.6.2 — Test integration con Claude Desktop (configurare server locale) | 1.5h |
| M1.6.3 — Test integration con Claude.ai web (Custom Connector add) | 1h |
| M1.6.4 — Test integration con ChatGPT Developer Mode | 1h |
| M1.6.5 — Verifica audit log per ogni chiamata test | 0.5h |
| M1.6.6 — UptimeRobot setup probe `/health` ogni 5 min | 0.5h |

#### M1.7 [P1] 30 query baseline primo run

| Task | Stima | Owner |
|---|---|---|
| M1.7.1 — Finalizzare lista 30 query (DECISION-OPEN-AN-001) | 2h | Alessio |
| M1.7.2 — Primo run baseline Claude.ai + ChatGPT (citation rate W0) | 3h | Alessio |
| M1.7.3 — Salvare risultato in `data/baseline_results/2026/W{N}/` | 0.5h | Alessio |
| M1.7.4 — Annotare baseline starting point per ognuna delle 30 query | 1h | Alessio |

#### M1.8 [P1] Submission Anthropic Directory (preparazione)

| Task | Stima | Owner |
|---|---|---|
| M1.8.1 — README pubblico bilingue del repo (D-GT-008) | 3h | Claudio + Romina |
| M1.8.2 — Logo 512x512 + 1024x1024 SVG | 2h | Stefany |
| M1.8.3 — Privacy policy MCP draft (`/mcp/privacy`) | 3h | Merari + Claudio |
| M1.8.4 — Terms of service MCP draft (`/mcp/terms`) | 2h | Merari |

### 5.4 Definition of Done

- [ ] Server live a `https://mcp.segmentamarketing.com/health` returns 200
- [ ] 4 tool Tier 1 funzionanti via MCP Inspector con dati reali (non placeholder)
- [ ] CI workflow passa (lint + test + type check + validate_data)
- [ ] Deploy automatico staging + production funzionante
- [ ] Test manuale Claude.ai Custom Connector: 4/4 tool callable e funzionanti
- [ ] Test manuale ChatGPT Developer Mode: 4/4 tool callable
- [ ] 30 query baseline primo run completato, dati archiviati
- [ ] README pubblico + logo + privacy + terms pronti per M3 submission
- [ ] Audit log mostra request_id correlato per ogni tool call test
- [ ] 0 errori 5xx negli ultimi 7gg in production

### 5.5 Output / Deliverable

- Repo GitHub pubblico live
- Server production live a `mcp.segmentamarketing.com`
- 4 file JSON dati popolati con info reali
- 30 query baseline starting point archiviato
- Tag git `v0.1.0` con release notes

### 5.6 Risk

- **R1.1**: Dati case study insufficienti (Merari non ottiene consensi) → `case_studies.json` con < 5 entry. Mitigazione: anonimizzazione obbligatoria di default per casi senza consenso esplicito (D-D-004).
- **R1.2**: Oracle Cloud Always Free deprecato o quota cambiata → ritardo deploy. Mitigazione: Hetzner VPS €4/mese o Railway $5/mese fallback (vedi 09-DEPLOYMENT sez. 4.1) — Dockerfile portabile, `docker-compose.yml` riusabile su qualsiasi VPS Linux.
- **R1.3**: Pydantic validation rejecta dati reali → JSON da rifare. Mitigazione: validation early in M1.4.6 prima di deploy.
- **R1.4**: Sito Hostinger di `segmentamarketing.com` non permette DNS modifica fluida → ritardo CNAME setup. Mitigazione: M0.2.4 chiusura DNS access prima di M1.

### 5.7 Stima ore totale M1

~20h effettive ÷ 2.5h/sett = **8 settimane calendar**.

(Se task M1.4 — popolare dati — richiede coinvolgimento team Segmenta che ha bandwidth limitato, può espandere a 10 settimane.)

---

## 6. M2 — Lead capture (Tier 2)

### 6.1 Goal

OAuth funzionante, 5 tool Tier 2 implementati, integrazioni Cal.com + HubSpot + Resend live, primi 5 lead reali catturati nel CRM Segmenta, privacy policy LFPDPPP pubblicata.

### 6.2 Status

🔒 **NOT STARTED** — predecessor M1.

### 6.3 Task

#### M2.1 [P0] Chiusure decisioni Merari pre-M2

| Task | Stima | Owner | Decisione |
|---|---|---|---|
| M2.1.1 — Conferma provider Booking (Cal.com vs Calendly) | 0.5h | Merari | DECISION-OPEN-IN-001 |
| M2.1.2 — Conferma provider CRM (HubSpot vs Pipedrive) | 0.5h | Merari | DECISION-OPEN-IN-002 |
| M2.1.3 — Conferma provider Email transactional | 0.5h | Claudio | DECISION-OPEN-IN-003 |
| M2.1.4 — Privacy policy LFPDPPP — legal review esterna (opzionale) | 3h | Merari | DECISION-OPEN-006 di MP |
| M2.1.5 — Setup account su provider scelti (API keys) | 2h | Claudio | M2.1.1-M2.1.3 |

#### M2.2 [P0] Layer auth implementazione

| Task | Stima | Dipendenze |
|---|---|---|
| M2.2.1 — `auth/storage.py` Redis wrapper tipizzato | 2h | M1.2.10 |
| M2.2.2 — `auth/rate_limit.py` sliding window Redis | 2.5h | M2.2.1 |
| M2.2.3 — `auth/registration.py` `/oauth/register` (RFC 7591) | 3h | M2.2.1 |
| M2.2.4 — `auth/discovery.py` `/.well-known/oauth-authorization-server` | 1h | M2.2.3 |
| M2.2.5 — `auth/authorize.py` `/oauth/authorize` con UI form HTML multi-locale | 4h | M2.2.3 |
| M2.2.6 — `auth/magic_link.py` generation + Redis state | 2h | M2.2.5 |
| M2.2.7 — Template email magic link (es-LATAM, es-MX, es-ES, en-US) | 3h | M2.2.6 |
| M2.2.8 — Callback handler `/oauth/callback` | 2h | M2.2.6 |
| M2.2.9 — `auth/jwt_handler.py` RS256 sign + verify | 2.5h | M2.2.1 |
| M2.2.10 — `/.well-known/jwks.json` JWKS endpoint | 1h | M2.2.9 |
| M2.2.11 — `auth/token.py` `/oauth/token` grant authorization_code | 3h | M2.2.9 |
| M2.2.12 — Refresh token rotation logic | 2h | M2.2.11 |
| M2.2.13 — `auth/revocation.py` `/oauth/revoke` | 1.5h | M2.2.11 |
| M2.2.14 — `auth/middleware.py` Bearer extraction + JWT verify | 2h | M2.2.9 |
| M2.2.15 — Audit log strutturato per ogni auth event | 1.5h | M2.2.14 |
| M2.2.16 — Test OAuth flow end-to-end (manuale + automated) | 3h | tutti M2.2.x |

#### M2.3 [P0] Integrazioni esterne

| Task | Stima | Dipendenze |
|---|---|---|
| M2.3.1 — `integrations/booking.py` interface astratta `BookingProvider` | 1h | M2.1.1 |
| M2.3.2 — Implementazione Cal.com (o Calendly) adapter | 4h | M2.3.1 |
| M2.3.3 — Webhook handler `/webhooks/calcom` con HMAC validation | 2h | M2.3.2 |
| M2.3.4 — `integrations/crm.py` interface astratta `CRMProvider` | 1h | M2.1.2 |
| M2.3.5 — Implementazione HubSpot v3 adapter (o Pipedrive) | 4h | M2.3.4 |
| M2.3.6 — Setup 10 HubSpot custom properties `mcp_*` (manuale dashboard) | 1h | Merari |
| M2.3.7 — `integrations/email.py` interface `EmailProvider` | 1h | M2.1.3 |
| M2.3.8 — Implementazione Resend (o SendGrid) adapter | 3h | M2.3.7 |
| M2.3.9 — Setup DKIM/SPF/DMARC DNS records | 2h | M2.3.8, Merari (DNS access) |
| M2.3.10 — Test deliverability M2 (100 email a domini MX/AR/CO/CL/PE) | 4h | M2.3.9 |
| M2.3.11 — `integrations/circuit_breaker.py` manuale Redis-backed | 2h | M2.2.1 |
| M2.3.12 — `integrations/slack.py` webhook notifier | 1.5h | M2.3.4 |
| M2.3.13 — `scripts/process_fallback_queue.py` per flush manuale | 2h | M2.3.4 |

#### M2.4 [P0] Implementazione 5 tool Tier 2

| Task | Stima | Dipendenze |
|---|---|---|
| M2.4.1 — `tools/tier2/calcular_presupuesto.py` + test | 3h | M2.3.5 |
| M2.4.2 — `tools/tier2/consultar_disponibilidad.py` + test | 2h | M2.3.2 |
| M2.4.3 — `tools/tier2/agendar_auditoria_gratuita.py` + test (timezone-aware) | 4h | M2.3.2, M2.3.5, M2.3.12 |
| M2.4.4 — `domain/crawler.py` BeautifulSoup4 implementation | 4h | — |
| M2.4.5 — `tools/tier2/diagnostico_seo_express.py` + test | 5h | M2.4.4, M2.3.8 |
| M2.4.6 — `tools/tier2/solicitar_propuesta_personalizada.py` + test | 4h | M2.3.5, M2.3.8, M2.3.12 |
| M2.4.7 — Template email `diagnostico_seo_report.html` | 2h | M2.4.5 |
| M2.4.8 — Template email `auditoria_confirmation.html` | 1.5h | M2.4.3 |
| M2.4.9 — Template email `propuesta_recibida.html` | 1.5h | M2.4.6 |

#### M2.5 [P0] Privacy & compliance

| Task | Stima | Owner |
|---|---|---|
| M2.5.1 — Privacy policy MCP testo finale (LFPDPPP primaria + GDPR/CCPA) | 4h | Merari + Claudio (+ legal review opzionale) |
| M2.5.2 — Pubblicazione su `segmentamarketing.com/mcp/privacy` | 1h | Team web Segmenta |
| M2.5.3 — Terms of service finale | 2h | Merari |
| M2.5.4 — Pubblicazione su `segmentamarketing.com/mcp/terms` | 0.5h | Team web Segmenta |
| M2.5.5 — Endpoint `/privacy/data-request` (M2 lightweight: email manuale) | 1h | Claudio |

#### M2.6 [P0] Test reale + validazione

| Task | Stima |
|---|---|
| M2.6.1 — Test OAuth flow completo con Claude.ai | 1h |
| M2.6.2 — Test OAuth flow completo con ChatGPT | 1h |
| M2.6.3 — Test ognuno dei 5 tool Tier 2 end-to-end | 3h |
| M2.6.4 — Test fallback queue (simulazione CRM down) | 1h |
| M2.6.5 — Test deliverability email reale (account personale + Merari) | 1h |
| M2.6.6 — Verifica 5 lead reali in HubSpot creati via MCP | — |

#### M2.7 [P1] Re-run 30 query baseline

| Task | Stima | Owner |
|---|---|---|
| M2.7.1 — 30 query baseline run W4 di M2 | 3h | Alessio |
| M2.7.2 — Confronto delta vs M1.7 baseline | 1h | Alessio |
| M2.7.3 — Decisione se SR-006 trigger se delta zero | 0.5h | Claudio |

### 6.4 Definition of Done

- [ ] OAuth flow completo funzionante: magic link → token → tool call
- [ ] Tutti i 5 tool Tier 2 testati end-to-end manualmente
- [ ] Almeno 5 lead reali generati via MCP visibili in HubSpot
- [ ] Test deliverability M2.3.10 conferma > 95% inbox rate sui domini target
- [ ] Privacy policy + Terms pubblicati e linkati dal server
- [ ] DKIM/SPF/DMARC verde su mxtoolbox
- [ ] Webhook Cal.com configurato + verificato
- [ ] Slack alerts test funzionanti su #leads-mcp e #alerts-mcp
- [ ] Fallback queue testata (simulazione CRM down) e lead recuperati
- [ ] 0 violazioni LFPDPPP nei test (audit log conferma email solo hash in log analitici)
- [ ] Test 30 query baseline mostra trend positivo o stabile

### 6.5 Output / Deliverable

- Server v0.2.0 con Tier 2 live
- 5+ lead reali in HubSpot tagged `mcp_*`
- Privacy policy + Terms live
- Tag git `v0.2.0`

### 6.6 Risk

- **R2.1**: Test deliverability fallisce → cambio provider necessario in mid-milestone. Mitigazione: Resend default + SendGrid fallback pronto.
- **R2.2**: Anthropic cambia spec MCP OAuth in M2 → refactoring necessario. Mitigazione: pin a versione protocol M1, migration controllata.
- **R2.3**: Merari blocca su privacy policy LFPDPPP per legal review → ritardo 2-4 settimane. Mitigazione: avviare legal review in M1.4.5.
- **R2.4**: Crawler `diagnostico_seo_express` triggera abuse-flag su siti grandi → blocco temporaneo. Mitigazione: user agent identificabile + rate limit per IP.
- **R2.5**: Bandwidth Claudio insufficiente per M2 (è il file più denso di lavoro) → estensione a 4-5 settimane. Accettato come risk realistico.

### 6.7 Stima ore totale M2

~35h ÷ 2.5h/sett = **14 settimane calendar**.

(Realistico assumendo che integrazioni esterne abbiano sempre qualche surprise di debug.)

---

## 7. M3 — GTM execution

### 7.1 Goal

Landing `/mcp` live. Banner CTA su sito principale. Blog post di lancio pubblicato in ES. Submission Anthropic Directory completata e idealmente approvata. Re-test 30 query con delta misurato vs M1.

### 7.2 Status

🔒 **NOT STARTED** — predecessor M2.

### 7.3 Task

#### M3.1 [P0] Landing page `/mcp`

| Task | Stima | Owner |
|---|---|---|
| M3.1.1 — Wireframe Figma di `/mcp` (mobile + desktop) | 4h | Stefany |
| M3.1.2 — Copy ES LATAM-neutral finale (8 sezioni) | 6h | Romina |
| M3.1.3 — Implementazione HTML/CSS responsive | 6h | Team web Segmenta o Claudio |
| M3.1.4 — Schema markup JSON-LD (SoftwareApplication + FAQPage + BreadcrumbList) | 2h | Alessio |
| M3.1.5 — 4 screenshot di conversazione Claude/ChatGPT in azione (Stefany editing) | 3h | Stefany |
| M3.1.6 — UTM tracking setup per CTAs | 1h | Alessio |
| M3.1.7 — Test SEO basic (PageSpeed, Lighthouse, schema validator) | 1.5h | Alessio |
| M3.1.8 — Deploy live a `segmentamarketing.com/mcp` | 1h | Team web Segmenta |

#### M3.2 [P0] Banner CTA su homepage Segmenta

| Task | Stima | Owner |
|---|---|---|
| M3.2.1 — Design banner mobile + desktop | 2h | Stefany |
| M3.2.2 — Copy variante 1 (informativa) + variante 2 (provocatoria) | 1.5h | Romina |
| M3.2.3 — Implementazione banner su homepage + sidebar blog | 3h | Team web Segmenta |
| M3.2.4 — A/B testing setup (default variante 1) | 1h | Alessio |

#### M3.3 [P0] Blog post di lancio

| Task | Stima | Owner |
|---|---|---|
| M3.3.1 — Outline detailed con Claudio | 1.5h | Romina + Claudio |
| M3.3.2 — Draft 2000-2500 parole | 6h | Romina |
| M3.3.3 — Revisione tecnica (Claudio) | 1h | Claudio |
| M3.3.4 — Revisione commerciale (Merari) | 1h | Merari |
| M3.3.5 — Revisione SEO (Alessio): keyword optimization, schema | 1.5h | Alessio |
| M3.3.6 — Asset visual (3-4 illustrazioni / screenshot) | 4h | Stefany |
| M3.3.7 — Cross-post draft per Medium + LinkedIn Article | 2h | Romina |
| M3.3.8 — Pubblicazione lunedì mattina CDMX | 0.5h | Romina |
| M3.3.9 — Cross-post Medium + LinkedIn + email newsletter | 2h | Romina |

#### M3.4 [P0] Anthropic Connector Directory submission

| Task | Stima | Owner |
|---|---|---|
| M3.4.1 — Demo video 1-2 min (screen recording + voice over) | 4h | Stefany + Claudio |
| M3.4.2 — Description finale per Directory (420 char target) | 1h | Romina + Claudio |
| M3.4.3 — Checklist submission (sez. 4.4 di `10-GTM.md`) verifica completa | 1h | Claudio |
| M3.4.4 — Submission via form Anthropic | 0.5h | Claudio |
| M3.4.5 — Email follow-up dopo 14 giorni se no response | 0.5h | Claudio |

#### M3.5 [P1] ChatGPT Apps submission

| Task | Stima |
|---|---|
| M3.5.1 — Studio attuali requisiti ChatGPT App Store (può essere cambiato) | 2h |
| M3.5.2 — Manifest file per OpenAI | 1h |
| M3.5.3 — Screenshot adapted per ChatGPT audience | 1.5h |
| M3.5.4 — Submission | 0.5h |

#### M3.6 [P1] Digital PR — first wave

| Task | Stima | Owner |
|---|---|---|
| M3.6.1 — Pitch list finalizzata con priority 1/2/3 | 3h | Romina + Alessio |
| M3.6.2 — Press kit pronto (logo, bio, screenshot, metrics base) | 2h | Stefany + Merari |
| M3.6.3 — Pitch email a ~10 pubblicazioni priority 1 (Merca2.0, InformaBTL, Forbes MX, Marketing4eCommerce ES, PuroMarketing, etc.) | 4h | Merari (autorevolezza CEO) |
| M3.6.4 — Follow-up 7 giorni dopo prima ondata | 2h | Romina |

#### M3.7 [P0] Re-test 30 query baseline

| Task | Stima | Owner |
|---|---|---|
| M3.7.1 — Run 30 query baseline W4 M3 | 3h | Alessio |
| M3.7.2 — Confronto trend M1 W0 vs M3 W4 (target ≥ 30% Claude, ≥ 25% ChatGPT) | 1h | Alessio |
| M3.7.3 — Confronto delta 10 query MX (target ≥ 40%) | 0.5h | Alessio |
| M3.7.4 — Decisione SR-006 / SR-010 trigger se sotto soglia | 0.5h | Claudio |
| M3.7.5 — Report mensile a Merari + decisione strategica | 1.5h | Claudio |

### 7.4 Definition of Done

- [ ] Landing `/mcp` live con Lighthouse score > 85
- [ ] Schema markup valida su Google Rich Results Test
- [ ] Banner CTA visibile su homepage Segmenta
- [ ] Blog post pubblicato + cross-posted su 3+ canali
- [ ] Anthropic Directory submission completata (in attesa di review)
- [ ] ChatGPT App submission completata
- [ ] First wave pitch (~10 email) inviata
- [ ] 30 query baseline mostra soglia Claude ≥ 30%, ChatGPT ≥ 25%, MX ≥ 40%
- [ ] Report mensile inviato a Merari con trend visibile

### 7.5 Output / Deliverable

- Landing `/mcp` live
- Banner CTA live
- Blog post pubblicato
- Submission Anthropic + ChatGPT inviate
- Press kit completo
- Report metrics M3 a Merari

### 7.6 Risk

- **R3.1**: Anthropic Directory submission rifiutata 2x → SR-001 trigger, sprint dedicato. Stima ritardo: +3-4 settimane.
- **R3.2**: 30 query baseline non mostra miglioramento → SR-006 trigger, freeze Tier 3 espansione.
- **R3.3**: Pitch wave 1 zero coverage → Romina seconda wave + pivot tono pitch.
- **R3.4**: Team web Segmenta non disponibile per landing → Claudio implementa direttamente (+3-5h).

### 7.7 Stima ore totale M3

~20h ÷ 2.5h/sett = **8 settimane calendar**.

---

## 8. M4 — Tier 3 + analytics dashboard

### 8.1 Goal

5 tool Tier 3 implementati. Dashboard analytics interna live. Tracking Share of Model parzialmente automatizzato.

### 8.2 Status

🔒 **NOT STARTED** — predecessor M3.

### 8.3 Task

#### M4.1 [P0] Implementazione 5 tool Tier 3

| Task | Stima | Dipendenze |
|---|---|---|
| M4.1.1 — `tools/tier3/obtener_caso_por_pais.py` + test (granularità subregion) | 3h | M1.3 |
| M4.1.2 — `tools/tier3/whatsapp_directo.py` + test (URL encoding) | 2h | — |
| M4.1.3 — Dataset `data/competitors_dataset.json` curato | 3h | Merari + Alessio |
| M4.1.4 — `tools/tier3/compare_agencies.py` + test | 4h | M4.1.3 |
| M4.1.5 — `integrations/seo_data.py` adapter DataForSEO (o equivalente) | 4h | DECISION-OPEN-IN-004 chiusa |
| M4.1.6 — `tools/tier3/analizar_competencia.py` (modo basico + completo) | 5h | M4.1.5 |
| M4.1.7 — Soft credit system implementation (Redis counter) | 2h | M4.1.6 |
| M4.1.8 — Cost cap monitoring + degrade automatico | 1.5h | M4.1.6 |
| M4.1.9 — `data/research_threads.json` setup iniziale | 1h | Romina |
| M4.1.10 — `tools/tier3/share_research.py` + test (email hash) | 3h | M4.1.9 |

#### M4.2 [P0] Decisioni Merari pre-M4

| Task | Stima | Owner |
|---|---|---|
| M4.2.1 — Conferma numeri WhatsApp per país | 0.5h | Merari (DECISION-OPEN-T3-001) |
| M4.2.2 — Conferma provider SEO data API | 0.5h | Merari (DECISION-OPEN-IN-004) |
| M4.2.3 — Threshold research_publication (default 30) | 0.5h | Romina (DECISION-OPEN-T3-003) |
| M4.2.4 — Re-approval budget se M3-M4 cost > $30/mese | 0.5h | Merari (DECISION-OPEN-DE-008) |

#### M4.3 [P0] Dashboard analytics interna

| Task | Stima | Owner |
|---|---|---|
| M4.3.1 — `scripts/generate_dashboard.py` aggregation logic | 5h | Claudio |
| M4.3.2 — `templates/dashboard.html` con 5 sezioni | 4h | Claudio |
| M4.3.3 — GitHub Action cron daily generation | 1.5h | Claudio |
| M4.3.4 — Upload su `admin.segmentamarketing.com/mcp-dashboard.html` (basic auth) | 2h | Team web Segmenta + Claudio |
| M4.3.5 — `scripts/dashboard_drill.py` CLI per drill-down | 3h | Claudio |
| M4.3.6 — Setup audit log per accesso analytics | 1h | Claudio |

#### M4.4 [P1] Automazione 30 query baseline

| Task | Stima | Dipendenze |
|---|---|---|
| M4.4.1 — Script `scripts/run_baseline_queries.py` con Anthropic API + OpenAI API | 4h | API keys disponibili |
| M4.4.2 — GitHub Action weekly cron run | 1h | M4.4.1 |
| M4.4.3 — Output aggregato auto-popolato in dashboard | 1.5h | M4.3.1 |
| M4.4.4 — Confronto trend M3 vs M4 automatizzato | 1h | M4.4.2 |

#### M4.5 [P1] Report mensile auto

| Task | Stima |
|---|---|
| M4.5.1 — `scripts/monthly_report.py` con template HTML | 4h |
| M4.5.2 — GitHub Action cron primo del mese | 1h |
| M4.5.3 — Test send a Merari + adjustment | 1h |

#### M4.6 [P2] WhatsApp Business API attivazione (opzionale)

| Task | Stima | Dipendenze |
|---|---|---|
| M4.6.1 — Setup account Twilio/MessageBird/360dialog | 2h | DECISION-OPEN-IN-007 |
| M4.6.2 — Verifica WhatsApp Business profilo | 2h | Merari |
| M4.6.3 — Webhook inbound message handler | 3h | — |
| M4.6.4 — Auto-reply primo messaggio post-link click | 2h | — |

#### M4.7 [P1] Re-test 30 query baseline M4

| Task | Stima | Owner |
|---|---|---|
| M4.7.1 — Run 30 query (automatizzato se M4.4 fatto, altrimenti manuale) | 1h auto / 3h manual | Alessio o cron |
| M4.7.2 — Confronto trend ultimi 4 mesi | 1h | Alessio |
| M4.7.3 — Decisione bump Anthropic submission se sotto soglia | 0.5h | Claudio |

#### M4.8 [P2] Digital PR — second wave

| Task | Stima | Owner |
|---|---|---|
| M4.8.1 — Second wave pitch (~15 pubblicazioni priority 2) | 4h | Romina |
| M4.8.2 — Eventuali interview / quotes per coverage | variabile | Merari |
| M4.8.3 — Documentazione menzioni esterne | 1h | Romina |

### 8.4 Definition of Done

- [ ] Tutti i 5 tool Tier 3 funzionanti e testati end-to-end
- [ ] Dashboard analytics live e accessibile a Claudio + Merari + Alessio
- [ ] 30 query baseline automatizzate (run settimanale senza intervento)
- [ ] Report mensile prima edizione consegnata a Merari
- [ ] WhatsApp Business API attivata o documentata decisione di rimandare
- [ ] ≥ 1 menzione esterna in pubblicazione di settore documentata
- [ ] Cost cap mensile non superato (verificato fine M4)
- [ ] KPI MASTER-PLAN soglie raggiunte o trend positivo verso soglie

### 8.5 Output / Deliverable

- Server v0.4.0 con Tier 3 live
- Dashboard live operativa
- Submission Anthropic Directory approvata (target)
- Report metrics ufficiale M4 a Merari
- Tag git `v0.4.0`

### 8.6 Risk

- **R4.1**: SEO data API provider scelto ha rate limit incompatibile → cambio provider mid-milestone.
- **R4.2**: Cost SEO API esplode → cap raggiunto, freeze automatic.
- **R4.3**: WhatsApp Business verification fallisce → feature rimandata a M5.
- **R4.4**: Dashboard troppo lenta a generare → ottimizzazione query Redis, eventuale move a Plausible Cloud anticipato.

### 8.7 Stima ore totale M4

~30h ÷ 2.5h/sett = **12 settimane calendar**.

---

## 9. M5 — Optimization (ongoing)

### 9.1 Goal

Refactoring guidato dai dati di utilizzo. Espansione content (EN blog, EN landing). A/B testing. Mantenimento e iteration continua.

### 9.2 Status

🔒 **NOT STARTED** — predecessor M4. Inizio target: ~5 mesi dopo M4.

### 9.3 Task — non più strutturato come milestone discreta, ma backlog continuo

#### M5.1 [P1] Content freshness

- Aggiornare `benchmarks.json` Q-end ogni trimestre.
- Aggiungere 2-3 nuovi case study ogni trimestre.
- Refresh `glosario.json` con nuovi termini emergenti (es. nuovi standard MCP).

#### M5.2 [P1] Tool description A/B testing

- Infrastruttura A/B per tool descriptions (DECISION-OPEN-AN-010).
- Test 2 varianti per i tool con citation rate basso.

#### M5.3 [P2] Espansione EN

- Blog post lancio versione EN (DECISION-OPEN-009 di MP).
- Landing `/mcp/en` localizzata.
- Tool description EN parallel (DECISION-OPEN-T1-004).

#### M5.4 [P2] Hot reload dati senza restart

- Implementare cache invalidation senza restart (DECISION-OPEN-D-003).

#### M5.5 [P3] Public dashboard / status page

- Pagina pubblica con uptime e metriche aggregate (DECISION-OPEN-AN-007).

#### M5.6 [P3] Espansione Brasile (post non-goal v1)

- Aggiungere `BR` agli enum `Pais` e `Locale`.
- Traduzione tool descriptions in portoghese.
- Compilazione benchmarks BR.

### 9.4 Definition of Done M5

M5 non ha DoD in senso classico. Cadenza:
- Review trimestrale con Merari per priorità.
- Sprint di 2-3 settimane ognuno su task specifici dal backlog.

---

## 10. Dipendenze cross-milestone

### 10.1 Catena di dipendenze critiche

```
M0.2.1 (budget Merari) ─┐
M0.2.2 (sede legale)    │
M0.2.3 (repo pubblico)  ├─▶ M1 (può partire)
M0.2.4 (DNS access)     │
M0.2.5 (GitHub account) ─┘

M1.4 (dati reali)       ─▶ M1.6 (validation E2E)
M1 completo             ─▶ M2

M2.1 (provider choice)  ─▶ M2.2-M2.4 (implementation)
M2.3.10 (deliverability)─▶ M2.4.5 (diagnostico_seo)
M2.5 (privacy LFPDPPP)  ─▶ M2.6 (validation reale)
M2 completo             ─▶ M3

M3.1 (landing)          ─┐
M3.2 (banner)           ├─▶ M3.4 (Anthropic submission)
M3.3 (blog post)        ─┘
M3 completo             ─▶ M4

M4.2 (decisioni)        ─▶ M4.1 (Tier 3 implementation)
```

### 10.2 Mappa decisioni di Merari pendenti

Lista cronologica di quando ogni decisione deve essere chiusa per non bloccare il progetto:

| Quando | Decisione | Bloccato fino a |
|---|---|---|
| Pre-M1 | Budget M0-M4, sede legale, repo pubblico, DNS, GitHub | M1 kickoff |
| Pre-M2 | Booking provider, CRM provider, email provider | M2.2 implementation |
| Durante M2 | Privacy policy legal review | M2.5 publish |
| Pre-M3 | DNS records, landing approval design | M3.1 implementation |
| Pre-M4 | WhatsApp numeri, SEO API provider, budget bump $30→$65 | M4.1 implementation |

### 10.3 Bandwidth team Segmenta

Stima del coinvolgimento team Segmenta per milestone (ore-uomo):

| Persona | M0 | M1 | M2 | M3 | M4 | M5 |
|---|---|---|---|---|---|---|
| **Claudio (dev solo)** | 7h | 20h | 35h | 8h | 30h | 5h/sett |
| **Merari** | 4h | 6h | 5h | 4h | 3h | 1h/sett |
| **Alessio** | 1h | 5h | 1h | 5h | 3h | 1h/sett |
| **Romina** | 1h | 3h | 1h | 12h | 4h | 2h/sett |
| **Stefany** | 0h | 2h | 0h | 10h | 1h | 0.5h/sett |
| **Team web Segmenta** | 0h | 2h | 1h | 6h | 2h | variabile |

### 10.4 Bottleneck previsti

- **M1.4 (dati reali)**: Merari + Romina sono il bottleneck. 7h totali in poche settimane può essere stretto.
- **M2.5.1 (privacy policy)**: legal review Messico può durare 2-4 settimane.
- **M3.3 (blog post)**: 12h di Romina concentrate.
- **M4.1 (Tier 3 dev)**: 30h di Claudio in 12 settimane = 2.5h/sett perfettamente al ritmo.

---

## 11. Quality gates

Definizioni standard di "ready for production" cross-milestone.

### 11.1 Code quality gate

Da passare prima di ogni release production:

- [ ] CI green (lint + test + type check)
- [ ] Coverage ≥ 80% overall, ≥ 90% domain layer
- [ ] No `# type: ignore` non giustificato
- [ ] No `print()` in code production (solo in `scripts/`)
- [ ] CHANGELOG.md aggiornato
- [ ] Smoke test post-deploy passa

### 11.2 Data quality gate

Da passare prima di ogni release con modifiche a `data/*.json`:

- [ ] `scripts/validate_data.py` passa senza errori
- [ ] `_meta.data_version` bumped
- [ ] `_meta.ultima_actualizacion` aggiornata
- [ ] Cross-reference check (servicios_aplicados → services.json) passa
- [ ] Hard rule consensimiento per casi pubblici verificata

### 11.3 Security quality gate

Da passare prima di ogni release production:

- [ ] No secret in repo (verificato con git-secrets o equivalent)
- [ ] Pre-commit hook attivo
- [ ] Dependabot 0 alert critici
- [ ] JWKS endpoint pubblico funzionante
- [ ] HSTS abilitato (verificato con ssllabs)

### 11.4 Privacy quality gate

Da passare prima di M2 production (e ad ogni release rilevante):

- [ ] Privacy policy live e accessibile
- [ ] Email loggati come hash (verificato con grep su log)
- [ ] Endpoint `/privacy/data-request` documentato
- [ ] Cross-border SCC documentate
- [ ] Audit log retention 90gg rispettato

---

## 12. Comunicazione e cadenza

### 12.1 Cadenza interna

| Cadenza | Cosa | Owner |
|---|---|---|
| **Continuous** | Aggiornamento SESSION-STATE.md | Claudio + Claude Code |
| **Daily** | Check dashboard interna (M4+) | Claudio |
| **Weekly** | Aggiornamento progress in `SESSION-STATE` o issue tracker | Claudio |
| **Bi-weekly** | Sync 15-30 min con Merari su status | Claudio + Merari |
| **Monthly** | Report auto-generato a Merari (M4+) | scripts |
| **Quarterly** | Presentation a Merari (decisioni strategiche) | Claudio |

### 12.2 Comunicazione issue critici

Stati che richiedono comunicazione immediata a Merari:

- Server production down > 1h
- Privacy concern (LFPDPPP / GDPR potential violation)
- Cost spike > 50% del budget atteso
- Anthropic submission rifiutata (1x = info, 2x = SR-001)
- Lead arrivato e non processato dal team > 48h (verso SR-005)

### 12.3 Documentazione incidents

Ogni incident P0/P1 (sez. 13 di `09-DEPLOYMENT.md`) genera `Docs/incidents/YYYY-MM-DD-titolo.md` con:
- Sintomi
- Impatto (utenti, tempo)
- Root cause
- Risoluzione
- Lessons learned
- Action items

---

## 13. Versioning di questo documento

| Versione | Data | Autore | Note |
|---|---|---|---|
| 1.0 | 2026-05-10 | Claude (proposta) + Claudio (revisione) | Prima stesura: M0-M5 dettagliato con ~215 task granulari, stime ore, dipendenze cross-milestone, quality gates, cadenza comunicazione. Timeline ricalibrata realistica: ~11 mesi M0→M4 (vs 12-13 settimane MASTER-PLAN v1.0/v1.1 — discrepanza segnalata in sez. 3, HC-001). |
| 1.1 | 2026-05-11 | Claude (harmony pass M0.3) + Claudio (review) | **HC-001 risolta**: MASTER-PLAN bumped a v1.2 con timeline ~6-7 mesi (assume Claude Code scrive codice). MILESTONES rimane source of truth granulare; ora coerente con MASTER. **HC-009**: linea 113 conteggio file aggiornato a 12 numerati + MILESTONES + SESSION-STATE + README. M0.1.13 status ✅. M0.3 (harmony pass) status ✅ con tutti subtask completati. M0.1.15 nuovo task per README aggiornato. |
| 1.2 | 2026-05-11 | Claude + Claudio (chiusura M0.2.1) | **M1.5.1-M1.5.4 aggiornati**: Setup hosting passa da Railway a Fly.io free tier. M1.5.1 ora include creazione 2 Fly.io app + region MEX (prod) + MIA (staging). M1.5.3 setup Upstash Redis (Fly.io non ha Redis add-on integrato). M1.5.4 secrets via `flyctl secrets set`. **R1.2 risk** rivisto: ora Fly.io down → fallback Railway. Allineato con MASTER v1.3 e 09-DEPLOYMENT v1.2. |
| 1.3 | 2026-05-11 | Claude + Claudio (ricalibrazione hosting Oracle Cloud) | **M1.5.1-M1.5.4bis riscritti**: Setup hosting passa da Fly.io a **Oracle Cloud Always Free** (D-MP-002 v1.4). M1.5.1 ora 3-4h (include bootstrap VPS Ubuntu + UFW + fail2ban). M1.5.4 include Tailscale SSH + .env con secrets locale. M1.5.4bis nuovo task per Caddyfile + docker-compose.yml + verifica HTTPS Let's Encrypt. R1.2 risk: ora Oracle Always Free deprecato → fallback Hetzner/Railway. Allineato con MASTER v1.4 e 09-DEPLOYMENT v1.3. |

---

## Note per il changelog

🟢 **HC-001 RISOLTA in harmony pass M0.3 (2026-05-11)**: il MASTER-PLAN è stato bumped a v1.2 con timeline ricalibrata a ~6-7 mesi M0→M4 (assumendo Claude Code scrive codice e Claudio fa review). MILESTONES e MASTER-PLAN ora sono **coerenti**.

`MILESTONES.md` resta **source of truth** delle stime operative granulari (task per task, dipendenze, owner). `MASTER-PLAN.md` sez. 7 è la sintesi macro per stakeholder.

---

**Fine MILESTONES.md v1.1.**
