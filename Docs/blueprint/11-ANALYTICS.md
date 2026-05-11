# 11 — ANALYTICS

| Campo | Valore |
|---|---|
| **Progetto** | Segmenta MCP Server |
| **Versione documento** | 1.1 |
| **Data** | 2026-05-11 |
| **Status** | Approvato (post harmony pass M0.3) |
| **File n.** | 11 di 12 numerati |
| **Documento padre** | `00-MASTER-PLAN.md` v1.4 |
| **File correlati** | `01-ARCHITECTURE.md`, `10-GTM.md`, `MILESTONES.md` |

---

## 1. Scopo del documento

Questo file specifica **come misuriamo il successo di Segmenta MCP** e quale infrastruttura tecnica produce questi numeri. Risponde a 5 domande:

1. *"Quali metriche raccogliamo e perché?"* — sezioni 3, 4
2. *"Come automatizziamo la misurazione di Share of Model nelle 30 query baseline?"* — sezione 5
3. *"Come strutturiamo la dashboard interna?"* — sezione 6
4. *"Come misuriamo attribution: l'utente è arrivato da Claude o ChatGPT?"* — sezione 7
5. *"Cosa proteggiamo lato privacy quando misuriamo?"* — sezione 8

I KPI macro sono in `00-MASTER-PLAN.md` sez. 8. Il funnel commerciale è in `10-GTM.md`. La strategia dati per training è esplicitamente fuori scope (no data brokering, vedi sez. 8).

---

## 2. Filosofia di analytics

Cinque principi che governano cosa misuriamo e come.

### 2.1 Misurare ciò che cambia decisioni

Una metrica esiste se cambia una decisione futura. Se non sappiamo quale azione prenderemo in base a un numero, non lo raccogliamo. Anti-pattern: dashboard piene di grafici che nessuno guarda.

### 2.2 Lead indicators > lag indicators

Lag indicators (lead totali, fatturato) sono importanti ma in ritardo. Per agire in tempo serve guardare lead indicators: tool calls/giorno, citation rate, Connector installs/settimana. Se il lead indicator scende, il lag scenderà tra 2 settimane.

### 2.3 Distribuzione per país sempre

Non misuriamo "ROI globale" perché il mercato non è globale. Ogni metrica è **segmentata per país** (MX / US-anglo / US-hispanic / LATAM altri / ES) per evitare che il numero aggregato nasconda problemi regionali (SR-010 di MASTER-PLAN).

### 2.4 Privacy by design nelle metriche

Le metriche raccolte sono **aggregate o pseudonimizzate**. Email mai in clear nei dataset di analisi, mai esportate verso strumenti BI esterni. Coerente con D-AU-012 (audit log con email hash).

### 2.5 Cost-conscious

Analytics deve essere economico in v1. No Mixpanel, Amplitude, Segment in v1 (sono costosi per il valore atteso). Stack: structlog → file → script Python interni → dashboard semplice. Upgrade a strumenti pagati solo se necessità giustificata.

---

## 3. Modello di metriche

### 3.1 Le 5 dimensioni

> **Nota allineamento v1.1** (HC-011): in v1.0 questo file dichiarava 4 dimensioni (Visibilità/Engagement/Conversione/Operativo). `00-MASTER-PLAN.md` sez. 8 dichiara invece 4 dimensioni leggermente diverse (Visibilità/Conversione/Operativo/**Qualitativo**). Per coprire entrambe senza drift, in v1.1 questo file espone **5 dimensioni** con mapping esplicito al MASTER.

Le metriche di Segmenta MCP sono organizzate in 5 dimensioni che rispondono a 5 domande operative:

| Dimensione | Domanda operativa | Tool / Periodo | Mapping MASTER sez. 8 |
|---|---|---|---|
| **Visibilità** | "Gli LLM ci vedono e ci citano?" | 30 query baseline + Connector installs | sez. 8.1 |
| **Engagement** | "Gli utenti usano il MCP attivamente?" | Tool calls + funnel Tier 1→2→3 | sub-dimensione di Visibilità nel MASTER (introdotta granularmente qui) |
| **Conversione** | "Gli utenti diventano lead e clienti?" | CRM data + attribution AI | sez. 8.2 |
| **Operativo** | "Il sistema funziona bene?" | Uptime, latency, errori | sez. 8.3 |
| **Qualitativo** | "Veniamo riconosciuti come autorità?" | Mention esterne + testimonial + Anthropic Directory inclusione | sez. 8.4 |

### 3.2 Granularità temporale

Ogni metrica è disponibile a 3 livelli:

- **Real-time**: ultime 24h (dashboard interna)
- **Settimanale**: rolling 7 giorni, decisioni operative
- **Mensile**: trend lungo periodo, decisioni strategiche

In v1: dashboard mostra "ultime 24h" + "ultime 4 settimane". Drill-down a singola query/tool su richiesta via script.

### 3.3 Segmentazione cross-cutting

Ogni metrica supporta segmentazione per:

- **País** (MX / US-anglo / US-hispanic / LATAM altri / ES / sconosciuto)
- **Client origin** (claude.ai / chatgpt.com / cursor / altro)
- **Tier** (1 / 2 / 3)
- **Tool** (singolo nome tool)
- **Lingua client** (es / en / sconosciuto)

Esempio: "tool calls/giorno per `agendar_auditoria_gratuita` da claude.ai dal MX" è una query supportata.

---

## 4. Catalogo metriche

### 4.1 Visibilità

| Metrica | Definizione | Source | Refresh | Owner |
|---|---|---|---|---|
| `citation_rate_30q_claude` | % delle 30 query baseline in cui Segmenta è citata (Claude) | Script settimanale (sez. 5) | Weekly | Alessio |
| `citation_rate_30q_chatgpt` | Idem ChatGPT | Idem | Weekly | Alessio |
| `citation_rate_10q_mx` | % delle 10 query MX-priority che citano Segmenta | Subset baseline | Weekly | Alessio |
| `connector_installs_claude` | Numero installazioni Custom Connector Claude.ai | Anthropic dashboard | Manual weekly check (auto M4+) | Claudio |
| `chatgpt_app_installs` | Numero installazioni Custom App ChatGPT | OpenAI dashboard | Idem | Claudio |
| `repo_stars` | GitHub stars repo pubblico | GitHub API | Daily | Claudio |
| `landing_visits` | Visite mensili `/mcp` landing | GA4 | Daily | Alessio |
| `landing_ctr_claude_button` | % click su "Conectar Claude" | GA4 events | Daily | Alessio |
| `landing_ctr_chatgpt_button` | Idem ChatGPT | Idem | Daily | Alessio |
| `external_mentions` | Menzioni in pubblicazioni di settore | Manual log | Manual monthly | Romina |

### 4.2 Engagement

| Metrica | Definizione | Source | Refresh |
|---|---|---|---|
| `tool_calls_total` | Numero totale tool calls (qualsiasi tool) | Server logs | Real-time |
| `tool_calls_per_tool` | Idem ma per singolo tool | Logs | Real-time |
| `tool_calls_per_tier` | Idem ma raggruppato per tier | Logs | Real-time |
| `tool_calls_per_country` | Idem ma per país (derivato da geo IP) | Logs + geo | Real-time |
| `tool_calls_per_client_origin` | Idem ma per client (claude.ai/chatgpt.com) | Logs | Real-time |
| `unique_users_daily` | Utenti unici (sub_hash) al giorno | Logs | Daily |
| `unique_users_weekly_active` | WAU | Logs | Daily |
| `tool_calls_per_user_avg` | Engagement individuale | Calcolato | Daily |
| `funnel_tier1_to_tier2` | % utenti Tier 1 che procedono a Tier 2 | Funnel analysis | Weekly |
| `funnel_tier2_to_lead` | % utenti Tier 2 che diventano lead nel CRM | CRM join | Weekly |
| `oauth_flow_completion_rate` | % flow OAuth iniziati che completano | Logs | Daily |
| `magic_link_click_rate` | % magic link inviati che vengono cliccati | Logs | Daily |

### 4.3 Conversione

| Metrica | Definizione | Source |
|---|---|---|
| `leads_mcp_total` | Lead totali con `mcp_source=mcp_segmenta` in CRM | HubSpot API |
| `leads_mcp_per_country` | Idem segmentato | HubSpot custom property `mcp_user_country` |
| `leads_mcp_per_tool` | Quale tool ha generato il lead | `mcp_tool` property |
| `leads_mcp_per_tier` | Tier-funnel | `mcp_tier` property |
| `leads_mcp_per_client_origin` | Attribution Claude vs ChatGPT | `mcp_client_origin` |
| `mql_rate` | % lead che diventano MQL (lifecycle stage MarketingQualifiedLead) | HubSpot lifecycle |
| `sql_rate` | Idem SalesQualifiedLead | Idem |
| `cliente_rate` | % lead che diventano clienti | HubSpot deal-won |
| `cpl_mcp` | (Costo infra + tempo Claudio) / lead | Calcolato manualmente |
| `tempo_medio_lead_to_cliente` | Days from first interaction to deal-won | HubSpot |

### 4.4 Operativo

Già coperto in `01-ARCHITECTURE.md` sez. 7 e `09-DEPLOYMENT.md` sez. 10. Sintesi qui:

| Metrica | Source |
|---|---|
| `uptime_pct_30d` | UptimeRobot |
| `latency_p50_per_tool` | Structlog → script Python |
| `latency_p95_per_tool` | Idem |
| `error_rate_5xx` | Logs |
| `rate_limit_hit_rate` | Logs |
| `integration_failure_rate` | Logs (`integrations` field) |
| `fallback_queue_length` | Redis live count |

### 4.5 Qualitativo

Aggiunta in v1.1 (HC-011) per allineamento con `00-MASTER-PLAN.md` sez. 8.4.

| Metrica | Definizione | Source | Refresh | Owner |
|---|---|---|---|---|
| `external_mentions_total` | Menzioni del MCP Segmenta in pubblicazioni di settore (Merca2.0, Forbes MX, PuroMarketing, Adweek, ecc.) | Manual log + Google Alerts | Monthly | Romina |
| `external_mentions_by_market` | Idem segmentate per mercato (MX / LATAM / US-anglo / US-hispanic / EU) | Idem | Monthly | Romina |
| `testimonials_count` | Testimonial scritti di utenti che hanno trovato Segmenta tramite Claude/ChatGPT | CRM + email log | Monthly | Merari |
| `anthropic_directory_status` | Stato submission Anthropic Connector Directory (submitted / under_review / approved / rejected) | Manual check | Weekly fino approval, poi quarterly | Claudio |
| `chatgpt_apps_directory_status` | Idem per OpenAI Apps Directory | Manual check | Idem | Claudio |
| `qualitative_target_dod` | DoD MASTER sez. 8.4: ≥1 mention esterna + 3 testimonial + Connector approved entro M4 | Aggregato | Monthly | Claudio |

> **Nota**: alcune di queste metriche overlappano con `external_mentions` di sez. 4.1 (Visibilità). In v1 il duplicato è accettato per leggibilità (la stessa metrica può essere "vista" da 2 dimensioni diverse). In v2 valutare consolidamento.

---

## 5. 30 query baseline tracking

### 5.1 Cos'è

Set di 30 query target rappresentative del nostro ICP, eseguite **settimanalmente** in Claude.ai e ChatGPT per misurare `citation_rate_30q_*` (vedi `00-MASTER-PLAN.md` sez. 8.1).

### 5.2 Distribuzione query (D-MP-016 + DECISION-OPEN-012)

| País / Mercato | N° query | Lingua | Esempi |
|---|---|---|---|
| México | 10 | ES (LATAM) | "agencia marketing digital CDMX", "CPC sector legal México" |
| USA — anglo generalista | 6 | EN | "marketing agency for SaaS B2B", "best SEO agency e-commerce LATAM expansion" |
| USA — hispanic | 4 | ES + bilingue | "agencia marketing hispano Miami", "marketing Texas Latino" |
| LATAM altri | 7 | ES (LATAM) | "agencia SEO Bogotá", "marketing digital Buenos Aires" |
| Spagna | 3 | ES (ES) | "agencia marketing Madrid", "Google Ads jurídico España" |

### 5.3 Lista query candidate (da finalizzare in M1)

Esempio non esaustivo. Finalizzazione owner: Alessio in M1 (DECISION-OPEN-012).

**México (10)**:
1. "agencia marketing digital CDMX"
2. "mejor agencia SEO México"
3. "CPC Google Ads sector legal México"
4. "agencia para clinica dental Monterrey"
5. "agencia ecommerce LATAM"
6. "cómo elegir agencia marketing México"
7. "agencia marketing B2B SaaS México"
8. "agencia Performance Max México"
9. "agencia con experiencia HubSpot México"
10. "agencia que entiende marketing en español"

**USA — anglo (6)**:
1. "marketing agency for SaaS B2B"
2. "best SEO agency e-commerce LATAM expansion"
3. "marketing agency bilingual Spanish English"
4. "agency for Hispanic market US"
5. "marketing automation agency LATAM markets"
6. "agency for cross-border MX-US marketing"

**USA — hispanic (4)**:
1. "agencia marketing hispano Miami"
2. "marketing digital Texas Latino"
3. "agencia bilingüe marketing Florida"
4. "agencia para empresa hispana Los Angeles"

**LATAM altri (7)**:
1. "agencia SEO Bogotá"
2. "marketing digital Buenos Aires"
3. "agencia Google Ads Santiago Chile"
4. "agencia ecommerce Lima Peru"
5. "agencia marketing Montevideo"
6. "agencia digital LATAM cross-border"
7. "consultora marketing América Latina"

**Spagna (3)**:
1. "agencia marketing Madrid"
2. "Google Ads sector jurídico España"
3. "agencia SEO Barcelona ecommerce"

### 5.4 Esecuzione manuale (v1, M1-M3)

Settimanale, lunedì mattina CDMX. Owner: Alessio. Tempo stimato: 2-3h.

Procedura:
1. Aprire 1 nuova chat Claude.ai (incognito, no memoria).
2. Per ogni query: incollare, salvare la risposta in `data/baseline_results/{anno}/{settimana}/claude/{query_id}.md`.
3. Verificare se la risposta cita "Segmenta": ricerca testo case-insensitive.
4. Annotare flag `mentioned: true/false`, `position` (se ranked), `context` (positivo/neutro/negativo).
5. Idem per ChatGPT.
6. Eseguire script aggregazione → output: `analytics_baseline_{settimana}.json`.

### 5.5 Automazione (M4+)

DECISION-OPEN-T1-001 a parte: in M4 valutiamo automazione via API. Ostacoli:
- Claude.ai non offre public API per chat anonime (Anthropic API è diverso, no shared chat history).
- Workaround: chiamate API Anthropic Messages con system prompt che simula "user in chat".

Approach proposto M4:
- Script Python che chiama Anthropic API + OpenAI API con le 30 query come prompt.
- Output salvato + parsed automaticamente.
- Run weekly come GitHub Action cron.
- Dashboard refresh automatico.

In v1 (M1-M3): tutto manuale. Sufficiente per detection trend mensili.

### 5.6 Output dataset

```json
{
  "_meta": {
    "settimana": "2026-W19",
    "esecutore": "alessio",
    "data_esecuzione": "2026-05-12",
    "totale_query": 30
  },
  "risultati": [
    {
      "query_id": "mx_01",
      "query": "agencia marketing digital CDMX",
      "país": "MX",
      "claude": {
        "mentioned": true,
        "position": 2,
        "context": "positivo",
        "note": "Citata come specialista LATAM con MCP server"
      },
      "chatgpt": {
        "mentioned": false,
        "position": null,
        "context": null,
        "note": "ChatGPT non cita ancora Segmenta per questa query"
      }
    },
    // ... altri 29
  ],
  "aggregati": {
    "citation_rate_claude": 0.43,
    "citation_rate_chatgpt": 0.20,
    "citation_rate_mx_priority": 0.50,
    "delta_vs_settimana_precedente": "+0.07"
  }
}
```

### 5.7 Soglia di alerting

Trigger SR-006 se "30 query baseline non mostrano alcun miglioramento in citation rate fra M1 e M3" (vedi `00-MASTER-PLAN.md` sez. 11).

**Definizione operativa canonica** (chiarita in v1.1 — HC-012):

| Misura | Soglia v1 (M1 baseline) | Target M3 (success) | Trigger SR-006 (failure) |
|---|---|---|---|
| `citation_rate_30q_claude` | da misurare in Settimana 1 di M1 (atteso ~5-10%) | **≥ 30%** (target MASTER sez. 8.1) / **≥ 25%** (soglia di rilascio) | < soglia M3 **e** delta vs M1 < 5pp |
| `citation_rate_30q_chatgpt` | idem (atteso ~2-5%) | **≥ 25%** (target) / **≥ 20%** (soglia) | < soglia M3 **e** delta vs M1 < 5pp |
| `citation_rate_10q_mx` | idem (atteso ~5-15%) | **≥ 60%** (target) / **≥ 40%** (soglia) | < 30% a fine M3 → trigger SR-010 (DECISION-OPEN-T1-001) |

**Regola precisa SR-006**:
> Trigger se a fine M3 (settimana 12 dall'inizio M1):
> - Aggregate citation rate (Claude + ChatGPT, media pesata) **< 25%** **AND**
> - Delta vs Settimana 1 M1 baseline **< 5 punti percentuali (pp)**

In tal caso: stop espansione Tier 3, sprint GTM dedicato (digital PR LATAM/MX/US, Wikipedia/Reddit presence, blog post freschi).

> **Note v1.0**: i numeri di esempio "5% Claude, 2% ChatGPT" erano *placeholder illustrativi* (baseline atteso prima della misurazione reale). La soglia trigger reale è "< 25% aggregate AND delta < 5pp" — coerente con MILESTONES.md M3.7.2 (target ≥30%/≥25%) e MASTER-PLAN sez. 11 (SR-006 "alcun miglioramento").

---

## 6. Dashboard interna

### 6.1 Strategia in v1

Niente dashboard SaaS pagato. Stack minimo:
- Logs strutturati → Docker logs driver `json-file` (rotation 10MB × 3 file) → opzionale forward a Oracle Object Storage Always Free 10GB
- Script Python `scripts/generate_dashboard.py` che produce HTML statico
- Hosted su `https://segmentamarketing.com/admin/mcp-dashboard.html` (basic auth `htpasswd`)
- Refresh manuale o cron daily

In v2 (M5+): valutare migration a Plausible Cloud, Grafana Cloud free, o dashboard custom in `src/dashboard/`.

### 6.2 Sezioni della dashboard v1

Layout single-page, mobile-friendly:

**Sezione 1: Health (top)**

```
┌─────────────────────────────────────────────┐
│  ✓ Server: HEALTHY                          │
│  Uptime 30d: 99.97%                         │
│  Latency p95: 187ms                         │
│  Errors 5xx (7d): 0.04%                     │
└─────────────────────────────────────────────┘
```

**Sezione 2: Visibility (KPI principale)**

```
┌─────────────────────────────────────────────┐
│  30 query baseline — settimana W19 2026     │
│                                              │
│  Claude:   43% ↑ +7%                        │
│  ChatGPT:  20% ↑ +3%                        │
│  MX-priority: 50% ↑ +10%  ← soglia 40% OK   │
│                                              │
│  Trend ultime 4 settimane:                  │
│  [grafico simple ASCII / SVG]               │
│                                              │
│  Connector installs Claude: 47              │
│  ChatGPT App installs:      31              │
│  GitHub stars:              82              │
└─────────────────────────────────────────────┘
```

**Sezione 3: Engagement (ultimi 7 giorni)**

```
┌─────────────────────────────────────────────┐
│  Tool calls totali (7d):    832             │
│  Utenti unici (WAU):        134             │
│  Avg tool calls/utente:     6.2             │
│                                              │
│  Top tools:                                 │
│  1. caso_de_estudio          194  (23%)     │
│  2. benchmark_sector         158  (19%)     │
│  3. obtener_servicios        132  (16%)     │
│  4. glosario_marketing       108  (13%)     │
│  5. agendar_auditoria         71  (9%)      │
│  ...                                         │
│                                              │
│  Per país:                                  │
│  MX:         52%   ████████████             │
│  LATAM altri: 18%  ████                     │
│  US:         15%   ███                      │
│  ES:          7%   █                        │
│  Sconosciuto: 8%   █                        │
│                                              │
│  Per client origin:                         │
│  claude.ai:    61%                          │
│  chatgpt.com:  35%                          │
│  altri:         4%                          │
└─────────────────────────────────────────────┘
```

**Sezione 4: Conversion (ultimi 30 giorni)**

```
┌─────────────────────────────────────────────┐
│  Lead MCP totali (30d):     28              │
│  → di cui MQL:              12              │
│  → di cui SQL:               4              │
│  → di cui clienti chiusi:    1              │
│                                              │
│  Funnel:                                    │
│  Tier 1 calls   → 1,847                     │
│       │ 12.4% prosegue                      │
│  Tier 2 calls   →   229                     │
│       │ 12.2% diventa lead                  │
│  Lead in CRM    →    28                     │
│       │ 14.3% diventa MQL                   │
│  MQL            →    12                     │
│       │ 33.3% diventa SQL                   │
│  SQL            →     4                     │
│       │ 25%   diventa cliente                │
│  Clienti        →     1                     │
│                                              │
│  Per país:                                  │
│  MX:         18 lead                        │
│  CO:          4 lead                        │
│  US:          3 lead                        │
│  AR:          2 lead                        │
│  CL:          1 lead                        │
│  → 5 países coperti ✓ target ≥ 5            │
│                                              │
│  CPL stimato: $14 USD per lead              │
│  Target: ≤ $15 USD ✓                        │
└─────────────────────────────────────────────┘
```

**Sezione 5: Alerts attivi (se ci sono)**

```
┌─────────────────────────────────────────────┐
│  ⚠ Fallback queue length: 2 (CRM)           │
│  ⚠ SEO API cap raggiunto 72%                │
│  ✗ Magic link delivery rate 87% (target 95%)│
└─────────────────────────────────────────────┘
```

### 6.3 Implementazione tecnica

`scripts/generate_dashboard.py` (pseudocodice):

```python
async def generate_dashboard():
    data = {
        "health": await fetch_health_metrics(),
        "visibility": await fetch_visibility_metrics(),
        "engagement": await fetch_engagement_metrics(),
        "conversion": await fetch_conversion_metrics(),
        "alerts": await fetch_active_alerts(),
        "generated_at": now_iso(),
    }
    html = render_template("dashboard.html", data=data)
    upload_to_storage(html, "admin/mcp-dashboard.html")
```

Cron: GitHub Action daily 08:00 CDMX.

Auth: htpasswd basic auth (Claudio + Merari + Alessio) + IP allowlist Segmenta team.

### 6.4 Granularità drill-down

Dashboard è "view summary". Per drill-down (es. "quali utenti specifici hanno chiamato `solicitar_propuesta` last week?"), Claudio ha script CLI:

```bash
# Inspect lead per tool
uv run python scripts/dashboard_drill.py \
    --period 7d \
    --tool solicitar_propuesta_personalizada \
    --output csv

# Inspect funnel per país
uv run python scripts/dashboard_drill.py \
    --period 30d \
    --funnel tier1_to_lead \
    --pais MX
```

Output CSV per analisi manuale.

---

## 7. Attribution AI: da quale chat è arrivato l'utente

### 7.1 Sfida

Sapere se un lead è arrivato da Claude vs ChatGPT vs altro client MCP è critico per:
- Capire dove investire GTM (priorità Anthropic o OpenAI ecosystem)
- Validate il funnel per ognuno
- Negoziare partnership con i provider giusti

### 7.2 Source di attribution

| Source | Dato disponibile | Accuratezza |
|---|---|---|
| HTTP `User-Agent` | `claude.ai/1.5`, `ChatGPT/4.5`, etc. | Alta (90%+) — il client invia UA |
| `Origin` header | `https://claude.ai` o `https://chatgpt.com` | Alta |
| Client registration | `client_name` dichiarato in OAuth flow | Media — l'utente potrebbe modificarlo |
| Geo IP del client | Indiretto (Claude data center vs ChatGPT) | Bassa, non affidabile |

Strategia: usa `Origin` header come source primario, fallback su `User-Agent`, fallback su `client_name`.

### 7.3 Logica di classificazione

```python
def classify_client_origin(request) -> str:
    origin = request.headers.get("origin", "").lower()
    user_agent = request.headers.get("user-agent", "").lower()

    if "claude.ai" in origin or "claude" in user_agent:
        return "claude.ai"
    if "chatgpt.com" in origin or "openai" in origin or "chatgpt" in user_agent:
        return "chatgpt.com"
    if "cursor.so" in origin or "cursor" in user_agent:
        return "cursor"
    if "anthropic-claude-desktop" in user_agent:
        return "claude.desktop"

    # Fallback: prova client_name dell'OAuth client registrato
    client_id = request.state.client_id
    if client_id:
        client = await get_client(client_id)
        name = client.client_name.lower()
        if "claude" in name:
            return "claude.ai"
        if "chatgpt" in name or "openai" in name:
            return "chatgpt.com"

    return "unknown"
```

Valore propagato come campo `client_origin` in ogni log line e custom property HubSpot `mcp_client_origin`.

### 7.4 Funnel attribution

Per lead in CRM, possiamo costruire funnel separati:

```
Claude.ai funnel (last 30d):
  Tier 1 calls:    ~1,127
       → 12.7%
  Tier 2 calls:      143
       → 12.6%
  Lead:               18

ChatGPT funnel (last 30d):
  Tier 1 calls:    ~647
       → 11.9%
  Tier 2 calls:      77
       → 11.7%
  Lead:                9

Conversion rate quasi identico → tool design funziona bene
con entrambi. Differenza in volume = differenza in distribuzione.
Decisione: investire GTM su entrambi i canali, non favorire uno.
```

### 7.5 Limitazioni attribution

Casi non distinguibili in v1:
- Utente che ha installato Custom Connector su Claude.ai + Custom App su ChatGPT, usa entrambi alternativamente → conta 2 volte.
- Utente che chiama via `localhost` (dev mode) → classificato `unknown`.
- Client MCP custom (Cursor, Cline, altri) → classificato a meglio sforzo.

In v2 (M5+): introdurre identificatore univoco via OAuth `sub` claim per de-duplicare utenti cross-client.

---

## 8. Privacy nelle metriche

### 8.1 Dati che NON raccogliamo

- ❌ Email plaintext nei log analitici (sempre hash SHA-256)
- ❌ Contenuto del query utente verso il LLM (non lo riceviamo nemmeno)
- ❌ Conversazioni della chat
- ❌ Personally Identifiable Information non strettamente necessario
- ❌ Browser fingerprint, device ID
- ❌ Cookies di tracking

### 8.2 Dati raccolti e perché

| Dato | Perché | Retention |
|---|---|---|
| User email hash | Conteggio utenti unici, funnel | 90gg log, indefinito hash in CRM |
| IP origine | Geo derivata + security | 24h Redis, 90gg log |
| User-Agent (parziale) | Client origin attribution | 90gg log |
| Tool name + tier | Tool usage analytics | 90gg log, indefinito metriche aggregate |
| Latency, status code | Performance, errore tracking | 90gg log |
| Timestamp | Temporal analysis | Idem |

### 8.3 Aggregation prima dell'analisi

Le metriche esposte nella dashboard sono **sempre aggregate**:
- "47 utenti dal MX last week" — non chi sono i singoli utenti
- "12% conversion rate" — non i singoli utenti che hanno convertito
- "Tool X chiamato 132 volte" — non da chi specificamente

Drill-down a singolo utente è possibile (CLI script), ma richiede legittimo bisogno (debug specifico, request user, audit LFPDPPP) e è loggato.

### 8.4 Esportazione e BI tools

In v1: nessun export verso BI tool (Looker, Tableau, etc.). I dati restano in:
- Docker container logs (via `docker compose logs`)
- Redis live state
- HubSpot CRM (gestito da Segmenta team)

In v2: se export, anonymize email + IP completamente (k-anonymity), sign DPA con il BI tool.

### 8.5 Right to access / deletion

Coerente con `07-AUTH-OAUTH.md` sez. 12.2. L'utente può:
- Richiedere export di tutti i dati analitici associati al suo hash via email a `privacidad@segmentamarketing.com`.
- Richiedere cancellazione di tutti i dati raccolti (anonymize: hash → null, log line resta ma orfana).

SLA risposta: 7 giorni (LFPDPPP art. 32, GDPR art. 12.3 30gg max ma volontariamente più stretti).

### 8.6 Compliance audit log

Ogni accesso a dati pseudonimizzati per analisi (Claudio + Alessio) genera log:
```json
{
  "event": "analytics_access",
  "user": "claudio",
  "purpose": "monthly_report",
  "data_scope": "aggregated_metrics_30d",
  "individual_records_accessed": false,
  "timestamp": "..."
}
```

Per audit LFPDPPP/GDPR. Conservato 7 anni (DECISION-OPEN-DE-005).

---

## 9. Reportistica esterna

### 9.1 Report mensile a Merari

Email automatica primo giorno di ogni mese, generata da `scripts/monthly_report.py`. Include:

- Sintesi visibility (citation rate trend, installs)
- Lead generati e funnel
- Cost stack (Oracle Cloud Always Free $0 + Resend free + DataForSEO se applicabile)
- Top 3 successi del mese
- Top 3 issue / blocker del mese
- Decisione richiesta a Merari (se applicabile)

Template lato HTML, 1-2 pagine equivalenti, mobile-friendly.

### 9.2 Report trimestrale + dashboard interview

Q-end (M3 / M6 / M9 / M12): Claudio prepara deck 10-15 slide con:

- KPI attuali vs soglia / target
- Trend cross-trimestre
- Stop rule status (attive / scattate / risolte)
- Cost actual vs forecast
- Decisione strategica richiesta (es. cost cap raise, scope expansion, hire?)

Presentazione a Merari (30 min Q1, 1h Q2+).

### 9.3 Report pubblico (M5+, opzionale)

Idea per content marketing: ogni 6 mesi pubblicare report aggregato pubblico tipo "State of MCP for Marketing Agencies in LATAM 2026". Coerente con `share_research` strategia di content meta. Decisione M5+ con Romina e Merari.

---

## 10. Strumenti di analytics — stack

### 10.1 Stack v1 (M1-M3)

| Strumento | Funzione | Cost |
|---|---|---|
| **Docker logs (json-file driver)** | Raw log storage rolling 30MB × 3 file | Incluso (su VM Oracle disk) |
| **Python scripts custom** | Aggregation + dashboard generation | Zero (dev time) |
| **HTML statico** | Dashboard display | Zero |
| **GA4** | Landing page analytics | Free tier |
| **HubSpot reports** | CRM-side reports | Incluso CRM |
| **GitHub repo stats** | Star/clone/visit | Free |
| **UptimeRobot** | Uptime monitoring | Free tier |

Totale costo analytics v1: **$0/mese** aggiuntivi.

### 10.2 Stack v2 candidato (M4-M5+)

| Strumento | Funzione | Cost stimato |
|---|---|---|
| Plausible Cloud (landing) | GA4 alternative privacy-first | $9/mese |
| Grafana Cloud free | Metrics dashboard | Free → $19/mese |
| Sentry | Error tracking | $26/mese |
| Hotjar / Microsoft Clarity (landing UX) | Heatmap, session recording | Free / $32/mese |

Decisione tool by tool quando KPI giustificano. Mai upgrade speculativo.

---

## 11. Decisioni canoniche analytics (locked)

| ID | Decisione | Motivazione |
|---|---|---|
| **D-AN-001** | 4 dimensioni KPI: visibilità, engagement, conversione, operativo | Mapping chiaro alle KPI di MASTER-PLAN sez. 8. |
| **D-AN-002** | Granularità temporale: real-time, weekly, monthly | Mix di tempi per decisioni operative + strategiche. |
| **D-AN-003** | Segmentazione obbligatoria per país in tutte le metriche | D-MP-016 + SR-010 enforcement. |
| **D-AN-004** | 30 query baseline manuali in v1, automatizzate M4+ | Sufficiente per detection trend mensile in v1. |
| **D-AN-005** | Subset 10 query MX-priority con soglia separata | SR-010 di MASTER-PLAN. |
| **D-AN-006** | Dashboard interna statica HTML in v1, generata daily | Cost-conscious, sufficient per dev solo. |
| **D-AN-007** | Auth dashboard via htpasswd + IP allowlist | Semplice, sicuro abbastanza per team interno. |
| **D-AN-008** | Drill-down via CLI script con audit log access | Bilancio flessibilità + compliance. |
| **D-AN-009** | Attribution AI via `Origin` header primary, User-Agent fallback, client_name secondary | Trade-off accuratezza vs disponibilità dati. |
| **D-AN-010** | Custom property `mcp_client_origin` in HubSpot per attribution lead | Permette funnel separato Claude vs ChatGPT. |
| **D-AN-011** | Email sempre hash SHA-256 in log analitici | Privacy by design, coerente D-AU-012. |
| **D-AN-012** | Niente BI tool esterno in v1 | Cost-conscious, dati restano nei Docker logs su VM Oracle + CRM HubSpot. |
| **D-AN-013** | Report mensile auto-generato a Merari il giorno 1 | Disciplina comunicazione, evita "non comunico più". |
| **D-AN-014** | Report trimestrale presenza diretta (30min Q1, 1h Q2+) | Allinea Merari su decisioni strategiche. |
| **D-AN-015** | Compliance audit log per ogni accesso a dati pseudonimizzati | LFPDPPP/GDPR. |
| **D-AN-016** | Retention metriche aggregate indefinite, raw log 90gg | Trade-off insight vs storage. |
| **D-AN-017** | Drill-down a singolo utente solo per debug / audit / user request, sempre loggato | Privacy + auditabilità. |
| **D-AN-018** | Niente cookie di tracking sulla landing, niente fingerprint | Privacy by design, distintivo vs concorrenza. |
| **D-AN-019** | GA4 sufficient per landing analytics in v1 (no Plausible) | Free, già setup, sufficient. Plausible se Merari prefer privacy-first. |
| **D-AN-020** | Funnel Tier 1→Tier 2→Lead esposto sempre nella dashboard | Health del funnel = health del business. |
| **D-AN-021** | Costo per lead (CPL) calcolato manualmente per ora, automatico M4+ | Sufficient v1, dato sparso (infra costo + tempo Claudio). |

---

## 12. Decisioni aperte analytics

| ID | Decisione | Bloccare entro | Owner |
|---|---|---|---|
| **DECISION-OPEN-AN-001** | Finalizzazione lista esatta delle 30 query baseline | M1 | Alessio |
| **DECISION-OPEN-AN-002** | Automazione esecuzione 30 query via API: timing M4 vs M5 | M4 | Claudio |
| **DECISION-OPEN-AN-003** | Migration GA4 → Plausible per landing (privacy-first signaling)? | M5 | Merari + Alessio |
| **DECISION-OPEN-AN-004** | Integrazione Grafana Cloud per metriche live in dashboard | M5 | Claudio |
| **DECISION-OPEN-AN-005** | Sentry per error tracking aggregato | M3 | Claudio |
| **DECISION-OPEN-AN-006** | Heatmap / session recording su landing per UX optimization | M4 | Alessio |
| **DECISION-OPEN-AN-007** | Public dashboard / status page (transparency signaling) | v2 | Merari |
| **DECISION-OPEN-AN-008** | Annual public report "State of MCP for Marketing LATAM" | v2 | Romina + Merari |
| **DECISION-OPEN-AN-009** | Tracking di "tempo medio lead → cliente" automatizzato da HubSpot | M4 | Claudio + Merari |
| **DECISION-OPEN-AN-010** | A/B testing infrastruttura per tool descriptions in M5+ | M5 | Claudio |

---

## 13. Versioning di questo documento

| Versione | Data | Autore | Note |
|---|---|---|---|
| 1.0 | 2026-05-10 | Claude (proposta) + Claudio (revisione) | Prima stesura completa: 4 dimensioni KPI, 30 query baseline distribuite per país, dashboard interna statica, attribution AI Claude vs ChatGPT, privacy by design, report mensile + trimestrale. |
| 1.1 | 2026-05-11 | Claude (harmony pass M0.3) + Claudio (review) | **HC-011**: passaggio da 4 a 5 dimensioni KPI con mapping esplicito a `00-MASTER-PLAN.md` sez. 8. Aggiunta sez. 4.5 "Qualitativo" con 6 metriche (mention, testimonial, Anthropic Directory status). **HC-012**: sez. 5.7 riscritta con tabella canonica baseline/target/trigger e regola precisa SR-006 ("< 25% aggregate AND delta < 5pp"). |

---

## Note per il changelog

*(Sezione vuota in v1.0 — verrà popolata se emergono incongruenze nei file successivi che richiedono retrofitting in questo ANALYTICS.)*

---

**Fine 11-ANALYTICS.md v1.0.**
