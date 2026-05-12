# SESSION STATE

> **File vivo** — aggiornato continuamente durante lo sviluppo del progetto. Apri questo file all'inizio di ogni sessione di lavoro per orientarti rapidamente.

| Campo | Valore |
|---|---|
| **Progetto** | Segmenta MCP Server |
| **Versione blueprint** | v1.4 (deploy live su Cloud Run + custom domain; MASTER v1.5) |
| **Versione server** | **v0.0.1 LIVE** su https://mcp.segmentamarketing.com |
| **Status macro** | 🟢 **M1.5 COMPLETATO** — server live, TLS automatico, auto-deploy pipeline operativo |
| **Ultima modifica** | 2026-05-13 |
| **Prossima azione** | **M1.2** kickoff: implementare i 4 tool Tier 1 FastMCP (obtener_servicios, caso_de_estudio, benchmark_sector, glosario_marketing) |
| **Documenti governanti** | `00-MASTER-PLAN.md` v1.5 + tutti i 12 file numerati + `MILESTONES.md` |

---

## 1. Scopo di questo file

`SESSION-STATE.md` è il **dashboard testuale** del progetto. Risponde in 30 secondi a 4 domande quando torni dopo una pausa:

1. *"A che punto sono?"* — sezione 3 (Snapshot corrente)
2. *"Cosa devo fare adesso?"* — sezione 4 (Prossimi step)
3. *"Cosa è bloccato e perché?"* — sezione 5 (Blocker attivi)
4. *"Cosa è stato deciso di recente?"* — sezione 6 (Decisioni recenti)

Differenza con `MILESTONES.md`: `MILESTONES.md` è il piano completo (cosa va fatto), `SESSION-STATE.md` è lo stato corrente (cosa è stato fatto e cosa serve dopo).

---

## 2. Come usare questo file

### 2.1 Apertura sessione

1. Apri `SESSION-STATE.md` come primo file.
2. Leggi sez. 3 (Snapshot), sez. 4 (Prossimi step), sez. 5 (Blocker).
3. Apri il file specifico della milestone corrente in `MILESTONES.md` per dettaglio task.
4. Apri eventuali file blueprint rilevanti per quel task.

### 2.2 Chiusura sessione

1. Aggiorna sez. 3 con cosa è stato completato.
2. Aggiorna sez. 4 con il prossimo step concreto.
3. Aggiorna sez. 5 se hai scoperto nuovi blocker.
4. Aggiorna sez. 6 se hai preso decisioni canoniche.
5. Bump `Ultima modifica` nella tabella header.

### 2.3 Quando aggiornare durante la sessione

Non ogni 5 minuti. Aggiorna in 3 momenti:
- Quando completi un task (specie se P0/P1)
- Quando trovi un blocker
- Quando prendi una decisione canonica

### 2.4 Chi può aggiornarlo

- **Claudio**: sempre.
- **Claude Code**: solo su istruzione esplicita di Claudio. Mai aggiornamenti speculativi.
- **Altri team Segmenta**: no — Claudio aggiorna a nome del team.

---

## 3. Snapshot corrente

### 3.1 Status milestone

| Milestone | Status | Completion % | Note |
|---|---|---|---|
| **M0 — Foundation** | 🟢 QUASI COMPLETO | 99% | 14/14 task M0.1 completi; M0.3 (harmony pass) completato; M0.2.1 ($0 budget + Oracle Cloud Always Free), M0.2.2 (Messico), M0.2.5 (org GitHub `segmenta-ai`) chiuse 2026-05-11; restano BL-004 (DNS access via Merari) |
| **M1 — MVP Tier 1** | 🔒 NOT STARTED | 0% | Aspetta M0 chiusura |
| **M2 — Lead capture** | 🔒 NOT STARTED | 0% | — |
| **M3 — GTM** | 🔒 NOT STARTED | 0% | — |
| **M4 — Tier 3 + analytics** | 🔒 NOT STARTED | 0% | — |
| **M5 — Optimization** | 🔒 NOT STARTED | 0% | — |

### 3.2 File blueprint consegnati

| File | Versione | Status | Note |
|---|---|---|---|
| `00-MASTER-PLAN.md` | v1.4 | ✅ | Focus LATAM/MX/US/ES, privacy LFPDPPP, timeline ~6-7 mesi (HC-001), hosting Oracle Cloud Always Free (D-MP-002 v1.4) |
| `01-ARCHITECTURE.md` | v1.3 | ✅ | 5 layer, stack FastMCP+Python+**Oracle Cloud Always Free** + Caddy + Docker Compose |
| `02-CONVENTIONS.md` | v1.1 | ✅ | Bilingue IT/ES, ruff+mypy strict, Conventional Commits, slug pattern esplicito |
| `03-DATA-MODEL.md` | v1.1 | ✅ | 5 file JSON (incluso competitors_dataset), Pydantic v2, MercadoSubregional tipizzato |
| `04-TOOLS-TIER1.md` | v1.0 | ✅ | 4 tool public con descriptions ES LATAM-neutral |
| `05-TOOLS-TIER2.md` | v1.0 | ✅ | 5 tool gated, OAuth required, 21 decisioni D-T2 confermate |
| `06-TOOLS-TIER3.md` | v1.1 | ✅ | 5 tool avanzados, mix gating, pais_o_subregion tipizzato |
| `07-AUTH-OAUTH.md` | v1.0 | ✅ | OAuth 2.0 dynamic, magic link, RS256 |
| `08-INTEGRATIONS.md` | v1.2 | ✅ | Cal.com, HubSpot, **Resend confermato**, Slack, DataForSEO. Adapter pattern. |
| `09-DEPLOYMENT.md` | v1.3 | ✅ | **Oracle Cloud Always Free VPS**, Docker Compose + Caddy + Watchtower + Tailscale, ghcr.io image registry, smoke test cron |
| `10-GTM.md` | v1.1 | ✅ | 7 canali, 30+ pubblicazioni target, description Anthropic Directory ottimizzata |
| `11-ANALYTICS.md` | v1.1 | ✅ | Dashboard interna, 30 query baseline, attribution AI, 5 dimensioni KPI |
| `MILESTONES.md` | v1.3 | ✅ | M0-M5 dettagliato, ~215 task granulari, M1.5 setup Oracle Cloud VPS (~3-4h bootstrap) |
| `SESSION-STATE.md` | v1.1 | ✅ | Questo file — aggiornato 2026-05-11 post harmony pass |
| `README.md` | — | ✅ | Entry point pubblico, aggiornato 2026-05-11 (pivot LATAM, valuta USD) |

### 3.3 Code base

- Repo GitHub: **non ancora creato** (dependency M0.2.5)
- Server live: **non ancora deployato**
- Test passing: n/a (no code yet)
- Coverage: n/a

### 3.4 Dati popolati

- `data/services.json`: **placeholder draft** (in scaffold di prima conversazione, non in repo blueprint)
- `data/case_studies.json`: **placeholder draft**
- `data/benchmarks.json`: **placeholder draft**
- `data/glosario.json`: **placeholder draft**

I dati reali verranno popolati in **M1.4** con coinvolgimento Merari/Romina/Alessio.

### 3.5 Decisioni Merari pending (blocker M1 kickoff)

5 decisioni da chiudere prima di poter iniziare M1 — status post 2026-05-11:

- [x] **M0.2.1** ✅ Budget infra: target **$0/mese perpetuo** (Oracle Cloud Always Free + Upstash + Resend free tier); hard cap $30/mese. D-MP-002 ricalibrata 2 volte: Railway → Fly.io (v1.3) → Oracle Cloud Always Free (v1.4) dopo che Fly.io ha eliminato free tier perpetuo nel 2024.
- [x] **M0.2.2** ✅ Sede legale: **Messico** confermato. LFPDPPP primaria, Merari = responsable del tratamiento.
- [x] **M0.2.3** ✅ Repo GitHub pubblico (D-MP-008 confermato).
- [ ] **M0.2.4** Accesso DNS `segmentamarketing.com` — pending Merari (creazione CNAME `mcp.segmentamarketing.com` → `segmenta-mcp-prod.fly.dev` quando deploy ready in M1.1).
- [x] **M0.2.5** ✅ GitHub account host: org dedicata **`github.com/segmenta-ai/segmenta-mcp`** (Claudio crea org, Merari co-owner).

---

## 4. Prossimi step concreti

### 4.1 Step immediato (next session)

**Owner**: Claudio.

**Cosa fare**:
1. ✅ **Harmony pass M0.3 completato** il 2026-05-11. 12 incongruenze identificate (HC-001 → HC-012), tutte risolte tramite edit puntuali ai file blueprint. Vedi sez. 7 sotto.
2. Preparare meeting con Merari per chiudere **M0.2.1-M0.2.5** (decisioni canoniche bloccanti):
   - Doc 1-pager con sintesi progetto + ROI atteso + costo + decisioni richieste.
3. In stesso meeting Merari, chiudere **DECISION-OPEN-002 / -003 / -004** (provider Booking / CRM / Email): scoperto durante harmony pass che `08-INTEGRATIONS.md` tratta Cal.com / HubSpot / Resend come "default candidato" — il file ha disclaimer adapter pattern, ma chiudere le decisioni rimuove ambiguità per coding M2.

**Tempo stimato**: 1h preparazione doc + 30 min meeting con Merari.

### 4.2 Step dopo (post-M0 completion)

Una volta chiuse M0.2 e M0.3:
1. Tag git `blueprint-v1-complete`.
2. Backup fisico dei file (regola Claudio).
3. Kickoff M1 — setup repo GitHub (M1.1.1).

### 4.3 Aggiornamento timeline reale

Annotazione importante post-conversazione 2026-05-10:

> **Claudio**: "il codice lo scriverà tutto Claude Code, pertanto credo serva molto meno tempo per il completamento del progetto"

**Implicazione**: le stime ore in `MILESTONES.md` sono pensate come **ore-uomo equivalenti**, ma se Claude Code scrive il codice, il bottleneck reale diventa il **tempo di review e validation di Claudio**, non scrittura.

**Stima rivista (da consolidare in harmony pass)**:
- Tempo review tipicamente 30-40% del tempo di scrittura.
- Plus tempo di setup tool/account/decisione che resta uguale.

Rivisitazione plausibile:
| Milestone | Ore-uomo dichiarate | Tempo review effettivo Claudio | Tempo settimane (a 2.5h/sett review) |
|---|---|---|---|
| M0 | 15h (blueprint) | già incluso | 2 settimane |
| M1 | 20h | ~10h review + 5h setup | ~6 settimane |
| M2 | 35h | ~15h review + 5h setup | ~8 settimane |
| M3 | 20h | ~5h review + 8h content/design | ~5 settimane |
| M4 | 30h | ~12h review + 5h setup | ~7 settimane |
| **TOTALE M0→M4** | **120h** | **~65h** | **~6-7 mesi** (vs ~11 mesi originali) |

Discrepanza con MASTER-PLAN sez. 7 (12-13 settimane) **rimane significativa**. Possibili spiegazioni:
- MASTER-PLAN sez. 7 era ottimistica (target aggressivo, non realista)
- O assumeva pace 5+h/sett invece di 2.5h/sett

**Action item harmony pass**: aggiornare MASTER-PLAN sez. 7 con stima ricalibrata 6-7 mesi e nota su assunzioni.

---

## 5. Blocker attivi

### 5.1 Blocker P0 (impediscono M1 kickoff)

| ID | Blocker | Owner | Status | Età |
|---|---|---|---|---|
| BL-001 | ~~Decisione Merari su budget M0-M4~~ | Merari | 🟢 Chiuso 2026-05-11: $0 target perpetuo, Oracle Cloud Always Free (M0.2.1) | 1gg |
| BL-002 | ~~Decisione Merari su sede legale Messico LFPDPPP~~ | Merari | 🟢 Chiuso 2026-05-11: Messico confermato (M0.2.2) | 1gg |
| BL-003 | ~~Decisione Merari su repo GitHub pubblico~~ | Merari | 🟢 Chiuso 2026-05-11: pubblico confermato (D-MP-008) | 1gg |
| BL-004 | Accesso DNS `segmentamarketing.com` (Hostinger) | Merari | 🟢 Parzialmente chiuso 2026-05-12: Merari ha aggiunto record DNS Resend (DKIM + SPF + MX), dominio mcp.segmentamarketing.com VERIFIED. Resta A record `mcp.segmentamarketing.com` → IP VM Oracle (da aggiungere subito dopo provisioning VM, M1.5.1). DECISION-OPEN-DE-001 chiusa: provider DNS = **Hostinger** (non Cloudflare come presunto). | 2gg |
| BL-005 | ~~Decisione GitHub account host~~ | Merari + Claudio | 🟢 Chiuso 2026-05-11: org `segmenta-ai` (M0.2.5) | 1gg |

### 5.2 Blocker P1 (impediscono M2)

| ID | Blocker | Owner | Status |
|---|---|---|---|
| BL-006 | Conferma Booking provider (Cal.com vs Calendly) | Merari | 🟡 In stand-by: 08-INTEGRATIONS sez. 4 ha adapter pattern (HC-004), default Cal.com. Decisione Merari serve per coding M2.2 ma non blocca M1. |
| BL-007 | Conferma CRM provider (HubSpot vs Pipedrive) | Merari | 🟡 In stand-by: 08-INTEGRATIONS sez. 5 adapter pattern, default HubSpot. Idem BL-006. |
| BL-008 | ~~Conferma Email transactional provider~~ | Claudio | 🟢 Chiuso 2026-05-11: **Resend** free tier confermato (DECISION-OPEN-004 chiusa) |

### 5.3 Risk attivi (non bloccanti ma da monitorare)

| ID | Risk | Owner | Mitigazione |
|---|---|---|---|
| RI-001 | ~~Discrepanza timeline MASTER-PLAN vs MILESTONES~~ | Claudio | 🟢 Risolto in harmony pass M0.3 (HC-001) |
| RI-002 | Case study insufficienti per M1.4 (Merari potrebbe non ottenere consensi a tempo) | Merari | Anonimizzazione di default; SR-004 enforcement |
| RI-003 | Bandwidth Claudio multi-progetto (Keeper v2, Chirsan, Numely, MePA) | Claudio | Pace dichiarato 2.5h/sett; stop rule SR-008 |
| RI-004 | Provider integrazioni non chiusi (Cal.com/HubSpot/Resend) — coding M2 deve usare Adapter Pattern | Claudio + Merari | Disclaimer adapter pattern in 08-INTEGRATIONS sez. 4.1/5.1/6.1 (HC-004); chiudere DECISION-OPEN-002/003/004 in meeting Merari pre-M2 |

---

## 6. Decisioni recenti

### 6.1 Decisioni canoniche locked durante M0

Liste integrate dai vari file blueprint. Vedere file specifico per dettaglio motivazione.

#### Dal MASTER-PLAN (D-MP)

D-MP-001 (lingua bilingue IT prosa + ES tecnico), D-MP-002 (FastMCP Python + Railway), D-MP-003 (subdomain `mcp.segmentamarketing.com`), D-MP-004 (Tier system 3 livelli), D-MP-005 (pace 2-3h/sett), D-MP-006 (solo Segmenta no multi-tenant), D-MP-007 (tool descriptions ES neutro/LATAM), D-MP-008 (repo pubblico), D-MP-009 (MIT license), D-MP-010 (Conventional Commits + squash), D-MP-011 (SemVer), D-MP-012 (OAuth 2.0 dynamic), D-MP-013 (JSON file, no DB v1), D-MP-014 (privacy LFPDPPP primaria + GDPR/CCPA addendum), D-MP-015 (rate limit 60/Tier 1, 10/Tier 2-3), D-MP-016 (mercati primari MX/US/LATAM/ES), D-MP-017 (blog solo ES LATAM-first), D-MP-018 (USD valuta primaria).

#### Dall'ARCHITECTURE (D-A)

D-A-001 (Python 3.12 + FastMCP 3.2+), D-A-002 (single container monolite), D-A-003 (stateless server + Redis state), D-A-004 (JSON file in repo), D-A-005 (OAuth 2.0 dynamic registration RFC 7591), D-A-006 (magic link email only, no password), D-A-007 (rate limit per IP), D-A-008 (structlog JSON logging), D-A-009 (Prometheus metrics), D-A-010 (5 layer architetturali), D-A-011 (3 environment local/staging/prod), D-A-012 (idempotency Redis 24h TTL), D-A-013 (timeout 5-10s), D-A-014 (circuit breaker manuale Redis), D-A-015 (no Celery v1), D-A-016 (HTTPS obbligatorio HSTS), D-A-017 (MCP protocol latest stable), D-A-018 (Redis no Memcached), D-A-019 (Python typing strict), D-A-020 (no LLM result caching), D-A-021 (uv non pip).

#### Dalle CONVENTIONS (D-C)

D-C-001 (lingue: identificatori ES, log/commit EN, prosa IT, descriptions ES LATAM), D-C-002 (ruff unico formatter+linter), D-C-003 (mypy strict), D-C-004 (GitHub Flow esteso con develop), D-C-005 (Conventional Commits + squash), D-C-006 (branch protection con CI required), D-C-007 (uv gestore pacchetti), D-C-008 (pre-commit hooks obbligatori), D-C-009 (Pydantic v2 per ogni modello), D-C-010 (async-first I/O), D-C-011 (fixture mai con dati reali clienti, marker `_test_fixture: true`), D-C-012 (coverage 80% overall, 90% domain), D-C-013 (mock httpx via pytest-httpx), D-C-014 (doc tri-livello), D-C-015 (CHANGELOG Keep a Changelog), D-C-016 (SemVer + tag Git), D-C-017 (Dependabot patch auto-merge), D-C-018 (`CLAUDE.md` in root), D-C-019 (loop READ-PLAN-ACT-VERIFY-RECORD), D-C-020 (anti-pattern espliciti vietati), D-C-021 (file max 400 linee, funzioni max 50).

#### Dal DATA-MODEL (D-D)

D-D-001 (4 file JSON v1), D-D-002 (single source of truth), D-D-003 (Pydantic v2 strict), D-D-004 (hard rule consensimiento `publico=true` requires explicit consent), D-D-005 (anonimizzazione obbligatoria), D-D-006 (soft-delete via `publico: false`), D-D-007 (`id` immutabile), D-D-008 (USD canonico, MXN/EUR runtime), D-D-009 (editing solo via PR), D-D-010 (`_meta` obbligatorio), D-D-011 (no hot reload v1), D-D-012 (validation runtime al boot), D-D-013 (pre-commit hook validate_data), D-D-014 (glosario single definizione canonica + variantes display), D-D-015 (benchmarks struttura per canale, rangi p25-p75), D-D-016 (strategy fallback 4-step), D-D-017 (slug pattern kebab-case/snake_case), D-D-018 (enum Pais ISO 3166-1 + PaisExtendido aggregati), D-D-019 (conversione valuta hardcoded v1), D-D-020 (cache JSON in-memory startup), D-D-021 (cardinalità target v1).

#### Dai TOOLS-TIER1 (D-T1) — 20 decisioni

Vedi `04-TOOLS-TIER1.md` sez. 10.

#### Dai TOOLS-TIER2 (D-T2) — 21 decisioni

Vedi `05-TOOLS-TIER2.md` sez. 10.

#### Dai TOOLS-TIER3 (D-T3) — 20 decisioni

Vedi `06-TOOLS-TIER3.md` sez. 9.

#### Dall'AUTH (D-AU) — 25 decisioni

Vedi `07-AUTH-OAUTH.md` sez. 14.

#### Dalle INTEGRATIONS (D-IN) — 20 decisioni

Vedi `08-INTEGRATIONS.md` sez. 11.

#### Dal DEPLOYMENT (D-DE) — 25 decisioni

Vedi `09-DEPLOYMENT.md` sez. 14.

#### Dal GTM (D-GT) — 20 decisioni

Vedi `10-GTM.md` sez. 12.

#### Dall'ANALYTICS (D-AN) — 21 decisioni

Vedi `11-ANALYTICS.md` sez. 11.

**Totale decisioni canoniche locked in v1.1 blueprint** (post harmony pass M0.3):

| File | ID prefix | Conteggio |
|---|---|---|
| `00-MASTER-PLAN.md` v1.4 | D-MP | 18 |
| `01-ARCHITECTURE.md` | D-A | 21 |
| `02-CONVENTIONS.md` | D-C | 21 |
| `03-DATA-MODEL.md` | D-D | 21 |
| `04-TOOLS-TIER1.md` | D-T1 | 20 |
| `05-TOOLS-TIER2.md` | D-T2 | 21 |
| `06-TOOLS-TIER3.md` | D-T3 | 20 |
| `07-AUTH-OAUTH.md` | D-AU | 25 |
| `08-INTEGRATIONS.md` | D-IN | 20 |
| `09-DEPLOYMENT.md` | D-DE | 25 |
| `10-GTM.md` | D-GT | 20 |
| `11-ANALYTICS.md` | D-AN | 21 |
| **TOTALE** | — | **253 decisioni canoniche locked** |

### 6.2 Decisioni aperte da chiudere

Lista cronologica per quando vanno chiuse.

#### Pre-M1 (target chiusura: prossime 1-2 settimane)

- DECISION-OPEN-001 (brand MCP): Merari
- DECISION-OPEN-005 (GitHub account): Claudio + Merari
- DECISION-OPEN-011 (conferma sede legale): Merari
- DECISION-OPEN-012 (distribuzione 30 query baseline): Claudio + Alessio
- DECISION-OPEN-DE-001 (DNS provider): Merari
- ~~DECISION-OPEN-T-001~~ ✅ Chiusa 2026-05-11: Upstash diretto in v1; alternativa M3+ Redis self-hosted in container Docker sulla stessa VM Oracle (24GB RAM oversize)

#### Pre-M2

- DECISION-OPEN-002 (Booking platform): Merari + Claudio
- DECISION-OPEN-003 (CRM): Merari
- DECISION-OPEN-004 (Email transactional): Claudio
- DECISION-OPEN-006 (Privacy policy custom vs sito + addendum): Merari + legal
- DECISION-OPEN-AU-001 (Email provider scelta finale post-deliverability test): Claudio
- DECISION-OPEN-AU-008 (Geo IP provider): Claudio
- DECISION-OPEN-IN-001/002/003 (provider conferme)
- DECISION-OPEN-T2-002 (rate limit IP per diagnostico_seo)
- DECISION-OPEN-T2-003 (DataForSEO per backlink in v1?)
- DECISION-OPEN-C-001 (coverage 80% hard fail)
- DECISION-OPEN-C-002 (Dependabot auto-merge patch)
- DECISION-OPEN-T-002 (JWT HS256 vs RS256): risolto in `07-AUTH-OAUTH.md` D-AU-004 = RS256
- DECISION-OPEN-T-007 (versioning MCP protocol)

#### Pre-M3

- DECISION-OPEN-DE-003 (Sentry)
- DECISION-OPEN-IN-005 (background worker fallback queue)
- DECISION-OPEN-T-004 (Geolocation server-side vs client headers)
- DECISION-OPEN-T3-005 (link competidor in compare_agencies)
- DECISION-OPEN-AU-003 (captcha)
- DECISION-OPEN-AU-004 (data-request endpoint automatizzato)
- DECISION-OPEN-AU-005 (encryption email in JWT)
- DECISION-OPEN-T1-003 (relevancia_score in caso_de_estudio)

#### Pre-M4

- DECISION-OPEN-007 (Analytics dashboard host)
- DECISION-OPEN-008 (WhatsApp Business API provider)
- DECISION-OPEN-IN-004 (DataForSEO vs SEMrush vs Ahrefs)
- DECISION-OPEN-IN-007 (WhatsApp provider)
- DECISION-OPEN-IN-010 (Cal.com Teams plan)
- DECISION-OPEN-T3-001 (numeri WhatsApp per país)
- DECISION-OPEN-T3-002 (provider SEO data)
- DECISION-OPEN-T3-003 (threshold share_research)
- DECISION-OPEN-T3-004 (share_research publishing auto vs review)
- DECISION-OPEN-T3-008 (rate limit analizar_competencia)
- DECISION-OPEN-AN-002 (automazione 30 query timing)
- DECISION-OPEN-AN-005 (Sentry)
- DECISION-OPEN-AN-006 (Heatmap landing)
- ~~DECISION-OPEN-DE-002~~ ✅ Chiusa 2026-05-11: region Oracle Cloud **Mexico Central `mx-queretaro-1`** (prod) — ottimizza 17/30 query baseline priority alta + data residency LFPDPPP MX-aligned. Staging come 2° container sulla stessa VM (M3+). Fallback: mx-monterrey-1 o sa-saopaulo-1 se ARM A1 capacity non disponibile.
- DECISION-OPEN-DE-008 (cost cap aumento $30→$65)

#### Pre-M5

- DECISION-OPEN-009 (blog post EN timing)
- DECISION-OPEN-010 (versioning tool naming)
- DECISION-OPEN-T1-001 (suggerimenti glosario semantic search)
- DECISION-OPEN-T1-002 (locale-aware number formatting)
- DECISION-OPEN-T1-004 (idioma_output parameter)
- DECISION-OPEN-T-005 (OpenTelemetry tracing)
- DECISION-OPEN-T-008 (queue Redis worker)
- DECISION-OPEN-AU-002 (IP risk scoring v2)
- DECISION-OPEN-AU-007 (sessione remember me)
- DECISION-OPEN-AU-009 (auto-rotation JWT key)
- DECISION-OPEN-C-003 (security scanning bandit/semgrep)
- DECISION-OPEN-C-005 (lingua user-facing oltre log)
- DECISION-OPEN-DE-004 (status page pubblica)
- DECISION-OPEN-DE-005 (backup S3 7 anni)
- DECISION-OPEN-GT-002 (Show HN)
- DECISION-OPEN-GT-003 (speaking opportunity)
- DECISION-OPEN-GT-004 (blog EN timing)
- DECISION-OPEN-GT-005 (podcast guest)
- DECISION-OPEN-GT-006 (open source page)
- DECISION-OPEN-AN-003 (Plausible vs GA4)
- DECISION-OPEN-AN-004 (Grafana Cloud)
- DECISION-OPEN-AN-010 (A/B testing tool descriptions)

**Totale decisioni aperte**: ~70 punti distribuiti su M1-v2.

---

## 7. Incongruenze rilevate (harmony pass M0.3 — 2026-05-11)

Audit eseguito su tutti i 15 file MD da Claude Opus 4.7 con 4 agenti paralleli + cross-check coordinatore. 12 incongruenze identificate, tutte risolte.

| ID | File coinvolti | Incongruenza | Risoluzione applicata | Status |
|---|---|---|---|---|
| HC-001 | `00-MASTER-PLAN.md` sez. 7 vs `MILESTONES.md` sez. 3 | Timeline ~12-13 settimane vs ~11 mesi (o ~6-7 mesi con Claude Code) | MASTER-PLAN bumped a v1.2; sez. 7 ora dichiara ~6-7 mesi M0→M4 con tabella esplicita assunzioni | 🟢 Risolto |
| HC-002 | `README.md` | Pivot v1.1 LATAM non riflesso: cita Madrid + valuta EUR | Aggiornato: "México, USA (anglo+hispanic), LATAM, ES"; valuta USD; query esempio CDMX/Miami; link a blueprint canonico | 🟢 Risolto |
| HC-003 | `05-TOOLS-TIER2.md` | Sospetto sezione "Decisioni canoniche D-T2-XXX" mancante | **FALSO POSITIVO**: sez. 10 con D-T2-001 → D-T2-021 esiste già. L'audit agent aveva truncamento del file. Verificato durante harmony pass. | 🟢 N/A |
| HC-004 | `08-INTEGRATIONS.md` sez. 4.1, 5.1, 6.1, 9.2 | Provider Cal.com/HubSpot/Resend/DataForSEO trattati come "default candidato" mentre DECISION-OPEN-002/003/004 ancora aperte | Aggiunto disclaimer "Adapter Pattern v1" all'inizio di ogni sez.: implementiamo Protocol astratto + impl. concreto del default; swap futuro = solo nuovo file `integrations/<provider>.py` | 🟢 Risolto |
| HC-005 | `03-DATA-MODEL.md` sez. 5.2 + `06-TOOLS-TIER3.md` sez. 4.2 | Enum `MercadoSubregional` definito ma usato come `str` in case_studies + `obtener_caso_por_pais` | Tipizzazione esplicita: `subregion: MercadoSubregional \| None` e `pais_o_subregion: Pais \| MercadoSubregional` | 🟢 Risolto |
| HC-006 | `06-TOOLS-TIER3.md` sez. 6.6 vs `03-DATA-MODEL.md` sez. 3 | `competitors_dataset.json` (5° file dati) introdotto in 06 ma assente in inventario 03 | Aggiunto in 03 sez. 3 inventario + nuova sub-sez. con schema | 🟢 Risolto |
| HC-007 | `09-DEPLOYMENT.md` sez. 3.2/4 | Dockerfile e railway.toml citati ma non inclusi; deploy-production.yml dichiarato "stessa logica staging" senza YAML completo | Aggiunte sez. 3.3 (Dockerfile completo), 4.5 (railway.toml), 6.3 espansa (deploy-production.yml completo) | 🟢 Risolto |
| HC-008 | `05-TOOLS-TIER2.md` sez. 5.7, 6.7, 7.7 | Sospetto output sample incompleti | **FALSO POSITIVO**: tutti i sample sono completi. Audit agent aveva truncamento. Verificato durante harmony pass. | 🟢 N/A |
| HC-009 | `00-MASTER-PLAN.md` linea 9 | Conteggio file ambiguo: "00 di 12" vs sez. 15 elenca 14 vs `Docs/blueprint/` ne contiene 15 | Header MASTER chiarito: "00 di 14 documenti blueprint (12 numerati + MILESTONES + SESSION-STATE; README separato)" | 🟢 Risolto |
| HC-010 | `10-GTM.md` sez. 4.5 | Description Anthropic Connector Directory dichiarata "(420 caratteri)" ma effettiva 501 char | Conteggio aggiornato + nota sul limit Anthropic ~500 | 🟢 Risolto |
| HC-011 | `00-MASTER-PLAN.md` sez. 8 vs `11-ANALYTICS.md` sez. 4 | 4 dimensioni KPI MASTER (Visibilità/Conversione/Operativo/Qualitativo) ≠ 4 di ANALYTICS (Visibilità/Engagement/Conversione/Operativo) | 11-ANALYTICS sez. 4 aggiornato: 5 dimensioni esplicite con mapping a MASTER. "Engagement" diventata sub-dimensione di Visibilità; "Qualitativo" promossa a 4ª dimensione separata | 🟢 Risolto |
| HC-012 | `11-ANALYTICS.md` sez. 5.7 vs `MILESTONES.md` M3.7.2 | Soglia SR-006 trigger ambigua (esempio 5%/2% baseline vs target ≥30%/≥25%) | Aggiunta riga esplicita in sez. 5.7: "Trigger SR-006 = M3 fine senza ≥30% Claude né ≥25% ChatGPT, con miglioramento <5pp vs M1 baseline" | 🟢 Risolto |

**Cleanup minori** applicati durante stesso pass:
- `02-CONVENTIONS.md` sez. 2.1: aggiunta riga "Slug / ID record dati" + disambiguazione costanti SCREAMING_SNAKE_CASE
- `01-ARCHITECTURE.md` sez. 4.2: tabella Layer ora include colonna "Moduli corrispondenti"
- `MILESTONES.md` linea 113 + 134: status M0.1.13 aggiornato a ✅ Completato

---

## 8. Cronologia di alto livello

Log temporale degli eventi importanti del progetto.

| Data | Evento | Owner |
|---|---|---|
| 2026-05-10 | Brainstorming iniziale strategia MCP per Segmenta | Claudio + Claude (conversazione) |
| 2026-05-10 | Scaffolding MVP MCP server primo prototipo (test funzionale FastMCP) | Claude (codice) + Claudio (test) |
| 2026-05-10 | Avvio blueprint v2 dettagliato 12 file | Claude + Claudio |
| 2026-05-10 | Cambio focus geografico: da Madrid-centric a MX/US/LATAM/ES (MASTER-PLAN v1.1) | Claudio (input) |
| 2026-05-10 | Completamento 11 file blueprint + MILESTONES + SESSION-STATE | Claude + Claudio (approvals sequenziali) |

---

## 9. Risorse esterne di riferimento

URL e doc che Claudio (o Claude Code) consulterà durante lo sviluppo.

### 9.1 MCP protocol

- **Spec ufficiale**: https://modelcontextprotocol.io/specification/2025-06-18
- **Authorization**: https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization
- **FastMCP docs**: https://gofastmcp.com/
- **MCP examples**: https://github.com/modelcontextprotocol/servers
- **Awesome MCP**: https://github.com/punkpeye/awesome-mcp-servers

### 9.2 Standard / RFC

- RFC 6749 — OAuth 2.0
- RFC 7591 — Dynamic Client Registration
- RFC 7636 — PKCE
- RFC 8414 — Authorization Server Metadata
- RFC 9068 — JWT Profile for OAuth
- RFC 6750 — Bearer Token Usage
- LFPDPPP — Ley Federal de Protección de Datos México: https://www.diputados.gob.mx/LeyesBiblio/pdf/LFPDPPP.pdf
- INAI guidelines: https://home.inai.org.mx/

### 9.3 Tool documentation

- Oracle Cloud Always Free (hosting canonico v1.4): https://www.oracle.com/cloud/free/
- Caddy (reverse proxy + TLS auto): https://caddyserver.com/docs/
- Tailscale (SSH sicuro): https://tailscale.com/kb/
- Watchtower (auto-update Docker): https://containrrr.dev/watchtower/
- Upstash (Redis free tier): https://upstash.com/docs/redis
- Fly.io (deprecato come opzione, eliminato free tier perpetuo 2024): https://fly.io/docs/
- Railway (fallback paid se Oracle non disponibile): https://docs.railway.app/
- Cal.com API: https://cal.com/docs/api-reference/v2/introduction
- HubSpot API: https://developers.hubspot.com/docs/api/overview
- Resend: https://resend.com/docs
- DataForSEO: https://docs.dataforseo.com/v3/

### 9.4 Internal references

- Repo GitHub: `https://github.com/segmenta-ai/segmenta-mcp` (non ancora creato)
- Server staging: `https://mcp-staging.segmentamarketing.com` (non ancora deployato)
- Server production: `https://mcp.segmentamarketing.com` (non ancora deployato)
- Dashboard interna: `https://admin.segmentamarketing.com/mcp-dashboard.html` (M4+)
- Privacy policy: `https://segmentamarketing.com/mcp/privacy` (M2+)

---

## 10. Note per la prossima sessione

Spazio libero per appunti che Claudio vuole lasciarsi.

### 10.1 Promemoria attivi

- [ ] Eseguire harmony pass dei 13 file (M0.3)
- [ ] Preparare 1-pager per Merari con sintesi progetto + decisioni richieste
- [ ] Aggiornare timeline in MASTER-PLAN sez. 7 post-harmony
- [ ] Decidere se aprire branch "blueprint-v1-final" per consolidare versioni
- [ ] Backup fisico dei 13 file (pattern Claudio per ogni progetto)

### 10.2 Idee da valutare in milestone future

- **M2.4.5 idea**: per `diagnostico_seo_express`, valutare se aggiungere check llms.txt presence come quick win standalone (oltre all'analisi GEO/AEO già prevista).
- **M3.3 idea**: blog post lancio potrebbe includere comparison table "before MCP vs after MCP" come visual hook iniziale.
- **M4 idea**: dashboard interna potrebbe esporre KPI individuali per Merari, Alessio, Romina (chi è responsibile di cosa) per accountability.
- **M5 idea**: post-launch, ogni tool Tier 1 potrebbe avere "tool of the week" mini-blog dove Romina spiega un use case + come usare il tool. Content marketing meta.

### 10.3 Domande aperte

- È necessario un file `Docs/incidents/README.md` con template per future RCA? (Pre-M2 quando andiamo live.)
- Vale la pena pre-popolare `data/competitors_dataset.json` (M4) con 5-10 entry adesso per dare priorità a Romina nei mesi?
- Per il GTM, vale la pena pre-pitch *adesso* a 1-2 pubblicazioni che ci conoscono (warm leads) per primizia di lancio?

---

## 11. Versioning di questo documento

Aggiornato ad ogni sessione di lavoro significativa.

| Versione | Data | Note |
|---|---|---|
| 1.0 | 2026-05-10 | Stesura iniziale post-completion 13 file blueprint. M0 al 93%, pending M0.2 (decisioni Merari) e M0.3 (harmony pass). Discrepanza timeline MASTER-PLAN vs MILESTONES annotata in HC-001. Stima ricalibrata 6-7 mesi M0→M4 con Claude Code che scrive codice (vs 11 mesi senza). |
| 1.1 | 2026-05-11 | **Harmony pass M0.3 completato**. 12 incongruenze HC-001 → HC-012 risolte (vedi sez. 7). MASTER-PLAN bumped a v1.2 (timeline + conteggio file). README aggiornato (pivot LATAM + valuta USD). 05-TOOLS-TIER2 sez. 10 D-T2 aggiunta (21 decisioni). 09-DEPLOYMENT Dockerfile/railway.toml aggiunti. Totale decisioni canoniche locked: 253 (vs ~210 stimate in v1.0). M0 ora al 98% — resta solo M0.2 (decisioni Merari). |
| 1.2 | 2026-05-11 | **M0.2 chiuso parzialmente**: M0.2.1 (budget $0 target, Fly.io free tier — D-MP-002 ricalibrata), M0.2.2 (sede Messico), M0.2.3 (repo pubblico), M0.2.5 (org `segmenta-ai`). Restano: BL-004 (DNS access — solo a M1.1 quando deploy ready) e BL-006/007 (booking + CRM — gestiti da adapter pattern, non bloccanti). MASTER bumped a v1.3, 09-DEPLOYMENT bumped a v1.2 (migrazione completa Railway → Fly.io: sez. 4, 7, 9, 12.3 riscritte; fly.toml + fly.staging.toml; cost projection ricalcolata a $0/mese M0-M3). DECISION-OPEN-004 chiusa (Resend), DECISION-OPEN-005 chiusa (org segmenta-ai), DECISION-OPEN-011 chiusa (Messico), DECISION-OPEN-DE-002 chiusa (region MEX/MIA). M0 al 99% — pronto per M1 kickoff. |
| 1.3 | 2026-05-11 | **Ricalibrazione hosting Fly.io → Oracle Cloud Always Free**. Motivazione: Claudio ha verificato che Fly.io ha eliminato free tier perpetuo nel 2024 (richiede $5 credit + carta), incompatibile con vincolo "$0 hard". Comparativa Vercel/Cloudflare/Render fatta. Decisione: **Oracle Cloud Always Free** (1 VM ARM 4vCPU+24GB RAM perpetuo). MASTER v1.4 D-MP-002, 09-DEPLOYMENT v1.3 (sez. 4 riscritta con setup VPS step-by-step + docker-compose.yml + Caddyfile + Tailscale; sez. 7 nuova architettura ghcr.io + Watchtower; .env file su VM al posto di flyctl secrets). 01-ARCHITECTURE v1.3 stack tabella aggiornata. MILESTONES v1.3 M1.5 task riscritti (3-4h bootstrap VPS). DECISION-OPEN-DE-002 chiusa diversamente (São Paulo). DECISION-OPEN-T-001 chiusa diversamente (Upstash + alternativa Redis self-hosted). README aggiornato con setup Oracle. **M0 ancora al 99%** — pronto per M1 kickoff con setup Oracle ~3-4h. |

---

**Fine SESSION-STATE.md v1.0 — file vivo, aggiornare continuamente.**
