# 01 — ARCHITECTURE

| Campo | Valore |
|---|---|
| **Progetto** | Segmenta MCP Server |
| **Versione documento** | 1.2 |
| **Data** | 2026-05-11 |
| **Status** | Approvato (post harmony pass M0.3 + chiusura M0.2.1) |
| **File n.** | 01 di 12 numerati |
| **Documento padre** | `00-MASTER-PLAN.md` v1.3 |
| **File correlati** | `02-CONVENTIONS.md`, `03-DATA-MODEL.md`, `04-TOOLS-TIER1.md` |

---

## 1. Scopo del documento

Questo file descrive **come** il server MCP Segmenta è costruito tecnicamente. Risponde a tre tipi di domande:

1. *"Quali sono i pezzi del sistema e come comunicano?"* — sezioni 3, 4, 5
2. *"Quali decisioni tecniche sono bloccate, e perché?"* — sezione 12
3. *"Come si comporta il sistema in scenari specifici (cold start, errore, scaling)?"* — sezioni 6, 7, 9, 10

Il *cosa* (vision, scope, KPI) sta in `00-MASTER-PLAN.md`. Il *quando* (milestone, durate) sta in `MILESTONES.md`. I dettagli operativi di deploy stanno in `09-DEPLOYMENT.md`. Le specifiche dei singoli tool stanno in `04/05/06-TOOLS-TIER*.md`.

---

## 2. Principi guida

Cinque principi che sovraintendono ogni decisione tecnica del progetto. In caso di conflitto fra un principio e una scelta tattica, prevale il principio.

### 2.1 Stateless first

Il server non mantiene stato di sessione lato applicazione. Ogni chiamata tool è autocontenuta. Lo stato necessario (autenticazione utente, rate limit counter, idempotency key) vive in **storage esterno** (Redis o equivalente). Questo permette scaling orizzontale immediato e deploy rolling senza session affinity.

### 2.2 Lettura predominante, scrittura controllata

Il 90% delle chiamate tool sono read-only (Tier 1, parte di Tier 3). Questo guida l'ottimizzazione: cache aggressivo dei dati statici, lettura da JSON in memoria, latency p95 sotto 100ms per tool senza I/O. Le scritture (Tier 2: lead capture, booking) sono poche, asincrone, idempotenti.

### 2.3 Fail loud, fail safe

Errori tecnici devono essere visibili nei log e nei response (con codice errore stabile), mai silenziosi. Errori di business (input non valido, rate limit hit) tornano response strutturate, non eccezioni. Il server non degrada silenziosamente: se un'integrazione esterna è down, il tool corrispondente torna esplicitamente "servizio temporaneamente non disponibile" con `retry_after` indicato.

### 2.4 Boundary chiare, accoppiamento debole

I confini logici del sistema sono espliciti: codice tool ≠ codice integrazione ≠ codice auth. Cambiare provider booking (Cal.com → Calendly) deve toccare un solo modulo. Cambiare CRM (HubSpot → Pipedrive) idem. Sostituibilità è una feature, non un nice-to-have.

### 2.5 Observable by default

Ogni tool call genera almeno una struttura log standard (vedi sez. 7). Ogni errore è correlabile via `request_id`. Le metriche critiche (tool calls/min, error rate, latency p95) sono esposte sempre, non solo in produzione. Senza observability si vola alla cieca.

---

## 3. Stack tecnologico

### 3.1 Core stack

| Layer | Tecnologia | Versione minima | Motivazione |
|---|---|---|---|
| Linguaggio | Python | 3.12 | Skill Claudio, ecosistema MCP maturo, type hints moderni. |
| MCP framework | `fastmcp` | 3.2.0 | Standard de facto Python per MCP server, decorator-based, supporto streamable-http nativo, gestione OAuth integrata. |
| Web server | Starlette + Uvicorn | 0.36 / 0.27 | Embedded in FastMCP. ASGI standard, performance solide, supporto SSE per MCP. |
| Validation | Pydantic | 2.6 | Validazione input tool, modelli dati, schema JSON automatico. |
| HTTP client | `httpx` | 0.27 | Async-native, usato per integrazioni esterne (Cal.com, CRM, Resend). |
| Crawler | `BeautifulSoup4` + `httpx` | latest | Per `diagnostico_seo_express` (Tier 2). Niente Playwright in v1 (peso eccessivo). |
| OAuth | `authlib` | 1.3 | Standard mature, supporta dynamic client registration (RFC 7591). |
| Cache / state | Redis | 7.x | Rate limiting, idempotency keys, OAuth session store. |
| Email transactional | (vedi DECISION-OPEN-004) | - | Resend / SendGrid / Mailgun decisione M2. |
| Logging | `structlog` | 24.x | JSON logging strutturato, correlation IDs, livelli configurabili. |
| Metrics | `prometheus_client` | 0.20 | Standard de facto per metriche Python, scraping da Fly.io. |
| Test framework | `pytest` + `pytest-asyncio` | 8.x / 0.23 | Standard de facto. |

### 3.2 Stack di deploy

| Layer | Tecnologia | Motivazione |
|---|---|---|
| Containerization | Docker | Standard portabile, supporto Fly.io nativo. |
| Hosting compute | Fly.io | Free tier sufficiente per partire, dashboard semplice, supporto Dockerfile, dominio custom + HTTPS automatico. (Dettagli e alternative in `09-DEPLOYMENT.md`.) |
| Hosting Redis | Upstash Redis (free tier 10k cmd/giorno, 256 MB) | Provider esterno, free tier sufficiente M1-M3. Fly.io non ha Redis add-on nativo (a differenza di Railway). |
| DNS | Provider attuale di `segmentamarketing.com` (presunto Cloudflare o Hostinger) | Nessun cambiamento. CNAME su `mcp` subdomain. |
| TLS | Let's Encrypt via Fly.io | Automatico, no manutenzione. |
| CI/CD | GitHub Actions | Standard, integrazione nativa con repo pubblico. (Dettagli in `09-DEPLOYMENT.md`.) |
| Monitoring | Fly.io built-in + UptimeRobot per probe esterno | Gratis, sufficiente in v1. |

### 3.3 Stack escluso (e perché)

Decisioni esplicite di *non usare* certe tecnologie. Documentate per evitare che riemergano in discussioni future.

- ❌ **Cloudflare Workers** — più complesso per OAuth dinamico stateful, tooling Python non maturo, vincoli edge runtime su CPU time.
- ❌ **AWS Lambda** — cold start incompatibile con SLA latency p95, gestione DNS/HTTPS più macchinosa per un singolo dev.
- ❌ **Kubernetes self-hosted** — over-engineering per il volume previsto, costo cognitivo non giustificato.
- ❌ **TypeScript/Node** — pur essendo l'altro SDK MCP ufficiale, Python è il linguaggio principale di Claudio (skill esistente, allineato con altri progetti come Numely).
- ❌ **PostgreSQL/MySQL in v1** — D-MP-013 esclude database in v1. Dati statici in JSON file in repo.
- ❌ **Playwright/Selenium per crawling** — troppo pesante per il MVP di `diagnostico_seo_express`. BeautifulSoup + httpx coprono il 95% dei siti target.
- ❌ **Celery / RQ task queue** — niente background job complessi in v1. Le poche operazioni asincrone (invio email, webhook CRM) usano `asyncio.create_task` con retry inline.
- ❌ **gRPC** — il protocollo MCP è HTTP+SSE, non c'è ragione di introdurre un secondo protocollo interno.
- ❌ **GraphQL** — sovrastruttura non necessaria; i tool MCP hanno schema tipizzato già nativo.

---

## 4. Architettura logica del sistema

### 4.1 Componenti principali

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         CLIENT MCP                                       │
│  Claude.ai · Claude Desktop · ChatGPT (Dev Mode) · Cursor · altri       │
└──────────────────────┬──────────────────────────────────────────────────┘
                       │ HTTPS + SSE (streamable-http)
                       │ OAuth 2.0 dynamic (RFC 7591) per Tier 2/3
                       ▼
┌─────────────────────────────────────────────────────────────────────────┐
│              MCP SERVER (Segmenta)                                       │
│              mcp.segmentamarketing.com                                   │
│                                                                          │
│  ┌─────────────┐   ┌──────────────┐   ┌──────────────────────────────┐ │
│  │  Routing    │──▶│  Auth Layer  │──▶│  Tool Dispatcher             │ │
│  │  (Starlette)│   │  (authlib)   │   │  (FastMCP decorators)        │ │
│  └─────────────┘   └──────────────┘   └──────────────────────────────┘ │
│                                                  │                       │
│           ┌──────────────────────┬──────────────┴──────────────────┐   │
│           ▼                      ▼                                  ▼   │
│  ┌────────────────┐    ┌──────────────────┐         ┌──────────────────┐│
│  │ Tier 1 Tools   │    │ Tier 2 Tools     │         │ Tier 3 Tools     ││
│  │ (público)      │    │ (lead capture)   │         │ (avanzado)       ││
│  │                │    │                  │         │                  ││
│  │ - servicios    │    │ - diagnostico    │         │ - whatsapp       ││
│  │ - casos        │    │ - presupuesto    │         │ - share_research ││
│  │ - benchmark    │    │ - agendar        │         │ - competencia    ││
│  │ - glosario     │    │ - propuesta      │         │ - compare        ││
│  │                │    │ - disponibilidad │         │ - caso_pais      ││
│  └────────┬───────┘    └────────┬─────────┘         └────────┬─────────┘│
│           │                     │                            │          │
│           ▼                     ▼                            ▼          │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │  Data Layer (in-memory JSON cache + integrazioni esterne)          ││
│  └─────────────────────────────────────────────────────────────────────┘│
└──────────┬───────────────────┬─────────────────────┬─────────────────────┘
           │                   │                     │
           ▼                   ▼                     ▼
   ┌──────────────┐   ┌────────────────┐   ┌────────────────────┐
   │ JSON Files   │   │ Redis          │   │ External APIs      │
   │ (in repo)    │   │ - rate limit   │   │ - Booking platform │
   │ - servicios  │   │ - OAuth state  │   │ - CRM webhook      │
   │ - casos      │   │ - idempotency  │   │ - Email service    │
   │ - benchmark  │   │                │   │ - WhatsApp API     │
   │ - glosario   │   │                │   │                    │
   └──────────────┘   └────────────────┘   └────────────────────┘
```

### 4.2 Layer del server (responsabilità isolate)

Il codice del server è organizzato in **5 layer** con dipendenze unidirezionali (un layer chiama solo i layer sotto di sé):

| # | Layer | Responsabilità | Dipendenze | Moduli (vedi `02-CONVENTIONS.md` sez. 3.1) |
|---|---|---|---|---|
| 1 | **Transport** | Routing HTTP, SSE streaming, MCP protocol negotiation | FastMCP, Starlette | `src/segmenta_mcp/transport/` |
| 2 | **Auth** | OAuth 2.0 dynamic, JWT validation, rate limiting, request_id | Layer 1, Redis | `src/segmenta_mcp/auth/` |
| 3 | **Tool definitions** | Decorator `@mcp.tool`, validazione input/output via Pydantic | Layer 1, Layer 2 | `src/segmenta_mcp/tools/{tier1,tier2,tier3}/` |
| 4 | **Domain logic** | Logica di business pure functions: filtri case study, calcolo presupuesto, formatter risposte | Layer 5 (data) | `src/segmenta_mcp/domain/` |
| 5 | **Data & Integrations** | Caricamento JSON, chiamate API esterne, fallback | httpx, librerie SDK esterne | `src/segmenta_mcp/data/` + `src/segmenta_mcp/integrations/` |

Vincoli rigidi:
- Layer 4 (domain) **non importa** httpx o codice di integrazione direttamente — passa per Layer 5.
- Layer 3 (tools) **non implementa** logica di business — delega a Layer 4.
- Layer 1 e 2 sono **infrastruttura pura** — non sanno nulla del dominio Segmenta.
- Pattern "1 tool = 1 file": ogni tool è un modulo `.py` separato in `tools/tier{N}/<nome_tool>.py`.

Questa disciplina permette di testare Layer 4 in pure unit test (zero I/O), e Layer 5 in integration test isolati. La colonna "Moduli" mappa esplicitamente al directory layout in `02-CONVENTIONS.md` sez. 3.1.

---

## 5. Data flow

### 5.1 Caso 1 — Tool Tier 1 (público, no auth)

Esempio: utente chiede a Claude *"¿qué es el GEO?"*. Claude decide di chiamare `glosario_marketing(termino="GEO")`.

```
1. Client (Claude) ──HTTPS POST /mcp/tool──▶ Server
                          │ headers: Mcp-Session-Id, no Authorization
                          │ body: { tool: "glosario_marketing", args: { termino: "GEO" } }
                          │
2. Transport layer        │ → assegna request_id, inizia span log
                          │
3. Auth layer             │ → tier 1, no auth required
                          │ → rate limit check (60/min/IP) via Redis
                          │ → se OK, prosegue. Se rate limited, 429 con retry_after
                          │
4. Tool dispatcher        │ → identifica tool "glosario_marketing"
                          │ → valida args contro schema Pydantic
                          │
5. Domain logic           │ → cerca termine in cache JSON in-memory
                          │ → match esatto / fuzzy / fallback con suggerimenti
                          │
6. Response               │ → struttura output Pydantic
                          │ → log success con latency_ms
                          │
7. Server ──SSE response──▶ Client
                          │ body: { definicion, ejemplo, errores_comunes, ... }
```

Latency budget: < 50ms p95 (in-memory lookup, no I/O).

### 5.2 Caso 2 — Tool Tier 2 (lead capture, OAuth)

Esempio: utente chiede *"agéndame una auditoría gratis"*. Claude chiama `agendar_auditoria_gratuita(...)` ma il client non ha ancora token OAuth per il server Segmenta.

```
1. Client                 ──POST /mcp/tool──▶ Server
                          │ tool: agendar_auditoria_gratuita, no Authorization
                          │
2. Auth layer             │ → tier 2 → 401 Unauthorized + WWW-Authenticate header
                          │ → response include OAuth metadata URL
                          │
3. Client (OAuth flow)    │ ←────────────── inizia OAuth dynamic registration ─┐
                          │                                                     │
   Client ──GET /.well-known/oauth-authorization-server──▶ Server               │
                          │ → ritorna metadata OAuth (RFC 8414)                 │
                          │                                                     │
   Client ──POST /oauth/register──▶ Server                                      │
                          │ → registra client (RFC 7591), ritorna client_id     │
                          │                                                     │
   Client ──redirect user a /oauth/authorize──▶ Server                          │
                          │ → server invia magic link via email all'utente      │
                          │ → utente clicca link, sessione creata in Redis      │
                          │ → server fa redirect con auth_code                  │
                          │                                                     │
   Client ──POST /oauth/token──▶ Server                                         │
                          │ → scambia auth_code per access_token + refresh      │
                          │                                                     │
4. Client retry           │ ──POST /mcp/tool con Authorization: Bearer xxx──▶   │
                          │                                                     │
5. Auth layer             │ → valida JWT, estrae user_email                     │
                          │ → rate limit più stretto (10/min/IP)                │
                          │                                                     │
6. Tool dispatcher        │ → invoca agendar_auditoria_gratuita                 │
                          │                                                     │
7. Domain logic           │ → valida slot disponibili                           │
                          │                                                     │
8. Integration layer      │ → chiama API booking platform                       │
                          │ → su success, webhook al CRM Segmenta               │
                          │ → su failure integrazione, ritorna errore strutturato
                          │                                                     │
9. Response               │ ──▶ Client                                          │
                          │   con conferma slot + link videocall               ─┘
```

Latency budget: < 800ms p95 (include 2 chiamate esterne + webhook async).

Note critiche:
- **Magic link email** richiede integrazione email transactional pronta (DECISION-OPEN-004 risolta entro M2).
- **Idempotency**: la chiamata booking deve essere idempotente — l'utente potrebbe ritriare. Idempotency key in Redis con TTL 24h.

### 5.3 Caso 3 — Tool con failure mode integrazione esterna

Esempio: `solicitar_propuesta_personalizada` chiamato, ma l'API CRM è giù.

```
1. Tool invocato → Domain logic prepara payload propuesta
2. Integration layer → POST a CRM webhook → timeout / 503
3. Retry policy → 3 tentativi con exponential backoff (1s, 2s, 4s)
4. Tutti falliti → fallback:
     a) Salva il payload in Redis con TTL 7 giorni (chiave fallback_propuesta:{request_id})
     b) Invia email a alerts@segmentamarketing.com con il payload completo
     c) Risponde all'utente: "Tu solicitud fue recibida correctamente. El equipo te
        contactará en las próximas 24h." (vero — l'email arriva al team)
5. Background job (a M5, niente in v1) → riprova webhook ogni 1h fino a TTL.
   In v1: il team manualmente inserisce nel CRM dalla email.
```

Principio: **mai dire bugie all'utente, mai perdere un lead**. Se il sistema primario fallisce, il fallback email è il safety net.

---

## 6. Tier system — disciplina commerciale come architettura

Il tier system non è solo organizzazione logica; è un **vincolo architetturale** che si riflette in 3 strati concreti:

### 6.1 Strato auth

| Tier | Auth required | Rate limit (/min/IP) | Token TTL |
|---|---|---|---|
| 1 — público | No | 60 | n/a |
| 2 — lead capture | OAuth 2.0 + email verified | 10 | 7 giorni access, 30 refresh |
| 3 — avanzado | OAuth 2.0 + email verified + (in alcuni casi) crediti | 10 | 7 giorni access, 30 refresh |

### 6.2 Strato logging & analytics

I log differenziano il tier per consentire analisi separate:
- **Tier 1**: tracking aggregato (count per tool, country distribution dal IP), nessun PII.
- **Tier 2**: tracking individuale (user_email hash, tool calls history) per attribution e funnel analysis.
- **Tier 3**: tracking individuale + tag "post-conversion" o "intelligence" per separare metriche di retention vs acquisizione.

### 6.3 Strato deployment

Tier 1 deve essere disponibile **anche se** Tier 2/3 hanno problemi. Implementazione: i tool Tier 1 non hanno dipendenze hard verso Redis (degradano a "no rate limit" se Redis è down). I tool Tier 2/3 fail-safe se Redis è down (non possono operare senza idempotency check, quindi rispondono "servizio temporaneamente non disponibile").

Questa è una scelta esplicita: **proteggere l'esca a costo della conversione**, perché perdere visibilità sull'esca distrugge il funnel intero, mentre perdere temporaneamente conversione genera solo lead in ritardo.

---

## 7. Observability

### 7.1 Logging

**Formato**: JSON strutturato via `structlog`, una linea per evento. Output stdout (cattura Fly.io).

**Campi obbligatori in ogni log line**:
```json
{
  "timestamp": "2026-05-10T14:32:18.453Z",
  "level": "INFO",
  "request_id": "req_01JXXXXXX",
  "tier": "1",
  "tool": "glosario_marketing",
  "client_origin": "claude.ai" | "chatgpt.com" | "unknown",
  "user_country": "MX",
  "latency_ms": 23,
  "status": "success" | "error" | "rate_limited",
  "message": "tool_call_completed"
}
```

**Campi opzionali per error**:
```json
{
  "error_code": "INTEGRATION_TIMEOUT",
  "error_detail": "Cal.com API timed out after 5s",
  "retry_count": 2
}
```

**Livelli**:
- `DEBUG`: tracing dettagliato, abilitato solo in development.
- `INFO`: eventi normali (tool call, OAuth flow step).
- `WARN`: anomalie recuperate (retry success after failure, fallback attivato).
- `ERROR`: errori che richiedono attenzione umana (integrazione esterna down per > 5min, error rate elevato).
- `CRITICAL`: errori che bloccano il servizio (Redis irraggiungibile, configurazione mancante).

### 7.2 Metrics

Esposte su `/metrics` in formato Prometheus. Le metriche minime in v1:

| Metric | Tipo | Labels | Significato |
|---|---|---|---|
| `mcp_tool_calls_total` | Counter | `tool`, `tier`, `status` | Numero totale chiamate. |
| `mcp_tool_latency_seconds` | Histogram | `tool`, `tier` | Distribuzione latency. |
| `mcp_oauth_flow_total` | Counter | `step`, `status` | Tracking OAuth flow conversion. |
| `mcp_rate_limit_hits_total` | Counter | `tier` | Numero di rate limit triggered. |
| `mcp_integration_calls_total` | Counter | `integration`, `status` | Chiamate a Cal.com, CRM, email. |
| `mcp_integration_latency_seconds` | Histogram | `integration` | Latency integrazioni esterne. |
| `mcp_active_oauth_sessions` | Gauge | - | Sessioni OAuth attive (Tier 2/3). |

In M4 saranno scraped da una dashboard interna (vedi `11-ANALYTICS.md`). In v1 sono esposte ma non visualizzate (sufficient: Fly.io dashboard built-in).

### 7.3 Tracing

In v1: tracing implicito via `request_id` propagato nei log. Niente OpenTelemetry / Jaeger esplicito (costo cognitivo non giustificato).

In v2/M5 si valuta: OpenTelemetry per spans distribuiti se la complessità delle integrazioni cresce.

### 7.4 Alerting

In v1: alerting minimo. Tre canali:
- **UptimeRobot** ping `/health` ogni 5 min, alert via email se 2 fallimenti consecutivi.
- **Fly.io dashboard**: alert su CPU > 80% per > 5 min, memory > 80%.
- **Custom**: log line con livello `CRITICAL` triggera webhook a Slack del team Segmenta (in M2, con setup CRM).

In M5/v2: integrazione Sentry o equivalente per error tracking aggregato.

---

## 8. Sicurezza

### 8.1 Threat model (alto livello)

Le minacce realisticamente affrontabili in v1:

| Minaccia | Probabilità | Impatto | Contromisura |
|---|---|---|---|
| Rate limit abuse / DOS amatoriale | Media | Basso | Rate limit per IP, Cloudflare in front (gestito da Fly.io). |
| Credential stuffing su OAuth | Bassa | Medio | Magic link email-only (no password), session expiry 7gg. |
| SQL injection / data corruption | n/a | n/a | No database in v1. JSON read-only in repo. |
| Prompt injection via tool input | Media | Medio | Validazione strict Pydantic, no codice eseguito su input utente. (Vedi 8.3) |
| Lead exfiltration (data breach) | Bassa | Alto | Lead in CRM esterno, non in database del server. Server passa-attraverso. |
| Man-in-the-middle | Bassa | Alto | HTTPS obbligatorio, HSTS abilitato. |
| Compromise repo GitHub | Bassa | Alto | Secrets in Fly.io env, mai in repo. Branch protection su main. |
| Supply chain attack (dipendenza malevola) | Bassa | Alto | `requirements.txt` con versioni pinned, Dependabot abilitato. |

### 8.2 Secrets management

- Secrets vivono in **Fly.io environment variables** (criptate at-rest).
- Mai in `.env` committato. `.env.example` con placeholder è OK.
- Rotazione manuale ogni 90 giorni (incluso in checklist `09-DEPLOYMENT.md`).
- Esempi di secrets: API key Cal.com, API key CRM, JWT signing key, Resend API key.

### 8.3 Input validation

- Tutti gli input tool passano per Pydantic — type coercion + range check + enum.
- `diagnostico_seo_express` accetta URL: validazione `httpx.URL` + check schema `https://`, blocklist domini interni (no `localhost`, `127.0.0.1`, `*.internal`, IP privati RFC 1918).
- Email per OAuth: validazione formato + (in v2) verifica deliverability via API.
- Stringhe lunghe (es. brief in `solicitar_propuesta_personalizada`): limite 5000 caratteri, troncamento esplicito con notifica utente se superato.

### 8.4 Privacy

Cf. `00-MASTER-PLAN.md` D-MP-014 — giurisdizione primaria LFPDPPP, addendum GDPR/CCPA. Implementazione tecnica concreta:

- **Data minimization**: il server registra solo dati strettamente necessari (email per Tier 2, mai numero di telefono in Tier 1, mai dati sensibili tipo DNI).
- **Retention**: log con PII (Tier 2/3) → 90 giorni rolling. Log senza PII (Tier 1 aggregato) → 365 giorni. Dopo: aggregazione con drop dei dettagli identificabili.
- **Right to access / delete**: endpoint `/privacy/data-request` e `/privacy/data-deletion` (in M2, con OAuth attivo). In v1: indirizzo email `privacidad@segmentamarketing.com` per richieste manuali.
- **Cross-border transfer**: dati da utenti EU vanno via Fly.io US per il compute. Coperto da addendum GDPR (clausole contrattuali standard / SCC).

Dettagli completi in `07-AUTH-OAUTH.md` e `10-GTM.md` (privacy policy testuale).

---

## 9. Performance & scaling

### 9.1 Carico previsto

Stime basate sui KPI di `00-MASTER-PLAN.md`:

| Periodo | Tool calls/giorno (target) | Picco /min |
|---|---|---|
| Soft launch (M1-M2) | 20-50 | 5 |
| Post-GTM (M3-M4) | 100-300 | 20 |
| Steady state (M5+) | 500-1000 | 50 |
| Picco virale (caso miglior eccezionale) | 5000 | 200 |

### 9.2 Capacità del singolo container

Container Fly.io base (1 GB RAM, shared CPU) sostiene:
- Tier 1 tool: ~1000 req/sec teorico (tutto in memoria, no I/O).
- Tier 2 tool con integrazione: limited dalle API esterne (Cal.com ~100 req/sec free tier; CRM webhook ~10 req/sec sicuro).

Bottleneck reale in v1: **rate limit Cal.com / CRM**, non il server. La capacità del server è 10x rispetto al carico previsto in steady state.

### 9.3 Scaling strategy

**v1 (M1-M4)**: single container, no scaling automatico. Fly.io permette manual scaling se serve.

**v2 (post M5)**:
- Horizontal scaling tramite Fly.io autoscaling (2-4 container min/max).
- Sticky sessions **non necessarie** (server stateless — vedi principio 2.1).
- Redis è già esterno, scala indipendentemente.

**Trigger per scaling**:
- CPU sustained > 70% per > 10 min → +1 container.
- Latency p95 sustained > 800ms per > 5 min → investigation manuale prima di scaling (potrebbe essere un'integrazione lenta, non server overloaded).

### 9.4 Cold start

Il server in Python ha cold start ~3 secondi (caricamento JSON + warmup). Mitigazione:
- Fly.io: container "always on" sul piano usato. No cold start dopo prima richiesta.
- UptimeRobot ping ogni 5 min mantiene il container caldo.
- In v2, se passassimo a Fly.io con auto-stop, valuteremmo container "min instances = 1".

---

## 10. Resilience patterns

Pattern applicati ovunque l'architettura tocca componenti che possono fallire.

### 10.1 Timeout aggressive

Ogni chiamata HTTP esterna ha timeout esplicito:
- Tier 1 (no esterne): n/a.
- Tier 2 booking call: 5 secondi connect, 10 secondi total.
- Tier 2 CRM webhook: 3 secondi connect, 8 secondi total.
- Tier 2 email send: 3 secondi connect, 5 secondi total (poi fire-and-forget retry async).

### 10.2 Retry con exponential backoff

Per integrazioni idempotenti (CRM webhook, email send): 3 tentativi con backoff 1s, 2s, 4s.

Per booking call: **1 solo tentativo** (creare doppi appuntamenti è peggio che non crearli affatto). Idempotency key garantisce che retry futuri vengano riconosciuti.

### 10.3 Circuit breaker

In v1: implementazione manuale con counter Redis. Se un'integrazione fallisce ≥ 5 volte consecutive in 60 secondi, "apre il circuito" per 5 minuti — durante questo tempo i tool che la usano rispondono direttamente con fallback senza tentare la chiamata.

In v2: si valuta libreria dedicata (`circuitbreaker` o `pybreaker`).

### 10.4 Graceful degradation

| Componente down | Cosa succede |
|---|---|
| Redis | Tier 1 funziona senza rate limit. Tier 2/3 rispondono "Servicio temporalmente no disponible. Por favor, contáctanos directamente en hola@segmentamarketing.com" (HTTP 503). |
| Booking platform | `agendar_auditoria_gratuita` risponde con fallback: "Sistema de reservas temporalmente no disponible. ¿Quieres que te contactemos por email?" + collect email. |
| CRM webhook | Lead salvato in Redis fallback queue, email a alerts@. Risposta utente positiva (lead non perso). |
| Email transactional | `diagnostico_seo_express` risponde con preview inline + "El reporte completo te llegará por email en cuanto el sistema se restablezca". |
| Cache JSON corrotta | Health check fallisce → Fly.io riavvia container → caricamento da repo. |

### 10.5 Idempotency

Tutte le scritture (Tier 2) sono idempotenti via `idempotency_key` in Redis (TTL 24h).

Pattern:
1. Tool riceve chiamata, calcola hash determinístico di `(user_email, tool_name, key_args)`.
2. Check Redis: se key esiste, ritorna risultato salvato.
3. Altrimenti: esegue, salva risultato in Redis, ritorna.
4. TTL 24h: dopo 24h la chiamata è "nuova" anche se identica.

Questo protegge da:
- Click multipli dell'utente sul "agendar" button.
- Retry del client MCP per network failure.
- Sviluppatore in test che spamma la stessa chiamata.

---

## 11. Ambiente di esecuzione

### 11.1 Tre ambienti

| Ambiente | URL | Scopo | Dati |
|---|---|---|---|
| **Local** | `http://localhost:8000` | Dev quotidiano di Claudio | JSON in repo, Redis locale via Docker |
| **Staging** | `mcp-staging.segmentamarketing.com` | Pre-deploy validation, test integrazioni | JSON in repo (branch), Redis Fly.io, sandbox booking/CRM |
| **Production** | `mcp.segmentamarketing.com` | Live | JSON in repo (main), Redis Fly.io, prod booking/CRM |

### 11.2 Differenze tra ambienti

| Aspetto | Local | Staging | Production |
|---|---|---|---|
| Logging level | DEBUG | INFO | INFO |
| Rate limit | Disabilitato | Permissivo (300/min) | Standard (60/10) |
| Email send | Mock (log, no envio) | Sandbox (`*@staging.com`) | Reale |
| Booking platform | Mock o sandbox | Sandbox | Live |
| CRM webhook | Mock endpoint | Sandbox endpoint | Live endpoint |
| OAuth issuer | `localhost:8000` | `mcp-staging.segmentamarketing.com` | `mcp.segmentamarketing.com` |
| Allowed CORS origins | `*` | `claude.ai`, `chatgpt.com`, `localhost` | `claude.ai`, `chatgpt.com` |

### 11.3 Promotion flow

```
local (feature branch) ──PR──▶ staging (auto-deploy on merge to develop)
                                         │
                                         │ smoke test + manual QA
                                         ▼
                              production (auto-deploy on merge to main)
                                         │
                                         │ post-deploy verification
                                         ▼
                              UptimeRobot conferma uptime
```

Dettagli CI/CD in `09-DEPLOYMENT.md`.

---

## 12. Decisioni canoniche tecniche (locked)

Decisioni tecniche bloccate in v1.0 di questo file. Cambiarle richiede aggiornamento esplicito.

| ID | Decisione | Motivazione |
|---|---|---|
| **D-A-001** | Stack Python 3.12 + FastMCP 3.2+ | Skill Claudio, ecosistema MCP Python maturo, type hints moderni. |
| **D-A-002** | Single container monolite (no microservices) | Volume previsto basso, costo cognitivo microservices non giustificato. |
| **D-A-003** | Stateless server, stato in Redis | Permette scaling orizzontale immediato e deploy rolling senza session affinity. |
| **D-A-004** | Dati in JSON file in repo (no database) | Coerente con D-MP-013. Semplicità deploy + versioning Git automatico. |
| **D-A-005** | Auth: OAuth 2.0 dynamic registration (RFC 7591) per Tier 2/3 | Standard MCP, supportato nativamente da Claude e ChatGPT. |
| **D-A-006** | Magic link email come unico fattore auth (no password) | Mercato target B2B, ridotto attrito, no password leak risk. |
| **D-A-007** | Rate limit per IP (no per user in Tier 1, per user_email in Tier 2/3) | IP è solo "abuse prevention" in Tier 1. User-level più preciso dopo OAuth. |
| **D-A-008** | Logging JSON strutturato via structlog | Standard de facto per Python observability. |
| **D-A-009** | Metriche Prometheus, scraping da Fly.io | Standard, low overhead, sufficient per v1. |
| **D-A-010** | Cinque layer architetturali (Transport / Auth / Tools / Domain / Data&Integrations) | Disciplina di accoppiamento debole. Fa parte dei principi guida. |
| **D-A-011** | Tre ambienti (local, staging, production) con DNS distinti | Standard. Staging permette test integrazioni reali in sandbox. |
| **D-A-012** | Idempotency su ogni scrittura Tier 2 via Redis (TTL 24h) | Protegge da retry, click multipli, debugging in dev. |
| **D-A-013** | Timeout aggressivi su tutte le chiamate esterne (5-10s) | Meglio fallire chiaramente che restare appesi. |
| **D-A-014** | Circuit breaker manuale via Redis counter (no libreria in v1) | Sufficiente per il volume. Libreria valutata in v2. |
| **D-A-015** | No background job queue in v1 (Celery/RQ esclusi) | Niente job complessi. Async inline con `asyncio.create_task` è sufficiente. |
| **D-A-016** | HTTPS obbligatorio everywhere (HSTS abilitato) | Requisito Anthropic/OpenAI per Custom Connectors. |
| **D-A-017** | Versione MCP protocol: latest stable supportata da FastMCP 3.2 (al 2026-05-10: 2025-06-18) | Allineamento con SDK ufficiale. Major bump del protocollo verrà gestito quando emerge. |
| **D-A-018** | Redis (no Memcached, no in-memory only) | Persistence in caso di restart container, supporto data structures (sorted set per rate limit). |
| **D-A-019** | Python typing stretto: `from __future__ import annotations` ovunque, mypy in CI | Disciplina codice di un solo dev: il typing aiuta a non perdersi in 6 mesi. |
| **D-A-020** | Niente caching dei risultati LLM lato server | Coerente con principi: la cache lato LLM client è già presente, non duplichiamo. |
| **D-A-021** | Python virtual env via `uv` (no `pip` diretto, no `poetry`) | Standard moderno, 10x più veloce, allineato con altri progetti Claudio. |

---

## 13. Decisioni aperte tecniche

Decisioni tecniche da chiudere prima di milestone specifiche.

| ID | Decisione | Bloccare entro | Owner |
|---|---|---|---|
| ~~**DECISION-OPEN-T-001**~~ | ~~Provider Redis~~ → **Chiusa 2026-05-11**: Upstash diretto (free tier 10k cmd/giorno). Fly.io non ha Redis add-on integrato. Fly.io Redis dedicato ($1.94/mese) come fallback se Upstash insufficiente in M4+. | ✅ Chiusa | Claudio |
| **DECISION-OPEN-T-002** | Strategia di JWT signing: HS256 (simmetrica) vs RS256 (asimmetrica con JWKS) | M2 | Claudio |
| **DECISION-OPEN-T-003** | Approccio a `diagnostico_seo_express`: BeautifulSoup-only vs aggiunta di parser strutturato (es. `selectolax` per perf) | M2 | Claudio |
| **DECISION-OPEN-T-004** | Geolocation IP: gestione lato server (MaxMind / IPAPI) vs trust client headers | M3 | Claudio |
| **DECISION-OPEN-T-005** | OpenTelemetry tracing: introdurre già in v1 o rimandare a v2 | M5 | Claudio |
| **DECISION-OPEN-T-006** | Sentry o equivalente per error tracking aggregato | M3 | Claudio |
| **DECISION-OPEN-T-007** | Strategia versioning protocollo MCP: pinning a una versione vs auto-upgrade con FastMCP | M2 | Claudio |
| **DECISION-OPEN-T-008** | I/O scheduling per `share_research`: invio sincrono vs queue Redis con worker | M4 | Claudio |

---

## 14. Diagramma di stato del server

Stati possibili del server e transizioni:

```
                    ┌──────────────┐
                    │   STARTING   │
                    │   (boot)     │
                    └──────┬───────┘
                           │ JSON loaded, Redis ping OK
                           ▼
                    ┌──────────────┐
            ┌──────▶│   HEALTHY    │◀─────┐
            │       └──────┬───────┘      │
            │              │              │
            │              │ Redis fail   │
            │              ▼              │
            │       ┌──────────────┐      │ Redis recovers
            │       │   DEGRADED   │      │
            │       │ (Tier 1 only)│──────┘
            │       └──────┬───────┘
            │              │ Critical error (JSON corrupt, etc.)
            │              ▼
            │       ┌──────────────┐
            │       │  UNHEALTHY   │ ──── Fly.io restart ────┐
            │       └──────────────┘                          │
            │                                                 │
            └─────────────────────────────────────────────────┘
                              (back to STARTING)
```

**Transizione visibile via `/health` endpoint**:
- `HEALTHY`: HTTP 200, body `{"status": "healthy"}`.
- `DEGRADED`: HTTP 200, body `{"status": "degraded", "details": {...}}`.
- `UNHEALTHY`: HTTP 503, body `{"status": "unhealthy", "errors": [...]}`.

UptimeRobot probe configurato per considerare `200 + body contiene "healthy"` come UP. Status `degraded` → alert non bloccante. Status 503 → page Claudio.

---

## 15. Esempio concreto di flusso end-to-end

Per fissare le idee, qui un caso completo che attraversa tutti i layer:

**Scenario**: utente in CDMX chiede a ChatGPT (con il server Segmenta connesso come Custom App) un'auditoría gratis.

```
T+0ms:    Utente: "Quiero una auditoría SEO gratis para mi tienda online"
T+50ms:   ChatGPT decide: deve chiamare un tool. Sceglie agendar_auditoria_gratuita
          dopo aver chiamato obtener_servicios per capire cosa è disponibile.

T+100ms:  ChatGPT ──POST /mcp/tool {tool: obtener_servicios}──▶ Server Segmenta
          (Tier 1, no auth, no rate limit hit)
T+120ms:  Server risponde: catalogo servizi (in-memory lookup)
T+130ms:  ChatGPT mostra all'utente sintesi servizi.

T+200ms:  Utente: "Sí, agéndame esa auditoría"
T+250ms:  ChatGPT ──POST /mcp/tool {tool: agendar_auditoria_gratuita, args: {...}}──▶
T+260ms:  Server: tier 2, no Authorization header → 401 + WWW-Authenticate
T+270ms:  ChatGPT inizia OAuth flow:
          - GET /.well-known/oauth-authorization-server → metadata
          - POST /oauth/register → client_id assegnato
          - Redirect utente a /oauth/authorize → email magic link inviato
T+5min:   Utente clicca magic link nella sua email
T+5m+1s:  Server: sessione OAuth creata in Redis. Redirect con auth_code.
T+5m+2s:  ChatGPT: POST /oauth/token → access_token JWT
T+5m+3s:  ChatGPT: retry POST /mcp/tool con Authorization: Bearer {jwt}
          - Auth layer: JWT valido, user_email = "juan@tiendamx.com", tier 2
          - Rate limit check: 0/10/min, OK
          - Idempotency check: hash(juan, agendar, slot_2026_05_15) non presente
          - Domain logic: valida slot disponibile
          - Integration layer: POST a Cal.com API
          - Cal.com: 200 OK, booking_id ABC123
          - Integration layer: POST a CRM webhook (HubSpot)
          - HubSpot: 200 OK, lead_id 789
          - Domain logic: prepara response strutturata
          - Idempotency: salva risultato in Redis con TTL 24h
T+5m+5s:  Server ──response──▶ ChatGPT
          { confirmation: "Auditoría agendada para 2026-05-15 14:00 CDMX",
            videocall_link: "https://meet.segmenta.com/abc",
            summary: "..." }
T+5m+6s:  ChatGPT mostra all'utente conferma + link.
T+5m+7s:  Background: log line con tier=2, tool=agendar_auditoria_gratuita,
          status=success, integrations=[calcom_ok, hubspot_ok], latency_ms=2300

# In parallelo, sul team Segmenta:
T+5m+5s:  HubSpot ha creato lead → automation Segmenta:
          - Email a Merari: "Nuevo lead MCP: Juan, tienda online MX"
          - Slack #leads: notifica con dettagli
          - Auto-assign al sales rep MX
```

Questo esempio mostra: 5 layer del server toccati, 3 integrazioni esterne, OAuth flow, fallback non triggerato, log completo, attribution AI funzionante (`client_origin=chatgpt.com`).

---

## 16. Versioning di questo documento

| Versione | Data | Autore | Note |
|---|---|---|---|
| 1.0 | 2026-05-10 | Claude (proposta) + Claudio (revisione) | Prima stesura completa. |
| 1.1 | 2026-05-11 | Claude (harmony pass M0.3) + Claudio (review) | Sez. 4.2 tabella Layer ora include colonna esplicita "Moduli" che mappa ogni layer al directory layout di `02-CONVENTIONS.md` sez. 3.1. Aggiunto vincolo esplicito "1 tool = 1 file". Le 21 decisioni canoniche D-A-001 → D-A-021 restano locked. |
| 1.2 | 2026-05-11 | Claude + Claudio (chiusura M0.2.1) | **Hosting migrato Railway → Fly.io free tier** (allineato con MASTER v1.3 D-MP-002). Stack tabella sez. 3.1 aggiornata. Hosting Redis: Upstash diretto (Fly.io non ha Redis add-on integrato, a differenza di Railway). DECISION-OPEN-T-001 chiusa. Vari riferimenti a "Railway" sostituiti con "Fly.io" in sez. 7 (logging), 8 (security), 9 (capacity), 11 (environments). |

---

## Note per il changelog

*(Sezione vuota in v1.0 — verrà popolata se emergono incongruenze nei file successivi che richiedono retrofitting in questo ARCHITECTURE.)*

---

**Fine 01-ARCHITECTURE.md v1.0.**
