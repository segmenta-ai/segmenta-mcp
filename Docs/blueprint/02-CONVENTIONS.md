# 02 — CONVENTIONS

| Campo | Valore |
|---|---|
| **Progetto** | Segmenta MCP Server |
| **Versione documento** | 1.1 |
| **Data** | 2026-05-11 |
| **Status** | Approvato (post harmony pass M0.3) |
| **File n.** | 02 di 12 numerati |
| **Documento padre** | `00-MASTER-PLAN.md` v1.2 |
| **File correlati** | `01-ARCHITECTURE.md`, `09-DEPLOYMENT.md` |

---

## 1. Scopo del documento

Questo file definisce **come scriviamo codice, come lo organizziamo, come committiamo e come collaboriamo** sul repository Segmenta MCP. È pensato per due lettori:

1. **Claudio fra 6 mesi** che torna sul progetto dopo una pausa e ha bisogno di ritrovare lo stesso *stile* per non spaccare la coerenza.
2. **Claude Code** che lavora come pair-programmer e deve replicare le convenzioni esistenti senza creare drift.

Le convenzioni qui dentro non sono opinioni — sono *regole*. Quando una regola va contraddetta, va contraddetta esplicitamente in PR con motivazione, non sessile.

---

## 2. Lingua nel codice e nei dati

Coerentemente con D-MP-001 e D-MP-007 del MASTER-PLAN, il progetto è bilingue per principio. Le regole concrete:

### 2.1 Tabella di responsabilità linguistica

| Cosa | Lingua | Esempio |
|---|---|---|
| Documentazione `Docs/blueprint/*.md` (prosa, sezioni) | Italiano | "Questo file descrive..." |
| Identificatori Python (variabili, funzioni, classi, moduli) | Spagnolo | `obtener_servicios`, `caso_de_estudio`, `class CasoEstudio` |
| Tool `name` esposto via MCP | Spagnolo | `obtener_servicios`, `agendar_auditoria_gratuita` |
| Tool `description` esposta via MCP (vista dall'LLM) | Spagnolo (LATAM-neutral) | "Devuelve el catálogo completo de servicios..." |
| Messaggi di errore esposti all'utente finale | Spagnolo | "Servicio temporalmente no disponible" |
| Log messages (per Claudio, dev internal) | Inglese | `log.info("tool_call_completed")` |
| Commenti esplicativi nel codice (per Claudio) | Italiano | `# verifica idempotency su Redis` |
| Docstring delle funzioni Python | Spagnolo | `"""Devuelve el catálogo de servicios..."""` |
| Commit messages | Inglese | `feat(tools): add benchmark_sector with country filter` |
| Issue / PR title e body su GitHub | Inglese | "Fix rate limit calculation for OAuth tier" |
| README pubblico (`README.md` in root repo) | Spagnolo + inglese (sezioni separate) | Header inglese per Anthropic reviewers, sezione spagnola per utenti LATAM |
| Test names (function names) | Spagnolo | `def test_obtener_servicios_filtra_por_categoria():` |
| Test descriptions (docstring) | Italiano (interno) | `"""Verifica che il filtro categoria funzioni..."""` |
| Variabili d'ambiente | Inglese (SCREAMING_SNAKE_CASE) | `RESEND_API_KEY`, `CRM_WEBHOOK_URL` |
| Costanti di configurazione (env-derived) | Inglese (SCREAMING_SNAKE_CASE) | `RATE_LIMIT_TIER_1`, `JWT_ALGORITHM`, `MAX_QUERY_LENGTH` |
| Costanti di dominio (business logic) | Spagnolo (SCREAMING_SNAKE_CASE) | `IVA_MEXICO`, `CATEGORIAS_PRINCIPALES`, `MONEDAS_SOPORTADAS` |
| Slug / ID record dati JSON | Spagnolo, kebab-case lowercase | `"id": "seo-latam"`, `"id": "ferreteria-norteno-mx-2025"` |
| Slug glosario | Spagnolo, snake_case lowercase (per uniformità con identificatori Python) | `"id": "tasa_de_conversion"`, `"id": "embudo_de_ventas"` |
| File JSON dati (`data/*.json`) | Spagnolo (chiavi e valori) | `"servicios": [{"nombre": "SEO LATAM", ...}]` |
| Schema fields Pydantic | Spagnolo | `class Servicio(BaseModel): nombre: str` |
| Branch names | Inglese (kebab-case) | `feat/add-benchmark-tool`, `fix/oauth-redirect` |

### 2.2 Razionale

- **Identificatori in spagnolo** allineano col mercato target. Se domani assumiamo un dev LATAM, il codice è leggibile per loro. Se serve presentare il repo a un cliente messicano, è coerente.
- **Log e commit in inglese** sono per Claudio e per gli strumenti — GitHub, Fly.io, log aggregator. Inglese standard tecnico.
- **Documentazione blueprint in italiano** è per Claudio — lingua nativa, massima precisione concettuale.
- **Tool descriptions in ES LATAM-neutral** sono per l'LLM: visto da Claude/ChatGPT, deve sembrare un'API spagnola autentica. *Mai inserire termini italiani nelle descriptions visibili agli utenti finali — quello rivelerebbe l'origine del codice.*

### 2.3 Anti-pattern espliciti

❌ **Mischiare lingue dentro lo stesso identificatore**:
```python
# WRONG
def get_servicios(): ...
def obtener_services(): ...

# RIGHT
def obtener_servicios(): ...
```

❌ **Tool description con termini italiani**:
```python
# WRONG
@mcp.tool
def obtener_servicios(...):
    """Restituisce il catalogo dei servizi..."""  # italiano leak

# RIGHT
@mcp.tool
def obtener_servicios(...):
    """Devuelve el catálogo de servicios..."""
```

❌ **Commit message in spagnolo**:
```
# WRONG
git commit -m "feat: agregar herramienta de benchmark"

# RIGHT
git commit -m "feat(tools): add benchmark_sector tool"
```

❌ **Variabili d'ambiente in spagnolo**:
```bash
# WRONG
CLAVE_API_RESEND=xxx

# RIGHT
RESEND_API_KEY=xxx
```

---

## 3. Struttura del repository

### 3.1 Layout completo

```
segmenta-mcp/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml                    # Lint + test + type check su PR
│   │   ├── deploy-staging.yml        # Auto-deploy on merge to develop
│   │   └── deploy-production.yml     # Auto-deploy on merge to main
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   ├── PULL_REQUEST_TEMPLATE.md
│   ├── dependabot.yml
│   └── CODEOWNERS
├── .vscode/                          # Settings condivise (gitignored individual)
│   ├── settings.json
│   └── extensions.json
├── Docs/
│   └── blueprint/                    # I 12 file numerati + MILESTONES + SESSION-STATE
│       ├── 00-MASTER-PLAN.md
│       ├── 01-ARCHITECTURE.md
│       └── ...
├── src/
│   └── segmenta_mcp/
│       ├── __init__.py               # Versione: __version__ = "0.1.0"
│       ├── server.py                 # Entry point FastMCP, orchestrazione
│       ├── config.py                 # Settings via pydantic-settings
│       │
│       ├── transport/                # Layer 1
│       │   ├── __init__.py
│       │   ├── routes.py             # Custom routes (/health, /metrics, /)
│       │   └── middleware.py         # CORS, request_id, logging context
│       │
│       ├── auth/                     # Layer 2
│       │   ├── __init__.py
│       │   ├── oauth.py              # OAuth 2.0 dynamic registration
│       │   ├── jwt_handler.py        # Validation + signing
│       │   ├── magic_link.py         # Generation + email send
│       │   └── rate_limit.py         # Redis-backed sliding window
│       │
│       ├── tools/                    # Layer 3
│       │   ├── __init__.py
│       │   ├── tier1/                # Público
│       │   │   ├── __init__.py
│       │   │   ├── obtener_servicios.py
│       │   │   ├── caso_de_estudio.py
│       │   │   ├── benchmark_sector.py
│       │   │   └── glosario_marketing.py
│       │   ├── tier2/                # Lead capture
│       │   │   ├── __init__.py
│       │   │   ├── diagnostico_seo_express.py
│       │   │   ├── calcular_presupuesto.py
│       │   │   ├── agendar_auditoria_gratuita.py
│       │   │   ├── solicitar_propuesta_personalizada.py
│       │   │   └── consultar_disponibilidad.py
│       │   └── tier3/                # Avanzado
│       │       ├── __init__.py
│       │       ├── whatsapp_directo.py
│       │       ├── share_research.py
│       │       ├── analizar_competencia.py
│       │       ├── compare_agencies.py
│       │       └── obtener_caso_por_pais.py
│       │
│       ├── domain/                   # Layer 4 — pure logic
│       │   ├── __init__.py
│       │   ├── models.py             # Pydantic models condivisi
│       │   ├── filters.py            # Filtri case study, benchmark
│       │   ├── presupuesto.py        # Calcolo preventivo
│       │   ├── crawler.py            # Logica diagnostico SEO (parsing)
│       │   └── formatters.py         # Output formatting per LLM
│       │
│       ├── data/                     # Layer 5 — caricamento dati statici
│       │   ├── __init__.py
│       │   ├── loader.py             # Caricamento JSON con validazione
│       │   └── cache.py              # In-memory cache invalidation
│       │
│       ├── integrations/             # Layer 5 — chiamate API esterne
│       │   ├── __init__.py
│       │   ├── booking.py            # Cal.com / Calendly (interface unificata)
│       │   ├── crm.py                # HubSpot / Pipedrive
│       │   ├── email.py              # Resend / SendGrid
│       │   ├── whatsapp.py           # Twilio / 360dialog
│       │   └── circuit_breaker.py    # Implementazione manuale Redis-backed
│       │
│       └── observability/
│           ├── __init__.py
│           ├── logging.py            # structlog config
│           └── metrics.py            # Prometheus collectors
│
├── data/                             # JSON dati (in repo, versionati)
│   ├── services.json
│   ├── case_studies.json
│   ├── benchmarks.json
│   └── glosario.json
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                   # Fixtures pytest condivise
│   ├── unit/
│   │   ├── test_domain_filters.py
│   │   ├── test_domain_presupuesto.py
│   │   └── test_data_loader.py
│   ├── integration/
│   │   ├── test_tools_tier1.py
│   │   ├── test_tools_tier2.py
│   │   └── test_oauth_flow.py
│   └── fixtures/                     # JSON di test, MAI dati reali clienti
│       ├── services_test.json
│       └── case_studies_test.json
│
├── scripts/
│   ├── validate_data.py              # Valida JSON contro schema
│   ├── seed_redis.py                 # Setup Redis locale per dev
│   ├── generate_baseline_queries.py  # Setup 30 query baseline
│   └── test_30_queries.py            # Esegue le 30 query e logga risultati
│
├── .env.example
├── .gitignore
├── .python-version                   # 3.12
├── Dockerfile
├── docker-compose.yml                # Per dev locale: server + Redis
├── pyproject.toml                    # Configurazione completa progetto
├── uv.lock                           # Lock file dipendenze (uv)
├── README.md                         # Pubblico, per Anthropic + utenti
├── CHANGELOG.md                      # Keep a Changelog format
├── CONTRIBUTING.md                   # Come contribuire (anche per Claudio futuro)
├── LICENSE                           # MIT
├── SECURITY.md                       # Come segnalare vulnerabilità
└── CLAUDE.md                         # Istruzioni per Claude Code
```

### 3.2 Convenzioni di naming file

- **Moduli Python**: `snake_case.py`. Mai CamelCase, mai kebab-case.
- **JSON dati**: `snake_case.json` plurale per collezioni (`services.json`, `case_studies.json`).
- **Markdown blueprint**: `NN-NOME-MAIUSCOLO.md` con dash (es. `04-TOOLS-TIER1.md`).
- **Markdown root**: `MAIUSCOLO.md` standard GitHub (`README.md`, `CHANGELOG.md`, `LICENSE`).
- **Test files**: `test_*.py` (pytest auto-discovery default).
- **Fixture files**: `*_test.json` (suffisso `_test`, mai prefisso, evita confusione con file production).

### 3.3 File `CLAUDE.md`

File speciale in root del repo. Contiene istruzioni *per Claude Code* quando lavora sul progetto. Letto automaticamente all'inizio di ogni sessione. Convenzioni di Claudio per altri progetti applicate qui:

```markdown
# Istruzioni per Claude Code — Segmenta MCP

## Lingua
- Codice: identificatori in spagnolo, log/commit in inglese, docstring in spagnolo.
- Discussione con Claudio: italiano.

## Workflow
- Mai modificare `Docs/blueprint/*.md` senza richiesta esplicita.
- Sempre creare branch da `develop`, mai da `main`.
- Sempre eseguire `uv run pytest && uv run ruff check && uv run mypy src/` prima di proporre PR.

## Decisioni
- Tutte le decisioni canoniche del blueprint sono LOCKED. Se trovi conflitto, segnala in PR description, non modificare unilateralmente.
- Per dubbi su scope: consulta `00-MASTER-PLAN.md` sezione 4 (Scope) e 5 (Non-goals).

## File reference
- Architettura: `Docs/blueprint/01-ARCHITECTURE.md`
- Convenzioni: questo file (root) + `Docs/blueprint/02-CONVENTIONS.md`
- Spec tool: `Docs/blueprint/04/05/06-TOOLS-TIER*.md`
```

---

## 4. Coding style Python

### 4.1 Versione Python e features

- **Python 3.12** è il minimo. Nessun fallback per versioni precedenti.
- `from __future__ import annotations` in cima a **ogni** file `.py`. Permette type hints come stringhe (forward references gratuite).
- Type hints **obbligatori** su signature pubbliche (parametri + return). Le funzioni interne possono ometterli ma è raccomandato comunque.
- Usare le sintassi moderne: `list[str]` non `List[str]`, `dict[str, int]` non `Dict[str, int]`, `str | None` non `Optional[str]`.

### 4.2 Formatter e linter

| Tool | Versione min | Configurazione | Quando |
|---|---|---|---|
| **ruff** | 0.5.0 | `pyproject.toml` `[tool.ruff]` | Format + lint, pre-commit + CI |
| **mypy** | 1.10 | `pyproject.toml` `[tool.mypy]` (strict mode) | Type check, CI |
| **pytest** | 8.0 | `pyproject.toml` `[tool.pytest.ini_options]` | Test, CI + manual |

Niente `black`, niente `isort`, niente `flake8` separati: ruff li sostituisce tutti con configurazione unificata.

### 4.3 Configurazione ruff (estratto)

```toml
[tool.ruff]
line-length = 100             # 88 è troppo stretto per docstring spagnoli
target-version = "py312"
src = ["src", "tests"]

[tool.ruff.lint]
select = [
    "E", "W",       # pycodestyle
    "F",            # pyflakes
    "I",            # isort
    "N",            # pep8-naming
    "UP",           # pyupgrade (modernizza sintassi)
    "B",            # flake8-bugbear (anti-pattern)
    "C4",           # flake8-comprehensions
    "SIM",          # flake8-simplify
    "ARG",          # unused arguments
    "PTH",          # pathlib over os.path
    "ERA",          # eradicate commented code
    "RUF",          # ruff-specific
]
ignore = [
    "E501",  # line too long (gestito da formatter)
]

[tool.ruff.lint.per-file-ignores]
"tests/*" = ["ARG"]     # Test fixtures spesso unused arg

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

### 4.4 Configurazione mypy (estratto)

```toml
[tool.mypy]
python_version = "3.12"
strict = true
warn_return_any = true
warn_unused_ignores = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
no_implicit_optional = true
check_untyped_defs = true
plugins = ["pydantic.mypy"]

[[tool.mypy.overrides]]
module = "fastmcp.*"
ignore_missing_imports = true   # Se mypy non ha stub per FastMCP

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false   # Test pi-rilassati
```

### 4.5 Convenzioni di naming

| Cosa | Convenzione | Esempio |
|---|---|---|
| Variabili e funzioni | `snake_case` (spagnolo) | `obtener_servicios`, `caso_de_estudio` |
| Costanti modulo | `SCREAMING_SNAKE_CASE` (inglese o spagnolo) | `MAX_QUERY_LENGTH = 500`, `RATE_LIMIT_TIER_1 = 60` |
| Classi | `PascalCase` (spagnolo) | `class Servicio`, `class CasoEstudio` |
| Type aliases | `PascalCase` (spagnolo) | `Categoria = Literal["seo", "sem", ...]` |
| Privati / interni | Prefisso `_` | `def _hash_idempotency_key(...)` |
| Booleans | Prefisso `es_`, `tiene_`, `puede_` | `es_publico: bool`, `tiene_consentimiento: bool` |
| Funzioni async | Stesso del sync, niente `async_` prefix | `async def fetch_calcom_slot(...)` |
| Fixture pytest | `fixture_*` o nome descrittivo | `@pytest.fixture def servicios_validos():` |

### 4.6 Pattern preferiti

**Pydantic v2 per ogni modello dati**:
```python
from pydantic import BaseModel, Field

class Servicio(BaseModel):
    """Modelo de servicio del catálogo Segmenta."""

    id: str = Field(..., description="Identificador único, slug")
    nombre: str = Field(..., min_length=1, max_length=100)
    categoria: Categoria
    precio_usd: tuple[int, int] | None = Field(
        default=None,
        description="Rango (min, max) en USD",
    )
```

**Async-first per I/O**:
```python
# Tutte le funzioni di integrazione sono async.
# Per chiamate sincrone in contesti Pydantic/FastMCP, wrappare con asyncio.

async def fetch_calcom_slot(...) -> dict: ...
async def post_crm_webhook(...) -> bool: ...
```

**Dependency injection lightweight via `config`**:
```python
# config.py espone settings globali come singleton.
# I moduli importano config e leggono settings lazy.
from segmenta_mcp.config import settings

async def send_email(...):
    api_key = settings.RESEND_API_KEY  # validato all'avvio, mai None qui
```

**Mai global mutable state**:
```python
# WRONG
CACHED_SERVICES = []  # mutato runtime

# RIGHT
class CacheManager:
    def __init__(self): self._services = []
    def get_services(self) -> list[Servicio]: ...
```

### 4.7 Docstring style

Docstring in spagnolo (per allineamento con tool descriptions visibili agli LLM). Stile Google compatto:

```python
async def obtener_servicios(
    categoria: Categoria | None = None,
    pais: Pais | None = None,
) -> list[Servicio]:
    """Devuelve el catálogo de servicios filtrado opcionalmente.

    Args:
        categoria: Filtra por categoría de servicio. Si None, todas las categorías.
        pais: Filtra por país de operación. Si None, sin filtro geográfico.

    Returns:
        Lista de Servicio. Lista vacía si ningún servicio coincide.

    Raises:
        DataNotLoadedError: Si los datos JSON no fueron cargados al startup.
    """
```

### 4.8 Anti-pattern esplicitamente vietati

❌ **Wildcards di import**: `from foo import *`. Mai. Sempre import espliciti.

❌ **Mutable default args**: `def f(items=[])`. Mai. Usare `None` + check.

❌ **`print()` in codice production**: usare logger. `print` solo in script `scripts/`.

❌ **Eccezioni generiche `except Exception`**: catch specifici. Se proprio serve generico, sempre re-raise dopo logging.

❌ **`# type: ignore` senza commento**: sempre giustificare con `# type: ignore[error-code] # reason`.

❌ **Commenti che ripetono il codice**: il commento spiega *perché*, non *cosa*.
```python
# WRONG
# Itera sulla lista
for s in servicios:

# RIGHT
# Servicios filtrati per categoria attiva — esclusione hard-coded di "legacy"
# perché non più offerti dopo Q1 2026.
for s in servicios_attivi:
```

❌ **Funzioni > 50 linee**: refactor in funzioni più piccole.

❌ **File > 400 linee** (eccetto JSON dati): split in moduli logicamente coesi.

---

## 5. Git workflow

### 5.1 Branch strategy

Modello: **GitHub Flow leggermente esteso** con `develop` per staging.

```
main         ──▶ deploy automatico in production
develop      ──▶ deploy automatico in staging
feat/*       ──▶ branch corti, vita 1-7 giorni, merge in develop via PR
fix/*        ──▶ idem
chore/*      ──▶ idem (aggiornamenti dipendenze, refactoring)
docs/*       ──▶ idem (modifiche solo a Docs/, README, CHANGELOG)
hotfix/*     ──▶ branch da main per emergency fixes, merge in main + develop
```

### 5.2 Convenzioni branch name

Pattern: `<tipo>/<descrizione-kebab-case>`.

Esempi:
- `feat/add-benchmark-tool`
- `feat/oauth-magic-link`
- `fix/rate-limit-redis-key-collision`
- `chore/bump-fastmcp-3.3`
- `docs/clarify-tier-system-intro`
- `hotfix/critical-cors-misconfiguration`

Mai con username, mai con numeri di issue (l'issue va nel commit/PR body, non nel branch name).

### 5.3 Conventional Commits (D-MP-010)

Formato:
```
<tipo>(<scope>): <descrizione breve in imperativo, lowercase>

[corpo opzionale, spiega *perché* — il *cosa* è nel diff]

[footer opzionale: BREAKING CHANGE / Refs #issue / Co-authored-by:]
```

**Tipi accettati**:

| Tipo | Quando usare |
|---|---|
| `feat` | Nuova feature visibile al consumatore (nuovo tool, nuovo endpoint, etc.) |
| `fix` | Bug fix |
| `docs` | Solo documentazione |
| `style` | Cambio formattazione (no logica) |
| `refactor` | Refactoring (no nuova feature, no bug fix) |
| `perf` | Miglioramento performance |
| `test` | Aggiunta o modifica test |
| `build` | Sistema di build, dipendenze |
| `ci` | Configurazione CI/CD |
| `chore` | Manutenzione varia (env, settings) |
| `revert` | Reverte commit precedente |

**Scope tipici**:
- `tools`: cambia un tool MCP
- `auth`: layer auth
- `data`: file JSON dati
- `domain`: logica business
- `integrations`: chiamate esterne
- `transport`: routing, middleware
- `obs`: logging, metrics

**Esempi corretti**:
```
feat(tools): add benchmark_sector tool with country filter

The new tool exposes market KPIs (CPC, CPL, conversion rates) per
sector and country, sourced from data/benchmarks.json. Validates
country against allowed enum and falls back to nearest available.

Refs #14
```

```
fix(auth): correct rate limit Redis key TTL after token refresh

Previously the key TTL was reset on token refresh, allowing users to
exceed the 10/min limit by refreshing aggressively.
```

```
docs(blueprint): add 02-CONVENTIONS.md initial draft
```

```
chore(deps): bump fastmcp from 3.2.4 to 3.3.0
```

**Anti-pattern**:
```
# WRONG
update stuff
fix bug
WIP
asdf
Merge branch 'develop' into feat/something
```

### 5.4 Squash merge (D-MP-010)

**Tutte** le PR vengono mergiate in `develop` (o `main`, per hotfix) via **squash merge**. Il messaggio del squash deve seguire Conventional Commits — GitHub lo precompila col title della PR, quindi il *PR title* deve già essere conventional commit.

Linear history su `main` e `develop`. Niente merge commits.

### 5.5 PR template

`.github/PULL_REQUEST_TEMPLATE.md`:

```markdown
## What

<breve descrizione del cambiamento, 1-3 frasi>

## Why

<motivazione, link a issue / decisione blueprint se rilevante>

## How

<scelte tecniche notevoli, alternative scartate, trade-off>

## Testing

- [ ] Unit test aggiunti / aggiornati
- [ ] Integration test verificati
- [ ] `uv run pytest` passa localmente
- [ ] `uv run ruff check` passa
- [ ] `uv run mypy src/` passa
- [ ] Testato manualmente in local con MCP Inspector (se applicabile)

## Blueprint

- [ ] Modifiche compatibili con `00-MASTER-PLAN.md` scope/non-goals
- [ ] Modifiche compatibili con `01-ARCHITECTURE.md` decisioni canoniche
- [ ] Se nuova decisione tecnica: aggiunta a `01-ARCHITECTURE.md` sez. 12 o sez. 13

## Refs

Closes #<issue>
```

### 5.6 Branch protection

Configurazione GitHub repo:

**Su `main`**:
- Required reviews: 1 (anche se solo Claudio approva — disciplina anti-merge accidentale)
- Required status checks: `ci` (lint + test + type check), `deploy-staging` (must succeed in staging first)
- Require linear history: yes
- Allow force push: no
- Allow deletion: no

**Su `develop`**:
- Required status checks: `ci`
- Allow force push: no

Il "1 required review" può essere fatto da Claude Code o Claudio stesso (auto-approval delle proprie PR è permesso ma sconsigliato). Lo scopo non è gatekeeping, è freno alla velocità impulsiva.

### 5.7 Hotfix flow

In caso di bug critico in produzione:

```
1. git checkout -b hotfix/critical-x main
2. <fix minimale>
3. PR su main: review veloce, merge squash
4. main → auto-deploy production
5. PR di "back-merge" hotfix in develop: subito dopo
```

Hotfix è l'unica eccezione al flow `develop → main`.

---

## 6. Tooling locale di sviluppo

### 6.1 Setup ambiente

Il progetto usa `uv` (D-A-021) come gestore pacchetti. Setup completo:

```bash
# 1. Clona repo
git clone https://github.com/<owner>/segmenta-mcp.git
cd segmenta-mcp

# 2. Installa uv (una tantum)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 3. Crea virtualenv e installa dipendenze
uv sync                                  # legge uv.lock, crea .venv

# 4. Setup pre-commit
uv run pre-commit install

# 5. Avvia Redis locale via docker-compose
docker compose up -d redis

# 6. Configura .env
cp .env.example .env
# edit .env con i propri valori (Resend test API key, ecc.)

# 7. Run server in dev mode (stdio per MCP Inspector)
uv run python -m segmenta_mcp.server

# 8. (alternativa) Run in HTTP mode
uv run python -m segmenta_mcp.server --http
```

### 6.2 Comandi quotidiani

```bash
# Test
uv run pytest                                   # tutti i test
uv run pytest tests/unit/ -v                    # solo unit
uv run pytest -k test_obtener_servicios         # match nome test
uv run pytest --cov=src/segmenta_mcp            # con coverage

# Lint + format
uv run ruff format src/ tests/                  # autoformat
uv run ruff check src/ tests/                   # solo check
uv run ruff check --fix src/                    # autofix

# Type check
uv run mypy src/segmenta_mcp/

# Validazione dati JSON
uv run python scripts/validate_data.py

# 30 query baseline (manuale, in M1+)
uv run python scripts/test_30_queries.py
```

### 6.3 Pre-commit hooks

`.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: ruff-format
        name: ruff format
        entry: uv run ruff format
        language: system
        types: [python]

      - id: ruff-check
        name: ruff check
        entry: uv run ruff check --fix
        language: system
        types: [python]

      - id: mypy
        name: mypy
        entry: uv run mypy src/
        language: system
        pass_filenames: false
        types: [python]

      - id: validate-json
        name: validate data JSON
        entry: uv run python scripts/validate_data.py
        language: system
        pass_filenames: false
        files: ^data/.*\.json$

      - id: no-real-data-in-tests
        name: no real client data in test fixtures
        entry: bash -c 'grep -L "_test_fixture" tests/fixtures/*.json | xargs -I{} echo "Missing _test_fixture marker: {}" >&2; ! grep -L "_test_fixture" tests/fixtures/*.json | grep -q .'
        language: system
        files: ^tests/fixtures/.*\.json$
```

L'ultimo hook è una guardia: **mai mettere dati reali clienti nei fixtures di test**. Coerente con SR-004 di MASTER-PLAN.

### 6.4 Editor settings (raccomandazione)

VS Code `.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": ".venv/bin/python",
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.organizeImports": "explicit"
    }
  },
  "python.analysis.typeCheckingMode": "strict",
  "files.exclude": {
    "**/__pycache__": true,
    "**/.pytest_cache": true,
    ".mypy_cache": true,
    ".ruff_cache": true
  }
}
```

`.vscode/extensions.json` (raccomandate):

```json
{
  "recommendations": [
    "charliermarsh.ruff",
    "ms-python.python",
    "ms-python.mypy-type-checker",
    "tamasfe.even-better-toml",
    "redhat.vscode-yaml"
  ]
}
```

---

## 7. Testing

### 7.1 Tipi di test

| Tipo | Scope | Velocità | Quando girarli |
|---|---|---|---|
| **Unit** | Funzioni pure di Layer 4 (domain) | < 1ms each | Pre-commit, CI |
| **Integration** | Tool completi end-to-end con Redis + mock integrazioni esterne | < 100ms each | CI |
| **Contract** | Schema MCP esposto, OAuth metadata | < 50ms each | CI |
| **Smoke** | Server live, chiamata reale a 1-2 tool Tier 1 | < 5s | Post-deploy staging/production |
| **E2E manuale** | MCP Inspector + Claude Desktop con server locale | minutes | Pre-merge per feature critiche |

### 7.2 Coverage target

| Layer | Soglia | Target |
|---|---|---|
| Domain (Layer 4) | 90% | 95% |
| Tools (Layer 3) | 80% | 90% |
| Integrations (Layer 5) | 70% | 80% |
| Auth (Layer 2) | 85% | 95% |
| Transport (Layer 1) | 60% | 70% |
| **Overall** | 80% | 88% |

Coverage misurata con `pytest-cov`. CI fallisce se overall scende sotto soglia. Soglia per layer è guida, non hard-block (per evitare game).

### 7.3 Fixture management

- Fixture in `tests/fixtures/` sono **JSON di test**, mai dati reali clienti.
- Ogni fixture file ha un campo top-level `"_test_fixture": true` (verificato dal pre-commit hook).
- Fixture condivise globalmente in `tests/conftest.py` come `pytest.fixture`.
- Fixture pesanti (Redis container, mock booking server) sono `scope="session"`.

### 7.4 Naming dei test

```python
# Pattern: test_<funzione>_<scenario>_<expected_outcome>
def test_obtener_servicios_sin_filtro_devuelve_todos(): ...
def test_obtener_servicios_con_categoria_invalida_lanza_validation_error(): ...
def test_caso_de_estudio_con_pais_no_disponible_devuelve_lista_vacia(): ...
def test_oauth_token_expirado_devuelve_401(): ...
```

Test names sono in spagnolo (allineato col codice). Docstring opzionale in italiano per spiegare il setup complesso.

### 7.5 Mock e stub

- **Mai** chiamare API reali esterne nei test (anche staging API).
- Usare `pytest-httpx` per mockare httpx calls a Cal.com, CRM, Resend.
- Redis: usare container Docker reale (via `pytest-docker` o session fixture), non `fakeredis`. Il comportamento reale di TTL e atomic ops è troppo importante per mockarlo.
- FastMCP server: testare via `TestClient` di Starlette con app reale, non mock dell'intero framework.

---

## 8. Documentazione

### 8.1 Tre tipologie di documentazione

| Tipologia | Cosa | Dove | Per chi |
|---|---|---|---|
| **Blueprint** | Vision, scope, decisioni, architettura | `Docs/blueprint/*.md` | Claudio (interno) |
| **Pubblica** | Come usare il MCP, come connetterlo, cosa offre | `README.md`, landing page web | Utenti finali, Anthropic reviewer |
| **Sviluppo** | Come contribuire, come testare, come deployare | `CONTRIBUTING.md`, docstring | Dev (Claudio + Claude Code) |

Ogni tipologia ha audience e tono distinti. **Mai mischiarli nello stesso file**.

### 8.2 README.md (root repo)

Struttura:

```markdown
# Segmenta MCP Server

[Banner badges: build, license, MCP version]

> Servidor MCP de Segmenta Marketing — agencia digital LATAM/MX/US/ES.

## What is this?
[2-3 frasi inglese, per Anthropic reviewers e dev anglo]

## ¿Qué es esto?
[2-3 frasi spagnolo, per pubblico LATAM]

## Quick start
[Come connettere a Claude / ChatGPT in 30 secondi]

## Available tools
[Lista 14 tool con 1 riga di descrizione each]

## Privacy & legal
[Link a privacy policy, license MIT]

## For developers
[Link a CONTRIBUTING.md]

## Contact
[Email Segmenta]
```

### 8.3 CHANGELOG.md

Formato [Keep a Changelog](https://keepachangelog.com/) + SemVer:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Tool `benchmark_sector` with country filter (#14)

### Changed
- ...

### Fixed
- ...

## [0.2.0] - 2026-06-15

### Added
- Tier 2 tools: `agendar_auditoria_gratuita`, `diagnostico_seo_express`
- OAuth 2.0 dynamic registration

## [0.1.0] - 2026-05-25

Initial public release with 4 Tier 1 tools.
```

Aggiornato in ogni PR rilevante (entry sotto `[Unreleased]`). Release version (es. `0.2.0`) creata insieme al tag Git.

---

## 9. Workflow con Claude Code

Sezione dedicata al modo in cui Claude Code (l'assistente IDE-integrato) collabora sul progetto. Pattern consolidato dai progetti Keeper, Chirsan, Numely.

### 9.1 Loop standard

```
1. READ — Claude Code legge file rilevanti (blueprint, codice esistente, test esistenti)
2. PLAN — propone piano di lavoro a Claudio in chat (no codice ancora)
3. ACT — implementa, scrive test, esegue lint+test localmente
4. VERIFY — verifica che tutti i check passino
5. RECORD — apre PR con template compilato + aggiorna CHANGELOG
```

Claude Code **non procede oltre PLAN senza approvazione di Claudio**, salvo task triviali (typo fix, formatting).

### 9.2 Cose che Claude Code NON deve fare

- ❌ Modificare file in `Docs/blueprint/*.md` senza richiesta esplicita.
- ❌ Cambiare decisioni canoniche del blueprint (sez. 12 di `00-MASTER-PLAN.md` o `01-ARCHITECTURE.md`).
- ❌ Mergeare PR autonomamente.
- ❌ Pushare direttamente su `main` o `develop`.
- ❌ Aggiungere nuove dipendenze senza giustificazione + check licenze.
- ❌ Inserire dati reali clienti in test fixture o codice.
- ❌ Disabilitare type check, lint, o test "temporaneamente".
- ❌ Creare nuovi tool MCP senza che siano specificati in `04/05/06-TOOLS-TIER*.md`.

### 9.3 Cose che Claude Code DEVE fare

- ✅ Leggere `CLAUDE.md` all'inizio di ogni sessione.
- ✅ Eseguire lint + test prima di proporre PR.
- ✅ Compilare il PR template completamente.
- ✅ Aggiornare `CHANGELOG.md` per ogni feature/fix significativo.
- ✅ Segnalare in PR description se trova un'incongruenza nei blueprint (senza correggerla).
- ✅ Chiedere a Claudio prima di refactoring strutturale (cambio layer, spostamento moduli).

### 9.4 Sintassi per richieste a Claude Code

Convenzioni che Claudio usa parlando con Claude Code, ricorrenti in altri progetti:

- `READ <file>` → Claude legge e riassume
- `PLAN <task>` → Claude propone piano, no codice
- `IMPLEMENT <task>` → Claude esegue piano già concordato
- `REVIEW <PR/file>` → Claude critica, non modifica
- `FIX <issue>` → Claude implementa fix completo
- `EXPLAIN <area>` → Claude spiega senza modificare

---

## 10. Politica dipendenze

### 10.1 Aggiunta nuove dipendenze

Prima di aggiungere una dipendenza, verificare:

- [ ] **Necessità reale**: la libreria fa qualcosa che impiegheremmo > 4h a riscrivere male?
- [ ] **Mantenuta**: ultimo release < 12 mesi, > 50 stars su GitHub.
- [ ] **Licenza compatibile**: MIT, BSD-3, Apache-2.0. **No** AGPL, GPL-3, SSPL, BUSL.
- [ ] **Sicurezza**: nessuna CVE aperta non risolta su Snyk / OSV.
- [ ] **Footprint**: < 50 MB installato (eccetto ML/data libs giustificate).
- [ ] **Trasporto**: niente dipendenze che pullano gigabyte di binari (es. `tensorflow`, `torch`) — se servisse, valutare API esterna.

Aggiunta sempre via PR dedicata `chore(deps): add <package>`, con motivazione nel body.

### 10.2 Aggiornamento dipendenze

- **Dependabot** abilitato su GitHub, configurato per aprire PR settimanali per:
  - Patch updates: auto-merge se CI passa.
  - Minor updates: review manuale Claudio.
  - Major updates: review manuale + check changelog upstream.

- **Critical security patches**: PR aperta entro 24h, mergeata entro 48h.

`.github/dependabot.yml`:

```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
    open-pull-requests-limit: 5
    groups:
      patch-updates:
        update-types: ["patch"]
    labels:
      - "dependencies"

  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "monthly"
```

### 10.3 Lock file

`uv.lock` è committato. Garantisce riproducibilità tra dev, CI, deploy.

Mai installare con `uv pip install <pkg>` ad-hoc — sempre `uv add <pkg>` o edit di `pyproject.toml` + `uv lock`.

---

## 11. Versioning del server

### 11.1 SemVer (D-MP-011)

`MAJOR.MINOR.PATCH`:
- **MAJOR**: breaking change in tool schema o protocollo MCP supportato.
- **MINOR**: nuovo tool, nuovo parametro opzionale, miglioramento non-breaking.
- **PATCH**: bug fix, performance, refactoring interno.

Versione vive in `src/segmenta_mcp/__init__.py`:

```python
__version__ = "0.2.0"
```

E sincronizzata con `pyproject.toml`. Script `scripts/bump_version.py` automatizza l'update di entrambi.

### 11.2 Tag Git

Ogni release production ha tag `v<version>`:
```bash
git tag -a v0.2.0 -m "Release 0.2.0: Tier 2 tools"
git push origin v0.2.0
```

GitHub Action su tag pubblica release page con CHANGELOG estratto.

### 11.3 Versione 0.x vs 1.0

Durante M1-M2: `0.x` (pre-stable). Breaking change accettati (raro, comunicati in release notes).

`1.0.0` raggiunta quando:
- Tutti i criteri di successo "Soglia" di `00-MASTER-PLAN.md` sez. 8 sono met.
- Listing nel Connector Directory di Anthropic approvato.
- 30 giorni consecutivi di uptime > 99.5%.

Da `1.0.0` in poi: breaking change solo in MAJOR bump, comunicati 30 giorni prima.

---

## 12. Decisioni canoniche (locked)

| ID | Decisione | Motivazione |
|---|---|---|
| **D-C-001** | Identificatori Python in spagnolo, log/commit in inglese, prosa blueprint in italiano, tool descriptions ES LATAM-neutral | Allineamento mercato target + dev workflow + leggibilità Claudio. |
| **D-C-002** | `ruff` come unico formatter+linter (niente black/isort/flake8) | Tool moderno unificato, 10x più veloce, configurazione singola. |
| **D-C-003** | `mypy` strict mode | Disciplina di un solo dev: typing è il safety net. |
| **D-C-004** | GitHub Flow esteso con `develop` per staging | Workflow semplice, due ambienti chiari, no GitFlow complicazioni. |
| **D-C-005** | Conventional Commits + squash merge sempre | Standard, history linear leggibile, GitHub PR title diventa commit message. |
| **D-C-006** | Branch protection su `main` con CI required | Disciplina anti-merge accidentale anche per dev solitario. |
| **D-C-007** | `uv` come gestore pacchetti (no pip/poetry diretti) | Velocità, lock file robusto, allineato con altri progetti Claudio. |
| **D-C-008** | Pre-commit hooks obbligatori (ruff + mypy + JSON validation + no-real-data check) | Catch errori prima del push, evita CI failure prevenibili. |
| **D-C-009** | Pydantic v2 per tutti i modelli dati | Type safety, validazione automatica, schema JSON gratuito. |
| **D-C-010** | Async-first per I/O, sync solo per pure functions | Coerente con FastMCP/Starlette. |
| **D-C-011** | Test fixture mai con dati reali clienti, marker `_test_fixture: true` obbligatorio | Coerente con SR-004 MASTER-PLAN. |
| **D-C-012** | Coverage minimo 80% overall, 90% domain layer | Qualità misurabile, evita regression. |
| **D-C-013** | Mock httpx via `pytest-httpx`, mai chiamate reali in test | Test deterministici, no flakiness, no costi API. |
| **D-C-014** | Documentazione tri-livello: blueprint (interno) + README (pubblico) + CONTRIBUTING (dev) | Audience separati = chiarezza. |
| **D-C-015** | CHANGELOG aggiornato in ogni PR, formato Keep a Changelog | Tracciabilità release, comunicazione utenti. |
| **D-C-016** | SemVer per il server, tag Git per release production | Standard, GitHub releases automatiche. |
| **D-C-017** | Dependabot abilitato, patch auto-merge, minor/major review manuale | Sicurezza + manutenzione minimo overhead. |
| **D-C-018** | File `CLAUDE.md` in root con istruzioni per Claude Code | Pattern consolidato dai progetti Claudio precedenti. |
| **D-C-019** | Loop READ-PLAN-ACT-VERIFY-RECORD per Claude Code | Pattern consolidato Keeper v2. |
| **D-C-020** | Niente Wildcards di import, mutable defaults, generic excepts | Anti-pattern espliciti, controllati da ruff. |
| **D-C-021** | File Python max 400 linee, funzioni max 50 linee (eccetto JSON dati) | Leggibilità, refactor anticipato. |

---

## 13. Decisioni aperte

| ID | Decisione | Bloccare entro | Owner |
|---|---|---|---|
| **DECISION-OPEN-C-001** | Coverage soglia "hard fail" su CI: 80% overall hard, o solo warn? | M1 | Claudio |
| **DECISION-OPEN-C-002** | Auto-merge dependabot patch: SI o richiede review umana? | M1 | Claudio |
| **DECISION-OPEN-C-003** | Includere `bandit` o `semgrep` per security scanning automatico in CI | M3 | Claudio |
| **DECISION-OPEN-C-004** | Adottare `commitizen` per assistere il commit conventional, o lasciare manuale | M2 | Claudio |
| **DECISION-OPEN-C-005** | Se serve l'inglese in più punti del codice (per dev LATAM): valutare se restano i log internal-only o si traduce parte dei messaggi user-facing | M3 | Claudio + Romina |

---

## 14. Esempio: ciclo di vita di un commit

Per fissare le idee, qui il flusso completo dalla nuova feature al deploy production.

**Scenario**: Claudio (con Claude Code) aggiunge il filtro `pais` al tool `caso_de_estudio`.

```
Step 1 — branching
$ git checkout develop
$ git pull
$ git checkout -b feat/add-pais-filter-to-caso-de-estudio

Step 2 — implementation
- Edit src/segmenta_mcp/tools/tier1/caso_de_estudio.py: add pais parameter
- Edit src/segmenta_mcp/domain/filters.py: implement filter logic
- Edit tests/integration/test_tools_tier1.py: add 3 new test cases
- Edit CHANGELOG.md: add entry under [Unreleased] / Added

Step 3 — local checks
$ uv run ruff format src/ tests/
$ uv run ruff check src/ tests/
$ uv run mypy src/
$ uv run pytest

Step 4 — commit
$ git add -A
$ git commit -m "feat(tools): add country filter to caso_de_estudio

Allows filtering case studies by país (MX, US, AR, CO, CL, PE, ES).
Falls back to all countries if pais parameter is omitted or unrecognized.

Refs #23"

Step 5 — push e PR
$ git push -u origin feat/add-pais-filter-to-caso-de-estudio
# Apri PR su GitHub con template compilato

Step 6 — CI
- ci.yml triggered
- Lint passa
- Type check passa
- Test passa
- Coverage non scende sotto soglia
- ✅ Tutti i check verdi

Step 7 — review
- Claudio review (anche su sé stesso, disciplina)
- Eventuali change request → push nuovi commit nel branch (squash al merge)
- Approve

Step 8 — merge
- Squash & merge (GitHub UI)
- Branch auto-deleted

Step 9 — staging deploy
- deploy-staging.yml triggered su develop
- Container builded e pushed
- Fly.io deploy
- Smoke test post-deploy passa

Step 10 — manual verification staging
- Claudio testa via MCP Inspector contro mcp-staging.segmentamarketing.com
- OK

Step 11 — production deploy
- PR develop → main (titolo: "release: 0.2.0")
- Squash & merge
- deploy-production.yml triggered
- Tag v0.2.0 creato
- GitHub release pubblicata con changelog

Step 12 — post-deploy
- UptimeRobot conferma uptime
- Claudio aggiorna SESSION-STATE.md
```

L'intero flow è ottimizzato per essere fattibile in ~30 minuti totali (con codice già scritto). Nessun step è opzionale.

---

## 15. Versioning di questo documento

| Versione | Data | Autore | Note |
|---|---|---|---|
| 1.0 | 2026-05-10 | Claude (proposta) + Claudio (revisione) | Prima stesura completa. |
| 1.1 | 2026-05-11 | Claude (harmony pass M0.3) + Claudio (review) | Sez. 2.1 tabella linguaggi: aggiunte 4 righe (Costanti config / Costanti dominio / Slug record dati / Slug glosario) per disambiguare convenzioni che erano implicite. Riga "Variabili d'ambiente" rinominata da "snake_case uppercase" a "SCREAMING_SNAKE_CASE" (terminologia standard). |

---

## Note per il changelog

*(Sezione vuota in v1.0 — verrà popolata se emergono incongruenze nei file successivi che richiedono retrofitting in questo CONVENTIONS.)*

---

**Fine 02-CONVENTIONS.md v1.0.**
