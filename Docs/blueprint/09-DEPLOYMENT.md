# 09 — DEPLOYMENT

| Campo | Valore |
|---|---|
| **Progetto** | Segmenta MCP Server |
| **Versione documento** | 1.3 |
| **Data** | 2026-05-11 |
| **Status** | Approvato (post ricalibrazione hosting Fly.io → Oracle Cloud Always Free) |
| **File n.** | 09 di 12 numerati |
| **Documento padre** | `00-MASTER-PLAN.md` v1.4, `01-ARCHITECTURE.md` v1.3 |
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
   ┌────────────────────┐              ┌──────────────────────────┐
   │  GitHub Actions    │              │  ghcr.io                 │
   │  (CI: test+lint)   │──image push─▶│  (image registry)        │
   └────────────────────┘              └──────────┬───────────────┘
                                                  │ Watchtower polls 5min
                                                  ▼
   ┌────────────────────────────────────────────────────────┐
   │  Oracle Cloud Always Free VM (ARM 4vCPU + 24GB RAM)   │
   │  Region: sa-saopaulo-1                                 │
   │                                                         │
   │  ┌────────────┐   ┌────────────┐   ┌──────────────┐  │
   │  │ Caddy      │──▶│ app        │──▶│ Watchtower   │  │
   │  │ (TLS auto) │   │ (FastMCP)  │   │ (auto-update)│  │
   │  └────────────┘   └────────────┘   └──────────────┘  │
   │   docker compose network: mcp_internal                 │
   └────────────────────────────────────────────────────────┘
                                │
                                │ public traffic via :443
                                ▼
            ┌──────────────────────────────────────┐
            │  Hostinger DNS                        │
            │  mcp.segmentamarketing.com           │
            │   → A record → Oracle public IP     │
            └──────────────────────────────────────┘
                                │
                                │ TLS Let's Encrypt (Caddy auto)
                                ▼
                          End user / MCP client

   Out-of-band: Upstash Redis (separato, free tier 10k cmd/giorno)
                Resend SMTP (separato, free tier 100/giorno)
                Tailscale (SSH sicuro Claudio → VM, no port :22 pubblica)
```

### 3.2 Componenti

| Componente | Provider | Funzione |
|---|---|---|
| Source repo | GitHub (`github.com/segmenta-ai/segmenta-mcp`) | Storage codice + tag/release (DECISION-OPEN-005 chiusa) |
| CI | GitHub Actions | Lint + test + type check su PR |
| Container registry | GitHub Container Registry (ghcr.io) free per repo pubblici | Build image dal Dockerfile (vedi sez. 3.3), tag `:latest` + `:<sha>` |
| Compute | **Oracle Cloud Always Free** (1 VM ARM Ampere A1, 4 vCPU, 24GB RAM, 200GB block storage) | Esecuzione container Docker, region São Paulo (`sa-saopaulo-1`) o Phoenix (`us-phoenix-1`) |
| OS | Ubuntu 22.04 LTS | Security patch via `unattended-upgrades`, supporto fino aprile 2027 |
| Container orchestration | Docker Compose (single-host) | App + Redis + Caddy in 3 container, network bridge interna |
| Reverse proxy / TLS | Caddy (in container) | HTTPS automatico via Let's Encrypt, HSTS, HTTP/2, auto-renewal — zero config dopo install |
| Database state | **Upstash Redis free tier** (10k cmd/giorno, 256MB) — alternativa M3+: Redis self-hosted in container sulla stessa VM | OAuth state, idempotency, rate limit |
| DNS | **Hostinger** (DECISION-OPEN-DE-001 chiusa 2026-05-12) | A record `mcp.segmentamarketing.com` → IP pubblico Oracle VPS |
| Remote SSH | Tailscale free (max 100 device personali) | SSH sicuro alla VPS senza esporre porta 22 al pubblico |
| Monitoring uptime | UptimeRobot free | Probe `/health` ogni 5 min |
| Monitoring app | Caddy access log + structlog stdout, scrapable via Prometheus su `/metrics` (scrape esterno opzionale) | Metriche realtime, logs persistiti su volume Docker |
| Auto-update container | Watchtower in Docker | Polling ghcr.io ogni 5 min, restart graceful con nuovo image |
| Email transactional | **Resend free tier** (100/giorno = 3000/mese — DECISION-OPEN-004 chiusa) | (vedi `08-INTEGRATIONS.md` sez. 6) |
| Backup | GitHub repo + Upstash snapshot daily + Oracle Object Storage Always Free (10GB) per backup volume Caddy/data | Codice in repo, state snapshot Upstash 24h, volumi VPS backup notturno cron |

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

# Health check Docker (ridondante con Caddy upstream check ma utile per docker run locale)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8000/health',timeout=5).status==200 else 1)"

CMD ["python", "-m", "uvicorn", "segmenta_mcp.main:app", \
     "--host", "0.0.0.0", "--port", "8000", \
     "--no-access-log", "--proxy-headers"]
```

**Note**:
- Multi-stage riduce dimensione image finale a ~150 MB (vs ~600 MB single-stage).
- `--no-access-log` perché loggiamo manualmente con structlog (D-A-008).
- `--proxy-headers` perché il container `app` è dietro Caddy reverse proxy (X-Forwarded-For necessario per rate limit per IP).
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

## 4. Hosting: Oracle Cloud Always Free Tier

### 4.1 Razionale scelta (D-MP-002 v1.4)

Oracle Cloud Always Free è la scelta canonica post-ricalibrazione 2026-05-11 (target costo $0/mese **perpetuo**). Confronto:

| Provider | Pro | Contro | Decisione |
|---|---|---|---|
| **Oracle Cloud Always Free** | $0/mese **perpetuo** (politica dichiarata), 1 VM ARM Ampere A1 (4 vCPU + 24GB RAM, oversize per scope), 200GB block storage, 10TB outbound/mese, zero vendor lock-in (VPS Linux puro) | Setup iniziale ~3-4h, manutenzione ~15 min/mese, region São Paulo o Phoenix (no MX direct) | **Default v1.4** |
| Fly.io free | Region MEX + MIA, Dockerfile-native, esperienza PaaS smooth | **Free tier eliminato 2024**: ora $5 credit minimo + carta richiesta | ❌ Eliminato come opzione perché non più davvero free |
| Koyeb free | 1 servizio gratis, esperienza Fly.io-like | 1 servizio = no staging dedicato, free tier non perpetuo dichiarato | No (rischio Fly.io v2) |
| Render free | Setup veloce, free tier ufficiale | **Sleep 15 min idle** rompe OAuth magic link flow → lead persi | No (incompatibile con Tier 2) |
| Cloudflare Workers free | 100k req/giorno, edge globale | Python beta, 10ms CPU/req incompatibile crawler T2, refactor 40+ ore | No |
| Vercel free | Hobby tier $0 | Serverless mismatch architetturale con SSE MCP, 10s timeout Hobby | No |
| Heroku | Industry standard | Free tier rimosso 2022 | No |
| Railway Hobby | UI eccellente | $5/mese minimo, no free tier | Fallback paid se Oracle non disponibile in futuro |

### 4.2 Configurazione Oracle Cloud

**Account**: Oracle Cloud, tier "Always Free" (richiede verifica carta di credito ma non addebita mai per risorse Always Free).

**Region (Home Region irreversibile per Always Free)**: **Mexico Central (`mx-queretaro-1`)** primary — latenza ~5-30ms da MX (mercato primario), ~50-80ms da US, ~120-150ms da LATAM Sud. Bonus: data residency LFPDPPP-aligned (dati in MX). Fallback se ARM A1 non disponibile al signup: Mexico Northeast `mx-monterrey-1`, oppure São Paulo `sa-saopaulo-1`.

**VM (Compute Instance)**:
- Shape: `VM.Standard.A1.Flex` (ARM Ampere)
- **OCPU**: 2 (v1 iniziale) → upgrade gratuito a 4 quando ARM A1 capacity in Querétaro si libera
- **Memory**: 12 GB (v1 iniziale) → upgrade gratuito a 24 GB con upgrade OCPU
- Sempre dentro Always Free quota: 4 ARM OCPU + 24 GB RAM per tenant
- OS: Ubuntu 22.04 LTS (Canonical-Ubuntu-22.04-aarch64-2024.X.X)
- Boot volume: 50 GB (incluso in always free)
- Block storage extra: 100 GB disponibile (quota always free 200 GB totali)

> **Nota capacity ARM A1 (storico noto Oracle)**: Querétaro AD-1 in genere ha capacity ARM scarsa per shape 4+24. Iniziamo con 2+12 (capacity disponibile al 1°-2° tentativo) e upgradiamo gratuitamente a 4+24 in M2-M3 quando capacity si libera (mediamente entro 1-2 settimane su account nuovi). FastMCP usa ~200 MB RAM, quindi 12 GB sono comunque oversize 50x.

**Networking**:
- VCN (Virtual Cloud Network) di default Oracle
- Public subnet con IP pubblico riservato (always free fino a 2 IP)
- Security list: aperto inbound `:22` solo via Tailscale ACL, `:80` + `:443` open public per Caddy
- Egress: 10 TB/mese always free, hard cap (no overage)

**Plan**: Always Free Tier permanent. Nessun upgrade pianificato in v1-v2.

### 4.3 Resource sizing v1

| Risorsa | Allocato | Ragione |
|---|---|---|
| CPU | 4 vCPU ARM Ampere A1 | Massivamente oversize per Tier 1 (in-memory). Tier 2 SEO crawler comodo. |
| RAM | 24 GB | Massivamente oversize: Python + FastMCP + Pydantic ~150-200 MB → headroom 100x. Permette futuri Redis self-hosted, Caddy, Watchtower nello stesso host. |
| Disk | 200 GB block storage | OS + Docker images + volumes + log + 7gg backup retention |
| Redis | Upstash free 256 MB (10k cmd/giorno) — alternativa M3+: Redis container sulla stessa VM (no quota external) | OAuth state + rate limit + idempotency keys |
| Outbound | 10 TB/mese (always free hard cap) | Sufficiente per ~200k tool calls/giorno (~50 KB response media). Oltre il limit, traffic blocked (no overage charge). |

Auto-scaling: **non applicabile** (single VM). In M5+ se serve scale: provision 2ª VM Always Free + Caddy load balancer.

> **Vantaggio risorse oversize**: nessun memory leak può crashare il server in tempi normali. 24GB RAM = headroom per profiling con `tracemalloc` continuo, log retention generosa, eventuali futuri tool che caricano dataset più grandi.

### 4.4 Setup VPS step-by-step (one-time, ~3-4h)

Procedura M1.5.1. Documentata qui per ripetibilità in caso di disaster recovery.

**Pre-requisiti**:
- Account Oracle Cloud verificato
- SSH keypair generato (`ssh-keygen -t ed25519 -C "claudio@segmenta-mcp"`)
- Account Tailscale free creato

**Step 1 — Provision VM Oracle (~30 min)**:
1. Console Oracle → Compute → Instances → Create Instance
2. Name: `segmenta-mcp-prod`, Compartment: root
3. Image: Ubuntu 22.04 Minimal aarch64
4. Shape: `VM.Standard.A1.Flex` → 4 OCPU, 24 GB RAM
5. Networking: VCN default, public subnet, assign public IPv4
6. SSH keys: paste pubkey ed25519
7. Boot volume: 50 GB
8. Create

**Step 2 — Bootstrap Linux (~1h)**:

```bash
# SSH iniziale (porta 22 ancora aperta dal firewall Oracle)
ssh ubuntu@<public-ip>

# Update system
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl wget git vim ufw fail2ban unattended-upgrades

# Auto security updates
sudo dpkg-reconfigure --priority=low unattended-upgrades

# UFW firewall (preparatorio: prima setup Tailscale, poi chiudi :22)
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

# fail2ban con default jail.local
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo systemctl enable --now fail2ban
```

**Step 3 — Tailscale (SSH sicuro, chiudi porta 22 pubblica) (~15 min)**:

```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up --ssh --advertise-tags=tag:mcp-server

# Verifica accesso da laptop Claudio (Tailscale installato)
# tailscale ssh ubuntu@segmenta-mcp-prod

# Solo dopo aver verificato che Tailscale SSH funziona, chiudi :22 pubblico
sudo ufw delete allow 22/tcp
sudo ufw status numbered
```

**Step 4 — Docker + Docker Compose (~15 min)**:

```bash
# Docker Engine (script ufficiale)
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker ubuntu
newgrp docker  # apply group senza re-login

# Docker Compose plugin (incluso in get.docker.com 2024+)
docker compose version  # verifica installato
```

**Step 5 — Application directory + secrets (~30 min)**:

```bash
sudo mkdir -p /opt/segmenta-mcp
sudo chown ubuntu:ubuntu /opt/segmenta-mcp
cd /opt/segmenta-mcp

# Clona repo (read-only, deploy via GitHub Actions)
git clone https://github.com/segmenta-ai/segmenta-mcp.git .

# Crea .env file con secrets (mode 600, owner ubuntu only)
touch .env
chmod 600 .env
vim .env  # popola con tutte le secrets (vedi sez. 9.5)
```

**Step 6 — Caddy + docker-compose up (~30 min)**:

```bash
# Verifica DNS A record già propagato (M0.2.4)
dig +short mcp.segmentamarketing.com  # deve restituire IP pubblico Oracle

# Avvia stack
docker compose up -d

# Caddy ottiene certificato Let's Encrypt automaticamente
# Verifica
curl -I https://mcp.segmentamarketing.com/health
# Atteso: HTTP/2 200, valid TLS cert
```

**Step 7 — Watchtower auto-update (~10 min)**:

Già incluso nel `docker-compose.yml` (vedi sez. 4.5). Verifica che polli ghcr.io ogni 5 min:

```bash
docker compose logs watchtower | tail -20
```

**Step 8 — Backup cron giornaliero (~15 min)**:

```bash
# Cron user-level
crontab -e

# Aggiungi:
# 0 3 * * * /opt/segmenta-mcp/scripts/backup.sh
```

Vedi `scripts/backup.sh` in repo (rsync volumi → Oracle Object Storage Always Free 10GB).

**Step 9 — UptimeRobot probe esterno (~5 min)**:

Crea monitor HTTP(S) su `https://mcp.segmentamarketing.com/health`, interval 5 min, alert email.

**Effort totale ~3-4h**. Ripetibile in disaster recovery (provisioning + bootstrap completo: ~1.5h se Claudio ha familiarità).

### 4.5 `docker-compose.yml` (in repo root)

Sostituisce `fly.toml` (v1.2) in v1.3. Stack 3-container per single-host deployment Oracle Cloud.

```yaml
# /opt/segmenta-mcp/docker-compose.yml

services:
  app:
    image: ghcr.io/segmenta-ai/segmenta-mcp:latest
    container_name: segmenta-mcp-app
    restart: unless-stopped
    env_file: .env  # mode 600, owner ubuntu
    environment:
      ENV: production
      LOG_LEVEL: INFO
      PORT: "8000"
      HOST: 0.0.0.0
    volumes:
      - app_data:/app/data_runtime
      - ./logs:/app/logs
    networks:
      - mcp_internal
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8000/health',timeout=5).status==200 else 1)"]
      interval: 30s
      timeout: 10s
      start_period: 40s
      retries: 3
    labels:
      - "com.centurylinklabs.watchtower.enable=true"
    mem_limit: 512m   # Limit conservativo, headroom enorme su 24GB host
    cpus: 1.0

  caddy:
    image: caddy:2.8-alpine
    container_name: segmenta-mcp-caddy
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
      - caddy_data:/data
      - caddy_config:/config
    networks:
      - mcp_internal
    depends_on:
      - app
    labels:
      - "com.centurylinklabs.watchtower.enable=true"

  watchtower:
    image: containrrr/watchtower:latest
    container_name: segmenta-mcp-watchtower
    restart: unless-stopped
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ${HOME}/.docker/config.json:/config.json:ro  # per ghcr.io auth
    environment:
      WATCHTOWER_POLL_INTERVAL: 300  # 5 min
      WATCHTOWER_LABEL_ENABLE: "true"
      WATCHTOWER_CLEANUP: "true"      # rimuovi vecchi image dopo update
      WATCHTOWER_INCLUDE_RESTARTING: "true"
      WATCHTOWER_NOTIFICATIONS: shoutrrr
      WATCHTOWER_NOTIFICATION_URL: ${SLACK_WEBHOOK_URL_DEPLOYS}
    networks:
      - mcp_internal

networks:
  mcp_internal:
    driver: bridge

volumes:
  app_data:
  caddy_data:
  caddy_config:
```

### 4.5bis `Caddyfile` (in repo root)

Caddy gestisce HTTPS automatico via Let's Encrypt. Reverse proxy verso `app:8000`. Headers di sicurezza standard.

```caddyfile
# /opt/segmenta-mcp/Caddyfile

{
    # Email per Let's Encrypt notifications
    email claudio@segmentamarketing.com
}

mcp.segmentamarketing.com {
    encode gzip zstd

    # Reverse proxy verso container app
    reverse_proxy app:8000 {
        # Forward client IP per rate limit
        header_up X-Real-IP {remote_host}
        header_up X-Forwarded-For {remote_host}
        header_up X-Forwarded-Proto {scheme}

        # Health check upstream
        health_uri /health
        health_interval 30s
        health_timeout 10s
    }

    # Headers di sicurezza
    header {
        # HSTS 1 anno + preload
        Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"
        # Prevent clickjacking
        X-Frame-Options "DENY"
        # MIME sniffing
        X-Content-Type-Options "nosniff"
        # Referrer policy
        Referrer-Policy "strict-origin-when-cross-origin"
        # Remove server signature
        -Server
    }

    # Log strutturato (Caddy native JSON)
    log {
        output file /var/log/caddy/access.log {
            roll_size 100mb
            roll_keep 7
            roll_keep_for 720h  # 30gg
        }
        format json
    }
}
```

### 4.5ter `.env` template (in repo come `.env.example`)

```bash
# === Server core ===
ENV=production
LOG_LEVEL=INFO
PORT=8000
HOST=0.0.0.0
ISSUER_URL=https://mcp.segmentamarketing.com

# === OAuth / JWT ===
JWT_PRIVATE_KEY=<paste full PEM>
JWT_PUBLIC_KEY=<paste full PEM>
JWT_KEY_ID=key-2026-05
OAUTH_ALLOWED_REDIRECT_HOSTS=claude.ai,chatgpt.com,cursor.so

# === Redis (Upstash) ===
REDIS_URL=rediss://default:<password>@<host>.upstash.io:6379
REDIS_TLS=true

# === Email (Resend) ===
RESEND_API_KEY=re_xxxxxxxxxx
RESEND_FROM_EMAIL=hola@send.mcp.segmentamarketing.com

# === CRM (HubSpot — DECISION-OPEN-003 default) ===
HUBSPOT_PRIVATE_TOKEN=pat-na1-xxxxxxxxxx

# === Booking (Cal.com — DECISION-OPEN-002 default) ===
CALCOM_API_KEY=cal_xxxxxxxxxx
CALCOM_USERNAME=segmenta

# === Slack notifiche ===
SLACK_WEBHOOK_URL_LEADS_MCP=https://hooks.slack.com/services/xxx
SLACK_WEBHOOK_URL_ALERTS_MCP=https://hooks.slack.com/services/yyy
SLACK_WEBHOOK_URL_DEPLOYS=https://hooks.slack.com/services/zzz

# === Geo IP ===
IPINFO_TOKEN=xxxxxxxxxx  # opzionale, free tier funziona senza

# === SEO data (DataForSEO — Tier 3 only) ===
DATAFORSEO_LOGIN=xxxxxxxxxx
DATAFORSEO_PASSWORD=xxxxxxxxxx
```

**Permessi**: `chmod 600 .env`, `chown ubuntu:ubuntu .env`. Mai committare in repo (è in `.gitignore`).

**Aggiornamento secrets in production**: SSH via Tailscale → `vim /opt/segmenta-mcp/.env` → `docker compose up -d` (ricrea container con nuove env vars, no downtime grazie a Caddy che mantiene connessioni vecchie fino a graceful drain).

### 4.5quater Comandi operativi tipici

```bash
# SSH alla VPS (via Tailscale, porta 22 NON pubblica)
tailscale ssh ubuntu@segmenta-mcp-prod
# oppure se preferisci alias: ssh segmenta-mcp-prod

# Status stack
cd /opt/segmenta-mcp
docker compose ps
docker compose logs -f app  # tail logs container app
docker compose logs -f caddy  # tail logs Caddy
docker compose logs -f watchtower  # check auto-update activity

# Manual deploy (normalmente non serve, Watchtower fa polling)
docker compose pull app
docker compose up -d app

# Restart graceful (zero downtime grazie a Caddy buffer)
docker compose restart app

# Backup ad-hoc
sudo /opt/segmenta-mcp/scripts/backup.sh

# Disk space check
df -h /opt
docker system df

# Clean old images (Watchtower fa già se WATCHTOWER_CLEANUP=true)
docker image prune -a -f --filter "until=168h"  # > 7gg
```

### 4.5quinquies Staging environment (single VM, env switching)

In v1 **non c'è VM staging dedicata** (per disciplina e Always Free quota). Lo "staging" è gestito così:

**Opzione A — branch develop su VM identica**:
- Provision 2ª VM ARM (sempre Always Free quota disponibile, abbiamo usato 4 OCPU su 4 totali ARM, quindi serve cambiare shape — vedi nota sotto)
- Domain: `mcp-staging.segmentamarketing.com`
- Setup identico via stesso playbook

**Opzione B — staging su porta diversa stessa VM**:
- Container `app-staging` aggiuntivo nel `docker-compose.yml`, env `ENV=staging`, image `:develop` tag
- Caddy serve `mcp-staging.segmentamarketing.com` → `app-staging:8001`
- Stesse risorse host condivise (24GB RAM ne sopporta 5 senza problemi)

**Default v1**: opzione B (staging come secondo container sullo stesso host). Setup in M3 quando serve veramente, non in M1.

**Nota Always Free quota ARM**: total 4 OCPU + 24 GB RAM ARM per tenant. Già allocate tutte alla VM prod. Per 2ª VM ARM serve ridurre quota prod (es. 2 OCPU + 12 GB ciascuna) **oppure** usare 2 VM x86 micro Always Free (1/8 OCPU + 1 GB RAM ciascuna — solo per test, non per prod).

### 4.6 Health check

Caddy esegue upstream check HTTP su `/health` ogni 30s (configurato in `Caddyfile`). Docker `healthcheck:` directive in `docker-compose.yml` esegue lo stesso check internamente. Container `unhealthy` per > 90s → Docker `restart: unless-stopped` policy retry, max 5 retry → manual intervention via Tailscale SSH.

```python
@app.get("/health")
async def health() -> dict:
    """Health check per Caddy upstream check + UptimeRobot esterno."""
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
; Production — A record verso IP pubblico Oracle Cloud VPS
mcp.segmentamarketing.com.       A      <PUBLIC_IP_ORACLE_VM>     ; es. 132.226.X.X
mcp-staging.segmentamarketing.com. A    <PUBLIC_IP_ORACLE_VM>     ; stessa VM o 2ª se quota disponibile

; Email Resend (DKIM/SPF/DMARC) — vedi 08-INTEGRATIONS.md sez. 6.6
; Nota: Resend usa subdomain `send.mcp.segmentamarketing.com` come Return-Path
resend._domainkey.mcp.segmentamarketing.com.  TXT  "p=MIGfMA0... (DKIM public key 400+ char)"
send.mcp.segmentamarketing.com.   MX    10 feedback-smtp.<region>.amazonses.com.
send.mcp.segmentamarketing.com.   TXT   "v=spf1 include:amazonses.com ~all"
_dmarc.mcp.segmentamarketing.com. TXT   "v=DMARC1; p=quarantine; rua=mailto:dmarc@segmentamarketing.com; pct=100"

; OAuth metadata discovery (auto-served from server)
; No DNS record needed; il server espone /.well-known/oauth-authorization-server

; Optional: CAA per limitare CA per HTTPS (raccomandato)
mcp.segmentamarketing.com.       CAA    0 issue "letsencrypt.org"
```

A record → IP pubblico Oracle VPS. Caddy (in container) gestisce automaticamente TLS via Let's Encrypt al primo request HTTPS.

### 5.3 TLS

Configurazione automatica via Caddy:
- Provider CA: Let's Encrypt (Caddy default; ZeroSSL come fallback automatico)
- Algoritmo: ECDSA P-256 (default Caddy 2026)
- Renewal: automatico (Caddy controlla giornalmente, rinnova 30gg prima scadenza)
- HSTS abilitato in `Caddyfile`: `Strict-Transport-Security: max-age=31536000; includeSubDomains; preload`
- Storage cert: volume Docker `caddy_data` (persiste tra restart container)

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

### 6.2 Workflow CD post v1.3 (Oracle Cloud)

In v1.3 (post ricalibrazione hosting) i workflow CD sono cambiati radicalmente:

- **`build-publish.yml`** — riportato per intero in sez. 7.2 (build image + push a ghcr.io). Triggered su push `main`/`develop` o tag `v*`.
- **`smoke-test.yml`** — riportato in sez. 7.3 (cron ogni 15 min, controlla `/health` + endpoint critici production). Triggered su `schedule` + manual.
- **NO workflow `deploy-staging.yml` / `deploy-production.yml`**: Watchtower (in container sulla VM) pulla automaticamente il nuovo image dopo il push a ghcr.io. Niente push to deploy via SSH, niente `flyctl deploy`.

Vedi sez. 7.2 e 7.3 per YAML completi.

Tag git release automatico (`v<version>` su push `main` se versione cambia) + GitHub Release con CHANGELOG: vedi sez. 7.2bis sotto.

### 6.3 Workflow `tag-release.yml` (post v1.3)

Triggered su push a `main` quando `__version__` cambia in `src/segmenta_mcp/__init__.py`. Crea tag git + GitHub Release. NON deploya (deploy è Watchtower).

YAML (adattato in v1.3 — solo tag/release, no smoke test perché smoke è in cron schedulato):

```yaml
name: Tag release + GitHub Release

on:
  push:
    branches: [main]
    paths:
      - 'src/segmenta_mcp/__init__.py'
      - 'CHANGELOG.md'

jobs:
  release:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Extract version from package
        id: version
        run: |
          VERSION=$(grep -oP '__version__ = "\K[^"]+' src/segmenta_mcp/__init__.py)
          echo "VERSION=$VERSION" >> $GITHUB_ENV

      - name: Check if tag already exists
        id: tag_check
        run: |
          if git rev-parse "v${{ env.VERSION }}" >/dev/null 2>&1; then
            echo "exists=true" >> $GITHUB_OUTPUT
          else
            echo "exists=false" >> $GITHUB_OUTPUT
          fi

      - name: Tag release
        if: steps.tag_check.outputs.exists == 'false'
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git tag -a "v${{ env.VERSION }}" -m "Release v${{ env.VERSION }}"
          git push origin "v${{ env.VERSION }}"

      - name: Extract CHANGELOG section for this version
        if: steps.tag_check.outputs.exists == 'false'
        run: |
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
        if: steps.tag_check.outputs.exists == 'false'
        uses: softprops/action-gh-release@v2
        with:
          tag_name: v${{ env.VERSION }}
          name: v${{ env.VERSION }}
          body: ${{ env.CHANGELOG_BODY }}
          draft: false
          prerelease: false

      - name: Notify Slack — release tagged
        if: steps.tag_check.outputs.exists == 'false'
        uses: slackapi/slack-github-action@v1
        with:
          payload: |
            {"text": "🏷️ Release v${{ env.VERSION }} tagged. Build image triggerato in build-publish.yml. Watchtower aggiornerà la VM entro 5 min."}
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL_DEPLOYS }}
```

> **Vecchio YAML deprecato**: il `deploy-production.yml` v1.2 (con `flyctl deploy` + smoke test inline) è stato rimpiazzato. Il blocco YAML lungo che segue era v1.2 — preservato qui per riferimento storico, ma non in uso in v1.3.

<details>
<summary>YAML v1.2 deprecato (ex Fly.io deploy-production.yml)</summary>

```yaml

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

      - name: Wait for Oracle Cloud deploy
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

</details>

### 6.4 Tempi attesi (post v1.3, Oracle Cloud + Watchtower)

| Step | Durata tipica |
|---|---|
| CI workflow (lint + test + type check) | 2-3 min |
| GitHub Actions build + push image a ghcr.io | 3-5 min (build ARM64 + cache GHA) |
| Watchtower polling detection nuovo image | ≤ 5 min (polling interval 5 min, average 2.5 min) |
| Watchtower pull + container restart graceful | 30-60s (pull + start + Caddy upstream check) |
| Smoke test cron schedule (separato) | ogni 15 min, indipendente dal deploy |
| **Totale PR `main` → production live** | **~6-12 min** (mediamente ~8 min) |

> **Nota**: il flusso non è "garantito" entro X min come PaaS auto-deploy. Watchtower polling è asincrono; nel peggior caso un push a `main` può aspettare fino 5 min prima che Watchtower lo veda. Per deploy "subito": SSH Tailscale → `docker compose pull app && docker compose up -d app` (manuale, ~30s).

---

## 7. CD: GitHub Container Registry + Watchtower auto-pull

### 7.1 Architettura CD (post v1.3 ricalibrazione)

Differenza chiave vs PaaS (Fly.io/Railway): **non c'è "deploy command" che pushe codice alla VM**. Il flusso è:

1. GitHub Action su push → **build image Docker → push a `ghcr.io/segmenta-ai/segmenta-mcp:latest` + `:<sha>`**
2. **Watchtower** (in container sulla VM Oracle) polla ghcr.io ogni 5 min
3. Quando vede image nuovo → `docker pull` + `docker compose up -d app` graceful restart
4. Caddy mantiene connessioni esistenti durante restart (drain ~5s)
5. Watchtower notifica successo/failure su Slack

Trigger:
- Push to `main` → GitHub Action `build-publish.yml` push tag `:latest` + `:<sha>` → Watchtower production VM aggiorna entro ~5 min
- Push to `develop` → GitHub Action push tag `:develop` → Watchtower staging container (M3+) aggiorna entro ~5 min

### 7.2 Build & publish — `build-publish.yml`

```yaml
name: Build and publish image

on:
  push:
    branches: [main, develop]
    tags: ['v*']

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
        with:
          platforms: linux/arm64  # ARM Ampere su Oracle

      - name: Login to ghcr.io
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Determine tag
        id: tag
        run: |
          if [[ "${{ github.ref }}" == "refs/heads/main" ]]; then
            echo "tag=latest" >> $GITHUB_OUTPUT
          elif [[ "${{ github.ref }}" == "refs/heads/develop" ]]; then
            echo "tag=develop" >> $GITHUB_OUTPUT
          elif [[ "${{ github.ref }}" == refs/tags/v* ]]; then
            echo "tag=${GITHUB_REF#refs/tags/}" >> $GITHUB_OUTPUT
          fi

      - name: Build and push (ARM64)
        uses: docker/build-push-action@v5
        with:
          context: .
          platforms: linux/arm64
          push: true
          tags: |
            ghcr.io/segmenta-ai/segmenta-mcp:${{ steps.tag.outputs.tag }}
            ghcr.io/segmenta-ai/segmenta-mcp:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

### 7.3 Smoke test post-deploy — `smoke-test.yml`

Triggered manualmente o via Watchtower webhook su deploy successful (M3+). In v1 è schedule-based (cron ogni 15 min).

```yaml
name: Smoke test production

on:
  schedule:
    - cron: '*/15 * * * *'  # ogni 15 min
  workflow_dispatch:

jobs:
  smoke-test:
    runs-on: ubuntu-latest
    steps:
      - name: Health check
        run: curl -f https://mcp.segmentamarketing.com/health

      - name: OAuth discovery endpoint
        run: curl -f https://mcp.segmentamarketing.com/.well-known/oauth-authorization-server

      - name: Tier 1 tool call (no auth)
        run: |
          curl -f -X POST https://mcp.segmentamarketing.com/mcp/tools/call \
               -H "Content-Type: application/json" \
               -d '{"name": "obtener_servicios"}'

      - name: JWKS endpoint
        run: curl -f https://mcp.segmentamarketing.com/.well-known/jwks.json

      - name: Notify Slack on failure
        if: failure()
        uses: slackapi/slack-github-action@v1
        with:
          payload: |
            {"text": "🚨 Smoke test FAILED on production — vedi runbook 09-DEPLOYMENT sez. 13"}
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL_ALERTS }}
```

### 7.4 Failed deploy handling

Se nuovo image fallisce health check post-pull:
1. Watchtower restart container con nuovo image.
2. Container `app` exit code != 0 o `/health` 5xx ripetuti → Docker `restart: unless-stopped` policy retry.
3. Se 5 retry consecutivi falliscono → container in stato `restarting` (loop).
4. Caddy upstream check fallisce → ritorna 502/503 → UptimeRobot alert.
5. Smoke test cron rileva → Slack alert (`SLACK_WEBHOOK_URL_ALERTS`).
6. Claudio: SSH via Tailscale → `docker compose logs app` → identifica issue → revert manuale.

**Rollback rapido**: `docker compose pull app:<sha-precedente-stabile>` + `docker compose up -d app`. Senza `git revert` (che triggera nuovo build, lento).

### 7.5 Variables binding

Vedi sez. 9. Riepilogo:
- Secrets in `/opt/segmenta-mcp/.env` (mode 600, ubuntu owner)
- `docker-compose.yml` legge via `env_file: .env`
- Update: SSH → `vim .env` → `docker compose up -d app` → graceful restart in ~3s

**Nessun secret in GitHub Actions** (eccetto quelli per build/notifications): l'image non contiene credentials, solo applicazione. Tutto il binding env è runtime.

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
# Watchtower polling rileva nuovo image entro 5 min, restart graceful
# GitHub Action smoke test conferma successo

# 5. Verifica
curl https://mcp.segmentamarketing.com/health
```

Tempo totale: 3-7 minuti (1 min revert + 2 min Oracle Cloud build + 3 min smoke test).

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
| **Environment-specific (non-secret)** | Valori che cambiano tra staging/prod, non sensibili | `docker-compose.yml` `environment:` block | `git commit` (visibile in repo) |
| **Secrets** | Credentials, API keys, signing keys, JWT private key | `/opt/segmenta-mcp/.env` (mode 600, owner ubuntu, **never committed**) | SSH via Tailscale + `vim .env` + `docker compose up -d app` |

**Best practice secrets su Oracle Cloud Always Free**:
- File `.env` esiste solo sulla VM, mai in repo (`.gitignore` lo include esplicitamente).
- `chmod 600 .env` + `chown ubuntu:ubuntu` → solo user ubuntu può leggerlo. Container `app` accede via Docker bind mount mediato da `env_file:` direttiva (Docker risolve at startup, niente file mount diretto nel container = no risk leak).
- Backup secrets: copia manuale offline (1Password / Bitwarden personale Claudio). Mai in repo, mai in cloud storage non encrypted.
- **Update**: SSH → vim `.env` → `docker compose up -d app` → container restart con nuove vars in ~3s. Caddy mantiene connessioni esistenti (drain ~5s) → zero downtime per utenti.
- **Audit access**: `auditd` Linux logs ogni read di `/opt/segmenta-mcp/.env` se serve enforcement compliance LFPDPPP.

### 9.2 Variables list

Cataloghiamo tutte le env variables. Aggiornate quando se ne aggiungono.

#### Server core

| Variable | Type | Required | Default | Note |
|---|---|---|---|---|
| `ENV` | string | Yes | — | `local` / `staging` / `production` |
| `LOG_LEVEL` | string | No | `INFO` | `DEBUG` / `INFO` / `WARN` / `ERROR` |
| `PORT` | int | No | `8000` | Definito in `docker-compose.yml`, Caddy proxy a `app:8000` |
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
| `RESEND_FROM_EMAIL` | string | M2+ | `hola@send.mcp.segmentamarketing.com` (Resend richiede subdomain `send.` per best deliverability) |
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
| `CALCOM_API_KEY` | Ogni 6 mesi o on-demand | Genera new in Cal.com dashboard, SSH Tailscale → vim `/opt/segmenta-mcp/.env` → `docker compose up -d app` |
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
- Output: stdout container app → Docker logs driver `json-file` (rotation auto: 10MB max, 3 file) → opzionale forward a `journald` host
- Formato: JSON strutturato via `structlog`
- Livello produzione: INFO
- Retention: 30 giorni rolling sul host (logrotate Docker), 90 giorni se exported a Oracle Object Storage (M3+, 10GB Always Free)

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

Esposte su `/metrics` formato Prometheus. Oracle Cloud non scrape Prometheus automaticamente in v1. Strategie:

**v1**: SSH Tailscale + `htop` / `docker stats` per CPU/memory/network in real-time. Oracle Cloud Console mostra metriche VM-level (CPU usage avg, network bytes, disk IOPS) — sufficiente per troubleshooting.

**v2 / M4**: Esportare metriche custom a Grafana Cloud free tier (10k series) o Prometheus self-hosted in Docker stack sulla stessa VM (24GB RAM ne sopporta abbondantemente). Decisione DECISION-OPEN-T-005 di `01-ARCHITECTURE.md`.

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

V1: niente error tracking aggregato. structlog + Docker logs (`docker compose logs app`) + Slack alerts su CRITICAL coprono il 90% dei casi.

V2 / M3+: introdurre Sentry o equivalente.

### 10.5 Audit trail

Log con flag `event_type=auth_*` o `event_type=privacy_*` aggregati separatamente per audit LFPDPPP/GDPR.

In v1: query manuale via SSH Tailscale + `docker compose logs app | grep <pattern>` o `journalctl -u docker | grep`.

In v2: export periodico a S3 / Backblaze per long-term retention 7 anni (compliance).

---

## 11. Backup e disaster recovery

### 11.1 Cosa è backup-ato

| Risorsa | Backup | Restore time |
|---|---|---|
| **Codice** | GitHub repo | < 5 min (clone + deploy) |
| **JSON dati** | Versionati in repo | Inclusi nel codice |
| **Redis state** | Upstash snapshot automatico (every 24h, 7gg retention free tier). Se Redis self-hosted M3+: cron RDB dump + sync a Oracle Object Storage Always Free | < 30 min (restore from snapshot Upstash) |
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
1. SSH via Tailscale → `docker compose ps` per identificare container failed
2. `docker compose logs app --tail 100` → cerca CRITICAL log line
3. Se config issue:
   - Verifica env variables in `/opt/segmenta-mcp/.env` (chmod 600)
   - Restart manuale dal dashboard
4. Se code issue:
   - git revert dell'ultimo commit
   - git push origin main
   - Aspetta auto-deploy
5. Se persistente: rollback `docker compose pull app:<sha-precedente-stabile>` + `docker compose up -d app`
6. Aggiorna SESSION-STATE con incident
```

**Scenario 2: Redis Upstash down**

```
1. Check Upstash dashboard → confermare outage Redis (status.upstash.com)
2. Status notification: server entra in DEGRADED state automaticamente
   (Tier 1 funziona, Tier 2/3 risponde 503)
3. Comunicazione: status page (M3+) o Slack #alerts
4. Recovery: tipicamente Oracle Cloud/Upstash risolve in < 30 min
5. Restart del nostro container post-recovery (per riconnettere Redis pool)
```

**Scenario 3: Repo GitHub compromesso (account hijack)**

```
1. Revoca tutti i token GitHub Personal Access Tokens
2. Rotate all secrets in Oracle Cloud env (JWT keys, API keys provider)
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

Single container Oracle Cloud Hobby plan:
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

V1 plan: 1 container. M4+ valutiamo 2 container con load balancer Oracle Cloud.

### 12.3 Cost projection (post v1.3, hosting Oracle Cloud Always Free)

| Mese | Compute (Oracle) | Redis (Upstash) | Email (Resend) | SEO API | Totale | vs Cap $30 |
|---|---|---|---|---|---|---|
| M1 | $0 (Always Free perpetuo) | $0 (free, 10k cmd/giorno) | $0 (free, 100/giorno) | $0 | **$0** | ✅ -$30 |
| M2 | $0 (Always Free) | $0 (free) | $0 (free, < 100/giorno previsto) | $0 | **$0** | ✅ -$30 |
| M3 | $0 (Always Free) | $0 (free, < 10k cmd/giorno) | $0 (free, 50-100/giorno) | $0 | **$0** | ✅ -$30 |
| M4 | $0 (Always Free, oversize) | $0 (Upstash free) o $0 (Redis self-host nel container Docker sulla stessa VM) | $0-$20 (Resend Pro se > 100/giorno) | $0-$20 (DataForSEO trial) | **$0-$40** | ⚠️ se >$30: review Merari |
| M5+ | $0 (Always Free) | $0 (Redis self-host) | $20 (Resend Pro) | $40 (SEO data full) | **$60-$70** | ⚠️ richiede approval Merari |

**Vantaggio Oracle Cloud vs Oracle Cloud v1.2 baseline**:
- M4+: Redis può essere self-hosted nel Docker stack (la VM ha 24GB RAM, Redis usa ~50 MB) → eliminato costo Upstash paid in eventuale crescita.
- Compute resta $0 anche con scaling tool: 4 vCPU + 24GB RAM coprono volume previsto fino M5+ senza problemi.
- Outbound 10TB/mese hard cap (no overage): se traffico esplode oltre, server smette di rispondere ma mai bill surprise.

**Target costo canonico** (D-DE-020 v1.2, D-MP-002 v1.3): **$0 USD/mese M0-M3**, hard cap $30 USD/mese sempre, oltre = review Merari.

**Procedura monitoraggio costi**:

1. **Daily check** (Claudio, 1 min): Oracle Cloud Console → Networking → outbound usage rolling 30gg. Alert manuale se > 70% di 10 TB/mese (target unrealistic per v1, ma watch zero-effort).
2. **Weekly check** (Claudio, 5 min): Upstash dashboard → cmd/giorno rolling 7gg. Alert se > 7k/giorno (70% del free tier).
3. **Monthly review** (Claudio, 10 min): aggregate costs vs target. Documenta in `SESSION-STATE.md` sez. 6.
4. **Trigger over-cap (M4+)**: se 2 mesi consecutivi > $30, attiva SR-003. Opzioni:
   - **(A)** Ottimizzare: rate limit più aggressivo, cache aggressivo, ridurre scope tool gated
   - **(B)** Approval Merari per cap a $50/mese (nuovo canonico in MASTER)
   - **(C)** Migrazione: se Oracle Cloud free tier deprecato, fallback a Railway $5/mese

**Stop rule SR-003** (MASTER-PLAN sez. 11): spesa > cap per 2 mesi consecutivi → audit + rate limit + provider alternativo.

---

## 13. Runbook incidenti

Procedure operative per scenari ricorrenti. Da consultare durante incident, no decisioni in real-time.

### 13.1 P0 — Server completamente down (production)

**Sintomi**: `/health` torna 5xx o no response. Tutti i tool falliscono.

**Steps**:
1. **Acknowledge** alert (Slack, UptimeRobot SMS).
2. SSH via Tailscale → `cd /opt/segmenta-mcp && docker compose ps`
3. Check log degli ultimi 10 min — cerca `CRITICAL` o stack trace.
4. Se config issue: restart container dal dashboard.
5. Se code issue: rollback commit (sez. 8.2).
6. Se infrastruttura Oracle Cloud: aspetta + escalation a Oracle Cloud support.
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
1. SSH Tailscale → `htop` o `docker stats` per CPU/memory.
2. Se memory crescente: memory leak. Restart container come temp fix, investigare codice.
3. Se Redis latency: check Upstash dashboard. Se > 50ms p95: contact Oracle Cloud support.
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
1. GitHub Actions → check log build (image push to ghcr.io). Se push OK: SSH Tailscale → `docker compose logs app` per runtime.
2. Se build fail: codice non compila. Fix locale, push nuovo commit.
3. Se runtime fail post-build: probabilmente env variable mancante. Add e re-trigger deploy.
4. Old container resta vivo se rolling deploy: niente downtime.

---

## 14. Decisioni canoniche deployment (locked)

| ID | Decisione | Motivazione |
|---|---|---|
| **D-DE-001** | Hosting **Oracle Cloud Always Free** (D-MP-002 v1.4): 1 VM ARM Ampere A1 (4 vCPU + 24GB RAM) + Caddy reverse proxy + Docker Compose | Costo $0/mese **perpetuo** (Always Free dichiarato Oracle), risorse oversize, region São Paulo (~80ms da MX) o Phoenix, zero vendor lock-in (VPS Linux puro), SSE supportato nativamente. |
| **D-DE-002** | 2 environment: staging + production. Local è dev-only | Standard, coerente con `01-ARCHITECTURE.md` sez. 11. |
| **D-DE-003** | Branch strategy: develop→staging, main→production (D-C-004) | GitHub Flow esteso, semplice. |
| **D-DE-004** | Rolling deploy con health check obbligatorio | Zero downtime su deploy normali. |
| **D-DE-005** | TLS via Let's Encrypt (Oracle Cloud-managed) | Standard, no manutenzione. |
| **D-DE-006** | DNS **Hostinger** (confermato con Merari 2026-05-12) | Provider esistente Segmenta. Per Caddy + Let's Encrypt è sufficiente (no proxy/CDN davanti). Eventual upgrade a Cloudflare DNS in M3+ se serve DDoS mitigation. |
| **D-DE-007** | CI: GitHub Actions con uv sync, ruff, mypy, pytest, validate_data | Stack coerente con `02-CONVENTIONS.md`. |
| **D-DE-008** | Coverage minimum 80% su PR (hard fail) | D-C-012. |
| **D-DE-009** | Smoke test post-deploy: health + discovery + 1 tool Tier 1 | Conferma deploy effettivo, non solo container running. |
| **D-DE-010** | Rollback via `git revert` + push (no rollback manuale Oracle Cloud eccetto emergency) | Audit trail completo. |
| **D-DE-011** | Secrets in Oracle Cloud env, mai in repo. `.env.example` solo placeholder | Standard sicurezza. |
| **D-DE-012** | Pydantic settings con validation at startup | Fail fast su config invalida. |
| **D-DE-013** | JWT keypair rotation ogni 90gg, manuale v1, automatica v2 | Sicurezza vs effort. |
| **D-DE-014** | UptimeRobot probe `/health` ogni 5 min, alert email + SMS | Detection esterno, indipendente da Oracle Cloud. |
| **D-DE-015** | Health check semplice (data + redis), no integrations esterne | Rolling deploy non bloccato da deps esterni down. |
| **D-DE-016** | CORS allowlist stretto: claude.ai, chatgpt.com, cursor.so | Riduce errori integrazione, segnala intenzione. |
| **D-DE-017** | Logs JSON stdout, 30gg retention Oracle Cloud. M3+: export S3 90gg | Audit trail LFPDPPP, semplicità v1. |
| **D-DE-018** | RTO 30 min, RPO 6h | Realistic per single dev, no pretensione enterprise. |
| **D-DE-019** | Backup CRM mensile manuale via HubSpot export, Merari owner | Disaster recovery business data. |
| **D-DE-020** | **Target costo $0/mese M0-M3** (Oracle Cloud free + Resend free + Upstash free); hard cap $30/mese (rivedibile con approval Merari) | M0.2.1 chiusa 2026-05-11. Disciplina finanziaria allineata MASTER-PLAN v1.3. |
| **D-DE-021** | Runbook incidenti documentato + RCA post-mortem in `Docs/incidents/` | Disciplina operativa per dev solo. |
| **D-DE-022** | Niente error tracking aggregato in v1 (Sentry rimandato a M3+) | structlog + Slack alert su CRITICAL coprono 90% casi. |
| **D-DE-023** | Niente auto-scaling in v1 (manual scaling se serve) | Volume previsto basso, complessità non giustificata. |
| **D-DE-024** | Region Oracle Cloud: **`mx-queretaro-1` (Mexico Central, Querétaro)** primary per production. Fallback: `mx-monterrey-1` (Mexico Northeast) o `sa-saopaulo-1` (São Paulo) se ARM A1 capacity non disponibile al signup | Mexico Central: ~5-30ms da MX (mercato primario), ottimizza 17/30 query baseline. Bonus data residency LFPDPPP (dati restano fisicamente in MX, allineato con D-MP-014 sede legale messicana). |
| **D-DE-025** | Status page pubblica rimandata a v2 | Trust signal valutato post lanci pubblici. |

---

## 15. Decisioni aperte deployment

| ID | Decisione | Bloccare entro | Owner |
|---|---|---|---|
| ~~**DECISION-OPEN-DE-001**~~ | ~~Conferma DNS provider~~ → **Chiusa 2026-05-12**: Hostinger DNS. Merari ha aggiunto record Resend, può aggiungere A record VM Oracle quando ready. | ✅ Chiusa | Merari |
| ~~**DECISION-OPEN-DE-002**~~ | ~~Region Oracle Cloud~~ → **Chiusa 2026-05-11**: D-DE-024 dichiara `mex` per prod + `mia` per staging. | ✅ Chiusa | Claudio |
| **DECISION-OPEN-DE-003** | Sentry o equivalente per error tracking aggregato | M3 | Claudio |
| **DECISION-OPEN-DE-004** | Status page pubblica (statuspage.io, BetterUptime) per trust signal | M5 | Merari + Claudio |
| **DECISION-OPEN-DE-005** | Backup esportato a S3 / Backblaze per audit log retention 7 anni | M5 | Claudio |
| **DECISION-OPEN-DE-006** | Auto-scaling Oracle Cloud dopo soglie definite vs manuale | v2 | Claudio |
| **DECISION-OPEN-DE-007** | Multi-region active-active per resilience LATAM (Mexico City + US-West)? | v2 | Claudio + Merari |
| **DECISION-OPEN-DE-008** | Cost cap aumento da $30 a $65/mese in M3-M4: approval anticipata o on-demand? | M2 | Merari |

---

## 16. Versioning di questo documento

| Versione | Data | Autore | Note |
|---|---|---|---|
| 1.0 | 2026-05-10 | Claude (proposta) + Claudio (revisione) | Prima stesura completa: hosting Oracle Cloud, DNS Cloudflare, TLS Let's Encrypt, CI GitHub Actions, CD Oracle Cloud auto, rollback strategy, secrets management, runbook incidenti P0-P4, cost projection. |
| 1.1 | 2026-05-11 | Claude (harmony pass M0.3) + Claudio (review) | **HC-007**: aggiunta sez. 3.3 (Dockerfile multi-stage completo), sez. 3.4 (.dockerignore), sez. 4.4bis (railway.toml dichiarativo). Sez. 6.3 espansa con YAML completo `deploy-production.yml` (era stub). Sez. 12.3 cost projection ora include colonna "vs Cap $30" + procedura formale over-cap M3+ (3 opzioni A/B/C). Cross-ref con DECISION-OPEN-DE-001/-008 e DECISION-OPEN-AU-001/004. |
| 1.2 | 2026-05-11 | Claude + Claudio (chiusura M0.2.1) | **Hosting migrato Railway → Fly.io free tier** (D-MP-002 v1.3, D-DE-001 v1.2): costo target $0/mese, region MEX (prod) + MIA (staging). Sez. 4 riscritta. `railway.toml` sostituito da `fly.toml` + `fly.staging.toml` (sez. 4.4bis). Sez. 7 (CD) riscritta: deploy via GitHub Action + `flyctl deploy --remote-only`. Sez. 9.1 secrets management aggiornato a `flyctl secrets set`. D-DE-001/-020/-024 aggiornate. DECISION-OPEN-DE-002 chiusa. Cost projection sez. 12.3 ricalcolata a $0/mese M0-M3. Repo target ora `github.com/segmenta-ai/segmenta-mcp` (M0.2.5). |
| 1.3 | 2026-05-11 | Claude + Claudio (ricalibrazione hosting per stabilità free tier) | **Hosting ri-migrato Fly.io → Oracle Cloud Always Free** (D-MP-002 v1.4, D-DE-001 v1.3). Motivazione: Fly.io ha eliminato free tier perpetuo nel 2024, incompatibile con vincolo "$0 hard". Sez. 4 riscritta: VPS ARM 4vCPU+24GB RAM, region São Paulo, setup VPS step-by-step (sez. 4.4) con Tailscale + Docker + Caddy + Watchtower + UFW + fail2ban. `fly.toml` sostituito da `docker-compose.yml` + `Caddyfile` + `.env` template (sez. 4.5). Sez. 7 CD riscritta: build + push a ghcr.io via GitHub Action + Watchtower polling 5min sulla VM (no `flyctl deploy`). Sez. 9 secrets ora in `/opt/segmenta-mcp/.env` (mode 600, mai in repo). D-DE-001/-024 aggiornate. Smoke test diventa cron schedulato 15min. Setup iniziale ~3-4h, manutenzione mensile ~15 min. |

---

## Note per il changelog

*(Sezione vuota in v1.0 — verrà popolata se emergono incongruenze nei file successivi che richiedono retrofitting in questo DEPLOYMENT.)*

---

**Fine 09-DEPLOYMENT.md v1.0.**
