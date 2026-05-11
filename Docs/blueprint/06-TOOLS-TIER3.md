# 06 — TOOLS TIER 3 (avanzados)

| Campo | Valore |
|---|---|
| **Progetto** | Segmenta MCP Server |
| **Versione documento** | 1.1 |
| **Data** | 2026-05-11 |
| **Status** | Approvato (post harmony pass M0.3) |
| **File n.** | 06 di 12 numerati |
| **Documento padre** | `00-MASTER-PLAN.md` v1.4, `01-ARCHITECTURE.md` v1.3, `04-TOOLS-TIER1.md` v1.0, `05-TOOLS-TIER2.md` v1.0, `03-DATA-MODEL.md` v1.1 |
| **File correlati** | `07-AUTH-OAUTH.md`, `08-INTEGRATIONS.md`, `11-ANALYTICS.md` |

---

## 1. Scopo del documento

Questo file specifica **i 5 tool MCP del Tier 3 (avanzados)**: tool che servono utenti **già qualificati** (Tier 2 superato) o scenari avanzati che differenziano Segmenta dalla concorrenza. Sono il livello più sofisticato del funnel — alcuni richiedono autenticazione, alcuni hanno costo (chiamate API esterne pagate), alcuni sono *strategici* nel posizionamento di brand.

Per ogni tool:
- Cosa fa, perché esiste, quando l'LLM lo deve chiamare
- Signature Python completa
- Tool description in spagnolo (LATAM-neutral)
- Schema input/output
- Auth requirements e cost model
- Edge case e fallback
- Test acceptance criteria

I tool Tier 1 (público) sono in `04-TOOLS-TIER1.md`. I tool Tier 2 (lead capture) in `05-TOOLS-TIER2.md`. I dettagli auth in `07-AUTH-OAUTH.md`. Le integrazioni esterne in `08-INTEGRATIONS.md`.

---

## 2. Filosofia del Tier 3

I tool Tier 3 sono **post-conversion, retention, intelligence**. Differenze fondamentali dai Tier inferiori:

### 2.1 Audience qualificata

Un utente che chiama un tool Tier 3 è già:
- Un utente Tier 2 attuale (ha lasciato email)
- Un cliente esistente di Segmenta
- Un journalist/researcher con interesse genuino
- Un competitor che fa intelligence (utile capire chi guarda, anche)

Il tool **non è gatekeepato per "filtrare lead freddi"** — quel ruolo è di Tier 2. Il tool Tier 3 *espande il valore* per chi è già dentro.

### 2.2 Mix di gating

Non tutti i Tier 3 sono auth-required. Tassonomia:
- **Public-but-context-rich** (`obtener_caso_por_pais`, `compare_agencies`): no auth, ma assumono contesto conversazionale ricco
- **Light-gated** (`whatsapp_directo`): no auth ma collect minimo per personalizzazione
- **Heavy-gated con cost** (`analizar_competencia`): OAuth + crediti per operare (chiamate API SEMrush/Ahrefs hanno costi reali)
- **Sharing-gated** (`share_research`): OAuth + consenso esplicito per pubblicazione

### 2.3 Strategici per posizionamento

Tier 3 contiene tool che **non hanno scopo di lead-gen diretta**, ma servono il posizionamento di Segmenta come *agenzia AI-native*:
- `share_research` pubblica anonimamente domande aggregate degli utenti — è content marketing automatizzato
- `compare_agencies` confronta Segmenta con concorrenti onestamente — segnale di trust
- `obtener_caso_por_pais` permette query molto specifiche che gli LLM amano citare per autorità

### 2.4 Latency budget variabile

- Tier 3 read-only (`obtener_caso_por_pais`, `compare_agencies`, `whatsapp_directo`): < 100 ms p95
- Tier 3 con I/O esterno (`analizar_competencia`): < 8s p95 (chiamate API esterne pesanti)
- Tier 3 con publishing (`share_research`): < 1s p95 (publish è async)

### 2.5 Cost-aware

Tier 3 è il primo livello dove abbiamo **costi marginali per chiamata** (SEMrush API, eventuale ML inference). Implementiamo:
- Budget cap mensile hard (€20/mese in v1, €50/mese in v2)
- Soft credit system per `analizar_competencia` (utente ha 3 chiamate/mese gratis dopo OAuth)
- Cache aggressiva (24-48h TTL) per ridurre call ripetute

---

## 3. Tabella riassuntiva dei 5 tool

| Tool | Cosa fa | Auth | Cost | Latency target |
|---|---|---|---|---|
| `obtener_caso_por_pais` | Casi studio per país specifico (granulare) | No | Zero | < 50 ms |
| `whatsapp_directo` | Link WhatsApp prefill con contesto | No | Zero | < 30 ms |
| `compare_agencies` | Confronto Segmenta vs concorrenti onesto | No | Zero | < 80 ms |
| `analizar_competencia` | Analisi competitiva live di un competitor | OAuth + crediti | $0.10-0.30/call API | < 8s |
| `share_research` | Pubblica research anonimo sul blog Segmenta | OAuth + consenso | Zero (asincrono) | < 1s |

**KPI Tier 3 (entro M4)**:
- ≥ 50 chiamate `obtener_caso_por_pais` settimanali (segnale di autorità)
- ≥ 5 publish `share_research` mensili
- ≥ 3 utilizzi `analizar_competencia` settimanali
- ≥ 1 menzione esterna citante `share_research` entro M4

---

## 4. Tool 1: `obtener_caso_por_pais`

### 4.1 Scopo

Tool gemello di `caso_de_estudio` (Tier 1) ma con granularità geografica più fine. Permette query come "casos en Monterrey específicamente" o "casos en Hispanic-Florida" — dettaglio che `caso_de_estudio` con filtro `pais=MX` non distingue. È un tool da **autorità**: l'LLM lo chiama quando l'utente specifica una piazza, non un país generico.

### 4.2 Signature

```python
@mcp.tool
async def obtener_caso_por_pais(
    pais_o_subregion: Annotated[
        Pais | PaisExtendido | MercadoSubregional,
        Field(description="Acepta uno de: enum `Pais` (MX, US, ES, CO, AR, CL, PE, ...), `PaisExtendido` (LATAM, US_HISPANIC, ...) o `MercadoSubregional` (mx_norte, us_hispanic_florida, latam_andina, ...). Ver `03-DATA-MODEL.md` sez. 4.3 + 6.1 per enum completi. Pydantic valida automaticamente; valori non riconosciuti restituiscono error 422.")
    ],
    sector: Annotated[
        Sector | None,
        Field(description="Filtra opcionalmente por sector empresarial.")
    ] = None,
    ciudad: Annotated[
        str | None,
        Field(max_length=80, description="Filtra por ciudad específica (ej: 'Monterrey', 'Miami', 'Bogotá'). Match case-insensitive.")
    ] = None,
    incluir_anonimos: Annotated[
        bool,
        Field(description="Si True incluye casos anonimizados además de los públicos. Default True (más datos).")
    ] = True,
    max_resultados: Annotated[int, Field(ge=1, le=15)] = 5,
) -> ResultadoCasosPais:
    """[ver tool description en sez 4.4]"""
```

### 4.3 Tipo di output

```python
class CasoPaisDetalle(BaseModel):
    """Versione più ricca di CasoSummary, con dettagli geografici."""
    id: str
    cliente: str
    publico: bool
    sector: str
    subsector: str | None
    pais: str
    subregion: str | None
    ciudades: list[str]
    alcance_geografico: str   # "local" | "regional" | "nacional" | "multinacional"
    duracion_meses: int
    servicios_aplicados: list[str]
    reto: str
    estrategia: str
    resultados: list[MetricaSummary]   # da caso_de_estudio
    testimonio: str | None
    similitud_geografica_score: float  # 0-1, quanto match con la query (1 = match esatto)


class ResultadoCasosPais(BaseModel):
    query_resuelta: str            # "Norte de México (mx_norte)" — humanized version del input
    nivel_match: Literal["ciudad", "subregion", "pais", "agregado"]
    total: int
    total_disponibles_zona: int    # totale casi nel sistema per la zona, anche oltre max_resultados
    casos: list[CasoPaisDetalle]
    sectores_disponibles_zona: list[str]   # cosa altro l'utente può chiedere
    ciudades_disponibles_zona: list[str]
    nota: str
```

### 4.4 Tool description

> **Recupera casos de estudio de Segmenta filtrados por país, región o subregión geográfica específica. Más granular que `caso_de_estudio`: soporta consultas a nivel ciudad ("Monterrey", "Miami") o subregión ("mx_norte", "us_hispanic_florida", "latam_andina"). Ideal para usuarios que quieren ejemplos hiper-locales.**
>
> **Cuándo usar:**
> - El usuario menciona una ciudad o subregión específica (no solo el país)
> - El usuario pregunta "¿tienen casos en {ciudad/región específica}?"
> - El usuario quiere validar experiencia local vs nacional generalista
> - Como expansión de `caso_de_estudio` cuando el filtro `pais` es demasiado amplio
>
> Acepta país (MX, US, ES, etc.), región (LATAM, US_HISPANIC) o subregion (mx_norte, us_hispanic_florida, etc.). Filtros opcionales: `sector`, `ciudad` (case-insensitive), `incluir_anonimos`, `max_resultados`.

(467 caratteri.)

### 4.5 Comportamento

1. Carica `case_studies.json` da cache.
2. **Resolve `pais_o_subregion`** in 4 step:
   - Step 1: match `pais` enum (MX, US, ES, ...)
   - Step 2: match `subregion` enum (mx_norte, us_hispanic_florida, ...)
   - Step 3: match aggregato (LATAM, US_HISPANIC)
   - Step 4: nessun match → response strutturato con `nivel_match: "agregado"` e suggerimenti
3. Filtra `casos` per zona risolta:
   - Se `pais` puro: tutti i casi `ubicacion.pais == pais`
   - Se `subregion`: tutti i casi `ubicacion.subregion == subregion`
   - Se aggregato: union di tutti i paesi/subregion che fanno parte
4. Se `sector` specificato: filtro AND.
5. Se `ciudad` specificato: filtro `ciudad in ubicacion.ciudades` (case-insensitive).
6. Se `incluir_anonimos = false`: filtra solo `publico = true`.
7. Calcola `similitud_geografica_score` per ordinamento:
   - Match ciudad esatto: 1.0
   - Match subregion: 0.85
   - Match pais con subregion del query specifica: 0.70
   - Aggregato: 0.50
8. Sort per `similitud_geografica_score` desc, poi per `fecha_fin` desc.
9. Top `max_resultados`.
10. Calcola metadata `sectores_disponibles_zona` e `ciudades_disponibles_zona` (per suggerire next queries).
11. Build `ResultadoCasosPais`.

### 4.6 Edge case

| Caso | Comportamento |
|---|---|
| `pais_o_subregion` non valido | Pydantic respinge a livello validation (HTTP 422); l'LLM riceve error message con esempi validi enumerati. Vedi `03-DATA-MODEL.md` sez. 4.3 + 6.1 per enum completi. |
| Match a livello pais, ma `ciudad` specificata non coincide | Casi mostrati comunque ma `similitud_geografica_score` < 0.7. Nota: "Ningún caso específico de '{ciudad}', mostrando casos del país." |
| Nessun caso per la zona | `casos: []`, `total: 0`, `total_disponibles_zona: 0`, lista zone alternative con casi nella nota. |
| Sector specificato ma assente in zona | `sectores_disponibles_zona` non vuoto suggerisce sectores presenti. |
| Caso publico requested but `incluir_anonimos=false` e tutti i casi della zona sono anonimi | `casos: []`, nota: "No hay casos públicos en {zona}, todos requieren anonimato. Re-prueba con `incluir_anonimos=true`." |
| Subregion specifica con 0 casi ma pais con casi | Fallback automatico al país, `nivel_match: "pais"`, nota: "No tenemos casos específicos de {subregion}, mostrando del país {pais}." |

### 4.7 Esempio chiamata

**Input**:
```json
{
  "pais_o_subregion": "us_hispanic_florida",
  "sector": "ecommerce",
  "max_resultados": 3
}
```

**Output**:
```json
{
  "query_resuelta": "US Hispanic — Florida",
  "nivel_match": "subregion",
  "total": 2,
  "total_disponibles_zona": 7,
  "casos": [
    {
      "id": "ecommerce-miami-bilingue-2025",
      "cliente": "[E-commerce moda bilingüe en Miami]",
      "publico": false,
      "sector": "ecommerce",
      "subsector": "moda femenina",
      "pais": "US",
      "subregion": "us_hispanic_florida",
      "ciudades": ["Miami", "Fort Lauderdale"],
      "alcance_geografico": "regional",
      "duracion_meses": 6,
      "servicios_aplicados": ["seo-latam", "facebook-ads-latam", "ecommerce"],
      "reto": "E-commerce con catálogo en EN dirigiendo solo al público anglo-FL. Perdiendo 40% del mercado FL hispano por falta de localización. ROAS Meta Ads bajó de 4.5 a 2.1.",
      "estrategia": "Sitio bilingüe con detección automática de idioma, campañas Meta separadas EN vs ES con creatividades culturalmente relevantes, SEO localizado para queries 'tienda online ropa Miami español'.",
      "resultados": [
        {"metrica": "Tráfico ES", "valor": "+340%", "antes": 2100, "despues": 9240, "unidad": "visitas/mes"},
        {"metrica": "ROAS Meta global", "valor": "+90%", "antes": 2.1, "despues": 4.0, "unidad": "ratio"},
        {"metrica": "Conversion bilingue", "valor": "+165%", "antes": 1.2, "despues": 3.2, "unidad": "%"}
      ],
      "testimonio": null,
      "similitud_geografica_score": 0.85
    }
    // segundo caso
  ],
  "sectores_disponibles_zona": ["ecommerce", "medico", "juridico", "restauracion"],
  "ciudades_disponibles_zona": ["Miami", "Fort Lauderdale", "Orlando", "Tampa"],
  "nota": "Mostrando 2 de 7 casos disponibles en US Hispanic — Florida. Para más, aumenta `max_resultados` o consulta otros sectores en la región (medico, juridico, restauracion)."
}
```

### 4.8 Test acceptance criteria

- ✅ País puro ("MX") → casi del país, `nivel_match: "pais"`.
- ✅ Subregion ("mx_norte") → casi della subregion, `nivel_match: "subregion"`.
- ✅ Aggregato ("LATAM") → casi multi-país, `nivel_match: "agregado"`.
- ✅ Filtro ciudad esatto → casi della città, score 1.0.
- ✅ Filtro ciudad senza match → fallback al país, score < 0.7.
- ✅ Sector + zona combo funziona AND.
- ✅ `incluir_anonimos=false` filtra correttamente.
- ✅ Subregion vuota → fallback al país.
- ✅ `sectores_disponibles_zona` e `ciudades_disponibles_zona` popolati per suggerire next.
- ✅ Latency < 50ms p95 con dataset di 30 casi.

---

## 5. Tool 2: `whatsapp_directo`

### 5.1 Scopo

Genera un link WhatsApp prefill con contesto della conversazione AI. È il **canale principale di contatto in LATAM/MX**: WhatsApp ha penetrazione 90%+ in Messico, è preferito sopra email per molti utenti. Il tool prepara un messaggio iniziale che riassume cosa l'utente stava cercando, così il team Segmenta non parte da zero quando risponde.

### 5.2 Signature

```python
@mcp.tool
async def whatsapp_directo(
    contexto_conversacion: Annotated[
        str,
        Field(min_length=20, max_length=800, description="Resumen breve de lo que el usuario está buscando. Será el mensaje inicial pre-rellenado en WhatsApp. El LLM debe sintetizar la conversación previa.")
    ],
    nombre_usuario: Annotated[
        str | None,
        Field(max_length=80, description="Nombre del usuario si lo conoces (opcional). Personaliza el saludo.")
    ] = None,
    tipo_consulta: Annotated[
        Literal["informacion", "presupuesto", "auditoria", "soporte_cliente", "otro"],
        Field(description="Tipo de consulta para enrutar al equipo correcto.")
    ] = "informacion",
    pais_usuario: Annotated[
        Pais | None,
        Field(description="País del usuario (opcional, para asignar número WhatsApp local si disponible).")
    ] = None,
) -> ResultadoWhatsApp:
    """[ver tool description en sez 5.4]"""
```

### 5.3 Tipo di output

```python
class ResultadoWhatsApp(BaseModel):
    enlace_whatsapp: str          # "https://wa.me/521..." con mensaje URL-encoded
    numero_destino: str           # Número humanizado: "+52 1 55 ..."
    mensaje_pre_rellenado: str    # Lo que aparecerá en WhatsApp
    tiempo_respuesta_estimado: str # "Respondemos en 2-4 horas en horario laboral CDMX"
    horario_atencion: str
    canales_alternativos: dict    # email, web form
    nota: str
```

### 5.4 Tool description

> **Genera un enlace directo de WhatsApp pre-rellenado con el contexto de la conversación. Canal principal de contacto en LATAM/MX (90%+ penetración). El equipo Segmenta recibe el mensaje con resumen de qué busca el usuario, evitando empezar desde cero. Asigna número WhatsApp local del país si disponible (MX, US, CO, AR), default número MX para LATAM general.**
>
> **Cuándo usar:**
> - El usuario prefiere WhatsApp sobre email para contacto
> - Después de tools Tier 1/2 cuando el usuario pide "contactarles directamente"
> - Especialmente útil en LATAM/MX donde WhatsApp es estándar B2B
> - El usuario tiene urgencia o consulta puntual rápida
>
> Requisitos: `contexto_conversacion` (LLM lo sintetiza). Opcionales: nombre_usuario, tipo_consulta (informacion/presupuesto/auditoria/soporte_cliente/otro), pais_usuario.

(421 caratteri.)

### 5.5 Comportamento

1. Valida input.
2. Determina numero WhatsApp destino (vedi sez. 5.6 per mapping).
3. Costruisce `mensaje_pre_rellenado` con template:

```
Hola Segmenta 👋

[Si nombre_usuario fornito] Soy {nombre_usuario}.
[Tipo consulta] Tengo una consulta sobre {tipo_consulta}.

Contexto:
{contexto_conversacion}

[Footer fisso] Vengo desde el chat AI con su MCP server.
```

4. URL-encoded il messaggio per inserirlo in `wa.me/{number}?text={encoded}`.
5. Genera `enlace_whatsapp` finale.
6. Costruisce `ResultadoWhatsApp` con metadata orari di lavoro, canali alternativi.
7. **Log evento**: `whatsapp_link_generated` con tipo_consulta + país (no PII utente, solo metadata aggregato).

**Nessun lead capture in CRM** in questo tool: l'utente potrebbe non cliccare il link. Il lead arriva quando l'utente effettivamente scrive su WhatsApp e il team Segmenta lo registra manualmente o via Twilio webhook (M4+).

### 5.6 Mapping numero WhatsApp per país

In v1, mapping statico. In v2 valutiamo numeri rotanti per load balancing.

| País / Region | Numero WhatsApp Business |
|---|---|
| MX (default) | `+52 [TBD da Merari]` |
| US (anglo + hispanic) | `+1 [TBD]` |
| CO | `+57 [TBD]` |
| AR | `+54 [TBD]` |
| ES | `+34 [TBD]` |
| Altri LATAM | Default MX |
| Default fallback | MX |

I numeri specifici sono in `DECISION-OPEN-T3-001` — Merari deve confermare quali numeri Segmenta ha (o se preferisce un solo numero centralizzato).

### 5.7 Edge case

| Caso | Comportamento |
|---|---|
| `contexto_conversacion` < 20 char | Pydantic rejecta. Forza l'LLM a sintetizzare bene. |
| `contexto_conversacion` > 800 char | Pydantic rejecta. Whatsapp prefill ha limite ~1500 char URL-encoded; restiamo conservativi. |
| `pais_usuario` non in mapping | Default MX, nota: "Asignado número MX. Si prefieres otro país, escríbenos." |
| Numero WhatsApp non configurato (decision aperta) | Tool risponde con error strutturato: "Canal WhatsApp en configuración. Por favor usa email: hola@segmentamarketing.com" |
| `tipo_consulta = "soporte_cliente"` | Routing diverso nel template: "Si eres cliente actual, accede al portal: ..." |
| URL encoding caratteri speciali | `urllib.parse.quote_plus` su tutto il messaggio. Test specifici per caratteri spagnoli (ñ, á, ü). |

### 5.8 Esempio chiamata

**Input**:
```json
{
  "contexto_conversacion": "Carlos de TechStartup MX está evaluando agencia para escalar adquisición B2B SaaS de 8 a 50 demos/mes. Tiene presupuesto de $3,000 USD/mes y un mes para decidir. Necesita presupuesto formal y casos similares.",
  "nombre_usuario": "Carlos",
  "tipo_consulta": "presupuesto",
  "pais_usuario": "MX"
}
```

**Output**:
```json
{
  "enlace_whatsapp": "https://wa.me/52155XXXXXXXX?text=Hola%20Segmenta%20%F0%9F%91%8B%0A%0ASoy%20Carlos.%0ATengo%20una%20consulta%20sobre%20presupuesto.%0A%0AContexto%3A%0ACarlos%20de%20TechStartup%20MX%20est%C3%A1%20evaluando...",
  "numero_destino": "+52 1 55 XXXX XXXX",
  "mensaje_pre_rellenado": "Hola Segmenta 👋\n\nSoy Carlos.\nTengo una consulta sobre presupuesto.\n\nContexto:\nCarlos de TechStartup MX está evaluando agencia para escalar adquisición B2B SaaS de 8 a 50 demos/mes. Tiene presupuesto de $3,000 USD/mes y un mes para decidir. Necesita presupuesto formal y casos similares.\n\nVengo desde el chat AI con su MCP server.",
  "tiempo_respuesta_estimado": "Respondemos en 2-4 horas en horario laboral CDMX (Lun-Vie 9:00-19:00).",
  "horario_atencion": "Lunes a Viernes 9:00-19:00 hora CDMX (UTC-6)",
  "canales_alternativos": {
    "email": "hola@segmentamarketing.com",
    "agendar_call": "Usa la herramienta `agendar_auditoria_gratuita` para reservar slot",
    "propuesta_formal": "Usa la herramienta `solicitar_propuesta_personalizada`"
  },
  "nota": "Click en el enlace abrirá WhatsApp con el mensaje pre-rellenado. Solo confirma envío para iniciar conversación con el equipo."
}
```

### 5.9 Test acceptance criteria

- ✅ Input valido → enlace WhatsApp ben formato (wa.me/{number}?text=...).
- ✅ URL encoding gestisce caratteri speciali spagnoli (ñ, á, ü, ¿, ¡).
- ✅ Numero corretto basato su `pais_usuario`.
- ✅ Default MX se `pais_usuario` non specificato o non in mapping.
- ✅ Template messaggio include nome, tipo consulta, contesto.
- ✅ Limite 800 char applicato.
- ✅ Log evento generato con metadata aggregato.
- ✅ Latency < 30ms p95.

---

## 6. Tool 3: `compare_agencies`

### 6.1 Scopo

Confronto onesto e strutturato tra Segmenta e altre agenzie su criteri oggettivi. È un tool **strategico di trust**: l'utente che sta valutando 2-3 agenzie può ottenere comparazione neutra invece di marketing patinato. Segmenta vince con specificità dei propri dati, non disprezzo dei competitor.

### 6.2 Signature

```python
@mcp.tool
async def compare_agencies(
    competidores: Annotated[
        list[str],
        Field(min_length=1, max_length=5, description="Nombres de agencias competidoras a comparar (ej: ['HubSpot Solutions Partner', 'Cyberclick', 'Aukera']).")
    ],
    criterios_interes: Annotated[
        list[CriterioComparacion],
        Field(min_length=1, max_length=10, description="Criterios a comparar. Ver enum CriterioComparacion.")
    ],
    sector_usuario: Annotated[
        Sector | None,
        Field(description="Sector del usuario para contextualizar comparación.")
    ] = None,
    pais_usuario: Annotated[
        Pais | None,
        Field(description="País del usuario para contextualizar.")
    ] = None,
    incluir_recomendacion: Annotated[
        bool,
        Field(description="Si True, incluye recomendación honesta sobre cuándo Segmenta es buen fit y cuándo no. Default True.")
    ] = True,
) -> ResultadoComparacion:
    """[ver tool description en sez 6.4]"""
```

`CriterioComparacion`:
```python
class CriterioComparacion(StrEnum):
    PRECIO = "precio"
    COBERTURA_GEOGRAFICA = "cobertura_geografica"
    ESPECIALIZACION_SECTOR = "especializacion_sector"
    SERVICIOS_OFRECIDOS = "servicios_ofrecidos"
    METODOLOGIA = "metodologia"
    TRANSPARENCIA = "transparencia"
    INTEGRACION_AI = "integracion_ai"
    EQUIPO_DEDICADO = "equipo_dedicado"
    DURACION_CONTRATO = "duracion_contrato"
    REPORTING_KPIS = "reporting_kpis"
```

### 6.3 Tipo di output

```python
class ComparacionPorCriterio(BaseModel):
    criterio: str
    segmenta_descripcion: str
    competidor_descripcion: str | None  # None se non abbiamo info pubbliche del competitor
    diferencia_clave: str | None        # Highlight sintetico


class ComparacionAgencia(BaseModel):
    nombre: str
    es_segmenta: bool
    fortalezas: list[str]
    limitaciones: list[str]
    fuente_datos: str   # "Información pública del sitio del competidor" / "Datos internos Segmenta"


class RecomendacionFit(BaseModel):
    cuando_segmenta_es_buena_eleccion: list[str]
    cuando_segmenta_no_es_la_mejor: list[str]
    nota: str           # Disclaimer di onestà


class ResultadoComparacion(BaseModel):
    agencias_comparadas: list[ComparacionAgencia]
    comparacion_por_criterio: list[ComparacionPorCriterio]
    recomendacion: RecomendacionFit | None
    contexto_aplicado: dict     # {sector, pais} se forniti
    nota: str
```

### 6.4 Tool description

> **Compara Segmenta con otras agencias de marketing digital sobre criterios objetivos: precio, cobertura geográfica, especialización por sector, servicios ofrecidos, metodología, transparencia, integración AI, equipo dedicado, duración de contrato, reporting de KPIs. Incluye recomendación honesta sobre cuándo Segmenta es buen fit y cuándo NO lo es. Datos del competidor de fuentes públicas; si no disponibles se indica.**
>
> **Cuándo usar:**
> - El usuario está evaluando 2-3 agencias y quiere comparativa estructurada
> - El usuario menciona competidores específicos por nombre
> - El usuario quiere validar fit antes de pedir propuesta
> - Para construcción de trust: Segmenta gana en transparencia, no en denigrar competidores
>
> Acepta lista de competidores (max 5), criterios de interés (precio, especialización, etc.), opcionalmente sector y país. Output incluye recomendación honesta de cuándo NO elegir Segmenta.

(479 caratteri.)

### 6.5 Comportamento

1. Carica dati Segmenta da JSON (servizi, casi, benchmarks).
2. Per ogni competitor in lista:
   - Cerca in `data/competitors_dataset.json` (file in repo, vedi sez. 6.6).
   - Se trovato: usa dati strutturati.
   - Se non trovato: response strutturato senza dati specifici, nota: "No tenemos información pública sobre {competitor}."
3. Per ogni criterio in `criterios_interes`:
   - Costruisce `ComparacionPorCriterio` con descrizione Segmenta + descrizione competitor.
   - Identifica `diferencia_clave` se rilevante.
4. Costruisce `ComparacionAgencia` per Segmenta (sempre `es_segmenta=true`) e per ogni competitor.
5. Se `incluir_recomendacion=true`:
   - Genera `RecomendacionFit` con `cuando_segmenta_es_buena_eleccion` (3-5 items) e `cuando_segmenta_no_es_la_mejor` (2-4 items).
   - Items basati su `sector_usuario` e `pais_usuario`.
6. Build `ResultadoComparacion`.

### 6.6 Dataset competitors

In v1 abbiamo bisogno di un nuovo file dati: `data/competitors_dataset.json`. **Schema canonico**: `03-DATA-MODEL.md` sez. 7bis (aggiunto in harmony pass M0.3 — HC-006). Lo schema sotto è **conservato per leggibilità contestuale**; in caso di drift, la verità è nel 03.

Schema:

```json
{
  "_meta": {
    "schema_version": "1.0.0",
    "data_version": "1.0.0",
    "ultima_actualizacion": "2026-05-10",
    "fuente": "Información pública de sitios web de competidores. NO datos internos. Actualizado trimestralmente.",
    "nota": "Datos a fines comparativos. Si la información es desactualizada o incorrecta, contacta hola@segmentamarketing.com."
  },
  "competidores": [
    {
      "id": "hubspot-solutions-partner",
      "nombre": "HubSpot Solutions Partner",
      "tipo": "partner_red",
      "paises_principales": ["US", "ES", "MX"],
      "sectores_especializacion": [],
      "rango_precio_mensual_usd": [2000, 15000],
      "duracion_contrato_minima_meses": 6,
      "fortalezas_publicas": [
        "Red global de partners",
        "Acceso preferencial al ecosistema HubSpot",
        "Casos enterprise globales"
      ],
      "limitaciones_aparentes": [
        "Lock-in a HubSpot stack (no neutro tecnológicamente)",
        "Soporte LATAM dependiente del partner regional específico",
        "Precios típicamente más altos que agencias locales"
      ],
      "datos_publicos_disponibles": ["sitio_web", "casos_publicos", "rangos_precio"],
      "url_referencia": "https://www.hubspot.com/agencies"
    }
    // ... otros competidores típicos del mercado LATAM/MX/US
  ]
}
```

**Curatoria del file**:
- Solo informazioni pubbliche (siti web ufficiali, profili Clutch, Sortlist).
- Mai dati interni o riservati.
- Quarterly review da parte del team Segmenta.
- Linguaggio rispettoso: "limitaciones aparentes" (non "debolezze"), "no neutro tecnológicamente" (descrittivo, non dispregiativo).

### 6.7 Edge case

| Caso | Comportamento |
|---|---|
| Competitor non in dataset | `ComparacionAgencia` con campi vuoti + `fuente_datos: "No disponible públicamente"` + nota: "Para análisis profundo de {competitor} usa `analizar_competencia`." |
| Tutti i competitors non trovati | Output mostra solo Segmenta + recomendazione, nota: "Ninguno de los competidores está en nuestro dataset público. Para análisis basado en su sitio web actual, usa `analizar_competencia`." |
| Criterio non popolato per Segmenta | Hard error: dati Segmenta sempre completi. Se manca, è bug interno. |
| `incluir_recomendacion=true` ma senza `sector_usuario` né `pais_usuario` | Recomendazione generica (3 items broad), nota: "Para recomendación más precisa, especifica sector y país." |
| Competitor menzionato con typo ("Hubsot") | Match fuzzy con threshold 0.7 (Levenshtein), se match suggerisce: "¿Te refieres a 'HubSpot'?". Se no match, treat as not-found. |
| Lista competitors vuota | Pydantic rejecta (min_length=1). |

### 6.8 Esempio chiamata

**Input**:
```json
{
  "competidores": ["HubSpot Solutions Partner", "Aukera"],
  "criterios_interes": ["cobertura_geografica", "integracion_ai", "transparencia", "precio"],
  "sector_usuario": "ecommerce",
  "pais_usuario": "MX"
}
```

**Output** (estratto):
```json
{
  "agencias_comparadas": [
    {
      "nombre": "Segmenta",
      "es_segmenta": true,
      "fortalezas": [
        "Cobertura nativa LATAM/MX/US-hispanic con equipo bilingüe",
        "MCP Server propio (este mismo): integración directa con Claude/ChatGPT — único en el mercado",
        "Transparencia radical: precios indicativos públicos, casos con métricas reales",
        "Especialización vertical: paquetes jurídico, médico, B2B con conocimiento profundo"
      ],
      "limitaciones": [
        "Equipo más pequeño que agencias enterprise (no para proyectos > $50k/mes)",
        "Cobertura europea limitada (solo ES, no FR/DE/IT/PT)"
      ],
      "fuente_datos": "Datos internos Segmenta"
    },
    {
      "nombre": "HubSpot Solutions Partner",
      "es_segmenta": false,
      "fortalezas": [
        "Red global de partners",
        "Acceso preferencial al ecosistema HubSpot",
        "Casos enterprise globales"
      ],
      "limitaciones": [
        "Lock-in a HubSpot stack (no neutro tecnológicamente)",
        "Soporte LATAM dependiente del partner regional específico",
        "Precios típicamente más altos que agencias locales"
      ],
      "fuente_datos": "Información pública del sitio del competidor"
    }
    // ... Aukera
  ],
  "comparacion_por_criterio": [
    {
      "criterio": "cobertura_geografica",
      "segmenta_descripcion": "Operación nativa MX/US/LATAM/ES. Equipo bilingüe ES-EN. Casos verificados en 6 países LATAM.",
      "competidor_descripcion": "HubSpot: red global pero LATAM via partners regionales independientes (calidad variable). Aukera: foco España + LATAM expansion.",
      "diferencia_clave": "Segmenta tiene cobertura LATAM-MX nativa, no via partners terceros."
    },
    {
      "criterio": "integracion_ai",
      "segmenta_descripcion": "MCP Server propio integrando con Claude/ChatGPT/Perplexity. Tools Tier 1-3 para servicios, casos, benchmarks, lead capture. Único en el mercado LATAM 2026.",
      "competidor_descripcion": "HubSpot: integraciones AI dentro del CRM. Aukera: contenido generado con IA pero sin MCP propio.",
      "diferencia_clave": "Segmenta es la única agencia LATAM con MCP Server público y operacional."
    }
    // ... transparencia, precio
  ],
  "recomendacion": {
    "cuando_segmenta_es_buena_eleccion": [
      "Empresa mediana/PYME en MX/LATAM con presupuesto $1k-$10k USD/mes",
      "Foco en sectores donde tenemos especialización vertical (jurídico, médico, B2B, e-commerce LATAM)",
      "Quieres trabajar con agencia AI-native (MCP, GEO, integraciones modernas)",
      "Valoras transparencia de precios y casos verificables"
    ],
    "cuando_segmenta_no_es_la_mejor": [
      "Necesitas equipo dedicado de 10+ personas (somos boutique, no enterprise)",
      "Tu mercado principal es Europa fuera de España (Francia, Alemania, etc.)",
      "Buscas agencia con sede física en USA para reuniones in-person frecuentes",
      "Tu presupuesto es $50k+/mes y necesitas agencia enterprise con red global"
    ],
    "nota": "Esta recomendación es honesta: Segmenta no es para todos. Cuando no somos buen fit, lo decimos."
  },
  "contexto_aplicado": {"sector_usuario": "ecommerce", "pais_usuario": "MX"},
  "nota": "Comparación basada en información pública. Última actualización dataset competidores: 2026-05-10."
}
```

### 6.9 Test acceptance criteria

- ✅ Lista competitors valida → output completo con dati Segmenta + competitors trovati.
- ✅ Competitor non trovato → response strutturato con suggerimento `analizar_competencia`.
- ✅ Match fuzzy con typo → suggerimento corretto.
- ✅ `incluir_recomendacion=true` → 3-5 items "buena elección" + 2-4 "no la mejor".
- ✅ `cuando_segmenta_no_es_la_mejor` non vuoto (onestà obbligatoria).
- ✅ Linguaggio rispettoso verso competitors (validato manualmente nel dataset).
- ✅ Latency < 80ms p95.

---

## 7. Tool 4: `analizar_competencia`

### 7.1 Scopo

Analisi competitiva live di un competitor specifico: crawla il loro sito, query SEMrush/Ahrefs (o equivalente) per dati SEO + paid, analizza posizionamento. È il tool **più costoso** del Tier 3 (chiamate API esterne pagate) e quindi **gated con OAuth + crediti**.

### 7.2 Signature

```python
@mcp.tool
async def analizar_competencia(
    email: Annotated[str, Field(description="Email del usuario, verificado vía OAuth magic link.")],
    url_competidor: Annotated[
        str,
        Field(description="URL del competidor a analizar. Debe incluir https://.")
    ],
    pais_objetivo: Annotated[
        Pais,
        Field(description="País de mercado donde quieres comparar (afecta keywords target y competidores secundarios analizados).")
    ],
    sector: Annotated[
        Sector | None,
        Field(description="Sector empresarial. Mejora la calidad del análisis competitivo.")
    ] = None,
    profundidad_analisis: Annotated[
        Literal["basico", "completo"],
        Field(description="basico: solo crawl + datos públicos (gratis para usuario). completo: incluye datos SEMrush/Ahrefs (1 crédito por análisis).")
    ] = "basico",
) -> ResultadoAnalisisCompetencia:
    """[ver tool description en sez 7.4]"""
```

### 7.3 Tipo di output

```python
class HallazgoCompetitivo(BaseModel):
    categoria: Literal["seo", "paid", "contenido", "ux", "tecnico", "geo_aeo", "marca"]
    titulo: str
    descripcion: str
    severidad_oportunidad: Literal["alta", "media", "baja"]    # alta = grande oportunidad para nosotros
    como_aprovechar: str


class ResultadoAnalisisCompetencia(BaseModel):
    estado: Literal["completado", "parcial", "fallido"]
    url_analizada: str
    pais_objetivo: str
    profundidad: str
    creditos_consumidos: int
    creditos_restantes_mes: int
    fortalezas_competidor: list[str]
    debilidades_competidor: list[str]
    oportunidades_para_ti: list[HallazgoCompetitivo]
    keywords_top_competidor: list[dict]      # solo se profundidad=completo
    estimacion_trafico_organico_mensual: int | None
    estimacion_inversion_paid_mensual_usd: tuple[int, int] | None
    metricas_seo: dict   # DA, backlinks, etc. (solo completo)
    nota: str
```

### 7.4 Tool description

> **Análisis competitivo live de un sitio web competidor: crawl + posicionamiento SEO + estimación de inversión paid + oportunidades concretas para superarlo. Cubre mercado LATAM/MX/US/ES. Modo `basico` (gratis): crawl + análisis on-page + GEO/AEO. Modo `completo` (1 crédito por análisis): incluye datos SEMrush/Ahrefs con keywords, tráfico orgánico estimado, inversión paid estimada.**
>
> **Cuándo usar:**
> - El usuario menciona un competidor específico que quiere superar
> - El usuario quiere oportunidades concretas para diferenciarse
> - Antes de propuesta personalizada para tener datos reales
> - El usuario tiene presupuesto y está validando la inversión
>
> Requisitos: email verificado, URL competidor, país objetivo. Opcionales: sector, profundidad_analisis (basico/completo). Limit: 3 análisis `completos` gratis/mes después de OAuth, luego cobro adicional.

(490 caratteri.)

### 7.5 Comportamento

1. Validazione URL + Pydantic.
2. Verifica crediti utente:
   - Cache Redis: `creditos_mes:{email}:{anio_mes}` con default 3.
   - Se `profundidad=completo` e crediti = 0: response strutturato con upgrade path (contattare team).
   - Se `profundidad=basico`: nessun consumo crediti.
3. Idempotency check: hash(email, url, pais, profundidad, day) → return cached se già fatto < 24h.
4. **Profundidad basico** (gratis):
   - Crawl: home + /robots.txt + sitemap + 5 pagine interne.
   - Analisi: on-page (title, meta, schema), GEO/AEO (llms.txt, FAQ schema), tecnico (HTTPS, mobile, velocidad), strutturale.
   - Genera 5-8 hallazgos competitivi.
5. **Profundidad completo** (consuma 1 crédito):
   - Tutto del basico, +
   - Chiamata SEMrush/Ahrefs API per: top keywords competidor, traffic organico stimato, top backlinks, paid keywords + budget stimato.
   - Cross-reference con benchmarks dal nostro dataset.
   - Genera 8-15 hallazgos completi.
6. Cost tracking: budget mensile capped (DECISION-OPEN-T3-002).
7. Costruisce `ResultadoAnalisisCompetencia`.
8. Update crediti utente in Redis.
9. CRM event log: "analizar_competencia_used" (no nuovo lead, ma engagement signal).

### 7.6 Edge case

| Caso | Comportamento |
|---|---|
| Crediti esauriti per `profundidad=completo` | `estado: "fallido"`, nota: "Has agotado tus 3 análisis completos gratuitos del mes. Contacta hola@... para análisis adicional, o usa `profundidad=basico` (gratis ilimitado)." |
| URL competitor blocca via robots.txt | `estado: "parcial"`, nota: "El competidor bloquea crawler. Análisis basado solo en datos públicos." Nessun crédito consumato. |
| SEMrush/Ahrefs API down | Se `profundidad=completo`: degrada automaticamente a `basico`, nessun crédito consumato, nota: "Datos premium temporalmente no disponibles, mostrando análisis básico." |
| URL competitor è proprio del utente (auto-analisi) | Tool rejecta: "Para auditar tu propio sitio, usa `diagnostico_seo_express`." |
| Stesso analisi ripetuto < 24h | Return cached, nessun crédito consumato di nuovo. |
| Budget mensile API esaurito (cap globale Segmenta) | Per `profundidad=completo`: degrada automaticamente a `basico` per tutti gli utenti, alert email a Claudio. |
| `pais_objetivo` non supportato da SEMrush/Ahrefs API | Errore strutturato, suggerisce paesi simili supportati. |

### 7.7 Esempio chiamata

**Input** (basico):
```json
{
  "email": "marketing@miempresa.com",
  "url_competidor": "https://competidor-grande.com",
  "pais_objetivo": "MX",
  "sector": "ecommerce",
  "profundidad_analisis": "basico"
}
```

**Output** (estratto):
```json
{
  "estado": "completado",
  "url_analizada": "https://competidor-grande.com",
  "pais_objetivo": "MX",
  "profundidad": "basico",
  "creditos_consumidos": 0,
  "creditos_restantes_mes": 3,
  "fortalezas_competidor": [
    "Schema markup completo (Product, Organization, BreadcrumbList)",
    "Velocidad de carga excelente (1.2s)",
    "Catálogo extenso (5,000+ productos)",
    "Reviews integradas en cada PDP"
  ],
  "debilidades_competidor": [
    "Sin llms.txt (no optimizado para LLMs)",
    "Solo 3 schemas en homepage, faltante FAQPage",
    "Contenido bilingüe inexistente (solo ES, mercado bilingüe US-hispanic perdido)",
    "Blog con baja frecuencia (<1 post/mes)"
  ],
  "oportunidades_para_ti": [
    {
      "categoria": "geo_aeo",
      "titulo": "Diferenciación AI-search",
      "descripcion": "El competidor no tiene llms.txt ni FAQ schema. Implementarlo te dará ventaja en Claude/ChatGPT/Perplexity citaciones.",
      "severidad_oportunidad": "alta",
      "como_aprovechar": "Crea llms.txt en root + FAQ schema en al menos 5 páginas principales. Time-to-impact: 2-4 semanas."
    },
    {
      "categoria": "contenido",
      "titulo": "Frecuencia de blog",
      "descripcion": "El competidor publica <1 post/mes. Subir a 4-8 posts/mes te posicionará en keywords long-tail que ellos no cubren.",
      "severidad_oportunidad": "alta",
      "como_aprovechar": "Establece editorial calendar de 6-8 posts/mes en el blog, focus en queries de intención comercial."
    }
    // ... 3-6 más
  ],
  "keywords_top_competidor": [],
  "estimacion_trafico_organico_mensual": null,
  "estimacion_inversion_paid_mensual_usd": null,
  "metricas_seo": {},
  "nota": "Análisis básico (gratis). Para datos profundos (keywords, tráfico estimado, paid budget), usa `profundidad=completo` (1 crédito de 3 mensuales)."
}
```

### 7.8 Test acceptance criteria

- ✅ `profundidad=basico` → analisi via crawl, 0 crediti consumati.
- ✅ `profundidad=completo` → analisi completa, 1 crédito consumato, response include keywords e stime.
- ✅ Crediti esauriti + `completo` → fallisce graceful con upgrade path.
- ✅ SEMrush API down + `completo` → degrada a `basico` automaticamente, no crédito consumato.
- ✅ Idempotency 24h funziona (no double charge).
- ✅ URL competitor proprio dell'utente → rejecta con suggerimento `diagnostico_seo_express`.
- ✅ Budget cap globale rispettato.
- ✅ Latency < 8s p95 con `completo`, < 5s con `basico`.

---

## 8. Tool 5: `share_research`

### 8.1 Scopo

Permette all'utente di **pubblicare un research aggregato anonimo** sul blog di Segmenta. Esempio: 50 utenti chiedono "quanto costa SEO per medico CDMX?" → noi scriviamo automaticamente un article "Costo SEO Medico CDMX 2026: datos reales de 50 consultas". È **content marketing meta**: i tool stessi generano contenuto.

### 8.2 Signature

```python
@mcp.tool
async def share_research(
    email: Annotated[str, Field(description="Email del usuario, verificado vía OAuth magic link.")],
    tema_research: Annotated[
        str,
        Field(min_length=20, max_length=200, description="Tema sobre el cual el usuario quiere compartir su pregunta y agregarla a research. Ej: 'Costos de SEO para clínicas dentales en CDMX'.")
    ],
    pregunta_especifica: Annotated[
        str,
        Field(min_length=30, max_length=500, description="Pregunta específica del usuario que se compartirá anonimizada.")
    ],
    consenso_anonimato: Annotated[
        bool,
        Field(description="El usuario consiente publicación anonimizada. Debe ser True para proceder.")
    ],
    consenso_aggregacion: Annotated[
        bool,
        Field(description="El usuario consiente que la pregunta sea aggregada con otras similares en research público. Debe ser True para proceder.")
    ],
    sector: Annotated[Sector, Field(description="Sector empresarial del usuario.")],
    pais: Annotated[Pais, Field(description="País del usuario.")],
) -> ResultadoShareResearch:
    """[ver tool description en sez 8.4]"""
```

### 8.3 Tipo di output

```python
class ResultadoShareResearch(BaseModel):
    estado: Literal["aceptado", "ya_existe_thread", "rechazado_consenso"]
    research_id: str | None              # ID del thread di research
    tema_research_humanizado: str
    notificacion_publicacion: str        # "Te notificaremos por email cuando se publique el research."
    estimacion_publicacion: str          # "Cuando alcancemos 30 contribuciones similares, ~1-3 meses."
    contribuciones_actuales: int
    contribuciones_para_publicar: int    # threshold tipico 30
    nota: str
```

### 8.4 Tool description

> **Permite al usuario contribuir su pregunta de marketing a un research aggregado anónimo de Segmenta. Cuando alcanzamos 30+ contribuciones similares sobre un tema, publicamos research público con datos reales (ej: "Costos SEO para clínicas dentales CDMX: 47 consultas analizadas Q1-Q2 2026"). Es content marketing meta: los usuarios contribuyen anónimamente y reciben el research final por email.**
>
> **Cuándo usar:**
> - El usuario expresa interés en research público de Segmenta
> - Después de tools Tier 1 (preguntas exploratorias) cuando el usuario quiere amplificar la conversación
> - Como gesto de reciprocidad: usuario obtiene valor (research futuro) por contribuir su pregunta
>
> Requisitos: email verificado, tema, pregunta específica, consensos anonimato + aggregación. Sector y país del usuario.

(486 caratteri.)

### 8.5 Comportamento

1. Validazione consensi: se `consenso_anonimato=False` o `consenso_aggregacion=False` → `estado: "rechazado_consenso"`, nessun salvataggio.
2. Identifica thread research esistente:
   - Embedding del `tema_research` (in v1: simple keyword matching; v2: vector search).
   - Match con thread esistenti in `data/research_threads.json` (vedi sez. 8.6).
   - Se match > 0.7 similarity → aggrega lì.
   - Se no match → crea nuovo thread.
3. Salva contribuzione in Redis con TTL 6 mesi:
   - Key: `research:contributions:{thread_id}:{ulid}`
   - Value: `{pregunta_especifica, sector, pais, timestamp, email_hash}` (no email plaintext).
4. Update counter contribuzioni del thread.
5. Se counter ≥ threshold (default 30):
   - Trigger automatico per content team Segmenta (Slack alert al team #content).
   - Romina (Content Manager) decide priorità publishing.
6. Risponde all'utente con conferma.
7. Email automatica appena il research viene pubblicato (subscribe automatico).

### 8.6 Dataset research_threads

`data/research_threads.json`:

```json
{
  "_meta": {
    "schema_version": "1.0.0",
    "data_version": "1.0.0",
    "ultima_actualizacion": "2026-05-10",
    "threshold_publicacion": 30,
    "nota": "Threads de research generados desde MCP tool share_research."
  },
  "threads": [
    {
      "id": "rt_costos_seo_clinicas_cdmx",
      "tema_humanizado": "Costos de SEO para clínicas en CDMX",
      "keywords_clave": ["seo", "clinica", "cdmx", "medico", "costos", "precio"],
      "sectores_relacionados": ["medico"],
      "paises_relacionados": ["MX"],
      "estado": "abierto",     // "abierto" | "en_redaccion" | "publicado"
      "fecha_creacion": "2026-04-01",
      "url_publicacion": null,
      "contribuciones_totales": 12
    }
    // ... otros threads
  ]
}
```

In v1 il file è gestito manualmente da Romina (con assistenza Claudio). In v2 si valuta auto-generation di thread sulla base di clustering automatico delle contribuzioni.

### 8.7 Edge case

| Caso | Comportamento |
|---|---|
| `consenso_anonimato=False` | `estado: "rechazado_consenso"`, nota: "Se requiere consenso de anonimato para participar." Nessun side effect. |
| `consenso_aggregacion=False` | Idem. |
| Thread match ambiguo (più match con score simile) | Default a thread più recente, nota: "Tu pregunta se agregó al thread más similar. Si no coincide, escríbenos." |
| Stesso `(email, tema)` già contribuito | Idempotency: ignora silently, response stesso research_id, contribuciones_actuales invariato. |
| Threshold raggiunto durante questa chiamata | Risponde normalmente + alert interno Slack. Utente non riceve notifica speciale (per non creare aspettative). |
| Sistema di embedding/match non disponibile (v2) | Fallback a keyword matching exact su sector + país + parole chiave. |
| Thread `estado=publicado` viene contribuito di nuovo | Aggregato in nuovo thread "v2" (es. "Costos SEO clínicas CDMX 2027"). Automaticamente per period rolling annuale. |

### 8.8 Esempio chiamata

**Input**:
```json
{
  "email": "doctor@clinica.mx",
  "tema_research": "Costos de SEO para clínicas dentales en CDMX",
  "pregunta_especifica": "¿Cuánto cuesta hacer SEO para una clínica dental con 2 sucursales en CDMX, mercado boutique medium-high?",
  "consenso_anonimato": true,
  "consenso_aggregacion": true,
  "sector": "medico",
  "pais": "MX"
}
```

**Output**:
```json
{
  "estado": "aceptado",
  "research_id": "rt_costos_seo_clinicas_cdmx",
  "tema_research_humanizado": "Costos de SEO para clínicas dentales en CDMX",
  "notificacion_publicacion": "Te notificaremos por email cuando se publique el research. Estimación 1-3 meses.",
  "estimacion_publicacion": "Cuando alcancemos 30 contribuciones (actualmente 13), aproximadamente 1-3 meses.",
  "contribuciones_actuales": 13,
  "contribuciones_para_publicar": 30,
  "nota": "Tu pregunta se aggregó anónimamente al thread '{tema}'. Recibirás email cuando publiquemos el research público con datos reales y benchmarks. Mientras tanto, para respuesta inmediata sobre tu caso, usa `solicitar_propuesta_personalizada`."
}
```

### 8.9 Test acceptance criteria

- ✅ Consensi `true` → contribuzione salvata, response `aceptado`.
- ✅ Consensi `false` → `rechazado_consenso`, nessun salvataggio.
- ✅ Match thread esistente → aggrega correttamente.
- ✅ No match → crea nuovo thread.
- ✅ Idempotency su `(email, tema)`.
- ✅ Threshold raggiunto → Slack alert interno.
- ✅ Email del utente memorizzato come hash, mai plaintext nei dati di research.
- ✅ Latency < 1s p95.

---

## 9. Decisioni canoniche Tier 3 (locked)

| ID | Decisione | Motivazione |
|---|---|---|
| **D-T3-001** | 5 tool fissi in v1: obtener_caso_por_pais, whatsapp_directo, compare_agencies, analizar_competencia, share_research | Coverage retention + intelligence + posizionamento. |
| **D-T3-002** | Mix di gating: 3 tool no auth (obtener_caso, whatsapp, compare), 2 tool auth (analizar, share) | Audience qualificata, costi controllati, valore strategico variabile. |
| **D-T3-003** | Cost cap mensile 20 USD per Tier 3 v1 (50 USD in v2) | Disciplina di costo, evita esplosioni di chiamate API esterne. |
| **D-T3-004** | Soft credit system per `analizar_competencia`: 3 análisis completos gratis/mes, poi escalation manuale | Bilancia accessibility e cost control. |
| **D-T3-005** | Cache aggressiva 24h per `analizar_competencia`, 1h per altri Tier 3 read-only | Riduce ripetuti, predictable cost. |
| **D-T3-006** | Dataset competitors curato manualmente, solo info pubbliche, linguaggio rispettoso | Trust segnale di onestà. |
| **D-T3-007** | `compare_agencies` SEMPRE include `cuando_segmenta_no_es_la_mejor` | Onestà obbligatoria, segnale anti-marketing patinato. |
| **D-T3-008** | `share_research` threshold default 30 contribuzioni per publish | Volume sufficiente per contenuto credibile, raggiungibile in 2-3 mesi per tema popolare. |
| **D-T3-009** | `share_research`: email utente memorizzato come hash, mai plaintext | Privacy by design, anonimato vero. |
| **D-T3-010** | `whatsapp_directo`: nessun lead capture automatico, solo log evento | Conservativo: l'utente potrebbe non cliccare il link, evitare false positive in CRM. |
| **D-T3-011** | `whatsapp_directo` template: include footer "Vengo desde el chat AI con su MCP server" | Attribution per il team Segmenta, segnale di canale per analytics. |
| **D-T3-012** | `analizar_competencia`: degrade automatico da `completo` a `basico` se SEMrush down | Resilience: non bloccare l'utente per dipendenze esterne. |
| **D-T3-013** | `obtener_caso_por_pais` granularità subregion: enum `MercadoSubregional` per US-hispanic e MX | Allinea con D-MP-016 (mercati primari) e differenzia Florida vs Texas vs CDMX vs Monterrey. |
| **D-T3-014** | Tier 3 logging tag `tier: "3"` propagato per analytics segmentate | Permette dashboard separata per retention vs acquisizione. |
| **D-T3-015** | Test coverage Tier 3 ≥ 80% (vs 85% Tier 2, 90% Tier 1) | Tier 3 ha più integrazioni esterne mockate; soglia leggermente più bassa accettabile. |
| **D-T3-016** | `compare_agencies` requires `data/competitors_dataset.json` curato trimestralmente | Manutenzione attiva, evita dati desfasati. |
| **D-T3-017** | `share_research`: l'utente riceve email automatica di unsubscribe quando publica research | Trust, coerente con LFPDPPP/GDPR. |
| **D-T3-018** | Niente sharing dei dati di `analizar_competencia` aggregati nei research (solo le query share_research esplicite) | Linea netta tra intelligence privata e content pubblico. |
| **D-T3-019** | `whatsapp_directo` mapping numeri statico in v1 (DECISION-OPEN-T3-001 da chiudere con Merari) | Setup veloce; rotation/load balancing valutati v2. |
| **D-T3-020** | `obtener_caso_por_pais` ordinamento: similitud_geografica desc, poi fecha desc | Casos più rilevanti geograficamente prima, poi più recenti. |

---

## 10. Decisioni aperte Tier 3

| ID | Decisione | Bloccare entro | Owner |
|---|---|---|---|
| **DECISION-OPEN-T3-001** | Numeri WhatsApp Business per país: 1 centralizzato MX o multi-país? | M3 | Merari |
| **DECISION-OPEN-T3-002** | Provider per `analizar_competencia`: SEMrush API ($) vs Ahrefs API ($) vs DataForSEO ($) vs in-house crawler-only | M4 | Claudio |
| **DECISION-OPEN-T3-003** | Threshold `share_research` publish: 30 default, ma per temi caldi (es. GEO/AEO) abbassare a 20? | M4 | Romina |
| **DECISION-OPEN-T3-004** | `share_research`: pubblicazione automatizzata (Claude Code genera draft) o sempre review manuale Romina? | M4 | Merari + Romina |
| **DECISION-OPEN-T3-005** | `compare_agencies`: aggiungere campo "url_competidor_para_referencia" (link al loro sito)? Rischio: traffic loss verso competitor. | M3 | Merari |
| **DECISION-OPEN-T3-006** | `analizar_competencia`: piano premium (es. 10 análisis completi/mese a 50 USD) per utenti high-intent? | v2 | Merari |
| **DECISION-OPEN-T3-007** | `obtener_caso_por_pais`: quando aggiungere subregion brasiliana? (post non-goal v1, ma se aprite BR in 2027) | v2 | Merari |
| **DECISION-OPEN-T3-008** | Rate limit specifico per `analizar_competencia` (oltre i crediti): es. max 1/giorno per evitare abuse? | M4 | Claudio |
| **DECISION-OPEN-T3-009** | Tool aggiuntivo `pregunta_a_merari` (escalation diretta CEO via email)? Privilegio segno di brand. | v2 | Merari |
| **DECISION-OPEN-T3-010** | `share_research` threshold reset annuale per stesso tema (rolling vs cumulativo)? | M4 | Romina |

---

## 11. Versioning di questo documento

| Versione | Data | Autore | Note |
|---|---|---|---|
| 1.0 | 2026-05-10 | Claude (proposta) + Claudio (revisione) | Prima stesura completa. 5 tool Tier 3 con spec, signature, schema output, gating diferenciato (auth + cost), dataset competitors curato. |
| 1.1 | 2026-05-11 | Claude (harmony pass M0.3) + Claudio (review) | **HC-005**: `obtener_caso_por_pais.pais_o_subregion` tipizzato a `Pais \| PaisExtendido \| MercadoSubregional` (era `str`). Edge case table aggiornata di conseguenza. **HC-006 cross-ref**: sez. 6.6 ora rimanda a `03-DATA-MODEL.md` sez. 7bis come schema canonico per `competitors_dataset.json`. |

---

## Note per il changelog

Harmony pass M0.3 (2026-05-11): 2 fix di tipizzazione e cross-reference applicati. Le 20 decisioni canoniche D-T3-001 → D-T3-020 restano locked.

---

**Fine 06-TOOLS-TIER3.md v1.0.**
