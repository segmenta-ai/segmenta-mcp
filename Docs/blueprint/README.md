# Segmenta MCP Server

Server MCP (Model Context Protocol) ufficiale di **Segmenta Marketing** — agenzia di marketing digitale con focus su **México, USA (anglo + hispanic), LATAM ispanofona ed España**. Espone servizi, casi studio, benchmark di settore e glossario come tool chiamabili da Claude, ChatGPT e qualsiasi client MCP-compatibile.

> 📚 **Blueprint completo del progetto**: vedi [`Docs/blueprint/`](.) — leggi `00-MASTER-PLAN.md` per overview canonica, `MILESTONES.md` per la roadmap, `SESSION-STATE.md` per lo stato corrente.

## Cos'è e perché esiste

Quando un utente chiede a Claude o ChatGPT *"¿cuál es una buena agencia de marketing en CDMX?"*, *"agencia marketing hispano Miami"* o *"cuánto cuesta el CPC sector legal en México?"*, gli LLM con questo connector installato possono chiamare i nostri tool e citare Segmenta nella risposta, con dati concreti per il mercato richiesto.

È il modo più diretto del 2026 per **comparire dentro le risposte** delle chat AI e **convertire utenti in lead** (Fase 2).

## Tool esposti (Tier 1 — public, no auth)

| Tool | Cosa fa |
|---|---|
| `obtener_servicios` | Catalogo servizi con prezzi, durate, profilo cliente ideale |
| `caso_de_estudio` | Case study reali per settore con metriche concrete |
| `benchmark_sector` | KPI tipici del mercato spagnolo per settore |
| `glosario_marketing` | Definizioni termini con esempi e errori comuni |

## Setup locale

Richiede Python 3.11+. Consigliato `uv`:

```bash
# Clona o estrai il progetto
cd segmenta-mcp

# Installa dipendenze (uv è 10x più veloce di pip)
uv pip install -r requirements.txt
# oppure: pip install -r requirements.txt

# Test rapido in stdio (per MCP Inspector)
python server.py

# Test in modalità HTTP (per integrazione Claude/ChatGPT)
python server.py --http
# Server raggiungibile su http://localhost:8000/mcp/
```

## Test con MCP Inspector

L'Inspector è il tool ufficiale di Anthropic per debugging MCP server.

```bash
# In un terminale
python server.py

# In un altro terminale
npx @modelcontextprotocol/inspector
# Si apre a http://localhost:5173
# Connetti a stdio: command=python args=server.py
```

Nell'Inspector vedi i 4 tool, puoi chiamarli con input di test, vedere il JSON di output.

## Connessione a Claude Desktop (test locale)

Aggiungi a `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) o `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "segmenta": {
      "command": "python",
      "args": ["/path/assoluto/a/segmenta-mcp/server.py"]
    }
  }
}
```

Riavvia Claude Desktop. Se chiedi *"che servizi offre Segmenta?"* dovrebbe chiamare il tool.

## Connessione a Claude.ai (web — Custom Connector)

Una volta deployato in produzione (es. `https://mcp.segmentamarketing.com/mcp/`):

1. Claude.ai → Settings → Connectors → Add custom connector
2. Name: `Segmenta`, URL: `https://mcp.segmentamarketing.com/mcp/`
3. Salva. Ora qualsiasi conversazione può chiamare i tool.

## Connessione a ChatGPT

Settings → Apps → Advanced Settings → Enable Developer Mode → Crea app → URL `https://mcp.segmentamarketing.com/mcp/`.

## Deploy in produzione

### Opzione 1: Oracle Cloud Always Free (target $0/mese **perpetuo** — default v1)

Stack: 1 VM ARM Ampere A1 (4 vCPU, 24GB RAM) + Docker Compose + Caddy reverse proxy + Watchtower auto-update + Tailscale per SSH.

```bash
# 1. Provision VM Oracle (Console Oracle web, ~30 min)
#    Image: Ubuntu 22.04 Minimal aarch64
#    Shape: VM.Standard.A1.Flex (4 OCPU + 24GB RAM)
#    Region: mx-queretaro-1 (Mexico Central, ~5-30ms da MX)
#    Fallback se ARM A1 capacity esaurita: mx-monterrey-1 o sa-saopaulo-1
#    Storage: 50GB boot + 100GB block (Always Free quota)

# 2. SSH iniziale + bootstrap Linux (~1h)
ssh ubuntu@<public-ip>
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl git ufw fail2ban unattended-upgrades
sudo dpkg-reconfigure --priority=low unattended-upgrades

# 3. Setup Tailscale (SSH sicuro, chiudi porta 22 pubblica)
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up --ssh
sudo ufw allow 80/tcp && sudo ufw allow 443/tcp && sudo ufw --force enable

# 4. Install Docker
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker ubuntu
newgrp docker

# 5. Clone repo + secrets
sudo mkdir -p /opt/segmenta-mcp && sudo chown ubuntu:ubuntu /opt/segmenta-mcp
cd /opt/segmenta-mcp
git clone https://github.com/segmenta-ai/segmenta-mcp.git .
cp .env.example .env
chmod 600 .env
vim .env  # popola con secrets reali

# 6. DNS A record verso IP pubblico Oracle (richiede accesso DNS Merari, BL-004)

# 7. Avvia stack
docker compose up -d

# 8. Verifica HTTPS auto via Let's Encrypt
curl -I https://mcp.segmentamarketing.com/health
# Atteso: HTTP/2 200, valid TLS cert
```

**Costo**: **$0 USD/mese perpetuo** (Oracle Always Free dichiarata permanente). Setup iniziale ~3-4h, poi manutenzione ~15 min/mese (auto-updates Linux, Watchtower auto-update container).

📖 Playbook completo step-by-step: `Docs/blueprint/09-DEPLOYMENT.md` sez. 4.4.

### Opzione 2: Railway (fallback paid se Oracle non disponibile)

```bash
# Railway → New Project → Deploy from GitHub repo
# Railway rileva il Dockerfile e fa tutto. Aggiungi dominio custom.
```

Costo tipico: **$5-$15 USD/mese**. Da usare solo se Oracle Always Free deprecato in futuro.

### Opzione 3: VPS dedicato (Hetzner / DigitalOcean)

```bash
# Stesso setup Opzione 1 (Docker Compose + Caddy), su qualsiasi VPS Linux
# Hetzner Cloud: ~€4/mese (CX22, 2 vCPU + 4GB RAM)
docker compose up -d
```

Hostinger shared **non funziona** (no endpoint persistente).

### DNS

Punta `mcp.segmentamarketing.com` al server (CNAME o A record). HTTPS **obbligatorio** per i Custom Connectors di Claude/ChatGPT.

## Struttura progetto

```
segmenta-mcp/
├── server.py              # Server FastMCP + 4 tool
├── data/
│   ├── services.json      # Catalogo servizi
│   ├── case_studies.json  # Case study (sostituire placeholder con dati reali)
│   ├── benchmarks.json    # KPI di settore
│   └── glosario.json      # Glossario termini
├── pyproject.toml
├── requirements.txt
├── Dockerfile
├── .env.example
└── README.md
```

## ⚠️ Prima di andare in produzione

I file dati contengono **placeholder verosimili ma non reali**:

- `case_studies.json` — sostituire i metric con valori verificati e ottenere consenso scritto da ogni cliente prima di renderli pubblici
- `benchmarks.json` — validare i range con dati interni Segmenta delle ultime 4-8 campagne per settore
- `services.json` — confermare i range prezzo con il team commerciale

Ogni record con `"_placeholder": true` va rivisto.

## Roadmap

### ✅ Fase 1 (questo MVP)
- 4 tool public, no auth
- Deploy HTTP su dominio custom
- Submission a Anthropic Connector Directory

### 🔜 Fase 2 — Tier 2 lead capture (milestone M2, vedi `MILESTONES.md`)
5 tool gated con OAuth 2.0 dinamico:
- `diagnostico_seo_express` — crawla un URL e restituisce 5-10 quick win, report via email
- `calcular_presupuesto` — preventivo orientativo basato su input strutturati
- `agendar_auditoria_gratuita` — prenotazione call timezone-aware MX/US/LATAM
- `solicitar_propuesta_personalizada` — brief lungo che entra nel CRM
- `consultar_disponibilidad` — calendario di slot disponibili (read-only)

### 🔜 Fase 3 — Tier 3 advanzados (milestone M4)
5 tool avanzati per retention e intelligence:
- `whatsapp_directo` — link prefill con contesto conversazione (canale principale LATAM/MX)
- `share_research` — pubblicazione su channel pubblici di richieste anonimizzate
- `analizar_competencia` — analisi competitiva live (gated, costo crediti)
- `compare_agencies` — confronto onesto Segmenta vs altre agenzie
- `obtener_caso_por_pais` — case study filtrati per país specifico

Inoltre: analytics dashboard interna, automazione 30 query baseline settimanali, A/B test descrizioni tool per massimizzare citation rate.

## Promozione del connector

Avere il server live non basta. Distribuzione:

1. **Anthropic Connector Directory** — sottometti via [anthropic.com/partners](https://anthropic.com/partners) (review 2-4 settimane)
2. **Banner sito** — su segmentamarketing.com aggiungi CTA *"Conecta Segmenta a tu Claude/ChatGPT"* con bottone one-click
3. **Blog post originale** — *"Cómo conectar Segmenta a Claude para análisis SEO automatizado"* (ranka su query GEO + insegna l'uso)
4. **GitHub pubblico** — segnale di qualità tecnica + indicizzato dagli LLM
5. **Pitch a pubblicazioni MCP-focused** — WorkOS blog, leadgen-economy, AI newsletter spagnole

## Licenza

MIT — uso libero, mantieni attribuzione.

## Contatti

- Sito: https://segmentamarketing.com
- Email: hola@segmentamarketing.com
- LinkedIn: Segmenta by Merari Montoya
