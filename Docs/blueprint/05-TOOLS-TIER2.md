# 05 — TOOLS TIER 2 (con captura de lead)

| Campo | Valore |
|---|---|
| **Progetto** | Segmenta MCP Server |
| **Versione documento** | 1.0 |
| **Data** | 2026-05-10 |
| **Status** | Draft (in revisione) |
| **File n.** | 05 di 12 numerati |
| **Documento padre** | `00-MASTER-PLAN.md` v1.3, `01-ARCHITECTURE.md` v1.2, `03-DATA-MODEL.md` v1.1, `04-TOOLS-TIER1.md` v1.0 |
| **File correlati** | `06-TOOLS-TIER3.md`, `07-AUTH-OAUTH.md`, `08-INTEGRATIONS.md`, `11-ANALYTICS.md` |

---

## 1. Scopo del documento

Questo file specifica **i 5 tool MCP del Tier 2 (con captura de lead)**: tool che richiedono **identificazione minima** dell'utente (email verificata via magic link OAuth) e che generano **conversione commerciale** in cambio di valore concreto.

Per ogni tool:
- Cosa fa, perché esiste, quando l'LLM lo deve chiamare
- Signature Python completa
- Tool description in spagnolo (LATAM-neutral)
- Schema input/output
- **Lead capture flow** dettagliato (ciò che distingue Tier 2 da Tier 1)
- Integrazioni esterne richieste con error handling
- Edge case e fallback
- Test acceptance criteria

I tool Tier 1 (público) sono in `04-TOOLS-TIER1.md`. I tool Tier 3 (avanzados) sono in `06-TOOLS-TIER3.md`. **L'OAuth flow** e la **gestione magic link** sono dettagliati in `07-AUTH-OAUTH.md`. **I contratti API** delle integrazioni esterne sono in `08-INTEGRATIONS.md`.

---

## 2. Filosofia del Tier 2

I tool Tier 2 sono **il punto di conversione** del funnel. Devono soddisfare cinque criteri che li distinguono dal Tier 1:

### 2.1 Reciprocità prima della richiesta

L'utente fornisce email **solo dopo** aver ricevuto valore al Tier 1 (servizi, casi, benchmark, glosario). Non chiediamo email "fredda". Quando l'LLM chiama un tool Tier 2, l'utente è già in un flusso di scoperta — la richiesta di identificazione è naturale, non intrusiva.

### 2.2 Valore tangibile in cambio dell'email

Ogni tool Tier 2 deve **consegnare** qualcosa di sostanziale entro 60 secondi dalla verifica email:
- `diagnostico_seo_express`: report con 5-10 quick win specifici al sito dell'utente
- `calcular_presupuesto`: range di prezzo strutturato per il caso specifico
- `agendar_auditoria_gratuita`: conferma slot + link videocall
- `solicitar_propuesta_personalizada`: ricevuta + SLA "ti contatteremo entro 24h"
- `consultar_disponibilidad`: lista slot disponibili formattata

Se non possiamo consegnare valore, **non chiediamo email**.

### 2.3 Idempotency e safety

Le chiamate Tier 2 hanno side effect (creano lead nel CRM, prenotano slot, inviano email). Sono **idempotenti** via Redis idempotency key (vedi `01-ARCHITECTURE.md` sez. 10.5). Cliccare "agendar" 3 volte non crea 3 prenotazioni. Re-invocare lo stesso tool con lo stesso `(user_email, args)` restituisce lo stesso risultato della prima chiamata.

### 2.4 Fail-safe: mai perdere un lead

Se un'integrazione esterna fallisce (CRM down, Cal.com timeout), il tool **non perde l'informazione**. Pattern di fallback strutturato (vedi `01-ARCHITECTURE.md` sez. 10.4): salva in Redis fallback queue, invia email a `alerts@segmentamarketing.com`, risponde all'utente con messaggio onesto. Vedi sez. 9.

### 2.5 Latency budget più rilassato

Tier 1 < 50ms. Tier 2 < 800ms p95 perché include 1-2 chiamate API esterne (booking, CRM, email). Acceptable: l'utente ha appena verificato un magic link, è già in attesa di feedback.

---

## 3. Tabella riassuntiva dei 5 tool

| Tool | Cosa fa | Lead capture quality | Integrazione esterna | Latency target |
|---|---|---|---|---|
| `diagnostico_seo_express` | Audit SEO veloce di un sito + report email | Media-Alta (URL+email = qualified prospect) | Resend (email) + crawler interno | < 5s con crawl |
| `calcular_presupuesto` | Preventivo orientativo strutturato | Media (input strutturati = serio) | CRM webhook | < 800ms |
| `agendar_auditoria_gratuita` | Prenotazione slot videocall | **Alta** (commitment di tempo) | Booking + CRM webhook | < 1s |
| `solicitar_propuesta_personalizada` | Brief lungo per propuesta custom | **Massima** (intento d'acquisto) | CRM webhook + Slack alert | < 800ms |
| `consultar_disponibilidad` | Slot disponibili (read-only) | Bassa (esplorativa) | Booking platform read API | < 500ms |

**KPI aggregato Tier 2**: ≥ 5 lead qualificati/mese da MCP entro M2 (soglia `00-MASTER-PLAN.md` sez. 8.2).

---

## 4. Tool 1: `diagnostico_seo_express`

### 4.1 Scopo

Esegue un audit SEO veloce di un sito web fornito dall'utente, restituendo 5-10 quick win specifici e accionabili. Spedisce poi un report più dettagliato via email. È il **lead magnet principale**: trasforma una conversazione informativa in lead qualificato perché l'utente ha già condiviso (a) il proprio sito e (b) la propria email.

### 4.2 Signature

```python
@mcp.tool
async def diagnostico_seo_express(
    url: Annotated[
        str,
        Field(description="URL completa del sitio a auditar. Debe incluir https://. Ej: 'https://miempresa.com'.")
    ],
    email: Annotated[
        str,
        Field(description="Email del usuario para enviar el reporte detallado. Validada por OAuth magic link.")
    ],
    sector: Annotated[
        Sector | None,
        Field(description="Sector empresarial del sitio (opcional). Mejora la calidad de los quick wins. Si None, intenta detectar automáticamente.")
    ] = None,
    pais_objetivo: Annotated[
        Pais | None,
        Field(description="País objetivo de mercado para SEO (opcional). Si None, infiere desde idioma del sitio o IP.")
    ] = None,
) -> ResultadoDiagnostico:
    """[ver tool description en sez 4.4]"""
```

### 4.3 Tipo di output

```python
class QuickWin(BaseModel):
    """Singola raccomandazione actionable."""
    prioridad: Literal["critica", "alta", "media", "baja"]
    categoria: Literal["tecnico", "contenido", "on_page", "off_page", "ux", "geo_aeo"]
    titulo: str            # "Falta meta description en homepage"
    descripcion: str       # "La página principal no tiene meta description, lo que..."
    impacto_estimado: str  # "Mejora CTR esperado +15-25% en SERP"
    esfuerzo: Literal["bajo", "medio", "alto"]
    como_arreglar: str     # "En tu CMS, edita la página principal y agrega..."


class ResultadoDiagnostico(BaseModel):
    url_analizada: str
    timestamp: str
    score_global_0_100: int
    estado: Literal["completado", "parcial", "fallido"]
    quick_wins: list[QuickWin]
    metricas_clave: dict   # {trafico_estimado, palabras_indexadas, mobile_friendly, ...}
    reporte_completo_enviado_a: str
    reporte_completo_eta: str    # "El reporte detallado llegará a tu email en 5-10 minutos."
    proximos_pasos: list[str]
    nota: str
```

### 4.4 Tool description

> **Realiza un diagnóstico SEO express del sitio web del usuario y envía un reporte detallado por email. Identifica 5-10 oportunidades concretas (quick wins) priorizadas por impacto y esfuerzo: problemas técnicos, contenido, on-page, off-page, UX, y optimización GEO/AEO para Claude/ChatGPT. Compatible con sitios LATAM, México, US (anglo + hispanic), España.**
>
> **Cuándo usar:**
> - El usuario pregunta "¿qué problemas tiene mi sitio?" o pide análisis SEO
> - El usuario menciona su URL y quiere recomendaciones concretas
> - El usuario evalúa si necesita una agencia y quiere primera prueba de valor
> - El usuario quiere entender oportunidades de optimización antes de contratar
>
> **Requisitos:** URL completa con https://, email válido (verificado vía magic link OAuth). Opcionalmente `sector` y `pais_objetivo` para personalizar quick wins.
>
> El análisis express tarda 30-60 segundos. El reporte completo llega por email en 5-10 minutos.

(491 caratteri — sopra le 400 di norma; questo tool è critical e merita la descrizione lunga.)

### 4.5 Lead capture flow

```
0. LLM riceve dal utente: "audita mi sitio https://example.com"
1. LLM chiama diagnostico_seo_express(url, email=null) → server risponde 401
2. OAuth flow inizia (vedi 07-AUTH-OAUTH.md):
   - Server invia magic link a email che l'utente specifica nel client MCP
   - Utente clicca link → sessione creata
   - Token OAuth ritorna al client MCP
3. LLM retry diagnostico_seo_express(url, email) con Authorization: Bearer
4. Server:
   a. Valida URL: schema https://, domini ammessi, no IP privati
   b. Idempotency check: hash(email, url, day) → se già fatto < 24h → return cached
   c. Crawl sito (max 30s timeout): home + /robots.txt + sitemap.xml + 3 internal pages
   d. Analisi: technical (loading time, mobile, schema), on-page (title, meta, H1), GEO (llms.txt, FAQ schema)
   e. Genera 5-10 quick wins
   f. Salva report completo (più lungo) in Redis con TTL 24h
   g. Pubblica job async: invia email con link al report completo
   h. Crea lead in CRM con tag "mcp_diagnostico_seo"
5. Return immediato: ResultadoDiagnostico con quick wins inline + ETA email
6. Background: email arriva 5-10 minuti dopo con report HTML completo
```

### 4.6 Comportamento (dettaglio implementativo)

1. **Validazione URL**:
   - Schema deve essere `https://` (no `http://` per evitare warning sicurezza nel report).
   - Hostname risolto, no IP privati (RFC 1918), no `localhost`, no `*.internal`.
   - Lunghezza max 500 caratteri.
   - Robots.txt rispettato: se `User-agent: SegmentaMCPBot Disallow: /` → tool ritorna `estado: "fallido"` con nota: "El sitio bloquea nuestro crawler vía robots.txt. No podemos auditarlo."

2. **Crawl**:
   - HTTP client: `httpx` async con timeout 5s connect, 10s total per request.
   - User agent: `SegmentaMCPBot/1.0 (+https://segmentamarketing.com/mcp/bot)`.
   - Rispetta `robots.txt` strettamente.
   - Pagine analizzate: home + 3 pagine interne (link più visibili da home).
   - Limit complessivo: 30 secondi totale crawl, dopo abort → `estado: "parcial"` con quick wins basati su quanto raccolto.

3. **Analisi**:
   - **Tecnico**: status code, response time, Mobile-Friendly Test (lighthouse-style heuristics), HTTPS valid, redirect chains, broken images.
   - **On-page**: title tag (lunghezza, keyword), meta description (presente, lunghezza), H1 (presente, unico), heading hierarchy.
   - **Schema markup**: JSON-LD presente, tipi rilevanti per il sector, errori comuni.
   - **GEO/AEO**: presence of `/llms.txt`, FAQ schema, schema FAQPage/HowTo, structured author info (E-E-A-T signals).
   - **Off-page** (limitato): backlink count tramite API esterna se disponibile (DataForSEO o equiv.); altrimenti skip.
   - **UX**: viewport meta, image alt attributes random sample, skip-to-content link, lang attribute.

4. **Generazione quick wins**:
   - Algoritmo deterministico basato su check eseguiti.
   - Priorità: critica (impedisce indicizzazione), alta (impatto > 20% atteso), media, baja.
   - Ogni quick win ha `como_arreglar` con istruzione concreta in spagnolo.

5. **Score globale 0-100**: media ponderata dei check, weights pre-tarati.

6. **Async send report dettagliato**:
   - Background task `asyncio.create_task` (no Celery in v1).
   - Render template HTML con dati del crawl + quick wins espansi + diagrammi semplici (testo, no immagini complesse).
   - Email via Resend con sender `auditorias@segmentamarketing.com`.
   - Report HTML include: link a `agendar_auditoria_gratuita` nella stessa conversazione, e link a sito Segmenta.

7. **CRM lead creation**:
   - Webhook async con `tag: "mcp_diagnostico_seo"`, custom fields URL + sector + score globale.
   - Failed webhook → fallback Redis queue (vedi sez. 9).

### 4.7 Edge case

| Caso | Comportamento |
|---|---|
| URL non risolve (DNS error) | `estado: "fallido"`, nota: "No pudimos acceder al sitio. Verifica que la URL es correcta y accesible públicamente." Nessun lead creato. |
| URL torna 4xx/5xx | `estado: "parcial"` con 1 quick win critico: "El sitio retorna error HTTP {code}. Esto impide indexación y conversión." Lead creato. |
| Sito vuoto (HTML < 1KB) | `estado: "parcial"`, nota: "El sitio parece estar en mantenimiento o sin contenido. Re-intenta más tarde." |
| Sito blocca via robots.txt | `estado: "fallido"`, nota chiara, lead creato (utente mostra interesse). |
| Sito enorme (homepage > 5MB) | Process solo i primi 5MB, nota: "Sitio muy pesado, análisis sobre primeros 5MB de homepage." |
| Sito lento (> 10s response) | Quick win critico: "Velocidad de carga inaceptable ({tempo}s). Causa principal de bounce rate alto." |
| Email Resend send fallisce | Report salvato in Redis 24h, alert email a Claudio, response al utente: "Tu reporte completo se está procesando. Si no lo recibes en 30 min, escríbenos a hola@..." |
| CRM webhook fallisce | Lead salvato in Redis fallback queue, alert email, response utente OK comunque. |
| `sector` errato (fornito ma non corrisponde al sito) | Quick wins generici applicati. Nota: "Análisis sin contexto de sector. Para mejor calidad, especifica `sector`." |
| Stesso `(email, url, day)` già processato | Return cached da Redis, nota: "Diagnóstico repetido en menos de 24h, mostrando análisis previo." |
| `pais_objetivo` non specificato e impossibile da inferire | Default `LATAM`, nota in `metricas_clave`: "País objetivo no especificado, asumido LATAM." |
| Tool chiamato senza email (token OAuth scaduto) | 401 Unauthorized, ri-trigger OAuth flow nel client MCP. |

### 4.8 Esempio chiamata

**Input**:
```json
{
  "url": "https://miclinica-cdmx.example.com",
  "email": "doctor@miclinica.com",
  "sector": "medico",
  "pais_objetivo": "MX"
}
```

**Output (immediato)**:
```json
{
  "url_analizada": "https://miclinica-cdmx.example.com",
  "timestamp": "2026-05-10T15:42:18Z",
  "score_global_0_100": 47,
  "estado": "completado",
  "quick_wins": [
    {
      "prioridad": "critica",
      "categoria": "tecnico",
      "titulo": "Falta certificado HTTPS válido",
      "descripcion": "El sitio responde con HTTP en lugar de HTTPS, lo que penaliza el ranking en Google y genera advertencias de seguridad en navegadores.",
      "impacto_estimado": "Penalización de ranking medible. Tasa de rebote +30-50%.",
      "esfuerzo": "bajo",
      "como_arreglar": "Activa SSL gratis vía Let's Encrypt en tu hosting. La mayoría de hostings (Hostinger, GoDaddy, AWS) lo ofrecen en 1 click."
    },
    {
      "prioridad": "alta",
      "categoria": "geo_aeo",
      "titulo": "Sin schema MedicalEntity",
      "descripcion": "Las páginas de servicios médicos no incluyen schema JSON-LD tipo MedicalEntity ni Physician. Esto reduce visibilidad en AI Overviews y Google for Healthcare.",
      "impacto_estimado": "Visibilidad +20-40% en queries de salud en Google AI Overviews.",
      "esfuerzo": "medio",
      "como_arreglar": "Agrega schema JSON-LD con Physician + MedicalProcedure en cada página de tratamiento. Plugins como Rank Math (WordPress) lo facilitan."
    },
    {
      "prioridad": "alta",
      "categoria": "on_page",
      "titulo": "Meta descriptions ausentes en 8 páginas",
      "descripcion": "8 de las 10 páginas analizadas no tienen meta description. Google genera una automáticamente, perdiendo control sobre el snippet en SERP.",
      "impacto_estimado": "CTR en SERP +15-25%.",
      "esfuerzo": "bajo",
      "como_arreglar": "Edita cada página y agrega meta description de 120-155 caracteres con palabra clave + llamada a acción."
    }
    // ... 4-7 más
  ],
  "metricas_clave": {
    "tiempo_carga_homepage_s": 3.4,
    "mobile_friendly": true,
    "https": false,
    "robots_txt_present": true,
    "sitemap_xml_present": false,
    "llms_txt_present": false,
    "schema_jsonld_count": 1
  },
  "reporte_completo_enviado_a": "doctor@miclinica.com",
  "reporte_completo_eta": "El reporte detallado con todos los hallazgos llegará a tu email en 5-10 minutos.",
  "proximos_pasos": [
    "Revisa el reporte completo en tu email",
    "Si quieres ayuda implementando, agenda una auditoría gratuita con Segmenta usando agendar_auditoria_gratuita",
    "Para presupuesto orientativo, usa calcular_presupuesto"
  ],
  "nota": "Análisis automatizado. Para análisis humano profundo (200+ puntos, contenido, competencia), agenda auditoría con el equipo Segmenta."
}
```

### 4.9 Test acceptance criteria

- ✅ URL valida + email valida → analisi completa, lead creato in CRM, email inviata.
- ✅ URL invalida (no https://, IP privato, malformata) → Pydantic rejecta o early return con `estado: "fallido"`.
- ✅ Stesso `(email, url)` chiamato 2 volte in 24h → seconda chiamata return cached.
- ✅ Crawl timeout > 30s → `estado: "parcial"` con quick wins parziali.
- ✅ CRM webhook fallisce → response utente OK, alert a Claudio.
- ✅ Email Resend fallisce → report salvato in Redis, alert, response utente sì-onesta.
- ✅ Sito blocca robots.txt → `estado: "fallido"`, nota chiara, lead comunque creato.
- ✅ `sector` opzionale: assenza non blocca.
- ✅ Quick wins ordinati per priorità (critica → baja).
- ✅ Almeno 1 quick win categoria `geo_aeo` (allinea con strategia GEO).
- ✅ Latency response immediato < 5s p95 con sito di velocità normale.

---

## 5. Tool 2: `calcular_presupuesto`

### 5.1 Scopo

Restituisce un range di prezzo strutturato basato su input dell'utente (servizio desiderato, sector, país, tamaño empresa, scope). Non sostituisce la propuesta personalizada — è un *orientativo* che evita conversazioni iniziali su "quanto costa".

### 5.2 Signature

```python
@mcp.tool
async def calcular_presupuesto(
    email: Annotated[
        str,
        Field(description="Email del usuario, verificado vía OAuth magic link.")
    ],
    servicios_interes: Annotated[
        list[str],
        Field(min_length=1, max_length=5, description="Lista de IDs de servicios de interés (ej: ['seo-latam', 'google-ads-latam']). Para listar disponibles, usa obtener_servicios.")
    ],
    sector: Annotated[
        Sector,
        Field(description="Sector empresarial del usuario.")
    ],
    pais: Annotated[
        Pais,
        Field(description="País principal de operación.")
    ],
    tamano_empresa: Annotated[
        TamanoEmpresa,
        Field(description="Tamaño de la empresa: pyme, mediana, grande, corporativo.")
    ],
    presupuesto_mensual_max_usd: Annotated[
        int | None,
        Field(ge=0, le=100000, description="Presupuesto máximo mensual en USD que el usuario está dispuesto a invertir. Opcional pero ayuda a calibrar.")
    ] = None,
    objetivo_principal: Annotated[
        ObjetivoNegocio | None,
        Field(description="Objetivo principal del negocio: leads, ventas, branding, retencion, internacionalizacion.")
    ] = None,
    nombre_empresa: Annotated[
        str | None,
        Field(max_length=100, description="Nombre de la empresa del usuario (opcional, mejora calidad de seguimiento).")
    ] = None,
) -> ResultadoPresupuesto:
    """[ver tool description en sez 5.4]"""
```

`ObjetivoNegocio`:
```python
class ObjetivoNegocio(StrEnum):
    LEADS = "leads"
    VENTAS = "ventas"
    BRANDING = "branding"
    RETENCION = "retencion"
    INTERNACIONALIZACION = "internacionalizacion"
```

### 5.3 Tipo di output

```python
class ServicioPresupuesto(BaseModel):
    servicio_id: str
    nombre: str
    rango_mensual_usd: str        # "$1,200 – $3,500 USD/mes"
    rango_mensual_mxn: str
    rango_proyecto_unico_usd: str | None
    duracion_recomendada_meses: int
    prioridad_para_objetivo: int   # 1-3, dove 1 = top priority


class ResultadoPresupuesto(BaseModel):
    paquete_recomendado: str       # nome breve dell'overall package
    rango_total_mensual_usd: str   # "$3,000 – $7,500 USD/mes"
    rango_total_mensual_mxn: str
    duracion_minima_meses: int
    inversion_total_minima_usd: str  # mensual * minima
    servicios_incluidos: list[ServicioPresupuesto]
    ajustes_recomendados: list[str]  # se budget max < range, suggerimenti
    proximos_pasos: list[str]
    valido_hasta: str               # "Este presupuesto es válido por 30 días."
    nota: str
```

### 5.4 Tool description

> **Calcula un presupuesto orientativo personalizado para servicios de marketing digital de Segmenta, basado en servicios de interés, sector empresarial, país, tamaño de empresa y objetivo principal. Devuelve rango total mensual en USD/MXN, duración mínima recomendada, inversión total mínima, y desglose por servicio. Incluye ajustes recomendados si el presupuesto del usuario es ajustado.**
>
> **Cuándo usar:**
> - El usuario pregunta "¿cuánto me costaría hacer SEO + Google Ads para mi e-commerce?"
> - El usuario quiere un orientativo antes de pedir propuesta formal
> - El usuario compara opciones de inversión entre servicios diferentes
> - Como paso previo a `agendar_auditoria_gratuita` o `solicitar_propuesta_personalizada`
>
> Requisitos: email verificado, lista de servicios (usa `obtener_servicios` antes), sector, país, tamaño empresa. Opcionalmente: presupuesto máximo, objetivo, nombre empresa.

(440 caratteri.)

### 5.5 Lead capture flow

```
1. LLM chiama calcular_presupuesto sin auth → 401 → OAuth flow → token
2. LLM retry con auth + input completi
3. Server:
   a. Valida servicios_interes contro services.json (ogni id deve esistere)
   b. Per ogni servizio, recupera rango USD da services.json
   c. Applica modifier basati su:
      - tamano_empresa (pyme = base, grande = +30%, corporativo = +60%)
      - sector (alcuni settori più caro: legal +15%, fintech +20%)
      - pais (US +20% su LATAM, ES = LATAM, MX = LATAM)
   d. Calcola rango_total = sum dei rangi modificati
   e. Determina duracion_minima_meses = max delle durate dei servizi
   f. Se presupuesto_mensual_max_usd specificato e < rango_total.min:
      genera ajustes_recomendados (es. "Considera empezar solo con SEO en lugar de SEO + Google Ads")
   g. Salva presupuesto in Redis (TTL 30 giorni) con key {email}:{hash_args}
   h. Crea lead in CRM con tag "mcp_presupuesto", custom fields tutti gli input
4. Return ResultadoPresupuesto strutturato
```

### 5.6 Edge case

| Caso | Comportamento |
|---|---|
| `servicios_interes` con id inesistente | Errore strutturato: "El servicio 'X' no existe. Servicios disponibles: [...]" — invitare l'LLM a chiamare `obtener_servicios`. |
| Servizio non disponibile per `pais` | Warning in `nota`: "El servicio X no está disponible en {pais}. Excluido del cálculo. Servicios disponibles para {pais}: [...]" |
| `presupuesto_mensual_max_usd < rango_total.min` | `ajustes_recomendados` non vuoto con 2-4 alternative concrete (less servicios, durata maggiore, scope ridotto). |
| `tamano_empresa = "corporativo"` ma servizi solo pyme | Nota: "Para empresas corporate, recomendamos contacto directo con propuestas custom. Usa `solicitar_propuesta_personalizada`." |
| Lista `servicios_interes` solo con servizi mensili → nessun rango_proyecto | OK, campo `rango_proyecto_unico_usd: null`. |
| Mix di servizi mensili + proyecto único | Output include entrambi i ranghi (mensual per i ricorrenti, project per gli one-shot). |
| CRM webhook fallisce | Fallback Redis queue, response utente OK. |
| Stessa combinazione (email + servizi + altri arg) chiamata 2x in 30gg | Return cached, nota: "Presupuesto previo recuperado." |

### 5.7 Esempio chiamata

**Input**:
```json
{
  "email": "marta@miempresa.mx",
  "servicios_interes": ["seo-latam", "google-ads-latam"],
  "sector": "ecommerce",
  "pais": "MX",
  "tamano_empresa": "mediana",
  "presupuesto_mensual_max_usd": 5000,
  "objetivo_principal": "ventas",
  "nombre_empresa": "MiEmpresa S.A. de C.V."
}
```

**Output**:
```json
{
  "paquete_recomendado": "SEO LATAM + Google Ads para e-commerce mediana en México",
  "rango_total_mensual_usd": "$2,300 – $4,800 USD/mes",
  "rango_total_mensual_mxn": "$40,250 – $84,000 MXN/mes",
  "duracion_minima_meses": 6,
  "inversion_total_minima_usd": "$13,800 USD (6 meses al mínimo)",
  "servicios_incluidos": [
    {
      "servicio_id": "seo-latam",
      "nombre": "SEO LATAM",
      "rango_mensual_usd": "$1,000 – $2,800 USD/mes",
      "rango_mensual_mxn": "$17,500 – $49,000 MXN/mes",
      "rango_proyecto_unico_usd": null,
      "duracion_recomendada_meses": 6,
      "prioridad_para_objetivo": 2
    },
    {
      "servicio_id": "google-ads-latam",
      "nombre": "Gestión Google Ads LATAM",
      "rango_mensual_usd": "$1,300 – $2,000 USD/mes (mais presupuesto publicitario aparte de $1,500+ mensual)",
      "rango_mensual_mxn": "$22,750 – $35,000 MXN/mes",
      "rango_proyecto_unico_usd": null,
      "duracion_recomendada_meses": 3,
      "prioridad_para_objetivo": 1
    }
  ],
  "ajustes_recomendados": [
    "Tu presupuesto máximo ($5,000 USD) cubre el rango medio. Bien dimensionado.",
    "Para maximizar resultados rápidos, prioriza Google Ads en los primeros 3 meses.",
    "SEO empieza a entregar resultados consistentes desde el mes 4-5, prepara el flujo financiero."
  ],
  "proximos_pasos": [
    "Para presupuesto exacto y propuesta formal, usa `solicitar_propuesta_personalizada`",
    "Para hablar con el equipo, usa `agendar_auditoria_gratuita`",
    "Para ver casos similares en e-commerce México, usa `caso_de_estudio`"
  ],
  "valido_hasta": "Este presupuesto es válido por 30 días, hasta 2026-06-09.",
  "nota": "Rangos indicativos basados en sector ecommerce, país MX, empresa mediana. Precio final depende de scope, KPIs y complejidad del proyecto."
}
```

### 5.8 Test acceptance criteria

- ✅ Input validi → output con rango_total e desglose corretto.
- ✅ Servicio inesistente → errore strutturato con suggerimenti.
- ✅ Servicio non disponibile in `pais` → escluso con warning, calcolo continua sui restanti.
- ✅ `presupuesto_max < rango.min` → ajustes_recomendados non vuoto.
- ✅ Idempotency: stessa combinazione 30gg → return cached.
- ✅ Modifier `tamano_empresa` applicati correttamente (corporativo > grande > mediana > pyme).
- ✅ Modifier `pais` applicati (US +20%).
- ✅ Lead in CRM con tag corretto e custom fields popolati.
- ✅ Output sempre con `valido_hasta` calcolato correttamente.
- ✅ Latency < 800ms p95 (CRM webhook è il collo di bottiglia).

---

## 6. Tool 3: `agendar_auditoria_gratuita`

### 6.1 Scopo

Prenota uno slot di videocall gratuita con il team commerciale Segmenta. È il **tool conversion-critical** del Tier 2: l'utente che agenda è già nel funnel sales, costo per la generazione lead più alto ma intent altissimo.

### 6.2 Signature

```python
@mcp.tool
async def agendar_auditoria_gratuita(
    email: Annotated[
        str,
        Field(description="Email del usuario, verificado vía OAuth magic link.")
    ],
    nombre: Annotated[
        str,
        Field(min_length=2, max_length=100, description="Nombre y apellido del usuario para la videocall.")
    ],
    empresa: Annotated[
        str,
        Field(min_length=2, max_length=100, description="Nombre de la empresa del usuario.")
    ],
    url_sitio: Annotated[
        str | None,
        Field(description="URL del sitio web del usuario (opcional pero recomendado para preparar la call).")
    ] = None,
    sector: Annotated[
        Sector | None,
        Field(description="Sector empresarial. Mejora la asignación a especialista.")
    ] = None,
    pais: Annotated[
        Pais,
        Field(description="País del usuario para timezone-aware scheduling.")
    ] = Pais.MX,
    timezone: Annotated[
        str,
        Field(pattern=r"^[A-Z][a-z]+/[A-Z][a-z_]+$", description="Timezone IANA (ej: 'America/Mexico_City', 'America/New_York', 'Europe/Madrid'). Default basado en pais.")
    ] = "America/Mexico_City",
    slot_preferido_iso: Annotated[
        str | None,
        Field(pattern=r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}", description="Slot preferido en ISO 8601 (ej: '2026-05-15T14:00'). Si None, propone los 3 slots libres más cercanos.")
    ] = None,
    objetivo_call: Annotated[
        str,
        Field(min_length=20, max_length=500, description="Objetivo principal de la call. Ej: 'Quiero entender cómo mejorar mi SEO local en CDMX'.")
    ] = "Auditoría general de marketing digital",
    notas_adicionales: Annotated[
        str | None,
        Field(max_length=1000, description="Cualquier información adicional útil para preparar la call (presupuesto, urgencia, contexto).")
    ] = None,
) -> ResultadoAgendamento:
    """[ver tool description en sez 6.4]"""
```

### 6.3 Tipo di output

```python
class SlotDisponible(BaseModel):
    fecha_iso: str        # "2026-05-15T14:00:00"
    fecha_humanizada: str # "Jueves 15 de mayo, 14:00 (hora CDMX)"
    duracion_minutos: int
    asignado_a: str       # "Equipo Segmenta — especialista jurídico"


class ResultadoAgendamento(BaseModel):
    estado: Literal["confirmado", "slots_propuestos", "fallido"]
    slot_confirmado: SlotDisponible | None
    slots_propuestos: list[SlotDisponible]   # Solo se slot_preferido no disponible o no especificato
    booking_id: str | None
    videocall_link: str | None
    calendar_invite_enviado_a: str | None
    instrucciones_pre_call: list[str]
    notas: str
```

### 6.4 Tool description

> **Agenda una videocall gratuita de 30 minutos con el equipo Segmenta para auditoría personalizada de marketing digital. Timezone-aware: soporta MX, US (anglo + hispanic), LATAM (CO, AR, CL, PE, etc.) y España. La call incluye revisión de tu situación actual, identificación de oportunidades, y propuesta de servicios. Sin compromiso de compra, sin presión comercial.**
>
> **Cuándo usar:**
> - El usuario quiere hablar con un humano del equipo Segmenta
> - El usuario pide "agéndame", "podemos hablar", "quiero una reunión", "auditoría gratis"
> - Después de `diagnostico_seo_express` o `calcular_presupuesto`, como siguiente paso
> - El usuario expresa interés concreto en contratar pero quiere validar antes
>
> Requisitos: email verificado, nombre, empresa. Opcionales: url_sitio, sector, slot_preferido_iso, objetivo_call. Si no especificas slot, te propongo 3 slots disponibles cercanos en tu timezone.

(467 caratteri.)

### 6.5 Lead capture flow

```
1. LLM chiama agendar_auditoria_gratuita → OAuth flow se serve
2. Server:
   a. Valida input
   b. Idempotency check: hash(email, slot_preferido_iso) — se booking esiste già nello slot, return existing
   c. Se slot_preferido specificato:
      - Chiama Booking API: GET /availability?slot={slot}
      - Se libero: POST /bookings → confirma
      - Se occupato: GET /availability?around={slot}&n=3 → return 3 slots vicini
   d. Se slot_preferido NO specificato:
      - Chiama Booking API: GET /availability?from=now+24h&n=3 (next 3 slots, escludendo prossime 24h)
      - Return slots_propuestos (utente sceglie poi)
   e. Su confirma:
      - Crea evento calendar (booking platform genera videocall link)
      - Webhook al CRM con tag "mcp_call_agendada", priority "alta"
      - Slack alert al team #leads-mcp
      - Salva booking_id in Redis con TTL 90 giorni (per cancel future)
   f. Return ResultadoAgendamento
3. Email automatica dal booking platform al utente (calendar invite)
4. Email parallela dal CRM al sales rep assegnato con dettagli + url_sitio + sector
```

### 6.6 Edge case

| Caso | Comportamento |
|---|---|
| `slot_preferido_iso` nel passato | Pydantic permette parsing ma server rejecta: "El slot solicitado está en el pasado. Debe ser al menos 24h en el futuro." |
| `slot_preferido_iso` < 24h dal now | Rejecta: "Los agendamentos requieren al menos 24h de anticipación. Slots disponibles: [...]." |
| `slot_preferido_iso` occupato | `estado: "slots_propuestos"`, `slots_propuestos` con 3 alternative vicine al richiesto. |
| Nessuno slot disponibile next 14 days | `estado: "fallido"`, nota: "Calendario lleno en próximos 14 días. Escríbenos a hola@... para agenda extraordinaria." Lead creato con tag "mcp_call_no_slot". |
| Booking API timeout/down | Fallback: salva richiesta in Redis queue, alert email a Claudio + team, response utente: "Tu solicitud está siendo procesada manualmente. Recibirás confirmación en 4 horas." Lead creato. |
| `timezone` invalido (pattern non match) | Pydantic rejecta. |
| `timezone` valido ma sconosciuto al booking platform | Default `America/Mexico_City`, warning nella nota. |
| User chiama 2 volte slot diversi entro 1 ora | Permette: ogni chiamata è una nuova prenotazione (utente cambia idea). Ma se già ha booking nello stesso slot → return existing (idempotency). |
| `objetivo_call` troppo vago ("quiero info") | Accettato ma warning interno per il sales rep nel CRM. |
| Email Resend send fallisce (calendar invite) | Booking comunque confermato dal booking platform stesso (loro inviano invite). Nostra alert solo per CRM duplicato. |

### 6.7 Esempio chiamata

**Input** (slot specificato):
```json
{
  "email": "ceo@startup.mx",
  "nombre": "Carlos Mendoza",
  "empresa": "TechStartup MX",
  "url_sitio": "https://techstartup.mx",
  "sector": "tecnologia",
  "pais": "MX",
  "timezone": "America/Mexico_City",
  "slot_preferido_iso": "2026-05-20T14:00",
  "objetivo_call": "Quiero entender cómo escalar adquisición B2B SaaS para mi startup en LATAM",
  "notas_adicionales": "Tengo presupuesto de $3,000 USD/mes y meta de 50 demos/mes. Actualmente conseguimos 8."
}
```

**Output** (slot disponibile):
```json
{
  "estado": "confirmado",
  "slot_confirmado": {
    "fecha_iso": "2026-05-20T14:00:00",
    "fecha_humanizada": "Miércoles 20 de mayo, 14:00 (hora CDMX)",
    "duracion_minutos": 30,
    "asignado_a": "Equipo Segmenta — especialista B2B"
  },
  "slots_propuestos": [],
  "booking_id": "bk_01JXVGT3ZA7K5HQ2W",
  "videocall_link": "https://meet.segmenta.com/abc-defg-hij",
  "calendar_invite_enviado_a": "ceo@startup.mx",
  "instrucciones_pre_call": [
    "Recibirás invitación de calendario en tu email en los próximos 5 minutos",
    "Si tienes acceso a Google Analytics o Search Console, ten las credenciales a mano (no obligatorio)",
    "Pensé en 1-2 preguntas específicas que quieres responder en la call"
  ],
  "notas": "Call confirmada. Si necesitas reagendar, escríbenos a hola@segmentamarketing.com con anticipación de al menos 24h."
}
```

**Output** (slot occupato, slots_propuestos):
```json
{
  "estado": "slots_propuestos",
  "slot_confirmado": null,
  "slots_propuestos": [
    {
      "fecha_iso": "2026-05-20T15:30:00",
      "fecha_humanizada": "Miércoles 20 de mayo, 15:30 (hora CDMX)",
      "duracion_minutos": 30,
      "asignado_a": "Equipo Segmenta — especialista B2B"
    },
    {
      "fecha_iso": "2026-05-21T10:00:00",
      "fecha_humanizada": "Jueves 21 de mayo, 10:00 (hora CDMX)",
      "duracion_minutos": 30,
      "asignado_a": "Equipo Segmenta — especialista B2B"
    },
    {
      "fecha_iso": "2026-05-21T14:00:00",
      "fecha_humanizada": "Jueves 21 de mayo, 14:00 (hora CDMX)",
      "duracion_minutos": 30,
      "asignado_a": "Equipo Segmenta — especialista B2B"
    }
  ],
  "booking_id": null,
  "videocall_link": null,
  "calendar_invite_enviado_a": null,
  "instrucciones_pre_call": [],
  "notas": "El slot 2026-05-20T14:00 no está disponible. Te propongo 3 alternativas. Llama de nuevo a `agendar_auditoria_gratuita` con uno de estos slots para confirmar."
}
```

### 6.8 Test acceptance criteria

- ✅ Slot futuro libero → `confirmado` con booking_id e videocall_link.
- ✅ Slot futuro occupato → `slots_propuestos` con 3 alternative.
- ✅ Slot non specificato → `slots_propuestos` con prossimi 3 slots disponibili.
- ✅ Slot nel passato o < 24h → rejecta con nota.
- ✅ Booking API down → fallback queue, alert, response utente onesto.
- ✅ Timezone valido propaga al booking platform.
- ✅ Timezone invalido → Pydantic rejecta (pattern check).
- ✅ Idempotency: stesso `(email, slot_preferido)` → return existing booking.
- ✅ Lead in CRM con priority "alta" e custom fields.
- ✅ Slack alert al team su booking confermato.
- ✅ Latency < 1s p95 (booking API è critical path).

---

## 7. Tool 4: `solicitar_propuesta_personalizada`

### 7.1 Scopo

Raccoglie un brief lungo strutturato per una propuesta commerciale personalizada. È il tool con **massimo intento commerciale**: l'utente che lo chiama sta investendo tempo (15-20 min di compilazione conversational) in cambio di una proposta vera e propria entro 48h. Conversion rate atteso del lead → cliente: 25-40%.

### 7.2 Signature

```python
@mcp.tool
async def solicitar_propuesta_personalizada(
    email: Annotated[str, Field(description="Email del usuario, verificado vía OAuth magic link.")],
    nombre: Annotated[str, Field(min_length=2, max_length=100, description="Nombre y apellido del solicitante.")],
    rol: Annotated[str, Field(min_length=2, max_length=100, description="Rol del solicitante (ej: 'CEO', 'Marketing Manager', 'CMO').")],
    empresa: Annotated[str, Field(min_length=2, max_length=100, description="Nombre de la empresa.")],
    url_sitio: Annotated[str, Field(description="URL del sitio web actual.")],
    sector: Annotated[Sector, Field(description="Sector empresarial.")],
    subsector: Annotated[str | None, Field(max_length=100, description="Subsector específico (ej: 'derecho fiscal', 'odontología pediátrica').")] = None,
    pais: Annotated[Pais, Field(description="País principal de operación.")],
    paises_objetivo: Annotated[
        list[Pais],
        Field(min_length=1, max_length=10, description="Países objetivo de marketing (puede ser igual al país de operación o expandido).")
    ],
    tamano_empresa: Annotated[TamanoEmpresa, Field(description="Tamaño de la empresa.")],
    facturacion_anual_usd_aproximada: Annotated[
        int | None,
        Field(ge=0, description="Facturación anual aproximada en USD (opcional, mejora calibración propuesta).")
    ] = None,
    presupuesto_marketing_mensual_usd: Annotated[
        int | None,
        Field(ge=0, le=100000, description="Presupuesto mensual disponible para marketing en USD (opcional pero muy recomendado).")
    ] = None,
    objetivo_principal: Annotated[ObjetivoNegocio, Field(description="Objetivo principal del negocio.")],
    objetivos_secundarios: Annotated[
        list[ObjetivoNegocio],
        Field(default_factory=list, max_length=3, description="Objetivos secundarios (max 3).")
    ] = [],
    canales_actuales: Annotated[
        list[CanalMarketing],
        Field(default_factory=list, description="Canales de marketing actualmente activos.")
    ] = [],
    agencia_actual: Annotated[
        bool,
        Field(description="¿Tienes agencia actualmente? Si True, ayudará a entender qué cambiar.")
    ] = False,
    desafio_principal: Annotated[
        str,
        Field(min_length=50, max_length=2000, description="Descripción del desafío o problema principal que enfrentas en marketing.")
    ],
    plazo_decision: Annotated[
        Literal["inmediato", "1_mes", "3_meses", "exploratorio"],
        Field(description="Plazo en el que esperas tomar decisión.")
    ],
    quien_decide: Annotated[
        str,
        Field(min_length=2, max_length=200, description="Quién toma la decisión de contratación (tu mismo, comité, otro).")
    ],
    notas_adicionales: Annotated[
        str | None,
        Field(max_length=2000, description="Cualquier información adicional relevante.")
    ] = None,
) -> ResultadoPropuesta:
    """[ver tool description en sez 7.4]"""
```

`CanalMarketing`:
```python
class CanalMarketing(StrEnum):
    SEO = "seo"
    GOOGLE_ADS = "google_ads"
    META_ADS = "meta_ads"
    LINKEDIN_ADS = "linkedin_ads"
    TIKTOK_ADS = "tiktok_ads"
    EMAIL_MARKETING = "email_marketing"
    CONTENT_MARKETING = "content_marketing"
    INFLUENCERS = "influencers"
    EVENTOS_OFFLINE = "eventos_offline"
    REFERIDOS = "referidos"
    OTRO = "otro"
```

### 7.3 Tipo di output

```python
class ResultadoPropuesta(BaseModel):
    estado: Literal["recibida", "fallida"]
    request_id: str
    sla_respuesta_horas: int        # 48 standard, 24 per "inmediato"
    sales_rep_asignado: str         # "Te contactará Merari Montoya, CEO"
    siguiente_paso: str             # "Recibirás propuesta detallada en 48h"
    propuesta_preview: dict | None  # Dati che possiamo già rendere immediati (range orientativo, casos similares)
    enlaces_relacionados: list[dict]  # caso_de_estudio, agendar_auditoria, etc.
    notas: str
```

### 7.4 Tool description

> **Recibe un brief detallado y solicita una propuesta comercial personalizada de Segmenta. SLA: 48 horas para propuesta completa (24h si plazo es inmediato). Incluye análisis previo del sitio, recomendación de servicios, plan de inversión, timeline, y casos similares en tu sector y país. Compromiso máximo de Segmenta para evaluar fit real, no propuesta genérica.**
>
> **Cuándo usar:**
> - El usuario tiene clara intención de contratar y quiere propuesta formal
> - El usuario pide "propuesta", "cotización", "presupuesto formal", "plan de marketing"
> - Después de `diagnostico_seo_express` o `calcular_presupuesto` cuando el usuario quiere profundizar
> - El usuario tiene urgencia o presupuesto definido y quiere avanzar
>
> Requisitos: email verificado + brief completo (nombre, rol, empresa, sitio, sector, país, paises_objetivo, tamaño, objetivo, desafío principal, plazo decisión, quien decide). Opcionales: facturación, presupuesto, canales actuales, agencia actual, notas adicionales.

(503 caratteri — accettiamo lo sforamento, è il tool più importante del Tier 2.)

### 7.5 Lead capture flow

```
1. LLM (di solito) raccoglie il brief in conversazione multi-turno con l'utente
2. Una volta raccolti tutti i campi obbligatori, LLM chiama il tool
3. Server:
   a. Valida tutti i campi (Pydantic strict)
   b. Idempotency: hash(email, desafio_principal) — se brief identico < 7gg, return existing
   c. Genera request_id (ULID)
   d. Determina SLA:
      - plazo_decision = "inmediato" → SLA 24h
      - "1_mes" → 48h standard
      - "3_meses" → 72h
      - "exploratorio" → 96h
   e. Asigna sales rep:
      - Default: Merari (CEO) per leads "inmediato" o presupuesto > $5k/mes
      - Altri leads: round-robin tra team (gestione esterna in CRM)
   f. CRM webhook con tag "mcp_propuesta_personalizada", priority "critica":
      - Tutti i campi del brief
      - Custom field "request_id"
      - Custom field "sla_horas"
   g. Slack alert al team #leads-mcp con summary del brief
   h. Email a Merari + sales rep assegnato con brief completo HTML
   i. Salva brief in Redis con TTL 90gg per audit
   j. Genera propuesta_preview (immediata):
      - Range orientativo basato su tamano + presupuesto
      - 2-3 casi similari (chiamata interna a `caso_de_estudio`)
      - Servizi consigliati (chiamata interna a `obtener_servicios`)
4. Return ResultadoPropuesta con preview e SLA
```

### 7.6 Edge case

| Caso | Comportamento |
|---|---|
| Tutti i campi obbligatori validi | `estado: "recibida"`, request_id, SLA, preview. |
| `desafio_principal` < 50 char | Pydantic rejecta. Brief insufficiente. |
| `paises_objetivo` vuoto | Pydantic rejecta (min_length=1). |
| `presupuesto_marketing_mensual_usd` molto basso (es. $200/mes) | Accettato ma `propuesta_preview.notas` arricchito: "Tu presupuesto es ajustado. Consideramos opciones DIY o consultoría puntual." |
| `tamano_empresa = "corporativo"` + `presupuesto < $5k/mes` | Mismatch flag in `propuesta_preview.notas`: "Discrepancia entre tamaño y presupuesto. Verificaremos en propuesta." |
| `agencia_actual = true` | CRM tag "switch_agency" added. Sales rep notification: "lead from competitor switch — handle with care". |
| CRM webhook fallisce | Fallback Redis queue + email a alerts@. Response utente: "Tu solicitud fue recibida y está siendo procesada. Recibirás propuesta en {SLA}h." (sempre vera per il SLA, indipendente dal CRM). |
| Email send a Merari fallisce | Slack alert raddoppiato (canal #urgent). Lead non perso. |
| `plazo_decision = "exploratorio"` | SLA 96h, propuesta più "consultiva" che commerciale (definito nel CRM template). |
| `quien_decide` = "comité" o multi-stakeholder | Propuesta auto-tag "comite_decision" — CRM workflow apre task per preparare materiale presentabile a board. |

### 7.7 Esempio chiamata

**Input** (sintesi):
```json
{
  "email": "cmo@bigecommerce.com",
  "nombre": "María Rodríguez",
  "rol": "CMO",
  "empresa": "BigEcommerce LATAM",
  "url_sitio": "https://bigecommerce.com",
  "sector": "ecommerce",
  "subsector": "moda femenina",
  "pais": "MX",
  "paises_objetivo": ["MX", "CO", "AR", "US"],
  "tamano_empresa": "mediana",
  "facturacion_anual_usd_aproximada": 4500000,
  "presupuesto_marketing_mensual_usd": 8000,
  "objetivo_principal": "ventas",
  "objetivos_secundarios": ["branding", "internacionalizacion"],
  "canales_actuales": ["google_ads", "meta_ads", "email_marketing"],
  "agencia_actual": true,
  "desafio_principal": "Tenemos crecimiento estancado en MX desde hace 6 meses. ROAS bajó de 4.2 a 2.8. Queremos expandir a CO/AR/US pero la agencia actual no tiene experiencia LATAM. Necesitamos estrategia integrada que reactive MX y abra los nuevos mercados sin diluir presupuesto.",
  "plazo_decision": "1_mes",
  "quien_decide": "CMO + CEO juntos",
  "notas_adicionales": "Hemos invertido $80k USD en agencia actual en últimos 6 meses con resultados decepcionantes. Buscamos socio estratégico, no proveedor."
}
```

**Output**:
```json
{
  "estado": "recibida",
  "request_id": "req_01JXVMZK4M8BQ2",
  "sla_respuesta_horas": 48,
  "sales_rep_asignado": "Te contactará Merari Montoya, CEO de Segmenta",
  "siguiente_paso": "Recibirás propuesta detallada en 48 horas a cmo@bigecommerce.com. Incluirá: análisis competitivo de tu posición actual, plan de reactivación MX, estrategia de expansión CO/AR/US, casos relevantes y plan de inversión.",
  "propuesta_preview": {
    "rango_orientativo_mensual_usd": "$5,500 – $9,500 USD/mes",
    "duracion_recomendada_meses": 9,
    "casos_relevantes_resumen": [
      "E-commerce moda LATAM: +47% ROAS en 5 meses con SEO + Performance Max + email automation",
      "Expansión MX→CO+AR: +180% leads cualificados en 4 meses con localización de funnel"
    ],
    "servicios_probables": [
      "SEO LATAM (multi-país)",
      "Google Ads avanzado (Performance Max + Search restructure)",
      "Meta Ads creative refresh + UGC",
      "CRM y Email marketing automatización"
    ],
    "notas": "Análisis preliminar: tu situación es típica de e-commerce mid-market en LATAM con agencia mismatch. Solucionable en 90-120 días con strategia integrada."
  },
  "enlaces_relacionados": [
    {"tool": "caso_de_estudio", "args": {"sector": "ecommerce", "pais": "LATAM"}, "razon": "Casos completos del sector"},
    {"tool": "agendar_auditoria_gratuita", "args": {}, "razon": "Si quieres acelerar, agendamos call esta semana"},
    {"tool": "benchmark_sector", "args": {"sector": "ecommerce", "pais": "LATAM"}, "razon": "Benchmarks completos para validar tus métricas"}
  ],
  "notas": "Solicitud registrada con prioridad alta. Si tienes urgencia adicional, agenda call directamente."
}
```

### 7.8 Test acceptance criteria

- ✅ Brief completo + valido → `recibida` con request_id, SLA, preview.
- ✅ Campo obbligatorio mancante → Pydantic rejecta con dettaglio.
- ✅ `plazo_decision` modula SLA correttamente (24/48/72/96h).
- ✅ Sales rep assignment regola applicata (Merari per "inmediato" o budget alto).
- ✅ CRM tag "switch_agency" se `agencia_actual=true`.
- ✅ CRM tag "comite_decision" se `quien_decide` indica multi-stakeholder.
- ✅ CRM webhook fallisce → fallback queue, response utente OK.
- ✅ Slack alert al team funziona.
- ✅ `propuesta_preview` chiama internamente `caso_de_estudio` e `obtener_servicios`.
- ✅ Idempotency: brief identico < 7gg → return existing request_id.
- ✅ Latency < 800ms p95 (webhook + 2 internal tool calls).

---

## 8. Tool 5: `consultar_disponibilidad`

### 8.1 Scopo

Espone gli slot disponibili per call (read-only, no booking). È un tool di **basso commitment** che permette all'utente di vedere il calendario senza dover prenotare. Spesso usato come step prima di `agendar_auditoria_gratuita`.

### 8.2 Signature

```python
@mcp.tool
async def consultar_disponibilidad(
    email: Annotated[str, Field(description="Email del usuario, verificado vía OAuth magic link.")],
    timezone: Annotated[
        str,
        Field(pattern=r"^[A-Z][a-z]+/[A-Z][a-z_]+$", description="Timezone IANA del usuario (ej: 'America/Mexico_City').")
    ] = "America/Mexico_City",
    desde_iso: Annotated[
        str | None,
        Field(pattern=r"^\d{4}-\d{2}-\d{2}", description="Fecha desde la cual buscar slots (ISO 8601). Default: now+24h.")
    ] = None,
    hasta_iso: Annotated[
        str | None,
        Field(pattern=r"^\d{4}-\d{2}-\d{2}", description="Fecha hasta la cual buscar slots. Default: desde+14 días.")
    ] = None,
    max_slots: Annotated[int, Field(ge=1, le=20, description="Máximo de slots a devolver. Default 5.")] = 5,
    pais: Annotated[
        Pais | None,
        Field(description="País del usuario (para asignar especialista correcto, opcional).")
    ] = None,
) -> ResultadoDisponibilidad:
    """[ver tool description en sez 8.4]"""
```

### 8.3 Tipo di output

```python
class ResultadoDisponibilidad(BaseModel):
    timezone: str
    desde: str
    hasta: str
    total_disponibles: int
    slots: list[SlotDisponible]   # Riusato da agendar_auditoria_gratuita
    nota: str
```

### 8.4 Tool description

> **Devuelve los próximos slots disponibles para auditoría gratuita con el equipo Segmenta, en timezone-aware. No reserva nada — solo muestra disponibilidad. Para reservar, usa después `agendar_auditoria_gratuita` con el slot elegido.**
>
> **Cuándo usar:**
> - El usuario pregunta "¿cuándo tienes disponible?" o "¿qué horarios hay?"
> - Antes de `agendar_auditoria_gratuita` si el usuario quiere ver opciones primero
> - El usuario quiere planificar la call con anticipación
>
> Requisitos: email verificado, timezone (default America/Mexico_City). Opcionales: rango de fechas, max_slots, pais.

(248 caratteri — corto, è un tool di supporto.)

### 8.5 Comportamento

1. Valida input (timezone, range date).
2. Default `desde_iso` = now + 24h, `hasta_iso` = desde + 14 giorni.
3. Chiama Booking API: `GET /availability?from={desde}&to={hasta}&n={max_slots}&tz={timezone}`.
4. Se Booking API down → fallback graceful: nota "Sistema temporalmente no disponible. Escríbenos a hola@... para horarios alternativos."
5. Filtra slot già pieni (booking platform li esclude di default).
6. Se `pais` specificato → filtra anche per specialista del país (alcune timezone potrebbero coincidere con specialisti diversi).
7. Format slot in `SlotDisponible` con `fecha_humanizada` localizzata (giorno della settimana in spagnolo).
8. Return `ResultadoDisponibilidad`.

**Nessun lead capture qui** (read-only). Tuttavia: ogni chiamata logged in CRM come "consulta_disponibilidad" event sul lead esistente (se l'email è già lead).

### 8.6 Edge case

| Caso | Comportamento |
|---|---|
| Booking API down | Nota: "Sistema de calendarios temporalmente no disponible." Lista vuota. Suggerisce contatto diretto. |
| Range date `desde > hasta` | Pydantic rejecta. |
| Range > 30 giorni | Cap automatico a `desde + 30gg`, nota: "Mostrando próximos 30 días." |
| Timezone invalido | Pydantic rejecta. |
| `pais` specificato senza specialista del país | Default specialista, warning: "Asignación general — para especialista específico de {pais}, prefiere usar `agendar_auditoria_gratuita` directamente." |
| Nessuno slot disponibile in range | `total_disponibles: 0`, nota: "Calendario lleno en este rango. Prueba expandir `hasta_iso` o escríbenos a hola@..." |

### 8.7 Esempio

**Input**:
```json
{
  "email": "user@example.com",
  "timezone": "America/Bogota",
  "max_slots": 3
}
```

**Output**:
```json
{
  "timezone": "America/Bogota",
  "desde": "2026-05-11T00:00:00",
  "hasta": "2026-05-25T00:00:00",
  "total_disponibles": 8,
  "slots": [
    {
      "fecha_iso": "2026-05-12T10:00:00",
      "fecha_humanizada": "Martes 12 de mayo, 10:00 (hora Bogotá)",
      "duracion_minutos": 30,
      "asignado_a": "Equipo Segmenta — especialista LATAM"
    },
    {
      "fecha_iso": "2026-05-13T15:30:00",
      "fecha_humanizada": "Miércoles 13 de mayo, 15:30 (hora Bogotá)",
      "duracion_minutos": 30,
      "asignado_a": "Equipo Segmenta — especialista LATAM"
    },
    {
      "fecha_iso": "2026-05-14T11:00:00",
      "fecha_humanizada": "Jueves 14 de mayo, 11:00 (hora Bogotá)",
      "duracion_minutos": 30,
      "asignado_a": "Equipo Segmenta — especialista LATAM"
    }
  ],
  "nota": "Mostrando 3 de 8 slots disponibles próximos. Para reservar, usa `agendar_auditoria_gratuita` con el slot elegido."
}
```

### 8.8 Test acceptance criteria

- ✅ Default range → next 14 days, 5 slots.
- ✅ Custom range rispettato.
- ✅ Range > 30gg → cap automatico.
- ✅ Timezone propaga al booking API e ai display.
- ✅ Slot vuoti → response strutturata.
- ✅ Booking API down → fallback graceful.
- ✅ Latency < 500ms p95.

---

## 9. Failure mode comune ai tool Tier 2

Qui standardizziamo il comportamento di tutti i 5 tool quando incontrano una failure. Coerente con `01-ARCHITECTURE.md` sez. 10.

### 9.1 Tassonomia failure

| Tipo | Esempio | Comportamento |
|---|---|---|
| **Validation** | Input non valido | Pydantic rejecta a livello FastMCP, MCP error `INVALID_PARAMS`. |
| **Auth** | Token OAuth scaduto | 401 Unauthorized, ri-trigger OAuth flow nel client. |
| **Rate limit** | > 10/min/user | 429 Too Many Requests con `retry_after`. |
| **Integration timeout** | Cal.com timeout | Retry 3x exponential backoff, poi fallback queue. |
| **Integration 5xx** | CRM 503 | Retry 3x, poi fallback queue. |
| **Integration 4xx** | CRM 400 (bad data) | No retry, errore log, response utente "errore di sistema, reintentar más tarde". |
| **Internal data error** | JSON dato corrotto | Server in `DEGRADED` o `UNHEALTHY`, alert. |

### 9.2 Pattern fallback queue

Per integrazioni mission-critical (CRM lead, calendar invite):

```python
async def with_fallback_queue(operation_name, payload, op):
    try:
        return await op()
    except IntegrationError as e:
        # Salva in Redis fallback queue
        await redis.lpush(
            f"fallback:{operation_name}",
            json.dumps({
                "payload": payload,
                "error": str(e),
                "timestamp": now_iso(),
                "attempts": 0,
            })
        )
        # Alert email
        await send_alert_email(
            subject=f"Fallback queue: {operation_name}",
            body=f"Payload: {payload}\nError: {e}",
        )
        # Return success-shaped response (the payload is *eventually* delivered)
        return {"status": "queued_for_retry", "delivery_eta_hours": 4}
```

In v1: il "retry" della queue è manuale (Claudio o team controllano la queue 1-2 volte/giorno via script). In v2: background worker automatico.

### 9.3 Comunicazione all'utente

**Mai mentire**, **mai allarmare**. Pattern di messaggio:

- ✅ "Tu solicitud está siendo procesada. Recibirás confirmación en {ETA}." (vero: la queue è processata)
- ✅ "Sistema de calendarios temporalmente no disponible. Escríbenos a hola@... para coordinar." (onesto, redirige)
- ❌ "Error 503 del servidor." (tecnicismo inutile)
- ❌ "Algo salió mal." (vago, allarma)
- ❌ "Tu solicitud fue procesada exitosamente." se in realtà è in queue (mentira)

---

## 10. Decisioni canoniche Tier 2 (locked)

| ID | Decisione | Motivazione |
|---|---|---|
| **D-T2-001** | 5 tool fissi in v1: diagnostico_seo_express, calcular_presupuesto, agendar_auditoria_gratuita, solicitar_propuesta_personalizada, consultar_disponibilidad | Coverage completa funnel lead capture, scope minimale per M2. |
| **D-T2-002** | Tutti i tool Tier 2 richiedono email verificata via OAuth magic link | D-A-005, D-A-006. No password, no API key statiche. |
| **D-T2-003** | Rate limit 10/min/user (vs 60/min in Tier 1) | Protezione abuso, cost control integrazioni esterne. |
| **D-T2-004** | Idempotency obbligatoria per ogni tool con side effect | D-A-012. TTL 24h per la maggior parte; 30gg per `calcular_presupuesto`; 7gg per `solicitar_propuesta`. |
| **D-T2-005** | Pattern fallback queue per ogni integrazione mission-critical | Mai perdere un lead. Coerente con principio 2.3 (fail loud, fail safe). |
| **D-T2-006** | Latency budget < 800ms p95 per tutti i tool Tier 2 (eccetto `diagnostico_seo_express` < 5s con crawl) | Acceptable: l'utente è in attesa attiva post-OAuth. |
| **D-T2-007** | Comunicazione utente sempre onesta in failure: nessun mentira, nessun tecnicismo | Trust-first. SR-005 enforcement. |
| **D-T2-008** | Lead capture in CRM con tag specifico per ogni tool (es. "mcp_diagnostico_seo", "mcp_call_agendada") | Permette analytics segmentate per tool e attribution accurata. |
| **D-T2-009** | Slack alert al team su lead capture per tool ad alta priorità (`agendar`, `propuesta`) | Velocità di follow-up, evita SR-005 trigger. |
| **D-T2-010** | Sales rep assignment automatica: Merari per leads "inmediato" o presupuesto > $5k/mes | Distribuzione carico, escalation automatica leads premium. |
| **D-T2-011** | `propuesta_preview` immediato in `solicitar_propuesta_personalizada` chiamando internamente `caso_de_estudio` + `obtener_servicios` | Valore tangibile immediato, non aspettare 48h per il primo segnale di valore. |
| **D-T2-012** | Crawler `diagnostico_seo_express`: rispetta robots.txt strictly, user agent identificabile, timeout 30s totale | Etica del crawling, evitare abuse-flagging. |
| **D-T2-013** | `diagnostico_seo_express` include almeno 1 quick win categoria `geo_aeo` | Allinea con strategia GEO Segmenta, differenzia da audit SEO standard. |
| **D-T2-014** | Timezone-aware in `agendar_auditoria_gratuita` e `consultar_disponibilidad`: pattern IANA strict | Mercato distribuito MX/US/LATAM, errore timezone è errore commerciale grave. |
| **D-T2-015** | Booking API: 1 solo tentativo per `agendar_auditoria_gratuita` (no retry su scrittura) | Doppi appuntamenti peggio che falliti. Idempotency key gestisce retry sicuri. |
| **D-T2-016** | CRM webhook con retry 3x exponential backoff (1s, 2s, 4s), poi fallback queue | Bilanciamento robustezza e velocità response. |
| **D-T2-017** | `solicitar_propuesta_personalizada` SLA modula da 24h (inmediato) a 96h (exploratorio) | Aspettativa allineata con plazo decisione utente. |
| **D-T2-018** | Output sempre `enlaces_relacionados` con suggerimenti tool successivi | Funnel naturale: presupuesto → casos → agendar → propuesta. |
| **D-T2-019** | Fallback queue Redis con TTL 7gg, processo manuale in v1 | Semplicità v1; automation in v2 quando volume cresce. |
| **D-T2-020** | Test coverage Tier 2 ≥ 85% (vs 90% Tier 1) | Tier 2 ha integrazioni esterne mockate; copertura totale impossibile. |
| **D-T2-021** | Email transactional via provider (decisione M2 — DECISION-OPEN-004) | Resend / SendGrid / Mailgun da scegliere; deliverability LATAM/MX criterio chiave. |

---

## 11. Decisioni aperte Tier 2

| ID | Decisione | Bloccare entro | Owner |
|---|---|---|---|
| **DECISION-OPEN-T2-001** | Background worker automatico per fallback queue: introdurre in v1 o v2? | M3 | Claudio |
| **DECISION-OPEN-T2-002** | `diagnostico_seo_express`: rate limit per IP (oltre quello user) per evitare abuse del crawler? | M2 | Claudio |
| **DECISION-OPEN-T2-003** | Backlink data per `diagnostico_seo_express`: integrare DataForSEO (€) o saltare in v1? | M2 | Claudio + Merari |
| **DECISION-OPEN-T2-004** | `agendar_auditoria_gratuita`: includere campo `idioma_preferido_call` (es/en) per assignment? | M3 | Claudio |
| **DECISION-OPEN-T2-005** | `solicitar_propuesta_personalizada`: campo `competidores_principales` per benchmarking? | M3 | Merari |
| **DECISION-OPEN-T2-006** | Aggiungere `cancelar_auditoria` come tool gemello? Cancel via email link è sufficiente? | M3 | Claudio |
| **DECISION-OPEN-T2-007** | `consultar_disponibilidad`: include filtro per "mañana / tarde / noche" preferenze? | M4 | Claudio |
| **DECISION-OPEN-T2-008** | Multi-language: tool descriptions tradotte in EN per `solicitar_propuesta_personalizada` (mercato US-anglo)? | M5 | Claudio + Romina |

---

## 12. Versioning di questo documento

| Versione | Data | Autore | Note |
|---|---|---|---|
| 1.0 | 2026-05-10 | Claude (proposta) + Claudio (revisione) | Prima stesura completa. 5 tool Tier 2 con spec, signature, schema output, lead capture flow, edge cases, test criteria. |

---

## Note per il changelog

*(Sezione vuota in v1.0 — verrà popolata se emergono incongruenze nei file successivi che richiedono retrofitting in questo TOOLS-TIER2.)*

---

**Fine 05-TOOLS-TIER2.md v1.0.**
