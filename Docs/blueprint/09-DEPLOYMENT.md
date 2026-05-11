# 09 — DEPLOYMENT

| Campo | Valore |
|---|---|
| **Progetto** | Segmenta MCP Server |
| **Versione documento** | 1.2 |
| **Data** | 2026-05-11 |
| **Status** | Approvato (post harmony pass M0.3 + chiusura M0.2.1 hosting) |
| **File n.** | 09 di 12 numerati |
| **Documento padre** | `00-MASTER-PLAN.md` v1.3, `01-ARCHITECTURE.md` v1.1 |
| **File correlati** | `02-CONVENTIONS.md`, `07-AUTH-OAUTH.md`, `08-INTEGRATIONS.md` |

---

## 1. Scopo del documento

Questo file specifica **come il server MCP Segmenta arriva in produzione e ci resta**: hosting, DNS, HTTPS, secrets management, CI/CD, deploy strategy, rollback, observability operativa, runbook per incidenti.

Risponde a 5 domande:

1. *"Dove gira il server e come ci si arriva?"* — sezioni 3, 4, 5
2. *"Come deployamo, da local a production, senza rompere niente?"* — sezioni 6, 7, 8
3. *"Come gestiamo configurazione e secrets?"* — sezione 9
4. *"Come monitoriamo, alertiamo, rispondiamo a problemi?"* — sezioni 10, 11, 12
5. *"Cosa succede quando qualcosa va male?"* — sezione 13 (runbook)

L'architettura del server è in `01-ARCHITECTURE.md`. Le decisioni canoniche di deployment sono in sezione 14.

---

## 2. Filosofia operativa

Cinque principi che governano deploy e operations.

### 2.1 Deploy boring, monitor exciting

Il deploy stesso deve essere **noioso e ripetibile**: stesso comando, stesso risultato, ogni volta. La novità sta nel monitoring (cosa è cambiato, come si comporta in produzione). Niente deploy heroici, niente "questa volta lo facciamo manualmente".

### 2.2 Reversibile in < 5 minuti

Ogni deploy può essere **rolled back** in meno di 5 minuti: revert commit + deploy automatico. Niente release con fragility che richiedano "fixiamo in production".

### 2.3 Configurazione fuori dal codice

Tutto ciò che cambia tra ambienti (URL, secrets, feature flags) vive in **environment variables**, mai hardcoded. Il container ha il *codice*, l'ambiente ha la *configurazione*.

### 2.4 Observability prima di feature

Prima di aggiungere un tool nuovo, verifichiamo che il logging/metric per quel tool funzioni. Senza visibilità in produzione, ogni feature è un debito tecnico.

### 2.5 Disciplina di un solo dev

Claudio è il solo dev. Le pratiche scelgono il **path che minimizza errori operativi** anche a costo di velocità: branch protection anche con sé stesso, deploy automatico con health check obbligatori, no SSH manuale al container.

---

## 3. Architettura di deployment

### 3.1 Vista d'insieme

```
                    ┌────────────────────────────────────┐
                    │  GitHub repo (pubblico)            │
                    │  github.com/segmenta-ai/segmenta-mcp  │
                    └────────────┬───────────────────────┘
                                 │ webhook on push
              ┌──────────────────┴──────────────────┐
              │                                     │
              ▼                                     ▼
   ┌────────────────────┐              ┌────────────────────┐
   │  GitHub Actions    │              │  Fly.io           │
   │  (CI: test+lint)   │              │  (CD: build+deploy)│
   └────────┬───────────┘              └─────────┬──────────┘
            │ pass                               │
            ▼                                    ▼
   ┌────────────────────────────────────────────────────────┐
   │  Fly.io environments                                   │
   │                                                         │
   │  ┌─────────────────┐         ┌─────────────────────┐  │
   │  │ STAGING         │         │ PRODUCTION          │  │
   │  │ branch: develop │         │ branch: main        │  │
   │  │ mcp-staging.... │         │ mcp.segmenta...     │  │
   │  │ + Redis add-on  │         │ + Redis add-on      │  │
   │  └─────────────────┘         └─────────────────────┘  │
   └────────────────────────────────────────────────────────┘
                                │
                                │ public traffic
                                ▼
            ┌──────────────────────────────────────┐
            │  Cloudflare DNS                      │
            │  mcp.segmentamarketing.com → Fly.io │
            │  mcp-staging... → Fly.io            │
            └──────────────────────────────────────┘
                                │
                                │ TLS (Let's Encrypt via Fly.io)
                                ▼
                          End user / MCP client
```

### 3.2 Componenti

| Componente | Provider | Funzione |
|---|---|---|
| Source repo | GitHub (`github.com/segmenta-ai/segmenta-mcp`) | Storage codice + tag/release (DECISION-OPEN-005 chiusa) |
| CI | GitHub Actions | Lint + test + type check su PR |
| Container registry | Fly.io built-in | Build image dal Dockerfile (vedi sez. 3.3) |
| Compute | **Fly.io free tier** (3 shared-cpu-1x VMs, 256MB RAM) | Esecuzione container, region MEX (Mexico City) primary + MIA (Miami) optional secondary |
| Database state | **Upstash Redis free tier** (10k cmd/giorno, 256MB) | OAuth state, idempotency, rate limit |
| DNS | DNS provider esistente Segmenta (Cloudflare presunto — DECISION-OPEN-DE-001) | CNAME → Fly.io app domain |
| TLS | Let's Encrypt via Fly.io | HTTPS automatico, rotation 60gg |
| Monitoring uptime | UptimeRobot free | Probe `/health` ogni 5 min |
| Monitoring app | Fly.io dashboard built-in (CPU/memory/logs) + `/metrics` Prometheus per scrape esterno opzionale | Metriche realtime |
| Email transactional | **Resend free tier** (100/giorno = 3000/mese — DECISION-OPEN-004 chiusa) | (vedi `08-INTEGRATIONS.md` sez. 6) |
| Backup | GitHub repo + Upstash snapshot daily | Codice in repo, state snapshot Upstash 24h |

### 3.3 Dockerfile (in repo root)

Aggiunto in v1.1 (HC-007). Container production-ready, multi-stage per ridurre dimensione finale.

```dockerfile
# syntax=docker/dockerfile:1.7

# ---- Stage 1: build dependencies con uv ----
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1

# Installa uv (D-A-021, D-C-007)
COPY --from=ghcr.io/astral-sh/uv:0.5 /uv /uvx /usr/local/bin/

WORKDIR /app

# Copy lockfile e pyproject prima del codice → cache layer ottimale
COPY pyproject.toml uv.lock ./

# Installa solo dipendenze production (no dev/test)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# Copy applicazione e sync finale (link al venv)
COPY src/ ./src/
COPY data/ ./data/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# ---- Stage 2: runtime minimal ----
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

# Utente non-root per sicurezza
RUN groupadd -r segmenta && useradd -r -g segmenta -u 1001 segmenta

WORKDIR /app

# Copia venv built + codice + dati dal builder
COPY --from=builder --chown=segmenta:segmenta /app/.venv /app/.venv
COPY --from=builder --chown=segmenta:segmenta /app/src /app/src
COPY --from=builder --chown=segmenta:segmenta /app/data /app/data

USER segmenta

EXPOSE 8000

# Health check (ridondante con Fly.io probe ma utile per docker run locale)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8000/health',timeout=5).status==200 else 1)"

CMD ["python", "-m", "uvicorn", "segmenta_mcp.main:app", \
     "--host", "0.0.0.0", "--port", "8000", \
     "--no-access-log", "--proxy-headers"]
```

**Note**:
- Multi-stage riduce dimensione image finale a ~150 MB (vs ~600 MB single-stage).
- `--no-access-log` perché loggiamo manualmente con structlog (D-A-008).
- `--proxy-headers` perché Fly.io è dietro un reverse proxy (X-Forwarded-For necessario per rate limit per IP).
- Non includiamo `tests/` né `Docs/` nell'image: solo `src/` + `data/`.

### 3.4 `.dockerignore` (in repo root)

```
# Test, docs, dev tooling
tests/
Docs/
scripts/
.github/
.vscode/
.git/
.gitignore
.env
.env.local

# Python
__pycache__/
*.py[cod]
.pytest_cache/
.mypy_cache/
.ruff_cache/
htmlcov/
.coverage

# uv
.venv/

# OS
.DS_Store
Thumbs.db

# Editor
*.swp
*.swo
```

---

## 4. Hosting: Fly.io free tier

### 4.1 Razionale scelta (D-MP-002 v1.3)

Fly.io free tier è la scelta canonica post-chiusura M0.2.1 (target costo $0/mese). Confronto:

| Provider | Pro | Contro | Decisione |
|---|---|---|---|
| **Fly.io free** | $0/mese baseline, region MEX + MIA (latenza ottima LATAM/MX/US), Dockerfile-native, HTTPS gratis, custom domain gratis, SSE supportato, 160GB outbound/mese | 256MB RAM stretto (vs 512MB Railway), Redis non incluso → Upstash separato | **Default v1.3** |
| Railway Hobby | UI eccellente, Redis add-on integrato | $5/mese baseline minimo, region us-west solo | Fallback se Fly.io free tier viene deprecato |
| Cloudflare Workers free | 100k req/giorno, edge globale, $0/mese | Python beta limitato, 10ms CPU/req incompatibile con crawler T2, refactor stack 40+ ore | No (vedi M0.2.1 analysis) |
| Render free | Simile a Fly | Spin-down 15 min idle (rompe OAuth flow), region limitate | No |
| Heroku | Industry standard | Free tier rimosso 2022 | No |
| AWS Lambda | Serverless scala | Cold start, complessità SSE, no Python FastMCP nativo | No |
| VPS bare (DigitalOcean/Hetzner) | Controllo totale | Manutenzione manuale TLS/OS = bandwidth Claudio | No in v1 |

### 4.2 Configurazione Fly.io

**App**: `segmenta-mcp-prod` (production), `segmenta-mcp-staging` (staging) — 2 app separate per isolamento.

**Organization**: `segmenta-ai` (Fly.io org, allineata con GitHub org).

**Region** (primary): `mex` (Mexico City). Fallback secondary: `mia` (Miami).

**Service**: 1 servizio HTTP per app, deploy da Dockerfile in repo root.

**Plan v1**: **Free tier** — 3 shared-cpu-1x VMs gratis (256MB RAM ciascuna), 3GB persistent volume, 160GB outbound/mese.
- 1 VM staging + 1 VM production = 2 su 3 free quota usate. 1 VM rimanente = scale-up futuro.

**Plan M4+ (eventuale)**: Se Upstash free tier insufficiente, valutare Fly.io Redis dedicato ($1.94/mese) o passare a paid Upstash. Comunque target sotto cap $30/mese.

### 4.3 Resource sizing v1

| Risorsa | Allocato | Ragione |
|---|---|---|
| CPU | shared-cpu-1x (1 vCPU shared) | Sufficient per latency budget Tier 1 (in-memory). Tier 2 SEO crawler in budget grazie a httpx async. |
| RAM | 256 MB | Stretto: Python + FastMCP + Pydantic ~150-180 MB. Headroom ~70 MB. Memory profiling obbligatorio in M1. |
| Disk | 1 GB persistent volume (Fly volumes) | JSON dati + log buffer + temp crawl cache |
| Redis | Upstash free 256 MB (10k cmd/giorno) | OAuth state + rate limit + idempotency keys |
| Outbound | 160 GB/mese (free tier) | Sufficiente per <50k tool calls/giorno (~50 KB response media) |

Auto-scaling: **disabilitato in v1** (`auto_stop_machines = false` in fly.toml per evitare cold start). Manual scaling se serve (vedi sez. 9.3 di `01-ARCHITECTURE.md`).

> **Vincolo critico RAM**: 256MB è il limit free tier. Memory leak = restart. Setup obbligatorio: profiling con `tracemalloc` in M1.5; alert se RSS > 220 MB.

### 4.4bis `fly.toml` (in repo root)

Aggiunto in v1.2 (M0.2.1 chiusura, sostituisce railway.toml). Configurazione dichiarativa Fly.io: build, deploy, healthcheck, region, scaling.

```toml
# Documentazione: https://fly.io/docs/reference/configuration/
# App production
app = "segmenta-mcp-prod"
primary_region = "mex"  # Mexico City — latenza ottima LATAM/MX/US
kill_signal = "SIGINT"
kill_timeout = "5s"

[build]
  dockerfile = "Dockerfile"

[env]
  ENV = "production"
  LOG_LEVEL = "INFO"
  PORT = "8000"
  HOST = "0.0.0.0"

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = false   # Evita cold start MCP (importante per OAuth flow continuity)
  auto_start_machines = true
  min_machines_running = 1     # Almeno 1 sempre running per /health probe
  processes = ["app"]

  [[http_service.checks]]
    grace_period = "40s"
    interval = "30s"
    method = "GET"
    timeout = "10s"
    path = "/health"

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 256

[[mounts]]
  source = "segmenta_data"
  destination = "/app/data_runtime"
  initial_size = "1gb"

# File staging separato: fly.staging.toml
# app = "segmenta-mcp-staging", region = "mia" (Miami)
```

**File companion** `fly.staging.toml`:

```toml
app = "segmenta-mcp-staging"
primary_region = "mia"  # Miami — diverso da prod per testare cross-region
kill_signal = "SIGINT"
kill_timeout = "5s"

[build]
  dockerfile = "Dockerfile"

[env]
  ENV = "staging"
  LOG_LEVEL = "DEBUG"
  PORT = "8000"
  HOST = "0.0.0.0"

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = true    # Staging può andare in sleep per risparmiare quota free
  auto_start_machines = true
  min_machines_running = 0
  processes = ["app"]

  [[http_service.checks]]
    grace_period = "40s"
    interval = "60s"
    method = "GET"
    timeout = "10s"
    path = "/health"

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 256
```

**Comandi tipici**:
```bash
# Setup iniziale (una volta)
fly auth login
fly apps create segmenta-mcp-prod --org segmenta-ai
fly apps create segmenta-mcp-staging --org segmenta-ai
fly volumes create segmenta_data --size 1 --region mex --app segmenta-mcp-prod

# Deploy production
fly deploy --config fly.toml --remote-only

# Deploy staging
fly deploy --config fly.staging.toml --remote-only

# Logs realtime
fly logs --app segmenta-mcp-prod

# SSH dentro container (debug)
fly ssh console --app segmenta-mcp-prod

# Scale machines (M5+ se serve)
fly scale count 2 --app segmenta-mcp-prod
```

**Note**:
- `auto_stop_machines = false` in production = no cold start, ma consuma quota free (1 VM running 24/7).
- Free tier Fly: 3 shared-cpu-1x VMs gratis. Production usa 1, staging usa 1 (con auto_stop), 1 disponibile per scale futuro.
- Volume `segmenta_data` (1GB) persiste tra deploy — usato per cache JSON loaded + temp files crawler.
- `min_machines_running = 1` in production: garantisce che `/health` probe non triggeri restart.

### 4.4 Health check

Fly.io esegue probe HTTP su `/health` ogni 30s. Container `unhealthy` per > 90s → restart automatico.

```python
@app.get("/health")
async def health() -> dict:
    """Health check per Fly.io + UptimeRobot."""
    checks = {
        "data_loaded": await check_data_cache(),
        "redis": await check_redis_ping(),
        "uptime_seconds": app_uptime(),
    }
    all_ok = all(v for k, v in checks.items() if k != "uptime_seconds")
    return {
        "status": "healthy" if all_ok else "degraded",
        "checks": checks,
        "version": __version__,
    }
```

Health check NON include integrations esterne (Cal.com, HubSpot). Loro down NON deve causare restart del nostro server (vedi `01-ARCHITECTURE.md` sez. 14 sui stati DEGRADED vs UNHEALTHY).

---

## 5. DNS e TLS

### 5.1 Dominio

`segmentamarketing.com` è gestito esternamente (presunto Cloudflare DNS o Hostinger). Accesso DNS = via Merari.

**Subdomain dedicato**: `mcp.segmentamarketing.com` (D-MP-003 / D-A-003).

### 5.2 DNS records richiesti

```
; Production
mcp.segmentamarketing.com.       CNAME  segmenta-mcp-production.up.railway.app.
mcp-staging.segmentamarketing.com. CNAME  segmenta-mcp-staging.up.railway.app.

; Email (DKIM/SPF/DMARC) — vedi 08-INTEGRATIONS.md sez. 6.6
mcp.segmentamarketing.com.       TXT    "v=spf1 include:_spf.resend.com ~all"
resend._domainkey.mcp...         TXT    "k=rsa; p=MIGfMA0..."
_dmarc.mcp...                    TXT    "v=DMARC1; p=quarantine; rua=mailto:dmarc@..."

; OAuth metadata discovery (auto-served from server)
; No DNS record needed; il server espone /.well-known/oauth-authorization-server

; Optional: CAA per limitare CA per HTTPS
mcp.segmentamarketing.com.       CAA    0 issue "letsencrypt.org"
```

CNAME → Fly.io. Fly.io gestisce automaticamente TLS via Let's Encrypt.

### 5.3 TLS

Configurazione automatica via Fly.io:
- Provider CA: Let's Encrypt
- Algoritmo: ECDSA P-256 (default Fly.io 2026)
- Renewal: automatico ogni 60 giorni
- HSTS abilitato: `Strict-Transport-Security: max-age=31536000; includeSubDomains`

Verifica post-deploy:
- [ssllabs.com/ssltest](https://ssllabs.com/ssltest) → grade A o A+
- HSTS preload submission (M3+, opzionale)

### 5.4 CORS

Configurato in `transport/middleware.py`:

```python
ALLOWED_ORIGINS = {
    "production": [
        "https://claude.ai",
        "https://chatgpt.com",
        "https://cursor.so",  # se aggiungiamo Cursor
    ],
    "staging": [
        "https://claude.ai",
        "https://chatgpt.com",
        "http://localhost:*",  # dev tools
    ],
    "local": ["*"],
}
```

CORS non è una soluzione di sicurezza (può essere bypassato), ma riduce errori di integrazione e segnala intenzione.

---

## 6. CI: GitHub Actions

### 6.1 Workflow `ci.yml`

Triggered su PR verso `develop` o `main`. Esegue lint + test + type check.

```yaml
name: CI

on:
  pull_request:
    branches: [develop, main]
  push:
    branches: [develop, main]

jobs:
  ci:
    runs-on: ubuntu-latest
    services:
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v4

      - name: Setup uv
        uses: astral-sh/setup-uv@v3
        with:
          version: "0.5.x"
          enable-cache: true

      - name: Setup Python 3.12
        run: uv python install 3.12

      - name: Install dependencies
        run: uv sync --frozen

      - name: Lint (ruff)
        run: uv run ruff check src/ tests/

      - name: Format check (ruff)
        run: uv run ruff format --check src/ tests/

      - name: Type check (mypy)
        run: uv run mypy src/

      - name: Test (pytest)
        run: uv run pytest --cov=src/segmenta_mcp --cov-report=xml
        env:
          REDIS_URL: redis://localhost:6379
          # Mock secrets for test
          JWT_PRIVATE_KEY: ${{ secrets.TEST_JWT_PRIVATE_KEY }}

      - name: Coverage check
        run: |
          uv run coverage report --fail-under=80

      - name: Validate JSON data
        run: uv run python scripts/validate_data.py

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        if: github.event_name == 'pull_request'
```

Branch protection (D-C-006) richiede: `ci` passa prima di merge.

### 6.2 Workflow `deploy-staging.yml`

Triggered su push a `develop`. Fly.io si occupa del deploy automatico via webhook, ma usiamo un GitHub Action per **smoke test post-deploy**.

```yaml
name: Deploy staging — smoke test

on:
  push:
    branches: [develop]

jobs:
  wait-and-test:
    runs-on: ubuntu-latest
    steps:
      - name: Wait for Fly.io deploy
        run: |
          for i in {1..30}; do
            sleep 10
            VERSION=$(curl -s https://mcp-staging.segmentamarketing.com/health | jq -r .version)
            EXPECTED="${{ github.sha }}"
            if [[ "$VERSION" == *"${EXPECTED:0:7}"* ]]; then
              echo "Deploy detected"
              exit 0
            fi
          done
          echo "Deploy timeout"
          exit 1

      - name: Smoke test
        run: |
          # Health check
          curl -f https://mcp-staging.segmentamarketing.com/health

          # Discovery endpoint
          curl -f https://mcp-staging.segmentamarketing.com/.well-known/oauth-authorization-server

          # Tier 1 tool call (no auth)
          curl -f -X POST https://mcp-staging.segmentamarketing.com/mcp/tools/call \
               -H "Content-Type: application/json" \
               -d '{"name": "obtener_servicios"}'

      - name: Notify Slack
        if: failure()
        uses: slackapi/slack-github-action@v1
        with:
          payload: |
            {
              "text": "🚨 Staging deploy smoke test FAILED — sha ${{ github.sha }}"
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL_ALERTS }}
```

### 6.3 Workflow `deploy-production.yml`

Triggered su push a `main`. Stessa logica smoke test di staging, target production. In aggiunta:
- Tag git automatico `v{version}` se la versione in `__init__.py` è cambiata.
- GitHub Release pubblicata con CHANGELOG estratto.
- Notifica Slack di successo (non solo failure come staging).

YAML completo (espanso in v1.1 — HC-007):

```yaml
name: Deploy production

on:
  push:
    branches: [main]

jobs:
  wait-and-test:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # full history per CHANGELOG extract

      - name: Wait for Fly.io deploy
        run: |
          for i in {1..30}; do
            sleep 30
            STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://mcp.segmentamarketing.com/health || echo "000")
            if [ "$STATUS" = "200" ]; then
              echo "Deploy detected"
              exit 0
            fi
          done
          echo "Deploy timeout"
          exit 1

      - name: Smoke test
        run: |
          # Health check
          curl -f https://mcp.segmentamarketing.com/health

          # Discovery endpoint OAuth
          curl -f https://mcp.segmentamarketing.com/.well-known/oauth-authorization-server

          # Tier 1 tool call (no auth)
          curl -f -X POST https://mcp.segmentamarketing.com/mcp/tools/call \
               -H "Content-Type: application/json" \
               -d '{"name": "obtener_servicios"}'

          # JWKS endpoint
          curl -f https://mcp.segmentamarketing.com/.well-known/jwks.json

      - name: Extract version from package
        id: version
        if: success()
        run: |
          VERSION=$(uv run python -c "from segmenta_mcp import __version__; print(__version__)")
          echo "VERSION=$VERSION" >> $GITHUB_ENV
          echo "version=$VERSION" >> $GITHUB_OUTPUT

      - name: Check if tag already exists
        id: tag_check
        run: |
          if git rev-parse "v${{ env.VERSION }}" >/dev/null 2>&1; then
            echo "exists=true" >> $GITHUB_OUTPUT
          else
            echo "exists=false" >> $GITHUB_OUTPUT
          fi

      - name: Tag release
        if: success() && steps.tag_check.outputs.exists == 'false'
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git tag -a "v${{ env.VERSION }}" -m "Release v${{ env.VERSION }}"
          git push origin "v${{ env.VERSION }}"

      - name: Extract CHANGELOG section for this version
        if: success() && steps.tag_check.outputs.exists == 'false'
        id: changelog
        run: |
          # Estrai la sezione tra "## [VERSION]" e la successiva "## ["
          BODY=$(awk -v ver="${{ env.VERSION }}" '
            /^## \[/ { if (found) exit; if ($0 ~ "\\[" ver "\\]") found=1; next }
            found { print }
          ' CHANGELOG.md)
          {
            echo 'CHANGELOG_BODY<<EOF'
            echo "$BODY"
            echo 'EOF'
          } >> $GITHUB_ENV

      - name: Create GitHub Release
        if: success() && steps.tag_check.outputs.exists == 'false'
        uses: softprops/action-gh-release@v2
        with:
          tag_name: v${{ env.VERSION }}
          name: v${{ env.VERSION }}
          body: ${{ env.CHANGELOG_BODY }}
          draft: false
          prerelease: false

      - name: Notify Slack — success
        if: success()
        uses: slackapi/slack-github-action@v1
        with:
          payload: |
            {
              "text": "✅ Production deploy SUCCESS — v${{ env.VERSION }} (sha ${{ github.sha }})"
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL_DEPLOYS }}

      - name: Notify Slack — failure
        if: failure()
        uses: slackapi/slack-github-action@v1
        with:
          payload: |
            {
              "text": "🚨 PRODUCTION deploy smoke test FAILED — sha ${{ github.sha }} — vedi runbook 09-DEPLOYMENT.md sez. 13"
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL_ALERTS }}
```

### 6.4 Tempi attesi

| Step | Durata tipica |
|---|---|
| CI workflow (lint + test + type check) | 2-3 min |
| Fly.io build + deploy | 1-2 min |
| Smoke test post-deploy | 5-7 min (incluso wait per propagation) |
| **Totale PR → production live** | **~10 min** |

---

## 7. CD: Fly.io deploy via GitHub Actions

### 7.1 Trigger

Differenza chiave vs Railway: **Fly.io non ha auto-deploy da Git push**. Il deploy è triggered da GitHub Action che esegue `flyctl deploy --remote-only` con `FLY_API_TOKEN` come secret.

Trigger configurati:
- Push to `develop` → GitHub Action `deploy-staging.yml` esegue `flyctl deploy --config fly.staging.toml --remote-only`
- Push to `main` → GitHub Action `deploy-production.yml` esegue `flyctl deploy --config fly.toml --remote-only`

### 7.2 Build process

GitHub Action esegue:
1. Checkout del repo al SHA del push.
2. Setup `flyctl` CLI.
3. `flyctl deploy --remote-only` invia il build a Fly.io builder remoto.
4. Fly.io build dell'image Docker dal `Dockerfile`.
5. Push image al registry Fly.io (`registry.fly.io/segmenta-mcp-prod`).
6. Deploy nuova machine con strategia rolling.
7. Health check `/health` deve passare entro 60s (`grace_period` in fly.toml).
8. Routing del traffic alla nuova machine.
9. Termina vecchia machine dopo grace period.

### 7.3 Rolling deploy

Strategia: 1 vecchia machine viva mentre la nuova si avvia. Switchover atomico quando new is healthy.

Effetto utente: **0 downtime percepito** durante deploy normali. Latency spike trascurabile.

### 7.4 Failed deploy handling

Se health check fallisce ripetutamente:
1. Fly.io NON promuove la nuova machine (resta in stato `failed`).
2. Routing resta sulla vecchia (stable).
3. `flyctl deploy` exit code != 0 → GitHub Action fallisce → Slack alert (sez. 6.2/6.3).
4. Claudio investiga via `flyctl logs --app segmenta-mcp-prod` + GitHub Action logs.

**Nessun rollback automatico**: il vecchio container resta vivo, niente serve. Per "rollback" si fa `git revert` + push (sez. 8) oppure `flyctl releases rollback <release-id>` per emergenza.

### 7.5 Variables binding

Fly.io secrets si gestiscono via CLI: `flyctl secrets set XXX=yyy --app segmenta-mcp-prod`. Sono iniettate come env vars al container all'avvio. Riferimento dettaglio: sez. 9.

---

## 8. Strategy di rollback

### 8.1 Quando rollback

- Bug critico in produzione (errors > 5% per > 5 min, vedi SR-002).
- Comportamento di tool degradato in produzione che non si è visto in staging.
- Performance regression > 50% latency p95.
- Breaking change di MCP protocol non gestito.

### 8.2 Procedura rollback (< 5 min)

```bash
# 1. Identifica commit problematico
git log --oneline main

# 2. Crea revert commit
git checkout main
git pull
git revert <sha-bad-commit>

# 3. Push (triggera deploy automatico)
git push origin main

# 4. Monitora deploy
# Fly.io dashboard mostra nuovo deploy in progress
# GitHub Action smoke test conferma successo

# 5. Verifica
curl https://mcp.segmentamarketing.com/health
```

Tempo totale: 3-7 minuti (1 min revert + 2 min Fly.io build + 3 min smoke test).

### 8.3 Quando NON fare rollback

- Bug minore non blocking (toolinfo errato, log message brutto): fix forward.
- Issue di un'integrazione esterna (Cal.com down): non è il nostro server, niente rollback.
- Performance lieve degradation (< 20%): investigare prima di reagire.

### 8.4 Rollback di emergency (manual, < 2 min)

In caso estremo (server completamente down dopo deploy):

```bash
# Lista release recenti
flyctl releases --app segmenta-mcp-prod

# Rollback al release precedente
flyctl releases rollback <release-id> --app segmenta-mcp-prod
```

Tempo: < 1 min per switch traffic + warmup.

Da usare con prudenza: bypassa Git history, crea drift tra repo e prod. Subito dopo: aprire `git revert` PR per allineare repo a prod.

### 8.5 Hotfix flow

Vedi `02-CONVENTIONS.md` sez. 5.7. Schema:

```
hotfix/critical-x branch from main → minimal fix → PR to main →
squash merge → auto-deploy production → back-merge to develop
```

---

## 9. Configurazione e secrets

### 9.1 Tre layer di configurazione

| Layer | Cosa | Storage | Comando setup |
|---|---|---|---|
| **Code defaults** | Valori sicuri di fallback (es. timeout, port default) | `src/segmenta_mcp/config.py` | `git commit` |
| **Environment-specific (non-secret)** | Valori che cambiano tra staging/prod, non sensibili | `fly.toml` / `fly.staging.toml` `[env]` | `git commit` (visibile in repo) |
| **Secrets** | Credentials, API keys, signing keys | Fly.io secrets (encrypted at rest) | `flyctl secrets set KEY=value --app <app>` |

**Differenza Fly.io vs Railway**:
- Fly.io distingue tra `[env]` in `fly.toml` (visibili nel repo) e `secrets` (CLI-only, encrypted). Mai mettere credentials in `[env]`.
- Setup secret: `flyctl secrets set RESEND_API_KEY=re_xxx --app segmenta-mcp-prod`. Trigger restart automatico.
- Lista secrets (solo nomi, mai valori): `flyctl secrets list --app segmenta-mcp-prod`.
- Update richiede re-set (no edit-in-place).

### 9.2 Variables list

Cataloghiamo tutte le env variables. Aggiornate quando se ne aggiungono.

#### Server core

| Variable | Type | Required | Default | Note |
|---|---|---|---|---|
| `ENV` | string | Yes | — | `local` / `staging` / `production` |
| `LOG_LEVEL` | string | No | `INFO` | `DEBUG` / `INFO` / `WARN` / `ERROR` |
| `PORT` | int | No | `8000` | Fly.io sovrascrive automaticamente |
| `HOST` | string | No | `0.0.0.0` | Bind address |
| `ISSUER_URL` | string | Yes | — | `https://mcp.segmentamarketing.com` |

#### Auth / OAuth

| Variable | Type | Required | Note |
|---|---|---|---|
| `JWT_PRIVATE_KEY` | string (PEM) | Yes | RSA private key per signing |
| `JWT_PUBLIC_KEY` | string (PEM) | Yes | RSA public key per JWKS endpoint |
| `JWT_KEY_ID` | string | Yes | `kid` claim, ULID del key versioning |
| `OAUTH_ALLOWED_REDIRECT_HOSTS` | CSV | No | Default: `claude.ai,chatgpt.com,localhost` |

#### Redis

| Variable | Type | Required | Note |
|---|---|---|---|
| `REDIS_URL` | string | Yes | `redis://default:pwd@host:port/0` |
| `REDIS_TLS` | bool | No | `true` per Upstash production |

#### Integrazioni

| Variable | Type | Required | Tool che la usa |
|---|---|---|---|
| `CALCOM_API_KEY` | string | M2+ | Booking |
| `CALCOM_EVENT_TYPE_ID` | int | M2+ | Booking event default |
| `CALCOM_WEBHOOK_SECRET` | string | M2+ | Validazione webhook |
| `HUBSPOT_PRIVATE_TOKEN` | string | M2+ | CRM |
| `HUBSPOT_PORTAL_ID` | string | M2+ | CRM identification |
| `RESEND_API_KEY` | string | M2+ | Email |
| `RESEND_FROM_EMAIL` | string | M2+ | `noreply@mcp.segmentamarketing.com` |
| `SLACK_WEBHOOK_URL_LEADS` | string | M2+ | Slack alerts lead capture |
| `SLACK_WEBHOOK_URL_ALERTS` | string | Yes | Slack alerts errors |
| `IPINFO_TOKEN` | string | No | Geo IP (free tier OK senza token, paid con) |
| `DATAFORSEO_API_KEY` | string | M4+ | SEO data Tier 3 |
| `DATAFORSEO_LOGIN` | string | M4+ | DataForSEO auth |

### 9.3 Pydantic settings (pattern)

`src/segmenta_mcp/config.py`:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    """Application settings loaded from env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Server core
    ENV: str = Field(..., pattern=r"^(local|staging|production)$")
    LOG_LEVEL: str = "INFO"
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    ISSUER_URL: str = Field(..., pattern=r"^https://")

    # Auth
    JWT_PRIVATE_KEY: str = Field(..., min_length=200)
    JWT_PUBLIC_KEY: str = Field(..., min_length=100)
    JWT_KEY_ID: str = Field(..., min_length=10)
    OAUTH_ALLOWED_REDIRECT_HOSTS: list[str] = Field(
        default=["claude.ai", "chatgpt.com", "localhost"]
    )

    # Redis
    REDIS_URL: str
    REDIS_TLS: bool = False

    # Integrazioni — opzionali finché non attivate
    CALCOM_API_KEY: str | None = None
    CALCOM_EVENT_TYPE_ID: int | None = None
    HUBSPOT_PRIVATE_TOKEN: str | None = None
    RESEND_API_KEY: str | None = None
    SLACK_WEBHOOK_URL_LEADS: str | None = None
    SLACK_WEBHOOK_URL_ALERTS: str
    IPINFO_TOKEN: str | None = None
    DATAFORSEO_API_KEY: str | None = None
    DATAFORSEO_LOGIN: str | None = None


settings = Settings()  # validato all'avvio
```

Validation **at startup**: server non parte se manca una env required (D-D-012 stile per env). Fail fast.

### 9.4 Secrets rotation

| Secret | Rotation cadence | Procedura |
|---|---|---|
| `JWT_PRIVATE_KEY` / `_PUBLIC_KEY` | Ogni 90 giorni | Genera new pair, deploy con entrambi attivi (transition 7gg), rimuovi old |
| `CALCOM_API_KEY` | Ogni 6 mesi o on-demand | Genera new in Cal.com dashboard, update Fly.io env |
| `HUBSPOT_PRIVATE_TOKEN` | Ogni 6 mesi | Idem HubSpot |
| `RESEND_API_KEY` | Ogni 6 mesi | Idem Resend |
| Slack webhook URLs | On-demand (se compromessi) | Re-create in Slack |
| `CALCOM_WEBHOOK_SECRET` | Ogni 6 mesi | Re-generate, sync su Cal.com webhook config |

In v1: rotation manuale, calendar reminder. In v2: automation via script.

### 9.5 .env.example completo

`.env.example` committato (no secrets reali, solo placeholder con commenti):

```bash
# ============================================================
# Segmenta MCP Server — environment configuration
# Copy to .env (NOT committed) and fill with real values
# ============================================================

# --- Server core ---
ENV=local                                          # local | staging | production
LOG_LEVEL=DEBUG                                    # DEBUG | INFO | WARN | ERROR
PORT=8000
ISSUER_URL=http://localhost:8000                   # https://mcp.segmentamarketing.com in prod

# --- Auth (generate new keys per environment) ---
JWT_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----..."
JWT_PUBLIC_KEY="-----BEGIN PUBLIC KEY-----..."
JWT_KEY_ID=kid_01JX...

# --- Redis ---
REDIS_URL=redis://localhost:6379/0
REDIS_TLS=false

# --- Integrazioni (M2+) ---
# CALCOM_API_KEY=cal_live_...
# HUBSPOT_PRIVATE_TOKEN=pat-...
# RESEND_API_KEY=re_...
# SLACK_WEBHOOK_URL_ALERTS=https://hooks.slack.com/...
```

---

## 10. Observability operativa

### 10.1 Logging

Coerente con `01-ARCHITECTURE.md` sez. 7.1. Logs:
- Output: stdout (Fly.io li cattura)
- Formato: JSON strutturato via `structlog`
- Livello produzione: INFO
- Retention: 30 giorni in Fly.io, 90 giorni se exported a esterno (M3+)

Esempio log line production:

```json
{
  "timestamp": "2026-05-10T15:42:18.453Z",
  "level": "INFO",
  "request_id": "req_01JXVZL5HQNT...",
  "tier": "2",
  "tool": "agendar_auditoria_gratuita",
  "client_origin": "claude.ai",
  "user_country": "MX",
  "latency_ms": 2300,
  "status": "success",
  "integrations": ["calcom_ok", "hubspot_ok", "slack_ok"],
  "message": "tool_call_completed"
}
```

### 10.2 Metriche

Esposte su `/metrics` formato Prometheus. Fly.io non scrape Prometheus automaticamente in v1. Strategie:

**v1**: Fly.io dashboard built-in mostra CPU/memory/network/restart count. Sufficiente.

**v2 / M4**: Esportare metriche custom a Grafana Cloud free tier o Prometheus self-hosted in Fly.io. Decisione DECISION-OPEN-T-005 di `01-ARCHITECTURE.md`.

### 10.3 Uptime monitoring

UptimeRobot (free tier) probe su:
- `https://mcp.segmentamarketing.com/health` ogni 5 min
- `https://mcp-staging.segmentamarketing.com/health` ogni 5 min

Alert config:
- Email a Claudio se 2 check consecutivi falliscono.
- SMS a Claudio (numero personale) se production down per > 15 min.
- Slack ping `#alerts-mcp` se staging o production down.

UptimeRobot dashboard pubblica? **No in v1**, valutiamo trust signal in v2.

### 10.4 Error tracking

DECISION-OPEN-AU-005 / DECISION-OPEN-IN-006 aperta. Candidati:

| Provider | Pro | Contro |
|---|---|---|
| Sentry | Standard, free tier 5k events/mese | Poco "Latam-friendly" |
| GlitchTip | OSS, self-hosted possible | Manutenzione propria |
| Highlight.io | Modern UI, session replay | Più recente, meno feature |

V1: niente error tracking aggregato. structlog + Fly.io logs + Slack alerts su CRITICAL coprono il 90% dei casi.

V2 / M3+: introdurre Sentry o equivalente.

### 10.5 Audit trail

Log con flag `event_type=auth_*` o `event_type=privacy_*` aggregati separatamente per audit LFPDPPP/GDPR.

In v1: query manuale su Fly.io logs filtrando per pattern.

In v2: export periodico a S3 / Backblaze per long-term retention 7 anni (compliance).

---

## 11. Backup e disaster recovery

### 11.1 Cosa è backup-ato

| Risorsa | Backup | Restore time |
|---|---|---|
| **Codice** | GitHub repo | < 5 min (clone + deploy) |
| **JSON dati** | Versionati in repo | Inclusi nel codice |
| **Redis state** | Snapshot automatico Fly.io add-on (every 6h) | < 30 min (restore from snapshot) |
| **HubSpot CRM** | Backup manuale via export mensile (Merari) | Manuale |
| **Cal.com bookings** | Backup automatico Cal.com (loro responsabilità) | Manuale via UI |
| **Email logs Resend** | Retention 30gg lato Resend | n/a |

### 11.2 RTO / RPO target

- **RTO** (Recovery Time Objective): 30 min per recovery completo (server + state).
- **RPO** (Recovery Point Objective): 6h max data loss accettabile (snapshot Redis cadence).

In pratica:
- Data loss su Redis = perdita di sessioni OAuth attive (utenti rifanno login). Acceptable.
- Data loss su CRM (HubSpot) = ~6h di lead potenzialmente persi. Acceptable se rara.
- Data loss su codice: zero (Git repo è source of truth).

### 11.3 Disaster recovery runbook

**Scenario 1: Container production crashed e non si riavvia**

```
1. Check Fly.io dashboard → identifica errore boot
2. Check Fly.io logs → cerca CRITICAL log line
3. Se config issue:
   - Verifica env variables in Fly.io dashboard
   - Restart manuale dal dashboard
4. Se code issue:
   - git revert dell'ultimo commit
   - git push origin main
   - Aspetta auto-deploy
5. Se persistente: rollback via Fly.io dashboard al deploy precedente
6. Aggiorna SESSION-STATE con incident
```

**Scenario 2: Redis Upstash down**

```
1. Check Fly.io add-on dashboard → confermare outage
2. Status notification: server entra in DEGRADED state automaticamente
   (Tier 1 funziona, Tier 2/3 risponde 503)
3. Comunicazione: status page (M3+) o Slack #alerts
4. Recovery: tipicamente Fly.io/Upstash risolve in < 30 min
5. Restart del nostro container post-recovery (per riconnettere Redis pool)
```

**Scenario 3: Repo GitHub compromesso (account hijack)**

```
1. Revoca tutti i token GitHub Personal Access Tokens
2. Rotate all secrets in Fly.io env (JWT keys, API keys provider)
3. Audit commits recenti per malicious changes
4. Forza redeploy production con commit known-good
5. Notifica Anthropic + community se confirmed breach
```

**Scenario 4: Database leak / privacy breach**

```
Vedi SR-009 di MASTER-PLAN:
1. Freeze immediato Tier 2/3 (env var FEATURE_TIER2_ENABLED=false)
2. Audit tabelle Redis per dati esposti
3. Rotate tutti i token attivi (blocklist mass)
4. Notifica INAI entro 72h (LFPDPPP art. 20)
5. Notifica utenti impattati entro 72h
6. Public incident report
```

---

## 12. Performance e capacity planning

### 12.1 Capacity attuale (v1)

Single container Fly.io Hobby plan:
- ~50 req/sec sustained su Tier 1 (in-memory)
- ~10 req/sec sustained su Tier 2 (con I/O integrazioni)
- Burst tolerance: ~100 req/sec per < 30s

### 12.2 Trigger per scaling

**Vertical scaling** (più CPU/RAM):
- CPU sustained > 70% per > 10 min
- Memory > 80%
- Cost: passa a Pro plan ($20/mese baseline + usage)

**Horizontal scaling** (più container):
- 1 container non basta neanche con vertical max
- Latency p95 sustained > 800ms
- Cost: $5-15/mese per container aggiuntivo

V1 plan: 1 container. M4+ valutiamo 2 container con load balancer Fly.io.

### 12.3 Cost projection (post M0.2.1, hosting Fly.io)

| Mese | Compute (Fly) | Redis (Upstash) | Email (Resend) | SEO API | Totale | vs Cap $30 |
|---|---|---|---|---|---|---|
| M1 | $0 (free, 1 VM) | $0 (free, 10k cmd/giorno) | $0 (free, 100/giorno) | $0 | **$0** | ✅ -$30 |
| M2 | $0 (free, 2 VM stag+prod) | $0 (free) | $0 (free, < 100/giorno previsto) | $0 | **$0** | ✅ -$30 |
| M3 | $0 (free, GTM trigger) | $0 (free, < 10k cmd/giorno) | $0 (free, 50-100/giorno) | $0 | **$0** | ✅ -$30 |
| M4 | $0 (free) o $1.94 (Fly Redis se Upstash insufficiente) | $0-$10 (Upstash paid se > 10k cmd/giorno) | $0-$20 (Resend Pro se > 100/giorno) | $0-$20 (DataForSEO trial) | **$0-$50** | ⚠️ se >$30: review Merari |
| M5+ | $1.94 (Fly Redis) o $5 (Railway fallback) | $10 (Upstash paid) | $20 (Resend Pro) | $40 (SEO data full) | **$70-$80** | ⚠️ richiede approval Merari |

**Target costo canonico** (D-DE-020 v1.2, D-MP-002 v1.3): **$0 USD/mese M0-M3**, hard cap $30 USD/mese sempre, oltre = review Merari.

**Procedura monitoraggio costi**:

1. **Daily check** (Claudio, 1 min): Fly.io dashboard → outbound usage rolling 30gg. Alert manuale se > 70% di 160 GB/mese.
2. **Weekly check** (Claudio, 5 min): Upstash dashboard → cmd/giorno rolling 7gg. Alert se > 7k/giorno (70% del free tier).
3. **Monthly review** (Claudio, 10 min): aggregate costs vs target. Documenta in `SESSION-STATE.md` sez. 6.
4. **Trigger over-cap (M4+)**: se 2 mesi consecutivi > $30, attiva SR-003. Opzioni:
   - **(A)** Ottimizzare: rate limit più aggressivo, cache aggressivo, ridurre scope tool gated
   - **(B)** Approval Merari per cap a $50/mese (nuovo canonico in MASTER)
   - **(C)** Migrazione: se Fly.io free tier deprecato, fallback a Railway $5/mese

**Stop rule SR-003** (MASTER-PLAN sez. 11): spesa > cap per 2 mesi consecutivi → audit + rate limit + provider alternativo.

---

## 13. Runbook incidenti

Procedure operative per scenari ricorrenti. Da consultare durante incident, no decisioni in real-time.

### 13.1 P0 — Server completamente down (production)

**Sintomi**: `/health` torna 5xx o no response. Tutti i tool falliscono.

**Steps**:
1. **Acknowledge** alert (Slack, UptimeRobot SMS).
2. Apri Fly.io dashboard production environment.
3. Check log degli ultimi 10 min — cerca `CRITICAL` o stack trace.
4. Se config issue: restart container dal dashboard.
5. Se code issue: rollback commit (sez. 8.2).
6. Se infrastruttura Fly.io: aspetta + escalation a Fly.io support.
7. Aggiorna `#alerts-mcp` con stato ogni 15 min.
8. Post-incident: scrivi RCA (Root Cause Analysis) in `Docs/incidents/YYYY-MM-DD-incident.md`.

### 13.2 P1 — Tier 2 down (lead capture impossibile)

**Sintomi**: Tier 1 funziona, ma `agendar_auditoria_gratuita`/`solicitar_propuesta` falliscono.

**Possibili cause**:
- Cal.com API down → check loro status page
- HubSpot API down → check loro status page
- Resend down → magic link non recapitati
- Redis down → server in DEGRADED state

**Steps**:
1. Identifica integrazione fallita dai log (campo `integrations` nel log line).
2. Se integrazione esterna: aspetta loro recovery, monitora.
3. Lead arrivati durante outage: in fallback queue Redis. Check con `scripts/inspect_fallback_queue.py`.
4. Post-recovery: flush manuale fallback queue.

### 13.3 P2 — Latency degradata

**Sintomi**: `/metrics` mostra p95 > 1s su Tier 1 (target < 50ms).

**Possibili cause**:
- Memory leak progressivo
- Redis latency alta
- Logging eccessivo

**Steps**:
1. Check Fly.io dashboard CPU/memory.
2. Se memory crescente: memory leak. Restart container come temp fix, investigare codice.
3. Se Redis latency: check Upstash dashboard. Se > 50ms p95: contact Fly.io support.
4. Se né l'uno né l'altro: profile via `py-spy` (manuale, su staging).

### 13.4 P3 — Tool call individuale fallisce

**Sintomi**: 1 tool restituisce errore 500, altri OK.

**Steps**:
1. Identifica request_id dal log error.
2. Reproduce in staging con stesso input.
3. Se reproducible: bug. Crea issue, fix forward.
4. Se non reproducible: incident transitorio. Monitora.

### 13.5 P4 — Deploy fallito

**Sintomi**: Smoke test post-deploy KO.

**Steps**:
1. Fly.io dashboard → check log build/runtime.
2. Se build fail: codice non compila. Fix locale, push nuovo commit.
3. Se runtime fail post-build: probabilmente env variable mancante. Add e re-trigger deploy.
4. Old container resta vivo se rolling deploy: niente downtime.

---

## 14. Decisioni canoniche deployment (locked)

| ID | Decisione | Motivazione |
|---|---|---|
| **D-DE-001** | Hosting **Fly.io free tier** (D-MP-002 v1.3) | Costo $0/mese target, region MEX (Mexico City) ottimale per LATAM/MX/US, Dockerfile native, dominio + HTTPS auto, SSE supportato (richiesto da MCP). |
| **D-DE-002** | 2 environment: staging + production. Local è dev-only | Standard, coerente con `01-ARCHITECTURE.md` sez. 11. |
| **D-DE-003** | Branch strategy: develop→staging, main→production (D-C-004) | GitHub Flow esteso, semplice. |
| **D-DE-004** | Rolling deploy con health check obbligatorio | Zero downtime su deploy normali. |
| **D-DE-005** | TLS via Let's Encrypt (Fly.io-managed) | Standard, no manutenzione. |
| **D-DE-006** | DNS Cloudflare presunto (da confermare con Merari) | Veloce, programmable, default sviluppatore. |
| **D-DE-007** | CI: GitHub Actions con uv sync, ruff, mypy, pytest, validate_data | Stack coerente con `02-CONVENTIONS.md`. |
| **D-DE-008** | Coverage minimum 80% su PR (hard fail) | D-C-012. |
| **D-DE-009** | Smoke test post-deploy: health + discovery + 1 tool Tier 1 | Conferma deploy effettivo, non solo container running. |
| **D-DE-010** | Rollback via `git revert` + push (no rollback manuale Fly.io eccetto emergency) | Audit trail completo. |
| **D-DE-011** | Secrets in Fly.io env, mai in repo. `.env.example` solo placeholder | Standard sicurezza. |
| **D-DE-012** | Pydantic settings con validation at startup | Fail fast su config invalida. |
| **D-DE-013** | JWT keypair rotation ogni 90gg, manuale v1, automatica v2 | Sicurezza vs effort. |
| **D-DE-014** | UptimeRobot probe `/health` ogni 5 min, alert email + SMS | Detection esterno, indipendente da Fly.io. |
| **D-DE-015** | Health check semplice (data + redis), no integrations esterne | Rolling deploy non bloccato da deps esterni down. |
| **D-DE-016** | CORS allowlist stretto: claude.ai, chatgpt.com, cursor.so | Riduce errori integrazione, segnala intenzione. |
| **D-DE-017** | Logs JSON stdout, 30gg retention Fly.io. M3+: export S3 90gg | Audit trail LFPDPPP, semplicità v1. |
| **D-DE-018** | RTO 30 min, RPO 6h | Realistic per single dev, no pretensione enterprise. |
| **D-DE-019** | Backup CRM mensile manuale via HubSpot export, Merari owner | Disaster recovery business data. |
| **D-DE-020** | **Target costo $0/mese M0-M3** (Fly.io free + Resend free + Upstash free); hard cap $30/mese (rivedibile con approval Merari) | M0.2.1 chiusa 2026-05-11. Disciplina finanziaria allineata MASTER-PLAN v1.3. |
| **D-DE-021** | Runbook incidenti documentato + RCA post-mortem in `Docs/incidents/` | Disciplina operativa per dev solo. |
| **D-DE-022** | Niente error tracking aggregato in v1 (Sentry rimandato a M3+) | structlog + Slack alert su CRITICAL coprono 90% casi. |
| **D-DE-023** | Niente auto-scaling in v1 (manual scaling se serve) | Volume previsto basso, complessità non giustificata. |
| **D-DE-024** | Region Fly.io: `mex` (Mexico City) primary per production, `mia` (Miami) per staging | Fly.io supporta region MEX in 2026 — latenza ottima per LATAM/MX/US. Bonus: cross-region testing tra prod e staging. |
| **D-DE-025** | Status page pubblica rimandata a v2 | Trust signal valutato post lanci pubblici. |

---

## 15. Decisioni aperte deployment

| ID | Decisione | Bloccare entro | Owner |
|---|---|---|---|
| **DECISION-OPEN-DE-001** | Conferma DNS provider attuale di segmentamarketing.com (Cloudflare presunto) | M1 | Merari |
| ~~**DECISION-OPEN-DE-002**~~ | ~~Region Fly.io~~ → **Chiusa 2026-05-11**: D-DE-024 dichiara `mex` per prod + `mia` per staging. | ✅ Chiusa | Claudio |
| **DECISION-OPEN-DE-003** | Sentry o equivalente per error tracking aggregato | M3 | Claudio |
| **DECISION-OPEN-DE-004** | Status page pubblica (statuspage.io, BetterUptime) per trust signal | M5 | Merari + Claudio |
| **DECISION-OPEN-DE-005** | Backup esportato a S3 / Backblaze per audit log retention 7 anni | M5 | Claudio |
| **DECISION-OPEN-DE-006** | Auto-scaling Fly.io dopo soglie definite vs manuale | v2 | Claudio |
| **DECISION-OPEN-DE-007** | Multi-region active-active per resilience LATAM (Mexico City + US-West)? | v2 | Claudio + Merari |
| **DECISION-OPEN-DE-008** | Cost cap aumento da $30 a $65/mese in M3-M4: approval anticipata o on-demand? | M2 | Merari |

---

## 16. Versioning di questo documento

| Versione | Data | Autore | Note |
|---|---|---|---|
| 1.0 | 2026-05-10 | Claude (proposta) + Claudio (revisione) | Prima stesura completa: hosting Fly.io, DNS Cloudflare, TLS Let's Encrypt, CI GitHub Actions, CD Fly.io auto, rollback strategy, secrets management, runbook incidenti P0-P4, cost projection. |
| 1.1 | 2026-05-11 | Claude (harmony pass M0.3) + Claudio (review) | **HC-007**: aggiunta sez. 3.3 (Dockerfile multi-stage completo), sez. 3.4 (.dockerignore), sez. 4.4bis (railway.toml dichiarativo). Sez. 6.3 espansa con YAML completo `deploy-production.yml` (era stub). Sez. 12.3 cost projection ora include colonna "vs Cap $30" + procedura formale over-cap M3+ (3 opzioni A/B/C). Cross-ref con DECISION-OPEN-DE-001/-008 e DECISION-OPEN-AU-001/004. |
| 1.2 | 2026-05-11 | Claude + Claudio (chiusura M0.2.1) | **Hosting migrato Railway → Fly.io free tier** (D-MP-002 v1.3, D-DE-001 v1.2): costo target $0/mese, region MEX (prod) + MIA (staging). Sez. 4 riscritta. `railway.toml` sostituito da `fly.toml` + `fly.staging.toml` (sez. 4.4bis). Sez. 7 (CD) riscritta: deploy via GitHub Action + `flyctl deploy --remote-only` (Fly non ha auto-deploy da GitHub come Railway). Sez. 9.1 secrets management aggiornato a `flyctl secrets set`. D-DE-001/-020/-024 aggiornate. DECISION-OPEN-DE-002 chiusa. Cost projection sez. 12.3 ricalcolata a $0/mese M0-M3. Repo target ora `github.com/segmenta-ai/segmenta-mcp` (M0.2.5). |

---

## Note per il changelog

*(Sezione vuota in v1.0 — verrà popolata se emergono incongruenze nei file successivi che richiedono retrofitting in questo DEPLOYMENT.)*

---

**Fine 09-DEPLOYMENT.md v1.0.**
