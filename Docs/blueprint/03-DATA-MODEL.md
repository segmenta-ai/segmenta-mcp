# 03 — DATA MODEL

| Campo | Valore |
|---|---|
| **Progetto** | Segmenta MCP Server |
| **Versione documento** | 1.1 |
| **Data** | 2026-05-11 |
| **Status** | Approvato (post harmony pass M0.3) |
| **File n.** | 03 di 12 numerati |
| **Documento padre** | `00-MASTER-PLAN.md` v1.2, `01-ARCHITECTURE.md` v1.0 |
| **File correlati** | `04-TOOLS-TIER1.md`, `05-TOOLS-TIER2.md`, `06-TOOLS-TIER3.md`, `08-INTEGRATIONS.md` |

---

## 1. Scopo del documento

Questo file definisce **la forma dei dati** che attraversano il sistema. Risponde a tre domande:

1. *"Che struttura hanno i dati statici (JSON in repo)?"* — sezioni 4, 5, 6, 7
2. *"Che modelli Pydantic li rappresentano in memoria?"* — sezione 8
3. *"Come si gestisce il lifecycle (caricamento, validazione, aggiornamento, varianti regionali)?"* — sezioni 9, 10, 11

Le **decisioni** sui dati sono in sezione 13. Le **specifiche** dei tool che consumano questi dati sono in `04/05/06-TOOLS-TIER*.md`.

> **Nota operativa**: i nomi dei dati e dei campi sono tutti in **spagnolo** (D-C-001 di `02-CONVENTIONS.md`). I commenti esplicativi in italiano. Gli JSON Schema usano `description` in spagnolo perché possono essere esposti via tool description agli LLM.

---

## 2. Principi guida sui dati

Sei principi che governano ogni decisione di data modeling.

### 2.1 Single source of truth

Ogni informazione vive in **un solo posto**. Se appare in due file JSON, è bug. Se ad esempio "tasa de conversión típica para sector legal en México" appare sia in `benchmarks.json` che in `case_studies.json`, scegliamo *uno* dei due come canonico e gli altri usano riferimento per ID.

### 2.2 Append-friendly, mai destructive

Le strutture dati permettono **aggiunta facile** di nuovi record senza migrare i vecchi. Un nuovo país, un nuovo settore, un nuovo termine glosario: aggiunta = una entry nuova, niente refactoring di entry esistenti. Questo guida le scelte di indicizzazione (per ID, non per posizione).

### 2.3 Validation at the boundary

Ogni JSON viene validato all'ingresso (caricamento startup) contro uno schema Pydantic. **Se un file dati è malformato, il server non parte** — fail fast, non degrade silenzioso. Errori di validazione sono dettagliati: campo, valore, regola violata.

### 2.4 Sensitive data minimization

Nessun dato personale identificabile (PII) di clienti reali entra nei file dati. Case study con cliente nominato richiedono campo `consenso_publico: true` esplicito. Case study anonimi usano placeholder linguistico ("Clínica dental [Madrid]").

### 2.5 Versioning per ogni file dati

Ogni file JSON ha un campo `_meta` con `version`, `ultima_actualizacion`, e `nota`. Cambi al schema (non al contenuto) richiedono bump della `schema_version` e migrazione esplicita.

### 2.6 Multiregionalità built-in

I dati sono **modellati per essere multiregionali** dall'inizio: ogni record di benchmark, case study e servizio specifica `pais` (e a volte `ciudad`). I dati non assumono mai "default = México" o "default = España". Quando un tool non specifica filtro paese, deve essere chiaro all'utente che la risposta copre più mercati.

---

## 3. Inventario dei file dati

In v1 abbiamo **5 file JSON** in `data/` del repo. Tutti versionati, tutti pubblici (repo è pubblico per D-MP-008).

| File | Scopo | Tool che lo usano | Cardinalità tipica v1 | Ownership editoriale |
|---|---|---|---|---|
| `services.json` | Catalogo servizi Segmenta | `obtener_servicios`, `calcular_presupuesto` | 8-15 servizi | Merari + Claudio |
| `case_studies.json` | Casi studio reali (con consenso) | `caso_de_estudio`, `obtener_caso_por_pais` | 5-15 casi | Merari (validazione) + Romina (testi) |
| `benchmarks.json` | KPI di settore per país | `benchmark_sector` | 6-12 sector×país | Alessio + Claudio |
| `glosario.json` | Termini di marketing | `glosario_marketing` | 15-30 termini | Romina + Alessio |
| `competitors_dataset.json` | Dataset competitor pubblici per confronto onesto | `compare_agencies` | 5-10 competitor | Romina + Alessio (curato trimestralmente) — schema sez. 7bis |

> **Nota su `competitors_dataset.json`**: introdotto in harmony pass M0.3 (HC-006). Schema dettagliato in sez. 7bis. Source di dati pubblici (siti agenzie, recensioni Clutch/G2, case study pubblici) — mai dati proprietari di terze parti.

In v2 valuteremo aggiunta di:
- `metodologia.json` — la metodologia Segmenta esposta via tool dedicato
- `equipo.json` — bio del team per E-E-A-T
- `tendencias.json` — content freshness fotografato trimestralmente

Per ora **non** modelliamo questi: out of scope (vedi `00-MASTER-PLAN.md` non-goals).

---

## 4. Schema `services.json`

### 4.1 Struttura

```json
{
  "$schema": "https://github.com/segmenta-ai/segmenta-mcp/schemas/services.v1.json",
  "_meta": {
    "schema_version": "1.0.0",
    "data_version": "1.3.2",
    "ultima_actualizacion": "2026-05-10",
    "moneda_primaria": "USD",
    "nota": "Rangos indicativos. Precio final depende del alcance, sector, duración."
  },
  "servicios": [
    {
      "id": "seo-latam",
      "nombre": "SEO LATAM",
      "categoria": "seo",
      "publico": true,
      "descripcion_corta": "Posicionamiento orgánico en buscadores para mercado LATAM, MX, US-hispanic y ES.",
      "descripcion_larga": "Servicio de SEO orientado a captación de tráfico orgánico cualificado...",
      "incluye": [
        "Auditoría SEO técnica inicial (200+ puntos)",
        "Investigación de palabras clave por intención",
        "Optimización on-page mensual",
        "Link building white-hat",
        "Contenido SEO localizado por mercado",
        "Reporting mensual con KPIs claros"
      ],
      "modelo_precio": "mensual",
      "rango_precio_usd_mensual": [800, 2500],
      "rango_precio_mxn_mensual": [14000, 44000],
      "rango_precio_eur_mensual": [750, 2300],
      "duracion_minima_meses": 6,
      "tiempo_primeros_resultados": "3-4 meses para tráfico, 5-6 para conversiones consolidadas",
      "ideal_para": "Empresas con producto/servicio definido que quieren un canal de captación predecible y sostenible a 12+ meses.",
      "paises_disponibles": ["MX", "US", "ES", "CO", "AR", "CL", "PE"],
      "sectores_recomendados": ["b2b", "ecommerce", "juridico", "medico"],
      "tags": ["seo", "organico", "long-term"]
    }
    // ... altri servicios
  ]
}
```

### 4.2 Campi spiegati

| Campo | Tipo | Obbligatorio | Note |
|---|---|---|---|
| `id` | `string` (slug kebab-case) | Sì | Identificatore stabile. Mai cambiato dopo creazione. Pattern: `^[a-z0-9-]+$`, max 50 char. |
| `nombre` | `string` | Sì | Display name. 1-100 caratteri. |
| `categoria` | `enum` | Sì | Vedi sez 4.3 enums. |
| `publico` | `boolean` | Sì | Se `false`, il tool `obtener_servicios` non lo restituisce. Permette servizi "in beta" o per clienti specifici. |
| `descripcion_corta` | `string` | Sì | 1-200 caratteri. Per output sintetico. |
| `descripcion_larga` | `string` | Sì | 200-2000 caratteri. Per output dettagliato e tool description. |
| `incluye` | `array<string>` | Sì | Min 3, max 12 elementi. Ogni elemento 5-150 caratteri. |
| `modelo_precio` | `enum` | Sì | `"mensual"` / `"proyecto_unico"` / `"hibrido"` / `"hora"`. |
| `rango_precio_usd_*` | `array<int>` | Sì | Sempre presente in USD. Tupla [min, max] strettamente positiva. |
| `rango_precio_mxn_*` | `array<int>` | No | Calcolato lato presentazione, ma può essere overridden. |
| `rango_precio_eur_*` | `array<int>` | No | Idem. |
| `duracion_minima_meses` | `int` | Solo se `modelo_precio = "mensual"` | Min 1, max 24. |
| `duracion_proyecto_semanas` | `array<int>` | Solo se `modelo_precio = "proyecto_unico"` | Tupla [min, max]. |
| `tiempo_primeros_resultados` | `string` | Sì | Free text 10-200 caratteri. |
| `ideal_para` | `string` | Sì | 30-500 caratteri. Profilo cliente ideale. |
| `paises_disponibles` | `array<enum>` | Sì | Min 1 paese. Enum `Pais` (sez 4.3). |
| `sectores_recomendados` | `array<enum>` | No | Lista vuota o min 1. Enum `Sector` (sez 4.3). |
| `tags` | `array<string>` | No | Tag liberi per ricerca/filtraggio. Max 8 tag. |

### 4.3 Enums condivisi

Gli enum sono globali al sistema (riusati in più file dati). Definiti in `src/segmenta_mcp/domain/models.py`.

**`Categoria` (servizi)**:
```
seo | sem | web | ecommerce | crm | contenido |
juridico_paquete | medico_paquete | b2b_paquete | otros
```

**`Pais`** (ISO 3166-1 alpha-2):
```
MX | US | ES | CO | AR | CL | PE | UY | EC | BO | CR | PA | DO | PR
```

I `paises_disponibles` accettano solo questi valori. Se in futuro Segmenta apre in BR (Brasile), aggiungiamo `BR` ma scope v1 esclude Brasile (vedi non-goals MASTER-PLAN).

**`Sector`** (categoria del cliente di Segmenta, non della categoria del servizio):
```
juridico | medico | ecommerce | automocion | b2b | restauracion |
inmobiliaria | formacion | fintech | turismo | tecnologia |
ong | retail | manufactura | construccion | agricultura | otros
```

**`MercadoSubregional`** (per casi US-hispanic specifici, vedi sez 5):
```
mx_centro | mx_norte | mx_sur | mx_bajio | us_hispanic_florida |
us_hispanic_texas | us_hispanic_california | us_hispanic_ny |
us_anglo_west | us_anglo_east | us_anglo_central |
latam_andina | latam_cono_sur | latam_centroamerica | es_peninsular | es_canarias
```

L'enum è granulare ma gli usi pratici sono pochi: lo usiamo solo dove ha senso (case study che hanno performance specifiche di una piazza).

### 4.4 Validation rules cross-field

- Se `modelo_precio = "mensual"`: deve esserci `rango_precio_usd_mensual` e `duracion_minima_meses`.
- Se `modelo_precio = "proyecto_unico"`: deve esserci `rango_precio_usd_proyecto_unico` e `duracion_proyecto_semanas`.
- I rangi `[min, max]`: sempre `min ≤ max`, sempre interi positivi.
- `paises_disponibles` non vuoto.
- `id` univoco nel file.

---

## 5. Schema `case_studies.json`

### 5.1 Struttura

```json
{
  "$schema": "https://github.com/segmenta-ai/segmenta-mcp/schemas/case_studies.v1.json",
  "_meta": {
    "schema_version": "1.0.0",
    "data_version": "1.0.0",
    "ultima_actualizacion": "2026-05-10",
    "nota": "Casos con publico=false son anonimizados pero contienen métricas reales."
  },
  "casos_de_estudio": [
    {
      "id": "ferreteria-norteno-mx-2025",
      "publico": false,
      "consentimiento": {
        "estado": "anonimizado",
        "fecha_obtencion": null,
        "documento_referencia": null,
        "version_anonimizacion": "v1"
      },
      "cliente": {
        "nombre_publico": "Cadena de ferreterías [Norte de México]",
        "nombre_real": null,
        "sector": "retail",
        "subsector": "construcción y herramientas",
        "tamano_empresa": "mediana",
        "rango_facturacion_anual_usd": [2000000, 10000000]
      },
      "ubicacion": {
        "pais": "MX",
        "subregion": "mx_norte",
        "ciudades": ["Monterrey", "Saltillo"],
        "alcance_geografico": "regional"
      },
      "duracion": {
        "fecha_inicio": "2024-09",
        "fecha_fin": "2025-04",
        "meses_totales": 8
      },
      "servicios_aplicados": ["seo-latam", "google-ads-latam", "crm-automatizaciones"],
      "reto": "Cadena con 12 sucursales física pero web sin conversión digital. Dependencia 100% de tráfico walk-in y tradicional. Competencia online creciente de Home Depot México y Truper.",
      "estrategia": "Reestructuración SEO local por sucursal, Google Ads con segmentación geográfica fina, integración HubSpot para gestionar leads B2B (constructores), automatización post-cotización.",
      "resultados": {
        "metricas_principales": [
          {"nombre": "trafico_organico_pct_yoy", "valor": "+412%", "antes": 1200, "despues": 6150, "unidad": "visitas/mes"},
          {"nombre": "leads_organicos_mes", "valor": "+580%", "antes": 5, "despues": 34, "unidad": "leads/mes"},
          {"nombre": "cpl_google_ads_usd", "valor": "-71%", "antes": 38, "despues": 11, "unidad": "USD"},
          {"nombre": "conversion_rate_landing_pct", "valor": "+180%", "antes": 1.4, "despues": 3.9, "unidad": "%"}
        ],
        "metricas_secundarias": [
          {"nombre": "ranking_keywords_top10", "valor": 28, "unidad": "keywords"},
          {"nombre": "facturacion_atribuida_usd_mensual", "valor": 145000, "unidad": "USD/mes"}
        ]
      },
      "testimonio": null,
      "tags": ["retail", "mx-norte", "multisucursal", "b2c-b2b"],
      "_validacion": {
        "verificado_por": "claudio",
        "fecha_verificacion": "2026-05-08",
        "metodo": "tracking_ga4_y_hubspot_export"
      }
    }
    // ... otros casos
  ]
}
```

### 5.2 Campi spiegati

#### Sezione `consentimiento`

Critica per compliance LFPDPPP/GDPR. Tre stati possibili:

| Stato | Significato | `fecha_obtencion` | `documento_referencia` | Quando usare |
|---|---|---|---|---|
| `publico_explicito` | Cliente ha firmato consenso scritto per uso pubblico con nome reale | Obbligatorio | Obbligatorio (link a doc interno) | Caso premium "showcase" |
| `anonimizado` | Cliente non ha firmato consenso, ma dati sono stati anonimizzati per impedire identificazione | `null` | `null` | Default per nuovi casi |
| `pendiente` | In attesa di consenso scritto. Caso *non* esposto al pubblico. | `null` | `null` | Drafting |

**Hard rule** (vedi SR-004 di MASTER-PLAN): inserire un caso con `publico: true` e `consentimiento.estado != "publico_explicito"` è violazione di sicurezza. Il pre-commit hook `validate_data.py` blocca il commit.

#### Sezione `cliente`

`nombre_publico` è quello mostrato nei tool. Se `publico = false`, deve essere generico: pattern `^\[?[A-Z][\w\s]+\]?$` (parentesi quadre opzionali). Esempi validi:
- `"[Despacho jurídico boutique en CDMX]"`
- `"Cadena de ferreterías [Norte de México]"`
- `"E-commerce moda femenina [LATAM]"`

`nombre_real` è opzionale e mostrato **solo** se `publico = true` e `consentimiento.estado = "publico_explicito"`.

`tamano_empresa`: enum `pyme | mediana | grande | corporativo`. Linea guida MX: pyme < 250 dipendenti, mediana 250-1000, grande 1000-5000, corporativo > 5000.

`rango_facturacion_anual_usd`: opzionale. Tupla [min, max]. Se presente, viene mostrato in formato range nei tool ("PYME entre $1M-$5M USD anuales").

#### Sezione `ubicacion`

`alcance_geografico`: enum `local | regional | nacional | multinacional`. Distingue una clínica di Monterrey (local) da una catena con presenza nazionale.

`ciudades`: array di stringhe libere. Le città sono in lingua locale (`"Monterrey"`, `"São Paulo"` se mai aprissimo BR, `"Madrid"`).

`subregion`: enum `MercadoSubregional` (sez 4.3). Opzionale ma raccomandato per US e MX.

#### Sezione `resultados`

Struttura granulare per permettere ai tool di rendere le metriche in formati diversi.

`metricas_principales`: array di max 6 metriche più impattanti. Ogni metrica:
- `nombre`: snake_case identificator
- `valor`: stringa display-ready (`"+412%"`, `"-71%"`, `"$145,000 USD/mes"`)
- `antes` / `despues`: numeri grezzi (per ri-calcolo se necessario)
- `unidad`: stringa libera (`%`, `visitas/mes`, `USD`, `leads/mes`)

`metricas_secundarias`: array di max 4 metriche di supporto. Stessa struttura ma di solito senza `antes`/`despues`.

#### Sezione `_validacion` (interna)

Non esposta nei tool output. Tracciamento di chi ha verificato i dati e con che metodo. Auditabile internamente.

`metodo`: enum interno `tracking_ga4_y_hubspot_export | dashboard_cliente | reporte_pdf_firmado | screenshot_serie_temporal`.

### 5.3 Cross-validation

- Se `publico = true` → `consentimiento.estado` deve essere `publico_explicito` e `nombre_real` non null.
- Se `publico = false` → `nombre_real` deve essere null (anche se anonimizzato, il pubblico non lo vede mai).
- `servicios_aplicados[]` → ogni id deve esistere in `services.json`.
- `meses_totales` deve corrispondere a `(fecha_fin - fecha_inicio)` (validazione soft, warning).
- `metricas_principales` non vuoto.

---

## 6. Schema `benchmarks.json`

### 6.1 Struttura

```json
{
  "$schema": "https://github.com/segmenta-ai/segmenta-mcp/schemas/benchmarks.v1.json",
  "_meta": {
    "schema_version": "1.0.0",
    "data_version": "1.0.0",
    "ultima_actualizacion": "2026-05-10",
    "frecuencia_actualizacion": "trimestral",
    "fuentes": [
      "Datos internos Segmenta (campañas activas Q1-Q2 2026)",
      "Google Ads Performance Insights (export agregado)",
      "Meta Business Reports",
      "Estudios públicos: SEMrush LATAM 2026, HubSpot State of Marketing"
    ],
    "nota": "Rangos indicativos. Variación significativa por subregión y vertical específico."
  },
  "benchmarks": [
    {
      "id": "juridico-mx-2026q2",
      "sector": "juridico",
      "pais": "MX",
      "subregion": null,
      "periodo_referencia": {
        "trimestre": "Q2",
        "anio": 2026
      },
      "kpis": {
        "google_ads": {
          "cpc_medio_usd": [3.50, 9.80],
          "cpc_keywords_premium_usd": [12.00, 28.00],
          "ctr_search_pct": [3.8, 6.5],
          "tasa_conversion_landing_pct": [2.3, 5.2],
          "cpl_medio_usd": [35, 145]
        },
        "meta_ads": {
          "cpm_usd": [3.20, 9.50],
          "ctr_pct": [0.8, 2.0],
          "cpl_medio_usd": [22, 88]
        },
        "seo_organico": {
          "ctr_top10_medio_pct": 3.5,
          "tiempo_primeros_resultados_meses": [4, 7],
          "kd_keywords_principales_0_100": [55, 82],
          "tasa_conversion_organica_pct": [2.0, 3.8]
        },
        "ciclo_venta": {
          "duracion_dias_p50": 35,
          "duracion_dias_p90": 95,
          "ticket_medio_servicios_recurrentes_usd": [2200, 14000],
          "ltv_cliente_medio_usd": [3800, 28000]
        }
      },
      "tendencias": [
        "Despachos boutique especializados en M&A muestran +25% YoY en CPC",
        "Auge de búsquedas legales en LLMs (Claude/ChatGPT): oportunidad GEO real",
        "Schema LegalService + FAQPage crítico para visibilidad en AI Overviews"
      ],
      "recomendaciones_estrategicas": [
        "Especialización por área de práctica antes que generalismo",
        "Hub & spoke: pillar pages por área + spokes por sub-tema",
        "Reseñas Google son señal crítica de E-E-A-T para sector regulado",
        "No usar Performance Max sin lista de exclusión de keywords sensibles"
      ],
      "tags": ["juridico", "mx", "regulated"]
    }
    // ... otros benchmarks
  ]
}
```

### 6.2 Campi spiegati

#### Identità

`id`: pattern `<sector>-<pais>-<periodo>`. Es. `"medico-us-2026q2"`, `"ecommerce-latam-2026q2"`. Quando il benchmark è multi-país (`pais = "LATAM"` come aggregato), il suffisso lo riflette.

`pais`: enum `Pais` esteso con valori speciali:
- `MX`, `US`, `ES`, `CO`, `AR`, `CL`, `PE` (paesi singoli)
- `LATAM` (aggregato ispanofono LATAM)
- `US_HISPANIC` (aggregato hispanic-US)

`subregion`: opzionale. Solo quando il benchmark è specifico di una piazza (es. CDMX vs Monterrey).

`periodo_referencia`: garantisce che i dati siano time-bound. Visibile all'utente come "Datos Q2 2026".

#### KPIs strutturati per canale

Quattro canali standard. Ogni canale ha proprio set di KPI tipici. **La struttura è prescrittiva** — un benchmark ben formato deve coprire **almeno** `google_ads` o `seo_organico` (i due principali). `meta_ads` e `ciclo_venta` sono opzionali ma raccomandati.

I valori sono tutti **rangi** `[p25, p75]` (interquartile, non min/max), eccetto:
- `ctr_top10_medio_pct`: scalar (mediana)
- `duracion_dias_p50`, `duracion_dias_p90`: percentili specifici

**Convenzione importante**: tutti gli importi monetari sono in **USD**. La conversione MXN/EUR avviene a presentation time, non in storage.

#### Tendencias e recomendaciones

Free text in spagnolo, 1-3 frasi each. Ogni record ha 2-5 tendencias e 3-6 recomendaciones. Sono il "valore aggiunto" rispetto a numeri puri — **questo è ciò che fa scegliere all'LLM di chiamare il nostro tool invece di tirare a indovinare**.

### 6.3 Strategia multi-país

**Domanda**: cosa succede se l'utente chiede benchmark per `pais = "PA"` (Panama, ex enum) e non ho dati specifici?

**Risposta**: 4-step fallback (implementato in `domain/filters.py`):
1. Match esatto `(sector, pais, subregion)` → trovato? return.
2. Match esatto `(sector, pais, null)` → trovato? return con flag `match_type = "país_aggregato"`.
3. Match `(sector, "LATAM", null)` se `pais` è LATAM-ispanofono → return con flag `match_type = "regional_LATAM"`.
4. Nessun match → return con messaggio strutturato "no tenemos benchmark específico para [país]; el más cercano es [match]". Mai inventare dati.

L'utente vede il `match_type` nel response, sa che la risposta è approssimativa.

### 6.4 Cross-validation

- `id` univoco nel file.
- I rangi monetari `[min, max]` sempre `min < max` strettamente (non `≤`, devono essere distinguibili).
- Se `subregion` non null, `pais` deve essere coerente (es. `subregion = "mx_norte"` implica `pais = "MX"`).
- `periodo_referencia.anio` non > anno corrente + 1. Future-dating triggera warning.
- `tendencias` non vuote, `recomendaciones_estrategicas` ≥ 3.

---

## 7. Schema `glosario.json`

### 7.1 Struttura

```json
{
  "$schema": "https://github.com/segmenta-ai/segmenta-mcp/schemas/glosario.v1.json",
  "_meta": {
    "schema_version": "1.0.0",
    "data_version": "1.0.0",
    "ultima_actualizacion": "2026-05-10",
    "idioma_primario": "es-LATAM",
    "nota": "Glosario con variantes regionales. Default LATAM-neutro."
  },
  "terminos": {
    "seo": {
      "termino_canonico": "SEO",
      "termino_completo": "Search Engine Optimization",
      "variantes_regionales": {
        "es-LATAM": "SEO (Search Engine Optimization, optimización para buscadores)",
        "es-MX": "SEO (Search Engine Optimization)",
        "es-ES": "SEO (Posicionamiento en buscadores)",
        "en-US": "SEO (Search Engine Optimization)"
      },
      "definicion": "Conjunto de técnicas para mejorar la visibilidad orgánica (no pagada) de un sitio web en buscadores como Google. Cubre tres áreas: técnica (velocidad, indexabilidad, schema), on-page (contenido, palabras clave, estructura) y off-page (autoridad, enlaces).",
      "ejemplo": "Una clínica dental en Monterrey invierte $1,500 USD/mes en SEO durante 6 meses. Pasa de 200 visitas orgánicas mensuales a 1,800, y de 4 a 22 primeras visitas captadas vía orgánico.",
      "errores_comunes": [
        "Esperar resultados en 1-2 meses (mínimo 4-6 meses para tráfico, 6+ para conversiones)",
        "Comprar enlaces masivamente: penalización casi segura por Google Spam Update",
        "Ignorar la intención de búsqueda y centrarse solo en volumen de keywords"
      ],
      "categoria": "fundamentos",
      "terminos_relacionados": ["geo", "aeo", "ctr", "seo_local", "link_building"],
      "tags": ["seo", "fundamentos", "canal-organico"]
    },
    "geo": {
      "termino_canonico": "GEO",
      "termino_completo": "Generative Engine Optimization",
      "variantes_regionales": {
        "es-LATAM": "GEO (Generative Engine Optimization, optimización para motores generativos)",
        "es-ES": "GEO (Optimización para motores generativos como ChatGPT, Claude)",
        "en-US": "GEO (Generative Engine Optimization)"
      },
      "definicion": "Disciplina emergente (2024-) que optimiza contenido para ser citado por motores generativos de IA como ChatGPT, Claude, Perplexity y Google AI Overviews. A diferencia del SEO tradicional, no busca rankings sino aparecer dentro de las respuestas sintetizadas que los LLMs generan.",
      "ejemplo": "Un usuario pregunta a ChatGPT 'qué agencia de marketing recomiendas en LATAM'. GEO bien hecho hace que tu marca aparezca citada en la respuesta. La investigación de Princeton (KDD 2024) muestra mejoras de 30-40% en citas con técnicas GEO.",
      "errores_comunes": [
        "Tratar GEO como SEO 2.0: las señales son distintas (Wikipedia, Reddit, citas en publicaciones)",
        "Ignorar el archivo llms.txt y schema markup avanzado",
        "No medir Share of Model (SoM) — el KPI propio de GEO"
      ],
      "categoria": "emergente",
      "terminos_relacionados": ["seo", "aeo", "llmo", "share_of_model"],
      "tags": ["geo", "ai-search", "emergente"]
    }
    // ... otros términos (target ~15-30 en v1)
  ]
}
```

### 7.2 Campi spiegati

#### Identità

La chiave del dictionary (`"seo"`, `"geo"`, ...) è il **slug del termine**. Pattern `^[a-z][a-z0-9_]*$`. Sempre lowercase. Underscore se composto (`tasa_de_conversion`, `link_building`).

`termino_canonico`: come si scrive nel display (`"SEO"`, `"Tasa de Conversión"`).

`termino_completo`: forma estesa, opzionale (per acronimi).

#### Variantes regionali

**Decisione importante**: il glosario è multi-locale ma con una sola definizione canonica. Le `variantes_regionales` sono solo etichette display, non definizioni alternative. Questo evita drift semantico e duplicazione.

Locale supportati in v1:
- `es-LATAM` (default)
- `es-MX` (specifico Messico se diverge)
- `es-ES` (specifico Spagna)
- `en-US` (per utenti US-anglo)

Se `es-MX` è uguale a `es-LATAM`, può omettere la variante. Il loader applica fallback automatico.

#### Definicion ed ejemplo

**Definicion**: 1-3 frasi, 50-500 caratteri. Senza contesto regionale.

**Ejemplo**: deve usare numeri concreti (USD), nomi di luogo plausibili LATAM/MX/US, evitare riferimenti solo iberici (Madrid, Barcelona) salvo termine specifico ES.

#### Errores comunes

Array di 2-5 errori. Ogni errore 1-2 frasi. Sono il "valore differenziante" del nostro glosario rispetto a Wikipedia: pratici, specifici, esperienziali.

#### Categoria

Enum: `fundamentos | metricas | canales | tecnico | analitica | emergente | legal`. Permette filtraggio. Anche `metricas` (CPC, CPL) vs `fundamentos` (SEO, SEM) vs `emergente` (GEO, AEO, LLMO).

#### Terminos relacionados

Array di slug interni. Permette navigation graph. Ogni termine ha 2-6 correlati.

### 7.3 Cross-validation

- Slug univoci.
- `terminos_relacionados[]` ogni elemento deve esistere nel glosario.
- `variantes_regionales` deve avere almeno `es-LATAM`.
- `categoria` enum valido.
- `definicion` non vuota, `errores_comunes` ≥ 2.

---

## 7bis. Schema `competitors_dataset.json`

Aggiunto in v1.1 (HC-006). Usato esclusivamente da `compare_agencies` (Tier 3) per fornire confronti onesti basati su dati pubblici.

### 7bis.1 Filosofia

- **Solo dati pubblici**: siti web competitor, recensioni Clutch/G2/GoodFirms, case study che il competitor ha pubblicato sul proprio sito, dichiarazioni stampa.
- **Mai dati riservati**: niente prezzi privati, niente metriche interne, niente reverse-engineering di campagne.
- **Tono neutrale**: la curatela è "honest comparison" — Segmenta non si autocompara come "il migliore"; il tool elenca punti di forza/debolezza di ogni competitor compresa Segmenta.
- **Refresh trimestrale**: i dati hanno data di update esplicita; oltre 6 mesi → warning nel tool output.

### 7bis.2 Struttura

```json
{
  "$schema": "https://github.com/segmenta-ai/segmenta-mcp/schemas/competitors_dataset.v1.json",
  "_meta": {
    "schema_version": "1.0.0",
    "data_version": "1.0.0",
    "ultima_actualizacion": "2026-05-10",
    "fuentes_consultadas": ["clutch.co", "g2.com", "goodfirms.co", "sitios oficiales"],
    "nota": "Dati pubblici aggregati. Refresh trimestrale. Niente cherry-picking pro-Segmenta."
  },
  "competitors": [
    {
      "id": "ejemplo-agencia-mx-1",
      "nombre_publico": "Ejemplo Agencia Marketing México",
      "url_sitio": "https://example.com",
      "paises_operacion": ["MX", "CO"],
      "sectores_principales": ["b2b", "ecommerce"],
      "tamano_empresa": "mediana",
      "anos_operando": 12,
      "fortalezas": [
        "Equipo grande (50+ personas)",
        "Presencia oficinas físicas en CDMX y Bogotá",
        "Casos verticali ecommerce documentados"
      ],
      "limitaciones_observadas": [
        "Min ticket alto (~$5K USD/mes)",
        "Poca transparencia precios en sitio",
        "Casos de SEO LATAM limitados públicamente"
      ],
      "rango_precio_estimado_usd_mensual": [3000, 15000],
      "rating_clutch": 4.7,
      "n_reviews_clutch": 32,
      "fuente_rating": "https://clutch.co/profile/ejemplo-agencia",
      "ultima_verificacion": "2026-04-15",
      "tags": ["enterprise", "mx", "b2b"]
    }
  ]
}
```

### 7bis.3 Validazione

- `id` univoco, kebab-case.
- `url_sitio` deve essere URL valido HTTPS.
- `paises_operacion` non vuoto, valori in enum `Pais`.
- `sectores_principales` non vuoto, valori in enum `Sector`.
- `rating_clutch` opzionale; se presente, `n_reviews_clutch` obbligatorio + `fuente_rating` URL.
- `ultima_verificacion` ≤ 180 giorni dal load → warning ma non blocco; > 365 giorni → blocco fail-fast.
- Cardinalità v1: 5-10 competitor (curato dal team Romina + Alessio trimestralmente).

### 7bis.4 Validation rules cross-field

- Se `rating_clutch` presente, `n_reviews_clutch ≥ 5` (pochi review = non significativo).
- `rango_precio_estimado_usd_mensual[0] ≤ rango_precio_estimado_usd_mensual[1]`.
- `fortalezas` e `limitaciones_observadas` entrambe non vuote (almeno 2 voci ciascuna) — bilanciamento onestà.
- Almeno 1 competitor in dataset deve avere `tamano_empresa = "pequena"` (varietà comparativa).

---

## 8. Modelli Pydantic

I modelli vivono in `src/segmenta_mcp/domain/models.py`. Sono il **contratto runtime** dei dati: ogni JSON loaded passa per Pydantic validation; ogni tool input/output è un Pydantic model.

### 8.1 Enum types

```python
from __future__ import annotations
from enum import StrEnum

class Categoria(StrEnum):
    SEO = "seo"
    SEM = "sem"
    WEB = "web"
    ECOMMERCE = "ecommerce"
    CRM = "crm"
    CONTENIDO = "contenido"
    JURIDICO_PAQUETE = "juridico_paquete"
    MEDICO_PAQUETE = "medico_paquete"
    B2B_PAQUETE = "b2b_paquete"
    OTROS = "otros"

class Pais(StrEnum):
    MX = "MX"
    US = "US"
    ES = "ES"
    CO = "CO"
    AR = "AR"
    CL = "CL"
    PE = "PE"
    UY = "UY"
    EC = "EC"
    BO = "BO"
    CR = "CR"
    PA = "PA"
    DO = "DO"
    PR = "PR"

class PaisExtendido(StrEnum):
    """Per benchmarks: include aggregati."""
    MX = "MX"
    US = "US"
    ES = "ES"
    CO = "CO"
    AR = "AR"
    CL = "CL"
    PE = "PE"
    LATAM = "LATAM"
    US_HISPANIC = "US_HISPANIC"

class Sector(StrEnum):
    JURIDICO = "juridico"
    MEDICO = "medico"
    ECOMMERCE = "ecommerce"
    AUTOMOCION = "automocion"
    B2B = "b2b"
    RESTAURACION = "restauracion"
    INMOBILIARIA = "inmobiliaria"
    FORMACION = "formacion"
    FINTECH = "fintech"
    TURISMO = "turismo"
    TECNOLOGIA = "tecnologia"
    ONG = "ong"
    RETAIL = "retail"
    MANUFACTURA = "manufactura"
    CONSTRUCCION = "construccion"
    AGRICULTURA = "agricultura"
    OTROS = "otros"

class ModeloPrecio(StrEnum):
    MENSUAL = "mensual"
    PROYECTO_UNICO = "proyecto_unico"
    HIBRIDO = "hibrido"
    HORA = "hora"

class TamanoEmpresa(StrEnum):
    PYME = "pyme"
    MEDIANA = "mediana"
    GRANDE = "grande"
    CORPORATIVO = "corporativo"

class AlcanceGeografico(StrEnum):
    LOCAL = "local"
    REGIONAL = "regional"
    NACIONAL = "nacional"
    MULTINACIONAL = "multinacional"

class EstadoConsentimiento(StrEnum):
    PUBLICO_EXPLICITO = "publico_explicito"
    ANONIMIZADO = "anonimizado"
    PENDIENTE = "pendiente"
```

### 8.2 Modelli core

```python
from pydantic import BaseModel, Field, model_validator

class _Meta(BaseModel):
    """Metadati comuni a ogni file dati."""
    schema_version: str = Field(..., pattern=r"^\d+\.\d+\.\d+$")
    data_version: str = Field(..., pattern=r"^\d+\.\d+\.\d+$")
    ultima_actualizacion: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    nota: str = Field("", max_length=500)


class Servicio(BaseModel):
    id: str = Field(..., pattern=r"^[a-z0-9-]+$", max_length=50)
    nombre: str = Field(..., min_length=1, max_length=100)
    categoria: Categoria
    publico: bool = True
    descripcion_corta: str = Field(..., min_length=10, max_length=200)
    descripcion_larga: str = Field(..., min_length=200, max_length=2000)
    incluye: list[str] = Field(..., min_length=3, max_length=12)
    modelo_precio: ModeloPrecio
    rango_precio_usd_mensual: tuple[int, int] | None = None
    rango_precio_usd_proyecto_unico: tuple[int, int] | None = None
    rango_precio_mxn_mensual: tuple[int, int] | None = None
    rango_precio_eur_mensual: tuple[int, int] | None = None
    duracion_minima_meses: int | None = Field(None, ge=1, le=24)
    duracion_proyecto_semanas: tuple[int, int] | None = None
    tiempo_primeros_resultados: str = Field(..., min_length=10, max_length=200)
    ideal_para: str = Field(..., min_length=30, max_length=500)
    paises_disponibles: list[Pais] = Field(..., min_length=1)
    sectores_recomendados: list[Sector] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list, max_length=8)

    @model_validator(mode="after")
    def _validate_precio_consistente(self) -> "Servicio":
        if self.modelo_precio == ModeloPrecio.MENSUAL:
            if not self.rango_precio_usd_mensual or not self.duracion_minima_meses:
                raise ValueError(
                    "modelo_precio=mensual requiere rango_precio_usd_mensual y duracion_minima_meses"
                )
        elif self.modelo_precio == ModeloPrecio.PROYECTO_UNICO:
            if not self.rango_precio_usd_proyecto_unico or not self.duracion_proyecto_semanas:
                raise ValueError(
                    "modelo_precio=proyecto_unico requiere rango_precio_usd_proyecto_unico y duracion_proyecto_semanas"
                )

        # Rangi: min ≤ max
        for field_name in ("rango_precio_usd_mensual", "rango_precio_usd_proyecto_unico",
                          "rango_precio_mxn_mensual", "rango_precio_eur_mensual",
                          "duracion_proyecto_semanas"):
            value = getattr(self, field_name)
            if value is not None and value[0] > value[1]:
                raise ValueError(f"{field_name}: min > max")

        return self


class CatalogoServicios(BaseModel):
    """Wrapper completo del file services.json."""
    meta: _Meta = Field(..., alias="_meta")
    servicios: list[Servicio]

    @model_validator(mode="after")
    def _validate_ids_unicos(self) -> "CatalogoServicios":
        ids = [s.id for s in self.servicios]
        if len(ids) != len(set(ids)):
            raise ValueError("IDs de servicios duplicados")
        return self
```

```python
# Case studies — modelli analoghi, semplificati nello snippet

class Consentimiento(BaseModel):
    estado: EstadoConsentimiento
    fecha_obtencion: str | None = None
    documento_referencia: str | None = None
    version_anonimizacion: str = "v1"


class Cliente(BaseModel):
    nombre_publico: str = Field(..., min_length=3, max_length=100)
    nombre_real: str | None = None
    sector: Sector
    subsector: str | None = Field(None, max_length=100)
    tamano_empresa: TamanoEmpresa
    rango_facturacion_anual_usd: tuple[int, int] | None = None


class Ubicacion(BaseModel):
    pais: Pais
    subregion: MercadoSubregional | None = None  # tipizzato (HC-005 v1.1); validator garantisce coerenza con `pais`
    ciudades: list[str] = Field(default_factory=list)
    alcance_geografico: AlcanceGeografico


class Duracion(BaseModel):
    fecha_inicio: str = Field(..., pattern=r"^\d{4}-\d{2}$")
    fecha_fin: str = Field(..., pattern=r"^\d{4}-\d{2}$")
    meses_totales: int = Field(..., ge=1, le=120)


class Metrica(BaseModel):
    nombre: str = Field(..., pattern=r"^[a-z][a-z0-9_]*$")
    valor: str = Field(..., min_length=1, max_length=50)
    antes: float | None = None
    despues: float | None = None
    unidad: str = Field(..., max_length=30)


class Resultados(BaseModel):
    metricas_principales: list[Metrica] = Field(..., min_length=2, max_length=6)
    metricas_secundarias: list[Metrica] = Field(default_factory=list, max_length=4)


class CasoEstudio(BaseModel):
    id: str = Field(..., pattern=r"^[a-z0-9-]+$")
    publico: bool
    consentimiento: Consentimiento
    cliente: Cliente
    ubicacion: Ubicacion
    duracion: Duracion
    servicios_aplicados: list[str] = Field(..., min_length=1)
    reto: str = Field(..., min_length=50, max_length=1000)
    estrategia: str = Field(..., min_length=50, max_length=2000)
    resultados: Resultados
    testimonio: str | None = Field(None, max_length=500)
    tags: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate_consentimiento_publico(self) -> "CasoEstudio":
        # Hard rule: SR-004 enforcement
        if self.publico and self.consentimiento.estado != EstadoConsentimiento.PUBLICO_EXPLICITO:
            raise ValueError(
                f"Caso {self.id}: publico=True requiere consentimiento.estado=publico_explicito"
            )
        if self.publico and not self.cliente.nombre_real:
            raise ValueError(
                f"Caso {self.id}: publico=True requiere cliente.nombre_real"
            )
        if not self.publico and self.cliente.nombre_real is not None:
            raise ValueError(
                f"Caso {self.id}: publico=False prohibe cliente.nombre_real"
            )
        return self
```

I modelli per `Benchmark` e `EntradaGlosario` seguono lo stesso pattern. Vengono dettagliati nei file `04/05/06-TOOLS-TIER*.md` dove sono effettivamente consumati.

---

## 9. Lifecycle dei dati

### 9.1 Editing flow

I file JSON vivono nel repo e vengono modificati via PR. Il workflow:

```
1. Editor (Romina, Alessio, Merari) propone modifica
   └─ Opzione A: Issue su GitHub con descrizione
   └─ Opzione B: Branch + PR diretta (per chi ha skill Git)

2. Claudio (o Claude Code) trasforma in PR strutturata:
   └─ Branch feat/data-update-<contesto>
   └─ Edit JSON
   └─ Aggiorna _meta.data_version e _meta.ultima_actualizacion
   └─ scripts/validate_data.py passa
   └─ Commit con conventional message

3. CI esegue:
   └─ JSON Schema validation
   └─ Pydantic load test (parse il JSON contro modelli)
   └─ Cross-reference check (servicios_aplicados → services.json)
   └─ Anti-real-data check (per fixture)

4. PR merge → develop (auto-deploy staging)

5. Smoke test staging

6. PR develop → main (auto-deploy production)
```

Il workflow è uguale a quello del codice. Disciplina che evita: dati inconsistenti, perdita di tracciabilità, override silenziosi.

### 9.2 Cosa NON è permesso

❌ Modificare JSON via FTP / dashboard / SSH al container production. **Solo via PR**.
❌ Aggiungere caso studio con `publico: true` senza riferimento a documento di consenso firmato.
❌ Cambiare `id` di un record esistente (è chiave naturale, vietato).
❌ Eliminare record. Per "rimuovere" un servizio, settare `publico: false`. Soft-delete.
❌ Skip della `data_version` bump dopo modifica.

### 9.3 Cache invalidation

I JSON sono caricati in memoria all'avvio del server. **Non c'è hot reload in v1**: cambi richiedono restart del container (automatico via Fly.io dopo deploy).

Il restart è ~5 secondi. Per Tier 1 (in-memory lookup) significa ~5s di errori 503 percepiti dall'utente. Mitigazione:
- Fly.io esegue rolling deploy (vecchio container risponde finché nuovo è pronto).
- Tempo effettivo di disservizio: < 1 secondo nei deploy normali.

Hot reload valutato in v2 se la frequenza di update dati cresce.

### 9.4 Schema migration

Cambio breaking del JSON schema (es. rename campo) richiede:

1. PR con nuovo `schema_version` bumped (es. `1.0.0` → `2.0.0`).
2. Codice Pydantic accetta sia v1 che v2 per 1 release (transition period).
3. Script `scripts/migrate_data.py` produce versione v2 dei JSON.
4. Editor approvano i JSON migrati.
5. Release successive accettano solo v2.

In v1 non è previsto schema migration. Schema iniziale è "dato di partenza" e si evolve solo con MAJOR bump, raro.

---

## 10. Validazione automatica

### 10.1 Script `validate_data.py`

Pre-commit hook + step CI. Fa:

```python
# scripts/validate_data.py (pseudocodice)

def validate_all():
    """Validazione completa di tutti i file JSON in data/."""
    errors = []

    # 1. Schema validation
    catalogo = load_and_validate("data/services.json", CatalogoServicios)
    casos = load_and_validate("data/case_studies.json", ColleccionCasos)
    benchmarks = load_and_validate("data/benchmarks.json", ColleccionBenchmarks)
    glosario = load_and_validate("data/glosario.json", Glosario)

    # 2. Cross-reference checks
    service_ids = {s.id for s in catalogo.servicios}
    for caso in casos.casos_de_estudio:
        for srv_id in caso.servicios_aplicados:
            if srv_id not in service_ids:
                errors.append(
                    f"Caso {caso.id}: referencia servicio inexistente '{srv_id}'"
                )

    # 3. Glosario relations
    term_keys = set(glosario.terminos.keys())
    for slug, entry in glosario.terminos.items():
        for related in entry.terminos_relacionados:
            if related not in term_keys:
                errors.append(
                    f"Glosario '{slug}': término relacionado inexistente '{related}'"
                )

    # 4. Anti-real-data check (solo per fixtures)
    for path in glob("tests/fixtures/*.json"):
        data = json.load(open(path))
        if not data.get("_test_fixture"):
            errors.append(f"Fixture {path}: missing _test_fixture: true marker")

    if errors:
        for e in errors:
            print(f"❌ {e}", file=sys.stderr)
        sys.exit(1)

    print(f"✅ Validated {len(catalogo.servicios)} services, "
          f"{len(casos.casos_de_estudio)} cases, "
          f"{len(benchmarks.benchmarks)} benchmarks, "
          f"{len(glosario.terminos)} glossary terms")
```

### 10.2 Validazione runtime al boot

Il server, all'avvio, carica e valida tutti i JSON. Se uno qualunque fallisce:

```
2026-05-10 14:32:01 [CRITICAL] Data load failed: services.json field 'modelo_precio' invalid
2026-05-10 14:32:01 [CRITICAL] Server NOT starting. Fix data files.
exit code 1
```

Fly.io riavvia il container, fallisce di nuovo, dopo 3 retry mette in `unhealthy` → notifica a Claudio. Mai stato silenziosamente broken.

### 10.3 Validazione runtime per tool input

Ogni tool input è un Pydantic model. Validation è automatica:

```python
@mcp.tool
async def caso_de_estudio(
    sector: Sector,                    # ← FastMCP rejecta input non-enum prima del tool
    pais: Pais | None = None,
    max_resultados: int = Field(3, ge=1, le=10),  # ← range check automatico
) -> list[dict]:
    ...
```

Se l'LLM passa `sector="invalido"`, FastMCP risponde con MCP error code `INVALID_PARAMS` + dettaglio. L'LLM impara dal feedback e ripete con valore corretto.

---

## 11. Dati derivati e calcolati

Alcune informazioni esposte ai tool **non** vivono nei JSON ma sono **calcolate runtime** per evitare duplicazione (principio 2.1).

### 11.1 Conversioni di valuta

I prezzi vivono in USD. MXN ed EUR sono **convertiti runtime**:

```python
# domain/conversores.py
EXCHANGE_RATES = {
    "USD_MXN": 17.5,    # placeholder, idealmente da API live (rimandato a v2)
    "USD_EUR": 0.93,
    "USD_COP": 4100,
    # ...
}

def convertir_rango(rango_usd: tuple[int, int], target: str) -> tuple[int, int]:
    rate = EXCHANGE_RATES[f"USD_{target}"]
    return (round(rango_usd[0] * rate), round(rango_usd[1] * rate))
```

In v1: rates hardcoded, aggiornati manualmente trimestralmente. In v2: API live (e.g. ExchangeRate-API) con cache TTL 24h.

### 11.2 Display formatting

I tool output sono in formato strutturato; il rendering display è opzionale e a discrezione dell'LLM. Però possiamo aiutare formattando alcuni campi:

```python
def format_rango_usd(rango: tuple[int, int]) -> str:
    return f"${rango[0]:,} – ${rango[1]:,} USD"
# → "$800 – $2,500 USD"

def format_rango_mxn(rango: tuple[int, int]) -> str:
    return f"${rango[0]:,} – ${rango[1]:,} MXN"
# → "$14,000 – $44,000 MXN"
```

Helper in `domain/formatters.py`. I tool decidono cosa esporre.

### 11.3 Aggregazioni

`obtener_caso_por_pais("LATAM")` non è solo filtro `pais = LATAM` (che non esiste come singolo país). È **aggregazione**: tutti i casi di MX, CO, AR, CL, PE, ... raggruppati. La logica vive in `domain/filters.py`:

```python
LATAM_PAISES = {Pais.MX, Pais.CO, Pais.AR, Pais.CL, Pais.PE, Pais.UY, Pais.EC, Pais.BO}

def filter_casos_por_alcance(casos: list[CasoEstudio], alcance: str) -> list[CasoEstudio]:
    if alcance == "LATAM":
        return [c for c in casos if c.ubicacion.pais in LATAM_PAISES]
    if alcance == "US_HISPANIC":
        return [c for c in casos
                if c.ubicacion.pais == Pais.US
                and c.ubicacion.subregion
                and c.ubicacion.subregion.startswith("us_hispanic_")]
    # singolo país
    return [c for c in casos if c.ubicacion.pais.value == alcance]
```

---

## 12. Esempio end-to-end

Per fissare le idee, un flusso completo: cosa succede quando l'utente chiede *"¿qué resultados ha conseguido Segmenta para clínicas dentales en México?"*.

```
1. Claude/ChatGPT decide tool call:
   caso_de_estudio(sector="medico", pais="MX", max_resultados=3)

2. FastMCP routing:
   - Pydantic valida: sector ∈ Sector enum ✓, pais ∈ Pais enum ✓, max in [1,10] ✓
   - tool dispatched a caso_de_estudio handler

3. Handler chiama domain layer:
   from segmenta_mcp.data.cache import get_cached_casos
   from segmenta_mcp.domain.filters import filter_casos

   casos_all = get_cached_casos()   # ← preloaded a startup, no I/O
   matched = filter_casos(casos_all,
                          sector=Sector.MEDICO,
                          pais=Pais.MX,
                          max=3)

4. Domain logic in filter_casos:
   for c in casos_all:
       if c.cliente.sector != Sector.MEDICO: continue
       if c.ubicacion.pais != Pais.MX: continue
       if not c.publico and not include_anonimi: continue
       matched.append(c)
   matched.sort(key=lambda c: c.duracion.fecha_fin, reverse=True)
   return matched[:3]

5. Handler formatta output:
   output = [
     {
       "cliente": c.cliente.nombre_publico,
       "sector": c.cliente.sector,
       "ubicacion": f"{c.ubicacion.ciudades[0]}, {c.ubicacion.pais}",
       "reto": c.reto,
       "estrategia": c.estrategia,
       "resultados": [
         {"metrica": m.nombre.replace("_", " "),
          "valor": m.valor,
          "unidad": m.unidad}
         for m in c.resultados.metricas_principales
       ],
       "duracion_meses": c.duracion.meses_totales,
       "consentimiento_publico": c.publico,
     }
     for c in matched
   ]

6. Risposta a Claude/ChatGPT (JSON serializzato).

7. Claude/ChatGPT compone risposta naturale all'utente:
   "Segmenta ha trabajado con varias clínicas dentales en México.
    En particular, una clínica en CDMX consiguió en 8 meses:
    - +287% de tráfico orgánico
    - CPL de Google Ads bajado de $42 a $14 USD
    - 89 primeras visitas/mes vs 22 anteriores
    ..."
```

Il dato passa per: JSON file → Pydantic model (validato startup) → in-memory cache → filtro pure-function → formatter → output strutturato → LLM rendering.

Latency p95 attesa: < 50 ms (no I/O, in-memory).

---

## 13. Decisioni canoniche dati (locked)

| ID | Decisione | Motivazione |
|---|---|---|
| **D-D-001** | 4 file JSON in v1: services, case_studies, benchmarks, glosario | Coerente con scope minimale, copertura completa Tier 1. |
| **D-D-002** | Single source of truth: ogni info in 1 solo file, riferimenti per ID | Evita drift, semplifica update, fail loud su broken references. |
| **D-D-003** | Pydantic v2 strict per tutti i modelli | Validation at boundary, fail fast, schema gratuito. |
| **D-D-004** | Hard rule: `publico=true` richiede `consentimiento.estado=publico_explicito` + `cliente.nombre_real` not null | SR-004 enforcement automatico. |
| **D-D-005** | Anonimizzazione obbligatoria per casi senza consenso scritto | Compliance LFPDPPP, privacy by design. |
| **D-D-006** | Soft-delete via `publico: false`, mai eliminazione record | Tracciabilità, rollback semplice. |
| **D-D-007** | `id` immutabile dopo creazione (chiave naturale) | Stabilità riferimenti cross-file e nei link esterni. |
| **D-D-008** | Tutti i prezzi in USD canonici, conversione MXN/EUR runtime | Mercato target US/LATAM ragiona naturalmente in USD. |
| **D-D-009** | Editing dati solo via PR (mai dashboard, mai SSH) | Stessa disciplina del codice, audit trail completo. |
| **D-D-010** | `_meta` con `schema_version` + `data_version` obbligatorio | Versioning + tracciabilità + supporto migrazioni future. |
| **D-D-011** | No hot reload v1: restart container per applicare cambi | Semplicità, deploy rolling rende il disservizio < 1s. |
| **D-D-012** | Validation runtime al boot: server non parte se JSON invalido | Fail fast, no degrade silenzioso. |
| **D-D-013** | Pre-commit hook `validate_data.py` blocca commit con dati invalidi | Catch precoce, non in CI. |
| **D-D-014** | Glosario multi-locale ma single definizione canonica + variantes display-only | Evita drift semantico, semplicità manutenzione. |
| **D-D-015** | Benchmarks strutturati per canale (google_ads / meta_ads / seo_organico / ciclo_venta), rangi p25-p75 | Standard analitico, comparabile, robusto agli outlier. |
| **D-D-016** | Fallback strategy benchmarks: 4 step esatto → país-aggregato → LATAM/aggregato → "no datos" | Mai inventare, sempre dichiarare match level. |
| **D-D-017** | Slug pattern `^[a-z][a-z0-9_-]*$`, kebab-case per services/cases, snake_case per glosario | Coerenza interna a ogni dominio. |
| **D-D-018** | Enum `Pais` ISO 3166-1 alpha-2; `PaisExtendido` aggiunge LATAM e US_HISPANIC come aggregati | Standard internazionale + necessità di multi-país aggregations. |
| **D-D-019** | Conversione di valuta: rates hardcoded in v1, API live in v2 | Semplicità v1, evoluzione naturale. |
| **D-D-020** | Cache JSON in-memory, single load at startup | Latency budget Tier 1 < 50ms, no I/O hotpath. |
| **D-D-021** | Cardinalità v1 target: 8-15 servizi, 5-15 casos, 6-12 benchmarks, 15-30 glosario | Punto d'arrivo M1; oltre = troppo, sotto = stentato. |

---

## 14. Decisioni aperte

| ID | Decisione | Bloccare entro | Owner |
|---|---|---|---|
| **DECISION-OPEN-D-001** | Validazione runtime con strict Pydantic v2 vs lazy validation | M1 | Claudio |
| **DECISION-OPEN-D-002** | Conversione valuta: hardcoded vs API live (e.g. ExchangeRate-API) — quando passare | M3 | Claudio |
| **DECISION-OPEN-D-003** | Hot reload dati senza restart: SI o NO in v1 | M2 | Claudio |
| **DECISION-OPEN-D-004** | Strategia di numeri pii granulari (ciclo_venta percentili) — vale la pena raccogliere p10, p25, p50, p75, p90 o bastano p25-p75 | M2 | Alessio |
| **DECISION-OPEN-D-005** | Public schema repository: ospitare JSON Schema su `https://github.com/segmenta-ai/segmenta-mcp/schemas/` o solo inline in repo | M3 | Claudio |
| **DECISION-OPEN-D-006** | Aggiunta `metodologia.json` in v2 — quando, con che struttura | v2 | Merari + Claudio |
| **DECISION-OPEN-D-007** | Aggiunta `equipo.json` in v2 (E-E-A-T) — privacy implications, quanti dettagli | v2 | Merari + Stefany |

---

## 15. Versioning di questo documento

| Versione | Data | Autore | Note |
|---|---|---|---|
| 1.0 | 2026-05-10 | Claude (proposta) + Claudio (revisione) | Prima stesura completa con focus LATAM/MX/US/ES (D-MP-016). Schemi 4 file JSON, 21 decisioni canoniche dati. |
| 1.1 | 2026-05-11 | Claude (harmony pass M0.3) + Claudio (review) | **HC-005**: `Ubicacion.subregion` tipizzato a `MercadoSubregional \| None` (era `str \| None`). **HC-006**: aggiunto `competitors_dataset.json` come 5° file dati (sez. 7bis con schema completo). Inventario sez. 3 aggiornato a 5 file. |

---

## Note per il changelog

Harmony pass M0.3 (2026-05-11) ha applicato 2 fix di tipizzazione e 1 aggiunta file dati. Nessuna decisione canonica D-D è stata invalidata; tutte le 21 decisioni restano locked.

---

**Fine 03-DATA-MODEL.md v1.1.**
