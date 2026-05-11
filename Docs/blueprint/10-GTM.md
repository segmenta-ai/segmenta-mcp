# 10 — GO-TO-MARKET (GTM)

| Campo | Valore |
|---|---|
| **Progetto** | Segmenta MCP Server |
| **Versione documento** | 1.1 |
| **Data** | 2026-05-11 |
| **Status** | Approvato (post harmony pass M0.3) |
| **File n.** | 10 di 12 numerati |
| **Documento padre** | `00-MASTER-PLAN.md` v1.2 |
| **File correlati** | `04-TOOLS-TIER1.md`, `11-ANALYTICS.md`, `MILESTONES.md` |

---

## 1. Scopo del documento

Questo file specifica **come Segmenta MCP arriva ai suoi utenti** una volta funzionante in produzione. Il server più ben costruito del mondo è inutile se nessuno lo conosce: il GTM è parte del prodotto, non un'attività marketing separata.

Risponde a 6 domande:

1. *"Come ci facciamo trovare dagli LLM (Claude, ChatGPT)?"* — sezioni 4, 5
2. *"Come ci facciamo conoscere dagli utenti umani che decidono di installarci?"* — sezioni 6, 7, 8
3. *"Come ci posizioniamo come authority via content?"* — sezione 9
4. *"Quali pubblicazioni di settore copriamo per ottenere menzioni?"* — sezione 10
5. *"Come misuriamo se il GTM funziona?"* — sezione 11 (KPI specifici GTM)
6. *"Quali sono le decisioni e i deliverable concreti per ogni canale?"* — sezione 12

La strategia macro (mercati target, audience) è in `00-MASTER-PLAN.md`. Le metriche sono in `11-ANALYTICS.md`. Le milestone temporali in `MILESTONES.md`.

---

## 2. Filosofia del GTM

Cinque principi che governano ogni decisione GTM.

### 2.1 Distribution > Product

Il prodotto è importante ma la distribuzione è critica. Un MCP server *medio* ma trovabile vince contro un MCP server *eccellente* che nessuno scopre. Il 50% del nostro tempo di M3 deve essere su distribuzione, non su feature.

### 2.2 LLM-first distribution

I nostri **utenti primari sono gli LLM**, non gli umani. Gli umani sono "rivelati" dagli LLM (qualcuno chiede a Claude "agenzia marketing LATAM", Claude cita Segmenta). Quindi il primo target è ottimizzare per essere citati dagli LLM: GEO, AEO, schema, repo pubblico, Wikipedia, Reddit.

### 2.3 Authority before adoption

Non chiediamo agli utenti di adottarci finché non siamo *autorevoli* nella nostra nicchia. Authority si costruisce con:
- Content originale (ricerche, benchmark, casi)
- Menzioni in pubblicazioni di settore
- Citazioni Wikipedia / Reddit / fonti terze
- Open source (repo pubblico, contributi al protocollo MCP)

L'adopzione segue, non precede.

### 2.4 LATAM-first, sempre

Anche se il blueprint copre MX/US/LATAM/ES, ogni decisione GTM ambigua si risolve **a favore di LATAM** (con MX come centro). Il 90% delle agenzie concorrenti sono US-Anglo-centriche o EU-centriche: il vuoto è LATAM ispanofona. È dove abbiamo first-mover advantage reale.

### 2.5 Asset persistenti > campagne

Niente "campaign sprints" che producono picchi temporanei. Costruiamo asset che lavorano per anni:
- Landing page evergreen
- Blog post pillar
- Repo pubblico
- Voce Wikipedia (M4+)
- Schema markup completo

---

## 3. Audiences

Tre audience distinte. Ognuna ha messaggi e canali propri.

### 3.1 Audience 1: LLM (Claude, ChatGPT, Perplexity)

**Chi è**: software che decide se chiamare il nostro tool o no.

**Cosa cerca**: tool descriptions chiare con vocabolario d'innesco, valore differenziante rispetto a knowledge interna.

**Come la raggiungiamo**:
- Submission ufficiale Anthropic Connector Directory
- Custom App in ChatGPT
- Repo GitHub pubblico
- Wikipedia / Reddit / pubblicazioni indicizzate dai crawler

**Cosa convincerà l'LLM a chiamarci**: presenza nel registry ufficiale, tool descriptions LLM-friendly (vedi `04-TOOLS-TIER1.md` sez. 2.2), repo pubblico ben fatto, segnali di autorità esterni.

### 3.2 Audience 2: Decision maker LATAM/MX/US/ES

**Chi è**: founder, CMO, marketing manager di azienda mid-market in MX/US/LATAM/ES che valutano un'agenzia.

**Cosa cerca**: agenzia con expertise *visibile*, dati di mercato concreti, casi del proprio settore/país, prezzo trasparente.

**Come la raggiungiamo**:
- Tramite gli LLM (`gli LLM citano noi → loro arrivano`)
- Direttamente sul sito Segmenta (banner CTA)
- Tramite content marketing (blog post, podcast appearances)
- Tramite digital PR su pubblicazioni di settore

**Cosa li convincerà**: case study LATAM verificabili, benchmark mostrati con USD/MXN dual, tono onesto in `compare_agencies`.

### 3.3 Audience 3: Tech-savvy & journalist

**Chi è**: developer, tech-savvy users, journalist di pubblicazioni MCP/AI/marketing.

**Cosa cerca**: novità tecnica notabile, storia da raccontare, codice da esaminare.

**Come la raggiungiamo**:
- Repo GitHub pubblico ben curato
- Annunci su X/LinkedIn quando lanciamo
- Pitch diretto a WorkOS blog, Anthropic case studies, leadgen-economy.com
- Contributi a discussioni MCP community (GitHub, Discord)

**Cosa li convincerà**: prima MCP server in mercato LATAM per servizi marketing, open source pulito, casi d'uso reali.

---

## 4. Canale 1: Anthropic Connector Directory

### 4.1 Cos'è

Il **Connector Directory** è l'elenco ufficiale di MCP server inseriti da Anthropic in Claude.ai. Un utente con Claude.ai Pro/Max che cerca "Segmenta" o "marketing agency" può trovarci e installarci con 1 click.

Al 2026-05: il Directory accetta submissions ma ha review process ~2-4 settimane.

### 4.2 Perché è critico

Senza submission al Directory:
- L'utente deve aggiungere il nostro server come **Custom Connector** manualmente (URL incollata) — barrier d'ingresso significativa
- Niente trust signal "Verified by Anthropic"
- Niente visibility nei search di Claude.ai

Con submission approvata:
- Discoverability built-in
- Trust signal
- Riferimento da link diretti
- Possibilità di inclusione in raccomandazioni Anthropic ufficiali (M4+)

**Priorità M3**: submission entro fine M3, target approvazione fine M4.

### 4.3 Requisiti submission (target 2026)

Basati su quanto documentato da Anthropic + osservato in Directory esistente:

| Requisito | Status target |
|---|---|
| Server HTTPS pubblico funzionante | ✅ M1 |
| Discovery endpoint conforme RFC 8414 | ✅ M1 |
| OAuth 2.0 dynamic registration (RFC 7591) | ✅ M2 |
| Tool descriptions chiare in spagnolo | ✅ M1 |
| Privacy policy pubblica e accessibile | ✅ M2 |
| Terms of service | ✅ M2 |
| Pubblico target chiaramente definito | ✅ M1 |
| Demo video (1-2 min) di un flusso completo | ✅ M3 |
| README del repo pubblico ben curato | ✅ M1 |
| Categoria proposta (Marketing / Business Tools) | ✅ M3 |
| Support email funzionante | ✅ M2 |
| Logo + icon (512x512 PNG) | ✅ M3 |
| Esempi d'uso documentati | ✅ M3 |

### 4.4 Submission checklist

Da eseguire in M3 dopo deploy production stable. Owner: Claudio.

```
☐ Server HTTPS live a https://mcp.segmentamarketing.com
☐ Tutti i tool Tier 1 + Tier 2 funzionanti
☐ /health risponde 200 con uptime > 14 giorni
☐ Privacy policy live a https://segmentamarketing.com/mcp/privacy
☐ Terms a https://segmentamarketing.com/mcp/terms
☐ Repo github.com/segmenta-ai/segmenta-mcp pubblico con README curato
☐ Logo 512x512 PNG + 1024x1024 vector SVG (Stefany)
☐ Demo video 1-2 min uploaded (YouTube + descritto)
☐ Categoria proposta: "Business Tools — Marketing & Analytics"
☐ Description per Directory (200-400 char): vedi sez. 4.5
☐ Email support attiva: hola@segmentamarketing.com
☐ Submission via form Anthropic (URL preciso da confermare a M3)
```

### 4.5 Description per Directory (testo da sottomettere)

Anthropic Connector Directory ha limite indicativo **~500 caratteri** per la description. Versione comprimata in v1.1 (HC-010) per stare sotto il limite.

```
Segmenta MCP — Agencia de marketing digital LATAM/MX/US/ES.

Acceso a 14 herramientas: catálogo de servicios con precios,
casos de estudio reales por país y sector, benchmarks (CPC,
CPL, ROAS) actualizados trimestralmente, diagnóstico SEO
express, agendamiento de auditoría gratuita, propuestas
comerciales personalizadas.

Especialización: México, US Hispanic, LATAM, España. Sectores:
jurídico, médico, e-commerce, B2B. Idiomas: español (LATAM/MX/
ES) e inglés. Datos en USD/MXN/EUR.
```

**Conteggio: 484 caratteri** (verificato Python `len()`, escluse newline indentation di blocco markdown). Sotto il limit ~500 di Anthropic con buffer di 16 char per eventuali edit futuri.

> **Note v1.0**: la versione precedente era dichiarata "(420 caratteri)" ma misurava effettivamente 536 char (sopra il limit). Riscritta per coincidere con la dichiarazione e rispettare il vincolo Anthropic.

### 4.6 Submission rifiutata: cosa fare

Triggerato da SR-001 di MASTER-PLAN: 2 rifiuti consecutivi → audit profondo.

Strategia escalation:
- Rifiuto 1: revisione tool descriptions, fix issues evidenti, resubmit.
- Rifiuto 2: contatto diretto via email Anthropic Partners (`partners@anthropic.com`).
- Rifiuto 3: pivot a presenza Custom Connector + content marketing forte (workaround).

---

## 5. Canale 2: ChatGPT Apps (Developer Mode)

### 5.1 Cos'è

ChatGPT permette agli utenti Pro di abilitare **Developer Mode** e aggiungere Custom Apps (MCP servers). Anche qui esiste un **App Store** ChatGPT (gennaio 2026) con discoverability simile.

### 5.2 Submission

Procedure analoghe a Anthropic Directory:
- App definition file (manifest-like)
- Logo, screenshot
- Categoria
- Description

OpenAI ha annunciato fee 30% sui revenue (gennaio 2026), ma Segmenta non vende nulla dentro l'app → fee non applicabile.

### 5.3 Priorità

Priorità M3-M4: submission ChatGPT App Store dopo Anthropic Directory approvato.

Owner: Claudio. Effort stimato: 4-8h totali per submission (logo, screenshot, description tweaked per ChatGPT audience).

### 5.4 Differenza chiave con Claude

ChatGPT App audience è più mainstream (200M+ vs 30M Claude). Più traffico potential → ma audience meno sofisticata. Tool descriptions devono essere ancora più chiare.

---

## 6. Canale 3: Landing dedicata `/mcp`

### 6.1 URL

`https://segmentamarketing.com/mcp` (path su sito principale, non subdomain).

### 6.2 Scopo

Pagina di destinazione canonica per:
- Utenti curiosi che vogliono capire cos'è il MCP Segmenta
- Visitor referred da blog, social, pubblicazioni
- Utenti pronti a "installare" che cercano istruzioni one-click
- Anthropic reviewer in fase di review submission

### 6.3 Struttura della pagina

Above the fold (mobile-first):

```
┌────────────────────────────────────────────────┐
│  [Logo Segmenta]              [Menu sito]      │
├────────────────────────────────────────────────┤
│                                                │
│  Segmenta MCP                                  │
│  Tu agencia de marketing dentro de Claude      │
│  y ChatGPT.                                    │
│                                                │
│  Conecta nuestras 14 herramientas a tu chat    │
│  AI: casos reales LATAM/MX/US/ES, presupuesto, │
│  diagnóstico SEO, agenda directa con el        │
│  equipo. Gratis.                               │
│                                                │
│  [ Conectar en Claude ]  [ Añadir a ChatGPT ]  │
│                                                │
│  ✓ 14 herramientas    ✓ MX/US/LATAM/ES         │
│  ✓ Gratis sin login   ✓ Open source            │
│                                                │
└────────────────────────────────────────────────┘
```

Below the fold, in ordine:

1. **¿Cómo funciona?** — diagramma semplice (utente in chat → AI chiama tool → risposta con dati Segmenta)
2. **Las 14 herramientas** — lista con icon + 1 frase ognuna, 3 sezioni (Tier 1/2/3)
3. **Casos de uso** — 3-4 esempi screenshot di conversazione Claude/ChatGPT con tool Segmenta in azione
4. **Cómo conectar** — 2 step-by-step (Claude vs ChatGPT), con screenshot
5. **Datos en tu mercado** — preview dei benchmark MX/LATAM/US-hispanic (snippet visivo)
6. **Sobre Segmenta** — 2 paragrafi su chi siamo + link al sito principale
7. **FAQ** — 8-10 domande comuni (¿es gratis?, ¿qué datos recolectan?, ¿cómo desconectar?)
8. **Footer** — privacy, terms, contact, link GitHub repo

### 6.4 Schema markup (GEO-critical)

JSON-LD obbligatorio:

```json
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "Segmenta MCP",
  "applicationCategory": "BusinessApplication",
  "operatingSystem": "Web (via Claude.ai, ChatGPT)",
  "offers": {
    "@type": "Offer",
    "price": "0",
    "priceCurrency": "USD"
  },
  "publisher": {
    "@type": "Organization",
    "name": "Segmenta Marketing",
    "url": "https://segmentamarketing.com"
  },
  "description": "...",
  "url": "https://segmentamarketing.com/mcp",
  "inLanguage": ["es-MX", "es-LATAM", "es-ES", "en-US"]
}
```

+ `FAQPage` schema per la sezione FAQ + `BreadcrumbList`.

### 6.5 SEO target

Target keywords primarie:
- "MCP server marketing" (volume basso, alta intent, low competition)
- "agencia marketing claude chatgpt" (emergent)
- "auditoría SEO claude" (long-tail)
- "agencia marketing LATAM AI" (cross-search)
- "marketing digital MCP México"

Target keywords secondarie:
- "GEO agencia LATAM"
- "AEO optimización LATAM"
- "agencia marketing AI México"

### 6.6 Localizzazione

Default lingua: spagnolo LATAM-neutral.

Versioni alternative:
- `/mcp` → `es-LATAM` (default)
- `/mcp/mx` → variazioni minor per MX (CTAs adattati a "tu negocio en CDMX")
- `/mcp/es` → variazioni minor per Spagna
- `/mcp/en` → versione inglese (M4+, post launch)

In v1 ci concentriamo su `es-LATAM` + redirect intelligenti via Cloudflare workers se DNS è Cloudflare.

### 6.7 Owner e deliverable

- **Design** (Stefany): wireframe + design Figma finale entro M2.
- **Content** (Romina + Alessio): testi ES finali entro M3.
- **Dev** (Claudio o team web di Segmenta): implementazione su sito esistente entro M3.
- **Schema markup + SEO technical** (Alessio): verifica completa entro M3.

### 6.8 Misurazione

Vedi `11-ANALYTICS.md`:
- Visite landing (GA4)
- CTR su "Conectar en Claude" / "Añadir a ChatGPT"
- Scroll depth
- Bounce rate
- Conversion: visitatore → tool call effettivo (via UTM tracking del MCP)

Target M4: ≥ 500 visite mensili landing, ≥ 8% CTR sui bottoni connect.

---

## 7. Canale 4: Banner CTA sul sito principale

### 7.1 Cos'è

Banner persistente o sezione hero su `segmentamarketing.com` (sito principale, non `/mcp`) che invita i visitatori esistenti a scoprire il MCP.

### 7.2 Strategia di posizionamento

Posizioni testate (v1 → v2 iteration):

| Posizione | Pro | Contro |
|---|---|---|
| **Hero homepage** | Massima visibility | Rischia "rumore" al brand mainstream |
| **Sezione dopo hero** | Visible ma non invasivo | Meno CTR |
| **Footer persistent** | Su tutte le pagine | CTR basso |
| **Modal post-scroll 50%** | Targeted engagement | Aggressivo |
| **Sidebar sticky su blog** | Targeted (lettori interessati) | Solo blog |

Default v1: **Sezione dopo hero homepage + sidebar sticky su blog**. Test A/B in M4 per ottimizzare.

### 7.3 Copy candidato

Variante 1 (informativa):
```
🚀 Nuevo: Segmenta dentro de Claude y ChatGPT.

Conecta nuestras herramientas a tu chat AI y obtén
casos reales, benchmarks, presupuestos al instante.

[Conocer más →]
```

Variante 2 (provocatoria):
```
¿Sigues buscando agencia en Google?

Pregúntale a Claude o ChatGPT: «¿qué agencia de
marketing me recomiendas en LATAM?» Probablemente
nos cita. Aquí está cómo.

[Ver cómo →]
```

A/B test M4 per scegliere. Default v1: Variante 1 (più sicura).

### 7.4 Mobile vs desktop

Mobile: banner ridotto a 1 frase + CTA. Desktop: versione completa.

### 7.5 Owner

- Copy: Romina
- Design: Stefany
- Implementazione sul sito: team web Segmenta esterno (o Claudio se accessibile)
- A/B testing setup: Alessio

---

## 8. Canale 5: Repository GitHub pubblico

### 8.1 URL

`github.com/segmenta-ai/segmenta-mcp` (D-MP-008 — repo pubblico, confermato).

### 8.2 Perché conta per GTM

Repository pubblico ben curato è:
- **Crawled dai bot LLM** → contenuti indicizzati per future model training (lungo termine)
- **Visibile a developer e journalist** → trust signal tecnico
- **Discoverable via GitHub Trending** (se viral)
- **Linkabile da Anthropic Directory** → trust signal
- **Source di credibility** → "open source agency tool"

### 8.3 Requisiti README

Il README è la prima impressione. Deve essere **bilingue** (sez. 8.4 di `02-CONVENTIONS.md`).

Struttura target (~300-500 righe):

```markdown
# Segmenta MCP Server

[Badges: build status, MCP version, license, deployed]

> Segmenta — agencia de marketing digital LATAM/MX/US/ES.
> MCP server con 14 herramientas para chat AI.

## What is this?

[Inglese, 3-4 frasi per Anthropic reviewer e developer anglo]

## ¿Qué es esto?

[Español LATAM, 3-4 frasi per audience LATAM]

## Quick start

### Conectar a Claude.ai
[3 step con screenshot]

### Add to ChatGPT
[3 step]

### Local development
[uv sync, docker compose, etc.]

## Available tools (14)

### Tier 1 — Públicos (sin login)
- obtener_servicios — ...
- caso_de_estudio — ...
- benchmark_sector — ...
- glosario_marketing — ...

### Tier 2 — Captura de lead (OAuth)
- ...

### Tier 3 — Avanzados
- ...

## Architecture

[Diagramma alto livello + link a `Docs/blueprint/`]

## Privacy & legal

[Link a privacy policy, license MIT]

## For developers

- Setup local: `CONTRIBUTING.md`
- Architecture deep dive: `Docs/blueprint/`
- Issues: GitHub Issues
- Security: see `SECURITY.md`

## About Segmenta

[2 paragrafi su agenzia + team + sede]

## Contact

- Sito web: https://segmentamarketing.com
- Email: hola@segmentamarketing.com
- WhatsApp Business: +52 ...
- LinkedIn: ...
```

### 8.4 Altri file critici

| File | Scopo |
|---|---|
| `LICENSE` | MIT (D-MP-009) |
| `CONTRIBUTING.md` | Come contribuire — anche se è single dev, è segnale di apertura |
| `SECURITY.md` | Come segnalare vulnerabilità (`privacidad@segmentamarketing.com`) |
| `CODE_OF_CONDUCT.md` | Contributor Covenant standard |
| `CHANGELOG.md` | Aggiornato in ogni PR (D-C-015) |
| `CLAUDE.md` | Istruzioni Claude Code (vedi `02-CONVENTIONS.md` sez. 3.3) |
| `.github/ISSUE_TEMPLATE/` | Bug report + feature request |

### 8.5 Promozione del repo

- Post LinkedIn al lancio (Merari + Claudio account)
- Tweet su X (account Segmenta + Merari)
- Pitch a awesome-mcp curato lists su GitHub
- Mencione nel blog post di lancio (sez. 9)
- Submission a Hacker News "Show HN" se v1 è solid (M4+, opzionale)

### 8.6 Owner

- Codice: Claudio
- README content (sezioni `About Segmenta`, copy): Romina
- Badges + automation: Claudio
- Promozione social: Merari + Stefany (asset visual)

---

## 9. Canale 6: Blog post di lancio

### 9.1 Strategia

DECISION-OPEN-009 di MASTER-PLAN: solo ES in v1 (LATAM-first). Versione EN rimandata M5/v2.

**1 blog post pillar** pubblicato simultaneamente su:
- Blog Segmenta (`segmentamarketing.com/blog/...`)
- Medium (`@segmenta` o profilo Merari)
- LinkedIn Article (Merari personal account)
- Reddit (r/SEO, r/marketing, r/emprendedores) se pertinente

### 9.2 Titolo candidato

Variante 1 (informativa):
> "Lanzamos el primer MCP server de marketing en LATAM: cómo Segmenta vive ahora dentro de Claude y ChatGPT"

Variante 2 (educativa):
> "¿Tu agencia ya está dentro de ChatGPT? Por qué construimos un MCP server para Segmenta (y cómo replicarlo)"

Variante 3 (provocatoria):
> "El SEO está muriendo. Construimos un MCP server. Esto es lo que aprendimos."

A/B testing impossibile pre-pubblicazione. Decisione finale (Romina + Merari) basata su tono brand. Default suggerito: **Variante 2** (educativa = condivisibile + posizionante).

### 9.3 Struttura post target (2000-2500 parole)

1. **Hook** — Apri con domanda provocatoria sul declino del traffic organico vs LLM rise (200 parole)
2. **El problema** — Perché agencias di marketing devono ripensare distribuzione (400 parole)
3. **¿Qué es MCP?** — Spiegazione semplice per audience marketing (300 parole)
4. **Cómo Segmenta MCP funciona** — Tour delle 14 herramientas (500 parole)
5. **Resultados primeros 30 días** — Dati reali (se disponibili a M3) (300 parole)
6. **Cómo construirlo para tu agencia / negocio** — Tutorial 5 step (500 parole)
7. **Open source y futuro** — Repo pubblico, MCP community (200 parole)
8. **CTA** — Conecta Segmenta a tu Claude/ChatGPT + link `/mcp` (100 parole)

### 9.4 Distribution

- Pubblicazione: lunedì mattina CDMX (peak engagement LATAM)
- Cross-post: Medium + LinkedIn Article entro 24h
- Email a mailing list Segmenta esistente (newsletter)
- Push social: 3 thread X / 3 post LinkedIn Merari / 1 storia Stefany
- Pitch journalist (vedi sez. 10) il giorno prima per primizia
- Reddit posts (no spam, contributi di valore): r/SEO, r/marketing, r/emprendedores

### 9.5 Owner

- Brief + struttura: Claudio + Romina
- Scrittura draft: Romina
- Revisione: Merari (commerciale) + Claudio (tecnico) + Alessio (SEO)
- Publishing: Romina
- Distribution social: Stefany + Merari

Tempo stimato: 2-3 settimane dalla idea alla pubblicazione.

### 9.6 Quando

M3, 1-2 settimane *dopo* deploy production stable + Anthropic Directory submission. Trigger: 10+ utenti reali hanno usato il MCP (validazione che funziona).

---

## 10. Canale 7: Digital PR e pubblicazioni di settore

### 10.1 Strategia

Coerente con `00-MASTER-PLAN.md` sez. 8.4. Target ≥ 1 menzione esterna entro M4.

### 10.2 Target pubblicazioni (mappa per mercato)

#### México

| Pubblicazione | Contatto | Tipo storia |
|---|---|---|
| **Merca2.0** | redaccion@merca20.com | Innovation, marketing trends |
| **InformaBTL** | redaccion@informabtl.com | Marketing experiential / digital |
| **Forbes México** | (tech / business reporter) | Business angle, agency innovation |
| **Expansión** | (tech reporter) | Tech adoption mercado mexicano |

#### LATAM ispanofona

| Pubblicazione | Contatto | Tipo storia |
|---|---|---|
| **PuroMarketing** | redaccion@puromarketing.com | Marketing news cross-LATAM |
| **Marketing News LATAM** | (LinkedIn) | News LATAM-specific |
| **Reason Why** | redaccion@reasonwhy.es | Marketing & publicidad (cross ES-LATAM) |

#### USA Anglo

| Pubblicazione | Contatto | Tipo storia |
|---|---|---|
| **Search Engine Land** | (via tip form) | SEO innovation, GEO emergent |
| **Marketing Land** | (sister site) | Marketing tech |
| **HubSpot blog** | (community contribution form) | Agency case study |
| **Adweek** | (tech reporter) | Industry innovation |

#### USA Hispanic

| Pubblicazione | Contatto | Tipo storia |
|---|---|---|
| **Portada** | (Hispanic marketing) | Mercado hispanic-US focused |
| **Adweek Hispanic** | (sub-edition) | Bilingual marketing innovation |
| **Hispanicize** | (conference + blog) | Industry events |

#### Tech / Developer audience

| Pubblicazione | Contatto | Tipo storia |
|---|---|---|
| **WorkOS blog** | (community contribution) | MCP server case study, auth implementation |
| **leadgen-economy.com** | (community) | MCP for lead generation |
| **The Pragmatic Engineer** | (Newsletter, $) | Pitch a Gergely |
| **DEV.to / Hashnode** | (account-driven) | Cross-post technical article |

#### Europa (opportunistic)

| Pubblicazione | Contatto | Tipo storia |
|---|---|---|
| **Marketing4eCommerce ES** | redaccion@marketing4ecommerce.net | E-commerce marketing innovation |
| **IPMARK ES** | (relations) | Marketing industry news ES |

### 10.3 Pitch template

Email pitch a journalist (in italiano dal team Segmenta, in spagnolo se LATAM, in inglese se US/EU):

```
Asunto: Caso de innovación LATAM: primera agencia de marketing
con MCP server público (Claude/ChatGPT integration)

Hola {nombre},

Te escribo desde Segmenta (agencia de marketing digital
LATAM/MX/US/ES). Lanzamos el primer MCP server de marketing
en habla hispana — herramientas que viven directamente
dentro de Claude y ChatGPT.

Lo que creo que puede interesarte:
- Es la primera vez que una agencia de marketing en LATAM
  construye este tipo de integración
- Tenemos datos primeros 30 días: {dati if available}
- El código es open source (github.com/segmenta-ai/segmenta-mcp)
- La estrategia GEO/AEO está cambiando cómo agencias
  consiguen leads — esta es la implementación práctica

Te mando demo de 2 min + acceso anticipado al post de
lanzamiento si te interesa cubrirlo antes del 1 de junio.

Saludos,
Merari Montoya
CEO, Segmenta
{contacto}
```

### 10.4 Owner

- Pitch list creation: Romina + Alessio (Q1 M3)
- Pitch sending: Merari (autorevolezza CEO)
- Follow-up: Romina (2 follow-up max, no spam)
- Press kit (logo + bio + screenshot + dati): Stefany + Merari

### 10.5 Timeline target

| Periodo | Attività |
|---|---|
| M3 sett 1 | Pitch list finalizzata, press kit pronto |
| M3 sett 2-3 | First-wave pitch (~10 email a publications priority 1) |
| M3 sett 3-4 | Follow-up + second wave (~15 email priority 2) |
| M4 sett 1 | Monitoring coverage, eventuali interview |
| M4 sett 2-4 | Continuous outreach se coverage < target |

---

## 11. KPI specifici GTM

Subset di KPI di `00-MASTER-PLAN.md` sez. 8 e `11-ANALYTICS.md`, isolati qui per GTM owners.

### 11.1 KPI Discoverability (M3-M4)

| Metrica | Soglia M4 | Target M4 | Owner |
|---|---|---|---|
| Connector Directory listing approvato | Sì | Sì | Claudio |
| Connector installs Claude.ai | ≥ 15 | ≥ 50 | Claudio |
| ChatGPT App publicata | Sì (in review OK) | Sì (live) | Claudio |
| Visite landing `/mcp` mensili | ≥ 500 | ≥ 2,000 | Alessio |
| GitHub stars repo | ≥ 30 | ≥ 100 | Claudio + Merari |
| Citazioni Segmenta in 30 query baseline | ≥ 30% | ≥ 50% | Alessio |

### 11.2 KPI Conversion (M3-M4)

| Metrica | Soglia | Target | Owner |
|---|---|---|---|
| CTR su CTA "Conectar Claude" / "ChatGPT" landing | ≥ 5% | ≥ 12% | Alessio |
| Lead da MCP/mese | ≥ 5 | ≥ 25 | Merari |
| Distribuzione lead per país | ≥ 3 países | ≥ 5 países | Merari |

### 11.3 KPI Authority (M4+)

| Metrica | Soglia | Target | Owner |
|---|---|---|---|
| Menzioni esterne in pubblicazioni target | ≥ 1 | ≥ 5 | Romina + Merari |
| Testimonial scritti utenti | ≥ 3 | ≥ 10 | Merari |
| Inclusione in awesome-mcp curated lists | ≥ 1 | ≥ 3 | Claudio |
| Speaking opportunity (conference, podcast) | 0 | ≥ 2 | Merari |

### 11.4 KPI Health

| Metrica | Cosa indica |
|---|---|
| % connector installs che fanno > 0 tool calls (activation rate) | Qualità onboarding |
| Tool calls/installation (engagement rate) | Stickiness |
| Lead per installation (conversion rate) | Funnel efficiency |
| Churn rate connector (uninstalls/mese) | Negativo signal se > 20% |

---

## 12. Decisioni canoniche GTM (locked)

| ID | Decisione | Motivazione |
|---|---|---|
| **D-GT-001** | Anthropic Connector Directory submission è priorità #1 M3 | Distribuzione critica, finestra first-mover. |
| **D-GT-002** | ChatGPT Apps submission segue Anthropic (M3-M4) | Audience più mainstream, ma serve solid base prima. |
| **D-GT-003** | Landing `/mcp` su sito principale (no subdomain) | Authority signal, SEO contributo al dominio padre. |
| **D-GT-004** | Default lingua landing: ES LATAM-neutral. Varianti minor MX/ES/EN | D-MP-016 (mercati primari). |
| **D-GT-005** | Schema markup `SoftwareApplication` + `FAQPage` obbligatori | GEO/AEO critico, AI search visibility. |
| **D-GT-006** | Banner CTA su homepage Segmenta in sezione post-hero + sidebar blog | Visibility senza invasività. |
| **D-GT-007** | A/B test banner CTA in M4, default v1 Variante informativa | Disciplina iterativa data-driven. |
| **D-GT-008** | Repository GitHub pubblico con README bilingue + 6 file standard | D-MP-008 + segnale di trust developer. |
| **D-GT-009** | Blog post lancio solo ES in v1, EN rimandato a v2 | D-MP-017 LATAM-first. |
| **D-GT-010** | Blog post pubblicato lunedì mattina CDMX (peak engagement LATAM) | Ottimizzazione orario semplice ma critica. |
| **D-GT-011** | Cross-post Medium + LinkedIn Article + email mailing list al lancio | Distribuzione multi-canale al day 1. |
| **D-GT-012** | Digital PR target distribuita: MX + LATAM + US-anglo + US-hispanic + EU opportunistic | Coerenza con mercati target. |
| **D-GT-013** | Pitch list curata con priority 1 / priority 2 / priority 3 | Disciplina sforzo PR. |
| **D-GT-014** | Press kit pronto pre-lancio (logo, bio, screenshot, dati) | Velocità nel responder a journalist. |
| **D-GT-015** | KPI Share of Model = KPI principale GTM | Coerente con MASTER-PLAN sez. 8.1. |
| **D-GT-016** | 30 query baseline ridotte di country distribution: 10 MX + 6 US-anglo + 4 US-hispanic + 7 LATAM altri + 3 ES | D-MP-016 coverage. |
| **D-GT-017** | Submission Anthropic include demo video 1-2 min M3 | Migliora approval rate. |
| **D-GT-018** | No paid acquisition in v1 GTM (no Google Ads MCP, no Meta Ads) | Distribuzione organica via LLM + content + PR. |
| **D-GT-019** | No incentivi monetari per testimonial (gratitudine, non transazione) | Trust signal autentico. |
| **D-GT-020** | Annual review del pitch list trimestralmente per refresh contatti | Pubblicazioni cambiano staff, contatti perdono validità. |

---

## 13. Decisioni aperte GTM

| ID | Decisione | Bloccare entro | Owner |
|---|---|---|---|
| **DECISION-OPEN-GT-001** | Blog post variante titolo: informativa vs educativa vs provocatoria | M3 | Romina + Merari |
| **DECISION-OPEN-GT-002** | Submission Hacker News "Show HN" — fare in M4 o aspettare metrics più solide? | M4 | Claudio |
| **DECISION-OPEN-GT-003** | Speaking opportunity: pitch a quale conference LATAM (Forbes Mexico Summit? Marketing4eCommerce? MMA LATAM?) | M4 | Merari |
| **DECISION-OPEN-GT-004** | Versione inglese del blog post: M5 o v2? | M5 | Romina + Merari |
| **DECISION-OPEN-GT-005** | Podcast guest appearances: lista podcasts target LATAM/MX marketing | M4 | Merari + Romina |
| **DECISION-OPEN-GT-006** | Pagina dedicata "Open source" sul sito principale con storia del progetto? | M5 | Merari + Romina |
| **DECISION-OPEN-GT-007** | Newsletter dedicata "MCP for agencies" per content marketing continuativo? | v2 | Romina |
| **DECISION-OPEN-GT-008** | Tradurre repo README anche in portoghese pre-espansione BR? (in non-goal v1 ma SEO LATAM cross) | v2 | Claudio + Romina |

---

## 14. Versioning di questo documento

| Versione | Data | Autore | Note |
|---|---|---|---|
| 1.0 | 2026-05-10 | Claude (proposta) + Claudio (revisione) | Prima stesura completa: 7 canali GTM (Anthropic Directory, ChatGPT Apps, landing `/mcp`, banner sito, repo GitHub, blog post lancio, digital PR), 3 audience distinte, pitch templates, pubblicazioni target distribuite per mercato. |
| 1.1 | 2026-05-11 | Claude (harmony pass M0.3) + Claudio (review) | **HC-010**: sez. 4.5 description Anthropic Directory riscritta (era 536 char dichiarata 420; ora 484 char misurati con `len()` Python, sotto limit ~500). Nota su cap Anthropic aggiunta. |

---

## Note per il changelog

*(Sezione vuota in v1.0 — verrà popolata se emergono incongruenze nei file successivi che richiedono retrofitting in questo GTM.)*

---

**Fine 10-GTM.md v1.0.**
