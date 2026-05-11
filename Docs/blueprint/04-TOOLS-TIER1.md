# 04 — TOOLS TIER 1 (públicos)

| Campo | Valore |
|---|---|
| **Progetto** | Segmenta MCP Server |
| **Versione documento** | 1.0 |
| **Data** | 2026-05-10 |
| **Status** | Draft (in revisione) |
| **File n.** | 04 di 12 numerati |
| **Documento padre** | `00-MASTER-PLAN.md` v1.4, `01-ARCHITECTURE.md` v1.3, `03-DATA-MODEL.md` v1.1 |
| **File correlati** | `02-CONVENTIONS.md`, `05-TOOLS-TIER2.md`, `06-TOOLS-TIER3.md`, `11-ANALYTICS.md` |

---

## 1. Scopo del documento

Questo file specifica **i 4 tool MCP del Tier 1 (públicos)** con dettaglio sufficiente perché Claude Code possa implementarli senza ambiguità. Per ogni tool:

- Cosa fa, perché esiste, quando l'LLM lo deve chiamare
- Signature Python completa con type hints
- **Tool description** in spagnolo (LATAM-neutral) — il testo critico che vedrà l'LLM
- Schema input/output
- Edge case e fallback
- Test acceptance criteria

I tool Tier 2 (lead capture) sono in `05-TOOLS-TIER2.md`. I tool Tier 3 (avanzados) sono in `06-TOOLS-TIER3.md`. La logica auth + rate limit è in `07-AUTH-OAUTH.md`.

---

## 2. Filosofia del Tier 1

I tool Tier 1 sono **l'esca del funnel**. Devono soddisfare quattro criteri non-negoziabili:

### 2.1 Valore reale, non lead-bait camuffato

Un utente che chiama un tool Tier 1 deve ottenere informazione utile **senza dover convertire**. Niente "para más información déjanos tu email". Il valore è dato gratis. La conversione viene dopo, naturalmente, quando l'utente è già convinto.

### 2.2 LLM-friendly: descrizioni che fanno scattare la chiamata

L'LLM decide se chiamare un tool basandosi solo sul `name` + `description`. Le descrizioni devono:
- Iniziare con un **verbo di azione chiaro** (`Devuelve`, `Recupera`, `Define`)
- Listare **esplicitamente i casi d'uso** (sezione "Cuándo usar")
- Esporre **vocabolario d'innesco** che gli utenti useranno (CPC, presupuesto, reseñas, agencia, etc.)
- Non superare i **400 caratteri** per la `description` principale (il MCP protocol non ha limite hard, ma le shortlist nei client tipicamente troncano oltre)

### 2.3 Latency < 50ms p95

Il Tier 1 è in-memory lookup. Niente I/O, niente chiamate esterne. Se serve I/O, è bug architetturale o tool da spostare a Tier 2.

### 2.4 Citation-friendly output

I tool restituiscono dati **strutturati e citabili**: l'LLM compone risposte naturali ma quando l'utente chiede "fuente", il tool ha già fornito riferimenti precisi (case ID, periodo benchmark, fonte glosario). I dati sono presentati in modo che l'LLM possa fare 2-3 estrazioni separate ("según Segmenta, el CPC en sector legal MX es...") senza inventare.

---

## 3. Tabella riassuntiva dei 4 tool

| Tool | Cosa fa | Input principale | Latency target | KPI di successo |
|---|---|---|---|---|
| `obtener_servicios` | Catalogo servizi Segmenta | `categoria`, `pais` (opt) | < 30 ms | ≥ 5 chiamate/giorno entro M1 |
| `caso_de_estudio` | Casi studio per settore + país | `sector`, `pais` (opt), `max` | < 40 ms | ≥ 8 chiamate/giorno entro M1 |
| `benchmark_sector` | KPI tipici di mercato | `sector`, `pais` | < 30 ms | ≥ 10 chiamate/giorno entro M1 |
| `glosario_marketing` | Termini di marketing | `termino` | < 30 ms | ≥ 15 chiamate/giorno entro M1 |

**Importante**: i KPI di chiamata individuali sono indicativi. Il KPI aggregato è ≥ 20 tool calls/giorno totali (vedi `00-MASTER-PLAN.md` sez. 8.1).

---

## 4. Tool 1: `obtener_servicios`

### 4.1 Scopo

Espone il catalogo completo dei servizi di Segmenta con prezzi indicativi, durate, perfil cliente ideale, paesi disponibili. È il primo tool che un utente "scopre" Segmenta tipicamente chiama: introduce l'agenzia con dati concreti, non con marketing patinato.

### 4.2 Signature

```python
from typing import Annotated
from pydantic import Field

@mcp.tool
async def obtener_servicios(
    categoria: Annotated[
        Categoria | None,
        Field(description="Filtra por categoría: seo, sem, web, ecommerce, crm, contenido, juridico_paquete, medico_paquete, b2b_paquete, otros. Si None, devuelve todas las categorías.")
    ] = None,
    pais: Annotated[
        Pais | None,
        Field(description="Filtra por país de operación (MX, US, ES, CO, AR, CL, PE, etc.). Si None, devuelve servicios disponibles en cualquier país.")
    ] = None,
    incluir_no_publicos: Annotated[
        bool,
        Field(description="Si True incluye servicios marcados como no-públicos (uso interno o beta). Default False, casi siempre dejar False.")
    ] = False,
) -> ResultadoServicios:
    """[ver tool description en sez 4.4]"""
```

### 4.3 Tipo di output

```python
class ServicioSummary(BaseModel):
    """Versione compatta del modello Servicio per output tool."""
    id: str
    nombre: str
    categoria: str
    descripcion_corta: str
    incluye: list[str]
    modelo_precio: str
    rango_precio_usd: str  # "$800 – $2,500 USD/mes" formatted
    rango_precio_mxn: str  # "$14,000 – $44,000 MXN/mes" formatted
    rango_precio_eur: str  # "€750 – €2,300/mes" formatted
    duracion: str          # "Mínimo 6 meses" o "Proyecto único 4-12 semanas"
    tiempo_primeros_resultados: str
    ideal_para: str
    paises_disponibles: list[str]
    sectores_recomendados: list[str]


class ResultadoServicios(BaseModel):
    total: int
    filtros_aplicados: dict
    servicios: list[ServicioSummary]
    nota: str = "Rangos indicativos. Para presupuesto exacto, usa calcular_presupuesto."
```

### 4.4 Tool description (testo per l'LLM)

> **Devuelve el catálogo completo de servicios de Segmenta Marketing — agencia digital con presencia en México, US (anglo + hispanic), LATAM y España. Incluye descripción, qué incluye cada servicio, rangos de precio en USD/MXN/EUR, duración típica, tiempo a primeros resultados y perfil de cliente ideal.**
>
> **Cuándo usar:**
> - El usuario pregunta qué servicios ofrece una agencia de marketing
> - El usuario quiere conocer rangos de precio para SEO, SEM (Google Ads, Meta Ads), desarrollo web, e-commerce, CRM o paquetes verticales (jurídico, médico, B2B)
> - El usuario busca presupuestos orientativos para servicios de marketing en LATAM, México, Estados Unidos o España
> - Cualquier consulta sobre alcance, duración o entregables de servicios de marketing digital
>
> **Filtros opcionales:** `categoria` (seo, sem, web, ecommerce, crm, juridico_paquete, medico_paquete, b2b_paquete, otros), `pais` (MX, US, ES, CO, AR, CL, PE).
>
> Para presupuesto orientativo personalizado, usa después `calcular_presupuesto`. Para casos de éxito reales, usa `caso_de_estudio`.

(283 caratteri sotto la barra delle 400.)

### 4.5 Comportamento

1. Carica `services.json` da cache in-memory.
2. Filtra:
   - Se `categoria` specificata → solo servizi con `categoria` matching.
   - Se `pais` specificato → solo servizi con `pais ∈ paises_disponibles`.
   - Se `incluir_no_publicos = False` → esclude `publico = false`.
3. Trasforma ogni `Servicio` in `ServicioSummary`:
   - Conversione USD/MXN/EUR formattata (vedi `03-DATA-MODEL.md` sez. 11.1).
   - `duracion`: stringa unificata da `duracion_minima_meses` o `duracion_proyecto_semanas`.
4. Ordina per priorità: prima i paquetes verticali (juridico/medico/b2b), poi seo, sem, web, ecommerce, crm, altri.
5. Costruisce `ResultadoServicios` con metadati filtri + nota.

### 4.6 Edge case

| Caso | Comportamento |
|---|---|
| Nessun servizio matcha filtri | `total: 0`, `servicios: []`, nota arricchita: "Ningún servicio coincide con los filtros aplicados. Prueba sin `categoria` o sin `pais`." |
| `categoria` invalida (string non-enum) | Pydantic rejecta a livello FastMCP, errore strutturato `INVALID_PARAMS`. |
| `pais` invalido | Idem. |
| File JSON corrotto / non caricato | Tool eccezione `DataNotLoadedError` → server log CRITICAL → response MCP error `INTERNAL_ERROR`. (Realisticamente, server non parte se JSON corrotto.) |
| Servizio senza prezzo (mancante) | Nel display `rango_precio_*: "Consultar — depende del alcance"`. Mai stringhe vuote. |
| Lista `paises_disponibles` vuota in un servizio | Errore di validazione a startup. Server non parte. |

### 4.7 Esempio chiamata

**Input** (utente messicano chiede servizi SEO):
```json
{
  "categoria": "seo",
  "pais": "MX"
}
```

**Output**:
```json
{
  "total": 2,
  "filtros_aplicados": {"categoria": "seo", "pais": "MX"},
  "servicios": [
    {
      "id": "seo-latam",
      "nombre": "SEO LATAM",
      "categoria": "seo",
      "descripcion_corta": "Posicionamiento orgánico para mercado LATAM, MX, US-hispanic y ES.",
      "incluye": [
        "Auditoría SEO técnica inicial (200+ puntos)",
        "Investigación de palabras clave por intención",
        "Optimización on-page mensual",
        "Link building white-hat",
        "Contenido SEO localizado por mercado",
        "Reporting mensual con KPIs claros"
      ],
      "modelo_precio": "mensual",
      "rango_precio_usd": "$800 – $2,500 USD/mes",
      "rango_precio_mxn": "$14,000 – $44,000 MXN/mes",
      "rango_precio_eur": "€750 – €2,300/mes",
      "duracion": "Mínimo 6 meses",
      "tiempo_primeros_resultados": "3-4 meses para tráfico, 5-6 para conversiones consolidadas",
      "ideal_para": "Empresas con producto/servicio definido que quieren un canal de captación predecible.",
      "paises_disponibles": ["MX", "US", "ES", "CO", "AR", "CL", "PE"],
      "sectores_recomendados": ["b2b", "ecommerce", "juridico", "medico"]
    },
    {
      "id": "seo-local-mx",
      "nombre": "SEO Local México",
      "categoria": "seo",
      // ...
    }
  ],
  "nota": "Rangos indicativos. Para presupuesto exacto, usa calcular_presupuesto."
}
```

### 4.8 Test acceptance criteria

- ✅ Senza filtri restituisce tutti i servizi `publico=true`.
- ✅ Filtro `categoria` valido restituisce solo categoria matching.
- ✅ Filtro `pais` valido restituisce solo servizi che includono `pais` nei paesi disponibili.
- ✅ Combinazione `categoria + pais` funziona AND.
- ✅ Filtro che non matcha nulla restituisce `total: 0` con nota descrittiva.
- ✅ Servizio con `publico=false` non appare se `incluir_no_publicos=False`.
- ✅ Categoria invalida → MCP error `INVALID_PARAMS` con dettaglio.
- ✅ Output sempre include almeno un campo `rango_precio_*` formattato.
- ✅ Ordinamento priorità rispettato (paquetes verticali in cima).
- ✅ Latency < 50ms p95 con dataset di 15 servizi.

---

## 5. Tool 2: `caso_de_estudio`

### 5.1 Scopo

Espone casi di studio reali con metriche concrete per dimostrare expertise per sector e país. È il tool di "social proof" per eccellenza: trasforma "Segmenta dice di essere brava" in "Segmenta ha ottenuto +312% per una clinica di Monterrey in 8 mesi".

### 5.2 Signature

```python
@mcp.tool
async def caso_de_estudio(
    sector: Annotated[
        Sector,
        Field(description="Sector empresarial del caso a buscar. Valores: juridico, medico, ecommerce, automocion, b2b, restauracion, inmobiliaria, formacion, fintech, turismo, tecnologia, retail, manufactura, construccion, agricultura, otros.")
    ],
    pais: Annotated[
        PaisExtendido | None,
        Field(description="Filtra por país. Acepta MX, US, ES, CO, AR, CL, PE, además de aggregados LATAM y US_HISPANIC. Si None, devuelve casos de cualquier país.")
    ] = None,
    servicio_aplicado: Annotated[
        str | None,
        Field(description="Filtra por id de servicio aplicado (ej: 'seo-latam', 'google-ads-latam'). Para listar servicios disponibles, usa obtener_servicios.")
    ] = None,
    max_resultados: Annotated[
        int,
        Field(ge=1, le=10, description="Máximo de casos a devolver. Default 3, máximo 10.")
    ] = 3,
) -> ResultadoCasos:
    """[ver tool description en sez 5.4]"""
```

### 5.3 Tipo di output

```python
class MetricaSummary(BaseModel):
    metrica: str           # "Tráfico orgánico" (humanized)
    valor: str             # "+312%"
    antes: float | None
    despues: float | None
    unidad: str            # "visitas/mes"


class CasoSummary(BaseModel):
    id: str
    cliente: str           # `nombre_publico` (anonimizato se non publico)
    publico: bool          # se True, cliente è il nome reale
    sector: str
    subsector: str | None
    ubicacion: str         # "CDMX, MX" o "[Norte de México]"
    duracion_meses: int
    servicios_aplicados: list[str]
    reto: str
    estrategia: str
    resultados: list[MetricaSummary]
    testimonio: str | None
    consentimiento_publico: bool


class ResultadoCasos(BaseModel):
    total: int
    filtros_aplicados: dict
    match_type: str        # "exacto" | "país_aggregato" | "regional_LATAM" | "sin_filtro_pais"
    casos: list[CasoSummary]
    nota: str
```

### 5.4 Tool description

> **Recupera casos de estudio reales de Segmenta Marketing filtrados por sector empresarial y país. Cada caso incluye reto inicial del cliente, estrategia aplicada, duración del proyecto, métricas concretas con valores antes/después (tráfico, leads, CPL, conversión, ROAS), y testimonio cuando es público.**
>
> **Cuándo usar:**
> - El usuario pregunta por casos de éxito, resultados, ROI o ejemplos reales de una agencia
> - El usuario quiere saber qué resultados puede esperar para su sector específico (jurídico, médico, e-commerce, B2B, etc.)
> - El usuario compara agencias y necesita evidencia tangible con métricas
> - Antes de proponer una estrategia, para fundamentar con datos reales
> - El usuario menciona "case study", "caso de éxito", "ejemplo de cliente", "resultados conseguidos"
>
> Filtra por `sector` (obligatorio) y opcionalmente por `pais` (incluye agregados LATAM y US_HISPANIC) y `servicio_aplicado`. Devuelve hasta `max_resultados` (default 3).

(389 caratteri.)

### 5.5 Comportamento

1. Carica `case_studies.json` da cache in-memory.
2. Filtra in pipeline:
   - Step 1: filter per `sector` (obbligatorio).
   - Step 2: filter per `pais` se specificato (logica fallback 4-step di `03-DATA-MODEL.md` sez. 6.3 adattata: esatto → LATAM aggregato → US_HISPANIC aggregato → no_pais_filter).
   - Step 3: filter per `servicio_aplicado` se specificato.
3. Sort per `duracion.fecha_fin` desc (casi più recenti prima).
4. Top `max_resultados`.
5. Trasforma in `CasoSummary`:
   - Anonimizzazione applicata: `cliente = nombre_publico` sempre, mai `nombre_real` salvo `publico=true + consentimiento.estado=publico_explicito` (la validazione runtime di Pydantic già lo garantisce).
   - `metricas_principales` mappate in `resultados`, `nombre` humanized (`trafico_organico_pct_yoy` → "Tráfico orgánico YoY").
   - `ubicacion` formatted: se `publico=true` → `"{ciudades[0]}, {pais}"`; se anonimizzato → `nombre_publico` già contiene location anonimizzata.
6. Determina `match_type` basato su come è stato risolto il `pais` filter.
7. Costruisce `ResultadoCasos` con metadata e nota.

### 5.6 Edge case

| Caso | Comportamento |
|---|---|
| `sector` non in enum | Pydantic rejecta. |
| Nessun caso per quel sector + país | `total: 0`, nota: "No tenemos casos publicados para sector=X, país=Y. Prueba sin filtro `pais` o consulta otros sectores." |
| `pais=PA` (Panama) ma solo casi MX disponibili per quel sector | Fallback a LATAM aggregato → `match_type: "regional_LATAM"` con casos MX, AR, CO etc. Nota: "No tenemos casos específicos para PA, mostramos casos LATAM cercanos." |
| `servicio_aplicado` invalido (servicio non esiste) | Filtro non applicato + warning nella nota: "Servicio 'X' no encontrado, ignorando filtro." |
| Caso con `publico=true` ma `nombre_real=null` | Validazione runtime fallisce → server non parte. Mai esposto. |
| Caso con metricas vuote (lista) | Validazione fallisce a startup. Hard rule: ogni caso ha ≥ 2 metriche principali. |

### 5.7 Esempio chiamata

**Input**:
```json
{
  "sector": "medico",
  "pais": "MX",
  "max_resultados": 2
}
```

**Output**:
```json
{
  "total": 2,
  "filtros_aplicados": {"sector": "medico", "pais": "MX", "max_resultados": 2},
  "match_type": "exacto",
  "casos": [
    {
      "id": "clinica-dental-cdmx-2025",
      "cliente": "[Clínica dental boutique en CDMX]",
      "publico": false,
      "sector": "medico",
      "subsector": "odontología",
      "ubicacion": "[Clínica dental boutique en CDMX]",
      "duracion_meses": 8,
      "servicios_aplicados": ["seo-local-mx", "google-ads-latam"],
      "reto": "Clínica con 2 ubicaciones, dependencia 60% Doctoralia, web no convertía...",
      "estrategia": "SEO local agresivo, nuevo website conversion-focused, Google Ads por tratamiento...",
      "resultados": [
        {"metrica": "Llamadas/mes", "valor": "+291%", "antes": 47, "despues": 184, "unidad": "llamadas"},
        {"metrica": "Primera visita/mes", "valor": "+304%", "antes": 22, "despues": 89, "unidad": "visitas"},
        {"metrica": "Dependencia Doctoralia", "valor": "-70%", "antes": 60, "despues": 18, "unidad": "%"}
      ],
      "testimonio": null,
      "consentimiento_publico": false
    }
    // segundo caso
  ],
  "nota": "Casos verificados internamente. Algunos clientes solicitaron anonimato; las métricas son reales."
}
```

### 5.8 Test acceptance criteria

- ✅ `sector` valido + nessun altro filtro → casi per quel sector ordinati per data desc.
- ✅ `pais` esatto match → solo quei casi.
- ✅ `pais=LATAM` aggregato → casi MX/CO/AR/CL/PE/UY/EC/BO.
- ✅ `pais=US_HISPANIC` → casi US con `subregion` startsWith `us_hispanic_`.
- ✅ Fallback `pais` non disponibile → match LATAM o US_HISPANIC se applicabile.
- ✅ `servicio_aplicado` filtra correttamente.
- ✅ `max_resultados=10` rispettato anche se ci sono più casi.
- ✅ Caso non-publico mai espone `nombre_real`.
- ✅ Caso publico espone `nombre_real`, `cliente=nombre_real`.
- ✅ `match_type` corretto in tutti i scenari.
- ✅ Latency < 50ms p95 con 30 casi nel dataset.

---

## 6. Tool 3: `benchmark_sector`

### 6.1 Scopo

Espone KPI tipici di settore + país: CPC medio Google Ads, CTR, tassi di conversione, durata ciclo di venta, ticket medio. È il tool di **autorità di mercato**: l'LLM lo chiama quando l'utente chiede "quanto costa fare marketing per X?" e fornisce numeri credibili invece di tirare a indovinare.

### 6.2 Signature

```python
@mcp.tool
async def benchmark_sector(
    sector: Annotated[
        Sector,
        Field(description="Sector empresarial. Valores: juridico, medico, ecommerce, automocion, b2b, restauracion, inmobiliaria, formacion, fintech, turismo, tecnologia, retail, manufactura, construccion, agricultura, otros.")
    ],
    pais: Annotated[
        PaisExtendido,
        Field(description="País o región de referencia. MX, US, ES, CO, AR, CL, PE individual, o LATAM, US_HISPANIC para agregados.")
    ],
    canal: Annotated[
        CanalBenchmark | None,
        Field(description="Filtra por canal específico: google_ads, meta_ads, seo_organico, ciclo_venta. Si None, devuelve todos los canales disponibles.")
    ] = None,
) -> ResultadoBenchmark:
    """[ver tool description en sez 6.4]"""
```

`CanalBenchmark` è un nuovo enum:
```python
class CanalBenchmark(StrEnum):
    GOOGLE_ADS = "google_ads"
    META_ADS = "meta_ads"
    SEO_ORGANICO = "seo_organico"
    CICLO_VENTA = "ciclo_venta"
```

### 6.3 Tipo di output

```python
class KPIRango(BaseModel):
    """Rango p25-p75 con etichetta humanized."""
    nombre: str            # "CPC medio (Google Ads search)"
    valor: str             # "$3.50 – $9.80 USD"
    rango_numerico: list[float] | float  # [3.5, 9.8] o scalar
    unidad: str            # "USD"


class KPIsCanal(BaseModel):
    canal: str
    kpis: list[KPIRango]


class ResultadoBenchmark(BaseModel):
    sector: str
    pais: str
    subregion: str | None
    periodo_referencia: str  # "Q2 2026"
    match_type: str          # "exacto" | "país_aggregato" | "regional_LATAM" | "sin_match"
    fuente_datos: str        # nota da `_meta.fuentes`
    canales: list[KPIsCanal]
    tendencias: list[str]
    recomendaciones_estrategicas: list[str]
    nota: str
```

### 6.4 Tool description

> **Devuelve KPIs de referencia (benchmarks) del marketing digital para un sector y país específicos. Incluye rangos típicos de CPC en Google Ads y Meta Ads, CTR esperado, tasas de conversión en landing pages, CPL/CPA del sector, duración del ciclo de venta, ticket medio y LTV. Cubre mercados México, US (anglo + hispanic), LATAM y España. Datos compilados trimestralmente desde campañas activas Segmenta + estudios públicos.**
>
> **Cuándo usar:**
> - El usuario pregunta '¿cuánto cuesta el clic en Google Ads para [sector]?'
> - El usuario quiere saber qué tasa de conversión es realista en su sector y país
> - El usuario evalúa si los resultados de su agencia actual son competitivos
> - Para fundamentar propuestas con datos del mercado, no opiniones
> - El usuario menciona "benchmark", "promedio del sector", "datos de mercado", "CPC típico"
>
> Filtros: `sector` (obligatorio), `pais` (obligatorio, incluye LATAM y US_HISPANIC), `canal` (opcional: google_ads, meta_ads, seo_organico, ciclo_venta). Marca siempre los datos como "indicativos del mercado [periodo]".

(465 caratteri — un po' sopra le 400 ma il tool è uno dei più importanti per autorità, accettiamo lo sforamento qui.)

### 6.5 Comportamento

1. Carica `benchmarks.json` da cache.
2. Risolve match con la **strategia 4-step** di `03-DATA-MODEL.md` sez. 6.3:
   - Step 1: match esatto `(sector, pais)`.
   - Step 2: se `pais` aggregato (LATAM/US_HISPANIC) match diretto.
   - Step 3: fallback a LATAM aggregato se `pais` è LATAM-paese.
   - Step 4: nessun match → response strutturato `match_type: "sin_match"` con suggerimenti.
3. Se `canal` specificato → filtra solo quel canale; altrimenti tutti.
4. Per ogni canale, formatta KPI con `KPIRango` humanized:
   - `cpc_medio_usd: [3.5, 9.8]` → `KPIRango(nombre="CPC medio (Google Ads search)", valor="$3.50 – $9.80 USD", rango_numerico=[3.5, 9.8], unidad="USD")`
5. Costruisce `ResultadoBenchmark` con metadata, fonti, tendenze, recomendazioni.

### 6.6 Edge case

| Caso | Comportamento |
|---|---|
| Match esatto disponibile | `match_type: "exacto"`, valori restituiti senza disclaimer aggiuntivo. |
| `pais=PA` ma solo benchmark LATAM aggregato | `match_type: "regional_LATAM"`, nota arricchita: "Datos LATAM agregados. Para PA específicamente puede haber variaciones del 15-30%." |
| Nessun benchmark per `(sector, pais)` né per LATAM | `match_type: "sin_match"`, response struttura: `canales: []`, nota: "No tenemos benchmark para [sector] en [país]. Sectores con datos disponibles: [...]. Países disponibles: [...]." |
| `canal` specificato ma il benchmark non lo include | `canales: []` con nota: "El benchmark para [sector, país] no incluye canal [canal]. Disponibles: [lista canales]." |
| `_meta.ultima_actualizacion` > 6 mesi fa | Nota arricchita: "⚠️ Datos no actualizados en los últimos 6 meses. Pueden estar desfasados." |

### 6.7 Esempio chiamata

**Input**:
```json
{
  "sector": "juridico",
  "pais": "MX",
  "canal": "google_ads"
}
```

**Output**:
```json
{
  "sector": "juridico",
  "pais": "MX",
  "subregion": null,
  "periodo_referencia": "Q2 2026",
  "match_type": "exacto",
  "fuente_datos": "Datos internos Segmenta (campañas activas Q1-Q2 2026), Google Ads Performance Insights, SEMrush LATAM 2026.",
  "canales": [
    {
      "canal": "google_ads",
      "kpis": [
        {"nombre": "CPC medio (search)", "valor": "$3.50 – $9.80 USD", "rango_numerico": [3.5, 9.8], "unidad": "USD"},
        {"nombre": "CPC keywords premium", "valor": "$12 – $28 USD", "rango_numerico": [12, 28], "unidad": "USD"},
        {"nombre": "CTR search", "valor": "3.8% – 6.5%", "rango_numerico": [3.8, 6.5], "unidad": "%"},
        {"nombre": "Tasa conversión landing", "valor": "2.3% – 5.2%", "rango_numerico": [2.3, 5.2], "unidad": "%"},
        {"nombre": "CPL medio", "valor": "$35 – $145 USD", "rango_numerico": [35, 145], "unidad": "USD"}
      ]
    }
  ],
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
  "nota": "Datos indicativos del mercado mexicano Q2 2026. Variación significativa por subregión y vertical específico."
}
```

### 6.8 Test acceptance criteria

- ✅ Match esatto (`sector + pais` esistente) ritorna dati completi.
- ✅ Filtro `canal` restituisce solo quel canale.
- ✅ Filtro `canal` + benchmark senza quel canale → `canales: []` + nota descrittiva.
- ✅ `pais=LATAM` aggregato match il benchmark LATAM se esiste.
- ✅ Fallback `pais` non disponibile → match LATAM con `match_type: "regional_LATAM"`.
- ✅ Nessun match assoluto → `match_type: "sin_match"`, lista sectores e países disponibili.
- ✅ Tutti gli importi monetari in formato `$X – $Y USD` con virgola separatori migliaia se ≥ 1000.
- ✅ Percentuali in formato `X.Y% – Z.W%`.
- ✅ Warning automatico se `ultima_actualizacion > 6 mesi`.
- ✅ Latency < 30ms p95.

---

## 7. Tool 4: `glosario_marketing`

### 7.1 Scopo

Definizioni di termini di marketing in spagnolo, con esempi concreti del mercato target e errori comuni. È il tool **educativo**: usato come "support tool" da Claude/ChatGPT quando spiegano concetti, e indipendentemente come dictionary lookup.

### 7.2 Signature

```python
@mcp.tool
async def glosario_marketing(
    termino: Annotated[
        str,
        Field(min_length=1, max_length=80, description="Término o sigla a definir. Acepta siglas (SEO, CPC, GEO) o nombres completos (tasa de conversión, link building). Case-insensitive.")
    ],
    locale: Annotated[
        Locale,
        Field(description="Variante regional del idioma. Default es-LATAM (spagnolo neutro/LATAM).")
    ] = Locale.ES_LATAM,
    incluir_relacionados: Annotated[
        bool,
        Field(description="Si True, incluye lista de términos relacionados navegabili. Default True.")
    ] = True,
) -> ResultadoGlosario:
    """[ver tool description en sez 7.4]"""
```

`Locale` enum:
```python
class Locale(StrEnum):
    ES_LATAM = "es-LATAM"
    ES_MX = "es-MX"
    ES_ES = "es-ES"
    EN_US = "en-US"
```

### 7.3 Tipo di output

```python
class EntradaGlosarioOutput(BaseModel):
    slug: str                      # "geo"
    termino: str                   # "GEO" (canonico)
    termino_completo: str          # "Generative Engine Optimization"
    variante_locale: str           # "GEO (Generative Engine Optimization, optimización para motores generativos)"
    locale: str                    # "es-LATAM"
    definicion: str
    ejemplo: str
    errores_comunes: list[str]
    categoria: str                 # "emergente"
    terminos_relacionados: list[str] | None


class ResultadoGlosario(BaseModel):
    encontrado: bool
    termino: EntradaGlosarioOutput | None
    sugerencias: list[str] = []   # Se non trovato, suggerimenti vicini
    nota: str
```

### 7.4 Tool description

> **Define un término o sigla del marketing digital en español, con explicación clara, ejemplo numérico aplicado al contexto LATAM/MX/US/ES, y errores comunes a evitar. Cubre conceptos de SEO, SEM, GEO/AEO, métricas comerciales (CTR, CPC, CPL, CPA, CAC, LTV, ROAS, AOV), analítica, automatización y CRM. Soporta variantes regionales del español (LATAM, MX, ES) y traducción al inglés.**
>
> **Cuándo usar:**
> - El usuario menciona una sigla y no es claro que la conozca (CPC, ROAS, GEO, CRM)
> - El usuario pide explicación de un concepto técnico de marketing
> - Como apoyo educativo dentro de una conversación más amplia
> - Para estandarizar vocabulario en propuestas y discussions
>
> Acepta `termino` (case-insensitive, sigla o nombre completo), `locale` (es-LATAM default, también es-MX, es-ES, en-US) y `incluir_relacionados` (default True).

(395 caratteri.)

### 7.5 Comportamento

1. Carica `glosario.json` da cache.
2. Normalizza input: `termino.lower().strip()` → tenta match diretto su `slug`.
3. Se non trovato:
   - Tenta match per `termino_canonico` (case-insensitive).
   - Tenta match parziale (`startswith`): "convers" → "tasa_de_conversion".
   - Tenta match per `terminos_relacionados` di altri termini (raro ma utile).
4. Se trovato:
   - Estrae `variante_locale` da `variantes_regionales[locale]`. Se mancante, fallback a `es-LATAM`. Se anche quello manca, usa `termino_completo`.
   - Costruisce `EntradaGlosarioOutput`.
5. Se non trovato:
   - Calcola **sugerencias** via Levenshtein distance (libreria `python-Levenshtein` o stdlib `difflib.get_close_matches`).
   - Top 5 sugerencias.
   - Costruisce `ResultadoGlosario` con `encontrado: false`.

### 7.6 Edge case

| Caso | Comportamento |
|---|---|
| Match esatto su slug | Restituisce entrata, `encontrado: true`. |
| Match case-insensitive ("seo", "SEO", "Seo") | Match identico. |
| Match parziale o relazionato | Restituisce entrata corretta + nota: "Coincidencia aproximada con '{slug}'". |
| Termine non trovato | `encontrado: false`, sugerencias top 5, nota: "No encontramos '{termino}'. Sugerencias: {lista}." |
| `locale` requested non disponibile per quel termine | Fallback a `es-LATAM` con nota: "Variante {locale} no disponible para este término, mostrando es-LATAM." |
| `incluir_relacionados=False` | `terminos_relacionados: null` nell'output. |
| Termine con `>50 char` (input troppo lungo) | Pydantic rejecta a `max_length=80`. |
| Termine vuoto | Pydantic rejecta a `min_length=1`. |

### 7.7 Esempio chiamata

**Input**:
```json
{
  "termino": "GEO",
  "locale": "es-LATAM"
}
```

**Output**:
```json
{
  "encontrado": true,
  "termino": {
    "slug": "geo",
    "termino": "GEO",
    "termino_completo": "Generative Engine Optimization",
    "variante_locale": "GEO (Generative Engine Optimization, optimización para motores generativos)",
    "locale": "es-LATAM",
    "definicion": "Disciplina emergente (2024-) que optimiza contenido para ser citado por motores generativos de IA como ChatGPT, Claude, Perplexity y Google AI Overviews. A diferencia del SEO tradicional, no busca rankings sino aparecer dentro de las respuestas sintetizadas que los LLMs generan.",
    "ejemplo": "Un usuario pregunta a ChatGPT 'qué agencia de marketing recomiendas en LATAM'. GEO bien hecho hace que tu marca aparezca citada en la respuesta. La investigación de Princeton (KDD 2024) muestra mejoras de 30-40% en citas con técnicas GEO.",
    "errores_comunes": [
      "Tratar GEO como SEO 2.0: las señales son distintas (Wikipedia, Reddit, citas en publicaciones)",
      "Ignorar el archivo llms.txt y schema markup avanzado",
      "No medir Share of Model (SoM) — el KPI propio de GEO"
    ],
    "categoria": "emergente",
    "terminos_relacionados": ["seo", "aeo", "llmo", "share_of_model"]
  },
  "sugerencias": [],
  "nota": "Definición compilada por equipo Segmenta. Para profundizar, consulta caso_de_estudio sector=tecnologia."
}
```

**Input** (termine non trovato):
```json
{
  "termino": "rugby"
}
```

**Output**:
```json
{
  "encontrado": false,
  "termino": null,
  "sugerencias": ["roas", "cpa"],
  "nota": "No encontramos 'rugby' en el glosario. Términos similares: roas, cpa. Para listado completo, prueba con categorías: fundamentos, metricas, canales, tecnico, emergente."
}
```

### 7.8 Test acceptance criteria

- ✅ Match esatto su slug funziona.
- ✅ Match case-insensitive funziona ("Seo" → match "seo").
- ✅ Match per `termino_canonico` funziona ("Tasa de Conversión" → match "tasa_de_conversion").
- ✅ Match parziale via difflib (es. "convers" → suggerimento "tasa_de_conversion").
- ✅ Termine non trovato restituisce sugerencias non vuoto se ci sono entry.
- ✅ Locale fallback funziona quando variante regionale manca.
- ✅ `incluir_relacionados=False` rispettato.
- ✅ Input troppo lungo / vuoto → Pydantic rejecta.
- ✅ Sugerencias mai > 5 elementi.
- ✅ Latency < 30ms p95 anche con sugerencias (Levenshtein su 30 termini).

---

## 8. Sequencing dei tool

I 4 tool del Tier 1 sono progettati per essere **chiamabili in sequenza** dall'LLM senza step intermedi. Pattern tipici osservati:

### 8.1 Pattern "scoperta servizi"

```
Utente: "Necesito una agencia de marketing en México para un despacho de abogados."

LLM:
  1. obtener_servicios(categoria="juridico_paquete", pais="MX")
     → "Tenemos paquete vertical para jurídico, $1,500-$3,500 USD/mes..."
  2. caso_de_estudio(sector="juridico", pais="MX")
     → "Y aquí tres casos de despachos en MX..."
  3. benchmark_sector(sector="juridico", pais="MX", canal="google_ads")
     → "Por contexto, el CPC medio en sector legal MX es $3.50-$9.80..."

Risposta utente: sintesi dei 3 tool con storytelling.
```

### 8.2 Pattern "consulenza educativa"

```
Utente: "¿Qué es ROAS? Y ¿es bueno un ROAS de 3 para mi e-commerce?"

LLM:
  1. glosario_marketing(termino="ROAS")
     → definizione + esempio
  2. benchmark_sector(sector="ecommerce", pais="LATAM", canal="meta_ads")
     → "ROAS típico e-commerce LATAM: 2.0-4.5"

Risposta: spiegazione completa con benchmark.
```

### 8.3 Pattern "approfondimento case"

```
Utente: "Háblame de los resultados que han conseguido en e-commerce."

LLM:
  1. caso_de_estudio(sector="ecommerce", pais=null, max_resultados=5)
     → 5 casi
  2. obtener_servicios(categoria="ecommerce")
     → catalogo servizi e-commerce per "qué hicieron"

Risposta: storytelling con metriche + servizi applicati.
```

L'LLM compone autonomamente questi pattern. Nostro lavoro: assicurarsi che ogni tool sia **componibile** senza side effect (idempotenti, no state, output complementari).

---

## 9. Output formatting per LLM consumption

Sezione tecnica importante: come strutturiamo i campi stringa per massimizzare la qualità delle risposte LLM.

### 9.1 Numeri

- Importi monetari sempre con simbolo + spazio + valuta: `"$800 USD"`, `"€750"`, `"$14,000 MXN"`.
- Migliaia con virgole (formato US) per USD ed EN; con punti per ES e MXN nei display europei. **Per uniformità v1, sempre virgole**: `"$14,000 MXN"`. Si valuta locale-aware in v2.
- Percentuali con 1 decimale max: `"3.5%"`, `"+312%"`. Mai `"3.50%"`, mai `"+312.0%"`.
- Range: separatore `–` (en-dash, U+2013), spazi attorno: `"$3.50 – $9.80 USD"`. Mai `-`, `~`, `to`.

### 9.2 Stringhe descrittive

- Descrizioni 1-3 frasi, mai paragrafi lunghi: l'LLM legge meglio frasi separate.
- Niente bullet inline ("• ", "* ") nei campi stringa: l'LLM le aggiunge da sé se serve.
- Niente HTML, niente Markdown nei valori: solo plain text.
- Niente emoji nei dati (eccezione: `⚠️` solo in `nota` per warning critici come "datos desfasados").

### 9.3 Liste

- Liste sempre `list[str]` o `list[ModelloPydantic]`, mai stringhe con `;` come separator.
- Lunghezza tipica 3-6 elementi. Più di 8 elementi → considera splittare in due liste o usare `categoria`.

### 9.4 Date

- Formato `YYYY-MM` per mese/anno, `YYYY-MM-DD` per giorni completi. ISO 8601.
- Periodi: `"Q2 2026"` o `"H1 2026"`, mai `"primer semestre 2026"` (verbose).

### 9.5 Riferimenti incrociati

- ID di altri record: stringa esattta dello slug, es. `"servicios_aplicados": ["seo-latam", "google-ads-latam"]`.
- L'LLM **non** segue automaticamente questi link — ma li espone come "los servicios fueron X e Y". Se vuole dettaglio, chiama `obtener_servicios`.

---

## 10. Decisioni canoniche Tier 1 (locked)

| ID | Decisione | Motivazione |
|---|---|---|
| **D-T1-001** | 4 tool fissi in v1: `obtener_servicios`, `caso_de_estudio`, `benchmark_sector`, `glosario_marketing` | Coverage completa info pubblica Segmenta, scope minimale per M1. |
| **D-T1-002** | Tool descriptions in spagnolo LATAM-neutral, max ~400 char ognuna | Mercato target, leggibilità nei client MCP. |
| **D-T1-003** | Sezione "Cuándo usar" obbligatoria in ogni tool description con vocabolario d'innesco | Massimizza probability che LLM scelga il tool. |
| **D-T1-004** | Latency budget < 50ms p95 per ogni Tier 1 | Tutto in-memory, nessuna I/O nel hot path. |
| **D-T1-005** | Output strutturati Pydantic — mai stringhe HTML/Markdown nei valori | Coerenza, citation-friendly, l'LLM rende il display. |
| **D-T1-006** | `match_type` esposto in output di `caso_de_estudio` e `benchmark_sector` | Trasparenza su come è stato risolto il filtro `pais`. |
| **D-T1-007** | Anonimizzazione hard-rule in `caso_de_estudio` (Pydantic validator) | Compliance LFPDPPP, SR-004 enforcement. |
| **D-T1-008** | Importi sempre in USD canonico + conversione MXN/EUR formattata in output | Coerente con D-MP-018 e D-D-008. |
| **D-T1-009** | Strategia fallback 4-step per filtro `pais` in tutti i tool: esatto → aggregato → LATAM/US_HISPANIC → no_match | Mai inventare dati, sempre dichiarare match level. |
| **D-T1-010** | Suggerimenti via Levenshtein per `glosario_marketing` quando termine non trovato | UX: utente impara senza dover chiedere "lista termini disponibili". |
| **D-T1-011** | `obtener_servicios` ordina per priorità: paquetes verticali first, poi seo/sem/web/ecom/crm/altri | Highlight valore differenziante (paquetes verticali = alta margine). |
| **D-T1-012** | `caso_de_estudio` ordina per data desc | Casi più recenti prima. Freshness signal per LLM. |
| **D-T1-013** | Range valuta usando en-dash (`–`, U+2013), non hyphen | Tipograficamente corretto, leggibile. |
| **D-T1-014** | Locale support 4-livelli: es-LATAM (default), es-MX, es-ES, en-US | Mercati primari coperti, fallback automatico. |
| **D-T1-015** | Warning automatico in benchmark se `ultima_actualizacion > 6 mesi` | Trasparenza, evita di servire dati stantii. |
| **D-T1-016** | `obtener_servicios` filter `incluir_no_publicos` default `false` | Sicurezza by default; servizi beta/interni non esposti. |
| **D-T1-017** | Test coverage Tier 1 ≥ 90% | Tier 1 è critical path, deve essere robusto. |
| **D-T1-018** | Nessun side effect, nessun state mutation in Tier 1 | Permette caching aggressivo, idempotency naturale, parallelismo. |
| **D-T1-019** | Tool tag in output Tier 1: `tier: "1"` propagato in log per analytics | Permette segmentazione metriche per tier. |
| **D-T1-020** | Ogni tool include un `nota` testuale finale come campo di output | Spazio per warning, fonti, suggerimenti di tool successivi. |

---

## 11. Decisioni aperte Tier 1

| ID | Decisione | Bloccare entro | Owner |
|---|---|---|---|
| **DECISION-OPEN-T1-001** | Suggerimenti glosario: solo Levenshtein o aggiungere semantic search (embedding) in v2 | M5 | Claudio |
| **DECISION-OPEN-T1-002** | Locale-aware number formatting (`$14.000` per ES vs `$14,000` per US): v1 uniforme o v2 contestuale | M2 | Claudio |
| **DECISION-OPEN-T1-003** | Includere campo `relevancia_score` in `caso_de_estudio` output (per ordinamento alternativo) | M3 | Claudio + Alessio |
| **DECISION-OPEN-T1-004** | Aggiungere parametro `idioma_output` in tool Tier 1 per generare output in EN per US-anglo | M5 | Claudio + Romina |
| **DECISION-OPEN-T1-005** | Esporre uno shorthand tool `consultar_segmenta` che dispatcha a Tier 1 in base a query NL | v2 | Claudio |

---

## 12. Versioning di questo documento

| Versione | Data | Autore | Note |
|---|---|---|---|
| 1.0 | 2026-05-10 | Claude (proposta) + Claudio (revisione) | Prima stesura completa. 4 tool con spec dettagliate, signature, output schema, edge cases, test criteria. |

---

## Note per il changelog

*(Sezione vuota in v1.0 — verrà popolata se emergono incongruenze nei file successivi che richiedono retrofitting in questo TOOLS-TIER1.)*

---

**Fine 04-TOOLS-TIER1.md v1.0.**
