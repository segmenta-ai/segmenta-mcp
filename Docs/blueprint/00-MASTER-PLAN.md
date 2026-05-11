# 00 — MASTER PLAN

| Campo | Valore |
|---|---|
| **Progetto** | Segmenta MCP Server |
| **Versione documento** | 1.3 |
| **Data** | 2026-05-11 |
| **Status** | Approvato (post harmony pass M0.3 + chiusura M0.2 parziale) |
| **File n.** | 00 di 14 documenti blueprint (12 numerati `00-11` + `MILESTONES.md` + `SESSION-STATE.md`; `README.md` è entry point pubblico separato) |
| **Lingua** | Italiano (prosa) + spagnolo (identificatori e termini di marketing) |
| **Repository** | `github.com/segmenta-ai/segmenta-mcp` (pubblico — D-MP-008; org dedicata confermata 2026-05-11 chiudendo DECISION-OPEN-005) |
| **Owner tecnico** | Claudio (SEM Manager Segmenta — solo dev di questo progetto) |
| **Owner commerciale** | Merari Montoya (CEO Segmenta) |
| **Mercati target primari** | México, USA (generalista anglo + hispanic), LATAM ispanofona |
| **Mercati target secondari** | Europa (Spagna, Italia) — opportunistic, non priority |

---

## 1. Vision

**Segmenta MCP Server** è un servizio backend che espone informazioni e azioni dell'agenzia di marketing digitale Segmenta come *tool* chiamabili dai grandi modelli linguistici (Claude, ChatGPT e qualsiasi client compatibile con il protocollo MCP).

L'obiettivo a 12 mesi è duplice:

1. **Apparire dentro le risposte** generate da Claude e ChatGPT quando un utente cerca un'agenzia di marketing per il mercato messicano, US o LATAM, o quando chiede dati di settore (CPC, CPL, casi di successo) per quei mercati.
2. **Convertire quelle apparizioni in lead qualificati** offrendo, dentro la stessa conversazione, azioni concrete: un'auditoría SEO express, la prenotazione di una call gratuita, una propuesta personalizada.

In una frase: *trasformare la chat AI da concorrente del nostro sito a canale di lead generation diretto, con priorità sui mercati LATAM-MX-US dove Segmenta opera*.

---

## 2. Problema strategico — perché ora

### 2.1 Il contesto

Il traffico organico verso i siti di servizi sta calando rapidamente perché gli utenti ricevono risposte sintetiche dentro Claude / ChatGPT / Perplexity / Google AI Overviews invece di cliccare sui link blu. La ricerca di settore documenta:

- AI search engines gestiscono il **12-18%** delle query informazionali in inglese (Q1 2026) — un anno fa era sotto il 2%.
- Il traffico riferito da AI converte mediamente **5x meglio** del traffico organico classico, perché l'utente arriva con un'intenzione molto matura.
- Solo il **12% dei siti web** è ottimizzato per AI search engines — finestra di first-mover ancora aperta, **particolarmente in LATAM e nel mercato hispanic-US** dove la penetrazione GEO è la più bassa al mondo per lingua principale.

### 2.2 Il vantaggio competitivo del momento

A maggio 2026:

- Anthropic e OpenAI hanno lanciato **MCP Apps** (gennaio 2026): tool che vivono dentro Claude e ChatGPT con UI rendering e azioni eseguibili.
- Il **Connector Directory** ufficiale di Anthropic accetta submission ma è ancora poco popolato per il mercato in lingua spagnola — praticamente assente per LATAM.
- Le agenzie concorrenti di Segmenta nei mercati MX/US/LATAM **non hanno ancora** un MCP server pubblicato (verifica condotta su 30 query target distribuite sui mercati primari).

Costruire ora significa entrare nel mercato MCP del marketing digitale ispanofono come *primo player visibile*. Aspettare 12 mesi significa entrare come quinto o sesto in un mercato già consolidato.

### 2.3 Il problema del singolo concorrente "Wikipedia"

Gli LLM citano fonti terze più dei siti commerciali. Wikipedia è la fonte più citata da ChatGPT (47.9% delle citazioni su domande factual), Reddit per Perplexity (46.7%). Senza un MCP server proprio, l'unica leva su Segmenta è digital PR + content. Con un MCP server proprio, Segmenta diventa **fonte primaria attivamente interrogata** dall'LLM, non passivamente citata.

### 2.4 Specificità mercato hispanofono

Importante: la lingua spagnola non è monolitica. Variazioni rilevanti per il MCP:

- Lessico marketing: "ordenador" (ES) vs "computadora" (LATAM/MX), "móvil" (ES) vs "celular" (LATAM/MX), "PYME" (ES) vs "PyME" (MX)
- KPI di mercato: CPC settore legale a Madrid ≠ CPC settore legale a CDMX o Miami
- Compliance: le clínicas in MX seguono COFEPRIS, non Ley 14/1986 (Spagna)
- Hispanic US: pubblico bilingue, code-switching, KPI tipicamente più alti per concorrenza

I dati e le tool descriptions del server devono riflettere questa varianza. Default: spagnolo *neutro/LATAM*. Eccezioni esplicite quando un benchmark è specifico di una piazza.

---

## 3. Soluzione proposta — overview ad alto livello

Costruiamo un server MCP HTTPS pubblicato su sotto-dominio dedicato (`mcp.segmentamarketing.com`) che espone *tool* organizzati in tre livelli (`tier`) progressivamente più orientati alla conversione:

### Tier 1 — Tools públicos (no auth, alta frecuencia de llamada)

Strumenti educativi e informativi. Forniscono valore reale all'utente *senza* richiedere identificazione. Sono la "esca" che fa sì che l'LLM scelga di chiamare il nostro server invece di rispondere dalla propria conoscenza.

- `obtener_servicios` — catalogo servizi con prezzi indicativi (rangos USD primario, MXN/EUR conversione informativa)
- `caso_de_estudio` — case study reali con metriche, filtrabili per país y sector
- `benchmark_sector` — KPI tipici per settore + país (México, USA-anglo, USA-hispanic, LATAM, ES)
- `glosario_marketing` — definizioni termini con varianti regionali ES (LATAM/MX vs ES) ed equivalenti EN

### Tier 2 — Tools con captura de lead (gated, OAuth o email)

Strumenti che richiedono identificazione minima per essere chiamati. Sono il punto di conversione: l'utente che ottiene valore al Tier 1 e vuole approfondire entra qui e **lascia un contatto verificato**.

- `diagnostico_seo_express` — crawl del sito utente, 5-10 quick win, report via email
- `calcular_presupuesto` — preventivo orientativo basato su input strutturati (servizio, país, settore, scope)
- `agendar_auditoria_gratuita` — prenotazione call su piattaforma scelta (vedi DECISION-OPEN-002), timezone-aware
- `solicitar_propuesta_personalizada` — brief lungo che entra nel CRM
- `consultar_disponibilidad` — calendario di slot disponibili (read-only)

### Tier 3 — Tools advanzados (post-conversión, retention, intelligence)

Strumenti per l'utente già contattato o per scenari avanzati che differenziano Segmenta dalla concorrenza.

- `whatsapp_directo` — link prefill con contesto della conversazione AI (canale principale per LATAM/MX)
- `share_research` — pubblicazione automatica su channel pubblici di richieste di ricerca anonimizzate (lead magnet meta)
- `analizar_competencia` — analisi competitiva live di un competitor (gated, costo crediti)
- `compare_agencies` — confronto onesto Segmenta vs altre agenzie su criteri oggettivi
- `obtener_caso_por_pais` — ricerca caso studio per país specifico (MX, US, AR, CO, CL, PE, ES, etc.)

I dettagli architetturali completi — diagramma data flow, schema OAuth, stack tecnico — sono in **`01-ARCHITECTURE.md`**.

---

## 4. Scope (cosa è dentro)

### 4.1 Componenti prodotto

- Server MCP scritto in Python con `fastmcp` (versione ≥ 3.2)
- Deploy in container su Fly.io free tier (vedi D-MP-002, region MEX + MIA)
- Dominio dedicato `mcp.segmentamarketing.com` con HTTPS via Let's Encrypt
- 14 tool totali (4 Tier 1 + 5 Tier 2 + 5 Tier 3)
- 4 file dati JSON gestiti dal team Segmenta (`services.json`, `case_studies.json`, `benchmarks.json`, `glosario.json`)
- OAuth 2.0 dinamico per i tool Tier 2 e Tier 3 (vedi `07-AUTH-OAUTH.md`)
- Integrazioni con piattaforma booking, CRM, email transactional, WhatsApp Business API (vedi `08-INTEGRATIONS.md`)
- Health check + observability minimo (vedi `09-DEPLOYMENT.md`)

### 4.2 Componenti go-to-market

- Submission al Connector Directory ufficiale di Anthropic
- Pubblicazione come Custom App in ChatGPT (Developer Mode)
- Landing dedicata su `segmentamarketing.com/mcp` (vedi `10-GTM.md`)
- Banner CTA "Conecta Segmenta a Claude/ChatGPT" sulle pagine principali del sito (versione ES + versione MX se separate)
- **Blog post di lancio in spagnolo (LATAM-first)** — pubblicato simultaneamente sui canali Segmenta e cross-promosso. Versione EN rimandata alla v2 (vedi DECISION-OPEN-009)
- Repo GitHub pubblico con README esemplare (segnale tecnico per LLM)

### 4.3 Componenti analytics

- Dashboard interna leggera (vedi `11-ANALYTICS.md`)
- Tracking utilizzo tool, attribution AI, **baseline 30 query distribuite sui mercati target** (vedi sez. 8.1)
- Re-test settimanale automatizzato delle 30 query baseline

---

## 5. Non-goals (cosa esplicitamente non facciamo)

Lo scope è disciplinato. Le seguenti voci sono **fuori dal blueprint v1**, anche se potrebbero essere buone idee per il futuro:

- ❌ **Multi-tenant SaaS**: il server è solo per Segmenta. Non vendiamo questo come prodotto a clienti terzi (quello è eventualmente *un altro progetto* — cfr. SEO Lens).
- ❌ **App mobile nativa**: l'unica UI è dentro Claude/ChatGPT/altri client MCP.
- ❌ **Chatbot custom sul sito Segmenta**: usiamo l'infrastruttura LLM esistente, non costruiamo un'altra interfaccia conversazionale.
- ❌ **Pagamenti dentro l'MCP**: nessuna transazione passa per il server. Tutti i flussi commerciali avvengono off-MCP (call con il team, contratti firmati esternamente).
- ❌ **Portoghese / mercato Brasile**: rimandato a v2. La traduzione di tool descriptions, benchmark e glosario per il pubblico brasiliano è un investimento separato.
- ❌ **Blog post in inglese in v1**: l'EN è importante ma rimandato. ES LATAM-first è la priorità (vedi DECISION-OPEN-009).
- ❌ **A/B testing automatico delle descrizioni tool**: rimandato a M5. In v1 le descrizioni sono curate manualmente.
- ❌ **CMS proprio per i dati JSON**: in v1 i file JSON si modificano via PR su GitHub. (Eventuale dashboard editoriale rimandata.)
- ❌ **Reportistica per i clienti finali di Segmenta**: il MCP non genera report per i clienti dell'agenzia, solo per visitatori prospect.
- ❌ **Integrazione con il sito WordPress/Elementor di Segmenta**: il MCP è completamente separato. Comunicano solo via API pubbliche, non via plugin.
- ❌ **Self-hosted gateway**: usiamo Fly.io PaaS. Non gestiamo Kubernetes nostro né reverse proxy custom.
- ❌ **Versioning multipli concorrenti del server**: rilascio una versione alla volta. Niente blue/green deploy avanzato in v1.
- ❌ **Caching dei risultati LLM**: ogni chiamata tool è stateless. Niente sistema di caching lato server.
- ❌ **Dati dettagliati per Europa diversa da Spagna in v1**: i benchmark europei coprono solo ES (occasionale) — non IT, FR, DE, PT.

---

## 6. Stakeholder e responsabilità

| Persona | Ruolo | Responsabilità sul progetto |
|---|---|---|
| **Claudio** | SEM Manager Segmenta | Solo dev. Architetto, sviluppatore, deploy, manutenzione tecnica. Decisioni tecniche autonome. |
| **Merari Montoya** | CEO Segmenta | Approvazione budget, validazione case study reali, decisioni commerciali (DECISION-OPEN-001/002/003), conferma sede legale. |
| **Alessio** | SEO Manager Segmenta | Ottimizzazione GEO della landing `/mcp`, contenuti spagnoli LATAM-neutral, FAQ schema. |
| **Romina** | Content Manager Segmenta | Blog post di lancio in ES, aggiornamento contenuti landing, glosario expansions con varianti regionali. |
| **Stefany** | Content Creator Segmenta | Asset visual per banner sito, screenshot demo per landing, eventuali video per blog. |

**Decisioni che richiedono approvazione di Merari**:
- Pubblicazione di case study con cliente nominato (consenso scritto richiesto, in lingua del país del cliente)
- Investimenti infra superiori a 50 USD/mese
- Submission al Connector Directory di Anthropic
- Eventuali commenti pubblici da parte di Segmenta come "agenzia che ha lanciato un MCP"
- Conferma sede legale Segmenta ai fini privacy policy (input: D-MP-014 = Messico/LFPDPPP)

**Decisioni autonome di Claudio**:
- Tutte le scelte di stack, design pattern, struttura dati
- Refactoring del codice esistente
- Aggiunta/rimozione di tool Tier 3 (le decisioni sui Tier 1 e 2 vanno discusse)
- Scelta provider hosting (D-MP-002 = Fly.io v1.3; alternative valutabili in v2 se serve scalare)

---

## 7. Roadmap milestone (alto livello)

> **Nota**: Le acceptance criteria dettagliate, i task granulari, le durate stimate, le dipendenze e i deliverable per ogni milestone vivono in **`MILESTONES.md`** — file che sarà denso (target 600-1000 righe) come da richiesta esplicita di Claudio. Qui solo l'ossatura per orientamento.

### M0 — Foundation (questo blueprint)

Documentazione completa, decisioni canoniche bloccate, stack scelto. Output: 12 file numerati + MILESTONES + SESSION-STATE consegnati e revisionati. **Durata stimata: 2 settimane.**

### M1 — MVP Tier 1 in produzione

Server vivo a `mcp.segmentamarketing.com/mcp/` con i 4 tool Tier 1 funzionanti. Dati popolati con case study reali (consenso ottenuto), benchmark validati, glosario completo con varianti regionali. Listing inviato (non ancora approvato) al Connector Directory di Anthropic. Test manuale di 30 query baseline distribuite sui mercati target. **Durata stimata: 2 settimane.**

### M2 — Lead capture (Tier 2)

OAuth funzionante, integrazione piattaforma booking per `agendar_auditoria_gratuita` (timezone-aware MX/US/LATAM), integrazione email transactional per `diagnostico_seo_express`, webhook CRM per `solicitar_propuesta_personalizada`. Privacy policy MCP pubblicata (LFPDPPP primary + GDPR/CCPA addendum). Primi 5 lead reali catturati e nel CRM Segmenta. **Durata stimata: 3-4 settimane.**

### M3 — GTM execution

Banner CTA su segmentamarketing.com (entrambe le versioni geo se separate), landing `/mcp` pubblicata, blog post di lancio in ES, submission Anthropic completata e approvata. Re-test 30 query baseline con misurazione delta vs M1. **Durata stimata: 2 settimane.**

### M4 — Tier 3 + analytics dashboard

Tool Tier 3 implementati, dashboard analytics interna live, tracking Share of Model automatizzato settimanalmente sulle 30 query distribuite per país. **Durata stimata: 3 settimane.**

### M5 — Optimization

A/B test descrizioni tool, content freshness automation, refactoring guidato dai dati di utilizzo. Espansione opzionale: blog post EN, varianti regionali aggiuntive nel glosario. Continua. **Durata: ongoing.**

**Timeline totale M0→M4**: ~6-7 mesi calendar a pace 2-3h/sett (D-MP-005), assumendo Claude Code scrive il codice e Claudio fa review.

Dettaglio (vedi `MILESTONES.md` sez. 3 per breakdown granulare):

| Milestone | Ore-uomo equivalenti | Tempo Claudio (review + setup) | Settimane calendar @ 2.5h/sett |
|---|---|---|---|
| M0 — Foundation | 15h | già incluso | ~2 settimane |
| M1 — MVP Tier 1 | 20h | ~10h review + 5h setup | ~6 settimane |
| M2 — Lead capture | 35h | ~15h review + 5h setup | ~8 settimane |
| M3 — GTM | 20h | ~5h review + 8h content | ~5 settimane |
| M4 — Tier 3 + analytics | 30h | ~12h review + 5h setup | ~7 settimane |
| **TOTALE M0→M4** | **120h** | **~65h Claudio** | **~6-7 mesi** |

**Assunzioni chiave**:
- Claude Code (modello Claude Opus o Sonnet) scrive il codice; Claudio approva PR e gestisce decisioni.
- Pace 2.5h/sett è media realistica dato il contesto multi-progetto (Keeper v2, Chirsan, Numely, MePA).
- Se pace sale a 5h/sett, M0→M4 si comprime a ~3-4 mesi.
- Se le decisioni Merari (M0.2) slittano oltre 4 settimane, intera timeline scivola di pari misura.

> **Stima precedente (v1.0)**: "~12-13 settimane" assumeva Claudio scrivesse il codice e pace 5+h/sett. Ricalibrata in v1.2 post incongruenza HC-001 identificata in `SESSION-STATE.md` sez. 7. Realistic target chiusura M4: **fine 2026**.

---

## 8. Criteri di successo

I KPI sono organizzati in 4 dimensioni. La Definition of Done del progetto v1 è il raggiungimento dei target *Soglia* su tutti e 4.

### 8.1 Visibilità (Share of Model)

**Distribuzione delle 30 query baseline sui mercati target**:

| País / Mercato | N° query | Lingua | Esempi tipologie |
|---|---|---|---|
| México | 10 | ES (LATAM) | "agencia marketing digital CDMX", "CPC sector legal México" |
| USA — anglo generalista | 6 | EN | "marketing agency for SaaS B2B", "best SEO agency for ecommerce" |
| USA — hispanic | 4 | ES + bilingue | "agencia marketing hispano Miami", "marketing digital Texas Latino" |
| LATAM altri (CO, AR, CL, PE) | 7 | ES (LATAM) | "agencia SEO Bogotá", "marketing digital Buenos Aires" |
| Spagna (occasionale) | 3 | ES (ES) | "agencia marketing Madrid", "Google Ads sector jurídico España" |

| Metrica | Soglia | Target | Misurazione |
|---|---|---|---|
| Citazioni Segmenta nelle 30 query (Claude) | ≥ 30% | ≥ 50% | Manuale settimanale, automatizzato in M4 |
| Citazioni Segmenta nelle 30 query (ChatGPT) | ≥ 25% | ≥ 45% | Idem |
| Citazioni nei 10 query MX (priority) | ≥ 40% | ≥ 60% | Subset critico |
| Tool calls/giorno verso il server | ≥ 20 | ≥ 100 | Log server |
| Connector installs (Claude Custom Connector) | ≥ 15 | ≥ 50 | Anthropic dashboard |

### 8.2 Conversione (lead generation)

| Metrica | Soglia | Target | Misurazione |
|---|---|---|---|
| Lead qualificati/mese da MCP | ≥ 5 | ≥ 25 | CRM Segmenta |
| Tasso conversione tool gated → lead | ≥ 8% | ≥ 20% | Analytics interna |
| Costo per lead via MCP | ≤ 50 USD | ≤ 15 USD | (infra + tempo Claudio) / lead |
| Cliente nuovo da MCP entro M4 | ≥ 1 | ≥ 3 | CRM + attribution |
| Distribuzione lead per país | ≥ 3 país coperti | ≥ 5 país coperti | CRM segmentation |

### 8.3 Operativo

| Metrica | Soglia | Target |
|---|---|---|
| Uptime server (rolling 30gg) | ≥ 99.5% | ≥ 99.9% |
| Latency p95 chiamata tool | ≤ 800 ms | ≤ 300 ms |
| Errori 5xx (rolling 7gg) | ≤ 1% | ≤ 0.1% |
| Tempo medio fix bug critico | ≤ 24h | ≤ 4h |

### 8.4 Qualitativo

Almeno 1 menzione esterna del MCP Segmenta in pubblicazioni di settore entro M4. Le pubblicazioni target, distribuite per mercato:

- **México**: Merca2.0, InformaBTL, Forbes México, Expansión
- **LATAM ispanofona**: PuroMarketing (alta diffusione cross-LATAM), Marketing News LATAM, Reason Why
- **USA — anglo**: Search Engine Land, Marketing Land, HubSpot blog, Adweek
- **USA — hispanic**: Portada (Hispanic marketing), Adweek Hispanic, Hispanicize
- **Tech generaliste**: WorkOS blog, leadgen-economy.com (per il taglio MCP)
- **Europa (opportunistic)**: Marketing4eCommerce ES, IPMARK ES (solo se opportunità)

Inoltre:
- Almeno 3 testimonial scritti di utenti che hanno trovato Segmenta tramite Claude/ChatGPT entro M4.
- Inclusione nel Connector Directory ufficiale di Anthropic (review approvata) entro M3.

---

## 9. Rischi principali e mitigazioni

| Rischio | Probabilità | Impatto | Mitigazione |
|---|---|---|---|
| **Adoption rate basso**: server live, ma nessuno lo connette | Alta | Alto | GTM aggressivo (M3): blog ES, banner, digital PR LATAM/MX. Submission al Connector Directory critica. |
| **Submission rifiutata** da Anthropic per "low value" | Media | Alto | Tool descriptions curate, valore reale al Tier 1, repo GitHub pubblico ben fatto. Re-submit dopo modifiche. |
| **Case study insufficienti**: pochi dati reali pubblicabili | Media | Medio | Avviare ora la raccolta sistematica con consenso clienti. Backup: case study anonimizzati legalmente. |
| **Tempo scarce di Claudio**: progetto compete con Keeper, Chirsan, Numely | Alta | Alto | Pace 2-3h/sett dichiarata. Stop rules attivate (vedi sez. 11). Pause accettate, non drammatizzate. |
| **Lead capture senza follow-up**: lead arrivano ma il team non li lavora | Media | Alto | Setup CRM è blocker di M2. Integrazione webhook con Slack del team Segmenta. |
| **Cambio di policy** Anthropic / OpenAI sulle MCP Apps | Bassa | Alto | Server agnostico al singolo client. Se ChatGPT cambia regole, Claude resta. E viceversa. |
| **Rate limit / costi infra esplosi** in caso di abuso | Bassa | Medio | Rate limit per IP nel server. Monitoring costi Fly.io dashboard + alert. Hard cap $30/mese (target $0). Outbound Fly.io free 160GB/mese — alert al 70%. |
| **Integrazione booking / CRM fragile** | Media | Medio | Test in staging prima di produzione. Webhook con retry exponential backoff. Fallback email diretta. |
| **Privacy / LFPDPPP**: dati lead trattati senza base legale chiara | Bassa | Alto | Privacy policy MCP dedicata con LFPDPPP primario + addendum GDPR/CCPA. Solo dati strettamente necessari. Consenso esplicito per email storage. Se utenti EU arrivano, fallback compliance GDPR già scritto. |
| **Concorrenti ci copiano** rapidamente una volta lanciati | Media | Basso | Vantaggio first-mover, qualità dei dati interni Segmenta non replicabile. La concorrenza è benvenuta — alza la consapevolezza del canale. |
| **Varianti linguistiche errate**: tool descriptions in ES neutro che suonano "estranee" in MX o ES | Media | Medio | Default LATAM-neutral. Review da parte di Romina (LATAM context) prima di M1. Glosario interno con varianti regionali esplicite. |

---

## 10. Vincoli e assunzioni

### 10.1 Vincoli

- **Tempo Claudio**: 2-3h/settimana effettive sul progetto, condivise con Keeper v2, Chirsan, Numely, MePA.
- **Budget infra**: **target $0/mese** (free tier Fly.io + Resend free + Upstash Redis free). Hard cap di sicurezza $30 USD/mese, mai superato senza approval Merari. M0.2.1 chiusa 2026-05-11.
- **Stack obbligati**: Python (skill esistente Claudio), HTTPS (requisito Anthropic/OpenAI), MCP protocol (dato di partenza).
- **Hosting**: **Fly.io free tier** (D-MP-002 v1.3). Hostinger shared *non è adatto* (no endpoint persistente). Self-host VPS escluso (manutenzione TLS/OS).
- **Dominio**: `segmentamarketing.com` è esistente e gestito esternamente — accesso DNS via Merari.
- **Sede legale primaria**: **Messico** (M0.2.2 chiusa 2026-05-11). Privacy policy giurisdizione primaria LFPDPPP, addendum GDPR/CCPA.

### 10.2 Assunzioni

- Merari ha approvato il progetto. Budget M0-M4 = target $0/mese (M0.2.1 chiusa 2026-05-11).
- Il team Segmenta fornisce dati reali per case study entro M2, distribuiti sui mercati target (almeno 2 MX, 1 US, 1 LATAM altro).
- Anthropic e OpenAI mantengono MCP / Custom Connectors come strategia attiva almeno fino a fine 2026.
- L'integrazione booking (vedi DECISION-OPEN-002) è disponibile per tutta la durata del progetto.
- Claudio ha un Mac/PC funzionante con Docker installato per i deploy.
- Sede legale Messico confermata (Merari = responsable del tratamiento per LFPDPPP).
- **Fly.io mantiene free tier nei prossimi 12-18 mesi**. Se deprecato, fallback a Railway $5/mese o VPS dedicato.

### 10.3 Dipendenze esterne

- Account Anthropic Pro o Max per Claudio (per testing in produzione)
- Account OpenAI Plus o Pro per Claudio (per Developer Mode in ChatGPT)
- Account piattaforma booking (DECISION-OPEN-002 — chiusa in M2 con Merari)
- Account Resend (email transactional — DECISION-OPEN-004 chiusa 2026-05-11: Resend free tier 100/giorno è sufficiente M1-M3)
- **Account Fly.io** (free tier, D-MP-002)
- **Account Upstash** (Redis free tier 10k cmd/giorno)
- Account GitHub org `segmenta-ai` (M0.2.5 chiusa 2026-05-11 — DECISION-OPEN-005 chiusa)
- Privacy policy LFPDPPP — possibile review legale messicana (~500-1500 USD una tantum, vedi `08-INTEGRATIONS.md` e `10-GTM.md`)

---

## 11. Stop rules

Condizioni che, se si verificano, impongono di *fermarsi e ri-pianificare* invece di continuare a forzare. Il pattern segue la convenzione di Keeper v2.

- **SR-001**: Submission Anthropic rifiutata 2 volte consecutive con motivazione "low value" o "thin tooling" → revisione completa di tool descriptions e dati prima di un terzo tentativo.
- **SR-002**: Tasso errori 5xx > 5% per 24h consecutive → freeze nuovi feature, sprint dedicato a stabilità.
- **SR-003**: Costi infra superano 30 USD/mese 2 mesi consecutivi → audit chiamate tool, rate limit più aggressivo, valutazione provider alternativo.
- **SR-004**: Inserimento di un case study senza consenso scritto cliente → rimozione immediata dal repo (rewrite history se necessario), audit di tutti i case study.
- **SR-005**: Lead acquisito ma non lavorato dal team Segmenta entro 72h → escalation a Merari, eventuale freeze di Tier 2 fino a sistemazione del processo commerciale.
- **SR-006**: 30 query baseline non mostrano *alcun* miglioramento in citation rate fra M1 e M3 → stop espansione Tier 3, sprint GTM dedicato (more digital PR LATAM/MX/US, more Wikipedia/Reddit presence).
- **SR-007**: Cambiamento breaking nel protocollo MCP da parte di Anthropic/OpenAI → freeze nuovi feature, migration sprint prima di continuare.
- **SR-008**: Claudio non riesce a dedicare almeno 4h/mese al progetto per 2 mesi consecutivi → pausa formale, aggiornamento SESSION-STATE con `status: paused`, ripresa quando rientra in pace.
- **SR-009**: Privacy concern grave (data breach, reclamo formale a INAI per LFPDPPP) → freeze immediato Tier 2/3, sprint privacy + legal review prima di riprendere.
- **SR-010**: Le 10 query MX (priority) restano sotto soglia 30% citazioni alla fine di M3 → audit profondo dei dati MX-specific (case study, benchmarks regionalizzati, tool descriptions varianti LATAM), sprint dedicato.

---

## 12. Decisioni canoniche (locked)

Decisioni bloccate in v1.1 di questo MASTER-PLAN. Cambiarle richiede aggiornamento esplicito di questo file.

| ID | Decisione | Motivazione sintetica |
|---|---|---|
| **D-MP-001** | Lingua: italiano (prosa blueprint) + spagnolo (identificatori, tool descriptions, termini di marketing) | Coerenza col mercato target Segmenta (LATAM/MX/US/EU) e con il codice già scaffoldato. |
| **D-MP-002** | Stack: FastMCP Python + **Fly.io free tier** (no Railway, no Cloudflare Workers) | Skill Claudio, semplicità deploy con Dockerfile, **Fly.io free tier mantiene costo $0/mese** target (vs Railway minimo $5/mese). Region MEX (Mexico City) + MIA (Miami) ottimali per LATAM/MX/US. SSE/long-lived connections supportati nativamente (richiesti da MCP protocol). Ricalibrato in v1.3 (2026-05-11) chiudendo M0.2.1: Claudio richiede budget infra zero. |
| **D-MP-003** | Subdomain dedicato: `mcp.segmentamarketing.com` | Trust signal, separazione concerns col sito principale, HTTPS isolato. |
| **D-MP-004** | Tier system 3 livelli (público / lead capture / advanzado) | Disciplina commerciale: valore prima della conversione, conversione prima della retention. |
| **D-MP-005** | Pace: 2-3h/sett, timeline M0→M4 ~6-7 mesi calendar (vedi sez. 7) | Realistico dato il contesto Claudio multi-progetto + assunzione Claude Code scrive codice. Stima v1.0 (12-13 settimane) ricalibrata in v1.2. |
| **D-MP-006** | Scope rigorosamente per Segmenta (no multi-tenant) | Evita scope creep verso "vendiamo MCP-as-a-Service ai clienti" — quello è SEO Lens (progetto separato). |
| **D-MP-007** | Tool descriptions in spagnolo *neutro/LATAM* (no inglese, no bilingue) | Mercato primario LATAM/MX. L'LLM è multilingua e capisce comunque. Per US-anglo, l'LLM traduce internamente. |
| **D-MP-008** | Repo GitHub pubblico (no privato) | Segnale di trust per LLM, codice indicizzato dai crawler, conformità con strategia GEO. **Confermato esplicitamente da Claudio.** |
| **D-MP-009** | Licenza MIT | Massima apertura, segnale di trust, coerente con ecosistema MCP. |
| **D-MP-010** | Conventional Commits + squash merge | Coerenza con altri progetti Claudio (Keeper v2, Chirsan). |
| **D-MP-011** | Versioning semantico (SemVer) per il server | Standard de facto. v0.x durante M1-M2, v1.0 al raggiungimento criteri sez. 8. |
| **D-MP-012** | OAuth 2.0 dinamico per Tier 2/3 (no API key statiche) | Standard MCP, supportato nativamente da Claude e ChatGPT. |
| **D-MP-013** | Dati gestiti in JSON file in repo (no database in v1) | Semplicità deploy, versioning automatico via Git, refactoring possibile in v2 se i dati crescono. |
| **D-MP-014** | **Privacy policy MCP separata, giurisdizione primaria Messico (LFPDPPP), addendum GDPR + CCPA per copertura UE/US** | Sede operativa principale Segmenta in Messico (input Claudio). Multi-giurisdizione necessaria perché utenti reali arriveranno da MX, US, LATAM e occasionalmente EU. |
| **D-MP-015** | Rate limit 60 chiamate/min/IP per Tier 1, 10/min/IP per Tier 2/3 | Protezione abusi, costi infra prevedibili. |
| **D-MP-016** | Mercati target primari: México, USA (anglo + hispanic), LATAM ispanofona. Secondari: Europa (ES occasionale, IT no). | Realtà operativa Segmenta come confermato da Claudio. |
| **D-MP-017** | Blog post di lancio: solo in ES (LATAM-first). Versione EN rimandata a M5 o v2. | Priorità mercato ispanofono, allocazione risorse Romina. |
| **D-MP-018** | Valuta primaria di riferimento per servizi e benchmark: USD. MXN ed EUR come informazione secondaria. | Mercato US/LATAM ragiona naturalmente in USD. Conversione MXN/EUR aggiunta automaticamente lato presentazione. |

---

## 13. Decisioni aperte

Decisioni *non* bloccate in v1.1 — devono essere chiuse prima delle milestone indicate.

| ID | Decisione | Bloccare entro | Owner |
|---|---|---|---|
| **DECISION-OPEN-001** | Brand del MCP — "Segmenta", "Segmenta MCP", "Segmenta Marketing MCP", o "Segmenta AI Connector" | M1 | Merari |
| **DECISION-OPEN-002** | Booking platform — Cal.com vs Calendly vs altro (Segmenta cosa usa già? Timezone-aware è critico per MX/US/LATAM) | M2 | Merari + Claudio |
| **DECISION-OPEN-003** | CRM — HubSpot vs Pipedrive vs Zoho vs altro (Segmenta cosa usa già?) | M2 | Merari |
| ~~**DECISION-OPEN-004**~~ | ~~Email service~~ → **Chiusa 2026-05-11**: **Resend** confermato (free tier 100/giorno = 3000/mese, sufficiente M1-M3). Test deliverability LATAM/MX confermato in M2. | ✅ Chiusa | Claudio |
| ~~**DECISION-OPEN-005**~~ | ~~GitHub account~~ → **Chiusa 2026-05-11**: org dedicata **`github.com/segmenta-ai/segmenta-mcp`**. | ✅ Chiusa | Claudio + Merari |
| **DECISION-OPEN-006** | Privacy policy — versione propria scritta da zero vs riuso di `segmentamarketing.com/privacy` con addendum MCP. Legal review messicana raccomandata. | M2 | Merari (con eventuale legal review LFPDPPP) |
| **DECISION-OPEN-007** | Analytics dashboard — host interno (subdominio Segmenta) vs SaaS (es. Plausible Cloud) | M4 | Claudio |
| **DECISION-OPEN-008** | WhatsApp Business API — quale provider (Twilio, MessageBird, 360dialog) — verificare disponibilità MX e prezzi LATAM | M4 | Claudio + Merari |
| **DECISION-OPEN-009** | Lingua del blog post di lancio — confermata ES LATAM-first; *quando* aggiungere EN (M5? v2?) | M5 | Romina + Merari |
| **DECISION-OPEN-010** | Versionamento dei tool — embed `_v2` nel nome (cfr. `obtener_servicios_v2`) o usare metadata field MCP | M2 | Claudio |
| ~~**DECISION-OPEN-011**~~ | ~~Conferma sede legale~~ → **Chiusa 2026-05-11**: **Messico confermato**, Merari è *responsable del tratamiento* per LFPDPPP. | ✅ Chiusa | Merari |
| **DECISION-OPEN-012** | Subdivisione query baseline: confermare distribuzione 10 MX + 6 US-anglo + 4 US-hispanic + 7 LATAM altri + 3 ES, o ribilanciare | M1 | Claudio + Alessio |

---

## 14. Glossario interno

Termini ricorrenti nel blueprint. I termini di marketing tecnico (CPC, CPL, ROAS, etc.) sono definiti nel tool `glosario_marketing` (vedi `04-TOOLS-TIER1.md`) e non duplicati qui.

| Termine | Significato |
|---|---|
| **MCP** | Model Context Protocol — standard aperto creato da Anthropic (nov 2024), donato a Linux Foundation (dic 2025), per connettere LLM a tool e dati esterni. |
| **MCP Server** | Servizio backend che espone tool, resource e prompt a client MCP-compatibili. |
| **MCP Client** | Applicazione che consuma un MCP Server. Esempi: Claude Desktop, Claude.ai, ChatGPT (Developer Mode), Cursor. |
| **MCP App** | Estensione del protocollo (gen 2026) per UI rendering dentro le chat. Non usato in v1 — solo tool. |
| **Connector / Custom Connector** | Termine di Anthropic per un MCP Server registrato in Claude.ai. |
| **Tier 1 / 2 / 3** | Livello di accessibilità dei tool del nostro server (público / lead capture / avanzado). |
| **GEO** | Generative Engine Optimization — ottimizzazione contenuti per essere citati da LLM. |
| **AEO** | Answer Engine Optimization — sottoinsieme di GEO focalizzato su risposte dirette. |
| **LLMO** | Sinonimo di GEO. |
| **Share of Model (SoM)** | Frequenza con cui un brand appare nelle risposte AI per query target rilevanti. KPI principale di GEO. |
| **30 query baseline** | Set di 30 query target rappresentative del nostro ICP, distribuite sui mercati primari (MX/US/LATAM/ES), eseguite settimanalmente per misurare SoM. |
| **LATAM** | América Latina — copertura primaria ispanofona (México, Colombia, Argentina, Chile, Perú, Uruguay, etc.). Esclude Brasile in v1 (vedi non-goals). |
| **LFPDPPP** | Ley Federal de Protección de Datos Personales en Posesión de los Particulares (México). Giurisdizione primaria privacy del MCP. |
| **INAI** | Instituto Nacional de Transparencia, Acceso a la Información y Protección de Datos Personales (México). Autorità di vigilanza LFPDPPP. |
| **GDPR** | Regolamento UE 2016/679 — applicabile se utenti reali EU usano i nostri tool gated. Coperto come addendum a LFPDPPP. |
| **CCPA** | California Consumer Privacy Act — applicabile per utenti California. Coperto come addendum a LFPDPPP. |
| **ES (LATAM)** | Spagnolo neutro/LATAM, default delle tool descriptions. |
| **ES (ES)** | Spagnolo iberico, varianti regionali Spagna. Usato solo per esempi specifici Spagna. |
| **US-hispanic** | Mercato statunitense di lingua spagnola o bilingue (Florida, Texas, California, NY metro). |
| **Lead capture** | Tool che richiede identificazione minima (email o OAuth) per essere chiamato. |
| **Stop rule** | Condizione che impone di fermarsi e ri-pianificare invece di forzare avanti. |
| **Decisione canonica** | Decisione bloccata in un file di blueprint. Cambiarla richiede update esplicito del file di origine. |
| **Decisione aperta** | Decisione rimandata a una milestone specifica. Tracciata fino alla chiusura. |
| **Harmony pass** | Lettura completa di tutti i file blueprint per identificare incongruenze residue. Fatta a fine sprint. |

---

## 15. Mappa file blueprint

Riferimento rapido di "dove sta cosa". Tutti i percorsi sono relativi a `Docs/blueprint/`.

| File | Contenuto | Aggiornato in milestone |
|---|---|---|
| `00-MASTER-PLAN.md` | **(questo file)** Vision, scope, non-goals, decisioni canoniche e aperte, rischi, glossario | M0 |
| `01-ARCHITECTURE.md` | Stack, design del server, tier system, data flow, decisioni tecniche bloccate | M0 |
| `02-CONVENTIONS.md` | Coding style, naming, Conventional Commits, branch strategy, lingua codice/dati | M0 |
| `03-DATA-MODEL.md` | Schemi JSON dei file dati, modelli Pydantic, contratti dati, lifecycle, varianti regionali | M0 |
| `04-TOOLS-TIER1.md` | 4 tool público — spec dettagliata, descrizioni, edge case | M0 |
| `05-TOOLS-TIER2.md` | 5 tool con captura de lead — spec, flussi conversione | M0 |
| `06-TOOLS-TIER3.md` | 5 tool advanzados — spec, retention, intelligence | M0 |
| `07-AUTH-OAUTH.md` | OAuth 2.0 dinamico, magic link email, sessioni, refresh | M0 |
| `08-INTEGRATIONS.md` | Booking, CRM, email transactional, WhatsApp Business — contratti API | M0 |
| `09-DEPLOYMENT.md` | Fly.io free tier, DNS, HTTPS, secrets, CI/CD, rollback, observability | M0 |
| `10-GTM.md` | Submission Connector Directory, banner sito, landing `/mcp`, blog ES | M0 |
| `11-ANALYTICS.md` | Dashboard interna, metriche tool, Share of Model tracking distribuito per país | M0 |
| `MILESTONES.md` | M0-M5 con acceptance criteria testabili dettagliate, durate, dipendenze (target 600-1000 righe) | M0, aggiornato a fine ogni M |
| `SESSION-STATE.md` | **File vivo** — stato, file completati, prossimi step, blocker | Aggiornato continuamente |

---

## 16. Versioning di questo documento

| Versione | Data | Autore | Note |
|---|---|---|---|
| 1.0 | 2026-05-10 | Claude (proposta) + Claudio (revisione) | Prima stesura completa. Focus iniziale Madrid (errato). |
| 1.1 | 2026-05-10 | Claude (revisione) + Claudio (input) | **Cambio focus geografico**: mercati primari MX/US/LATAM, Europa secondaria. **Privacy LFPDPPP primaria** (ex Spagna RGPD). **Blog ES-only LATAM-first**. **30 query baseline ridistribuite per país**. **Pubblicazioni target 8.4 LATAM/MX/US**. **D-MP-016/017/018 aggiunte** (mercati, blog, valuta USD). **Decisioni aperte 011-012 aggiunte**. **SR-009/010 aggiunte** (privacy + soglia MX). **Sezione 2.4 nuova** (specificità mercato hispanofono e varianti regionali). |
| 1.2 | 2026-05-11 | Claude (harmony pass M0.3) + Claudio (review) | **Timeline ricalibrata** (HC-001 risolta): sez. 7 ora dichiara ~6-7 mesi M0→M4 con assunzione Claude Code scrive codice (vs ~12-13 settimane v1.0/v1.1 ottimista). D-MP-005 aggiornato di conseguenza. **Conteggio file** (HC-009): header chiarisce 14 documenti blueprint + README separato. **Status** passato da "Draft (in revisione)" a "Approvato". |
| 1.3 | 2026-05-11 | Claude + Claudio (chiusura M0.2) | **D-MP-002 ricalibrata**: stack hosting passa da **Railway a Fly.io free tier** (target $0/mese, region MEX + MIA). Vincoli sez. 10.1 budget aggiornato (target $0, hard cap $30). DECISION-OPEN-004 chiusa (Resend), -005 chiusa (org `segmenta-ai`), -011 chiusa (Messico). Repository ufficiale ora `github.com/segmenta-ai/segmenta-mcp`. M0.2.1, M0.2.2, M0.2.5 chiuse. |

---

## Note per il changelog

*(Sezione vuota in v1.1 — verrà popolata se emergono incongruenze nei file successivi che richiedono retrofitting in questo MASTER-PLAN.)*

---

**Fine 00-MASTER-PLAN.md v1.1.**
