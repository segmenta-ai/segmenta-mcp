# 08 — INTEGRATIONS

| Campo | Valore |
|---|---|
| **Progetto** | Segmenta MCP Server |
| **Versione documento** | 1.2 |
| **Data** | 2026-05-11 |
| **Status** | Approvato (post harmony pass M0.3 + chiusura DECISION-OPEN-004) |
| **File n.** | 08 di 12 numerati |
| **Documento padre** | `00-MASTER-PLAN.md` v1.3, `01-ARCHITECTURE.md` v1.1 |
| **File correlati** | `05-TOOLS-TIER2.md`, `06-TOOLS-TIER3.md`, `07-AUTH-OAUTH.md`, `09-DEPLOYMENT.md` |

---

## 1. Scopo del documento

Questo file specifica **come il server MCP Segmenta comunica con i sistemi esterni** che orchestra: la piattaforma di booking, il CRM, l'email transactional, l'API WhatsApp Business, e (Tier 3) le API SEO competitive.

Per ogni integrazione:
- Cosa fa, perché esiste, quale tool la consuma
- Provider scelto + alternative valutate
- Contratto API (endpoint, request, response)
- Retry strategy, timeout, error handling
- Fallback se il provider è giù
- Costi attesi e budget cap
- Monitoring e alerting specifico

L'architettura del retry/fallback generale è in `01-ARCHITECTURE.md` sez. 10. Le decisioni canoniche di questo file sono in sez. 11.

> **Nota**: alcune scelte di provider sono in `DECISION-OPEN-*` perché dipendono da capacity esistente in Segmenta (es. CRM già in uso) o da test di deliverability (email LATAM). I contratti API qui descritti sono *target* che ogni provider candidato deve soddisfare.

---

## 2. Filosofia delle integrazioni

Cinque principi che governano ogni integrazione esterna.

### 2.1 Provider sostituibile, contratto stabile

L'integrazione vive dietro un'**interfaccia astratta** in `src/segmenta_mcp/integrations/`. Cambiare provider (Cal.com → Calendly, HubSpot → Pipedrive) significa scrivere un nuovo adapter, non riscrivere i tool. Coerente con D-A-010 (5 layer architetturali) e principio 2.4 di `01-ARCHITECTURE.md` (boundary chiare, accoppiamento debole).

### 2.2 Fail loud localmente, fail safe globalmente

Quando un'integrazione fallisce, l'errore è **chiaro e tracciabile** (log + metriche). Ma il sistema **non degrada silenziosamente**: ha un fallback che protegge l'utente finale e il business (mai perdere un lead — vedi `05-TOOLS-TIER2.md` sez. 9.2).

### 2.3 Idempotency end-to-end

Ogni operazione di scrittura (creare booking, creare lead, inviare email) ha un `idempotency_key` propagato dal nostro MCP layer al provider. Retry safe: se il provider non risponde ma ha eseguito, il retry produce stesso risultato senza side effect duplicati.

### 2.4 Cost-aware

Ogni integrazione ha un **budget cap mensile** monitorato. Sopra soglia → degrade automatico (es. analizar_competencia degrada da `completo` a `basico`). Coerente con D-T3-003.

### 2.5 Observability uniforme

Ogni chiamata esterna genera la stessa struttura di log e metriche, indipendentemente dal provider. Un dashboard unico monitora tutte le integrazioni con stessa lente.

---

## 3. Mappa delle integrazioni

| Tool consumatore | Integrazione | Cosa fa | Criticità | Cost model |
|---|---|---|---|---|
| `agendar_auditoria_gratuita`, `consultar_disponibilidad` | **Booking platform** | Crea/legge slot calendar | Alta | Free tier sufficiente v1-v2 |
| `solicitar_propuesta_personalizada`, `agendar_auditoria_gratuita`, `diagnostico_seo_express`, `calcular_presupuesto` | **CRM** | Crea/aggiorna lead | Alta | Esistente in Segmenta |
| `diagnostico_seo_express`, magic link OAuth | **Email transactional** | Invia email automatiche | Critica | ~$10/mese (low volume v1) |
| `whatsapp_directo` (link generation) | **WhatsApp link** | wa.me URL (no API call) | Bassa | Zero |
| Tier 2 alert | **Slack webhook** | Notifica team su lead capture | Media | Zero (webhook) |
| `analizar_competencia` (modo `completo`) | **SEO data API** | Keywords, traffic, paid stima competitor | Media | $0.10-0.30/call, cap $20/mese |
| Tutto | **Geo IP** | Risolve location da IP per logging + risk scoring | Bassa | Free tier sufficiente |
| Tutto | **DNS / TLS** | DNS lookup + TLS handshake | Implicita | Zero |

---

## 4. Booking platform

> 🔧 **Adapter Pattern v1** (HC-004 v1.1): l'implementazione del booking è dietro un Pydantic `Protocol` (`BookingProvider`). Il default v1 è **Cal.com** (vedi sez. 4.4 per contratto API completo). Se DECISION-OPEN-002 chiude diversamente (es. Calendly), il cambio costa **un solo file** `integrations/booking_calendly.py` che implementa la stessa interfaccia — il tool layer (`agendar_auditoria_gratuita`, `consultar_disponibilidad`) e il dominio non cambiano. Test suite fornisce mock `BookingProvider` per CI.

### 4.1 Provider scelto

**Cal.com** è l'opzione preferita. DECISION-OPEN-002 di `00-MASTER-PLAN.md` rimane aperta finché Merari conferma cosa Segmenta usa già:

| Provider | Pro | Contro | Decisione |
|---|---|---|---|
| **Cal.com** | Open source, API REST completa, Free tier generoso, self-host opzionale | Meno noto in LATAM | **Default v1** se Segmenta non ha già un altro tool |
| **Calendly** | Standard di settore, marca riconoscibile | API meno flessibile, prezzo per seat | Se Segmenta lo ha già, lo usiamo |
| **TidyCal** | Economico, brand AppSumo | Meno feature avanzate | No |
| **Google Calendar API direct** | Massima flessibilità | Lavoro custom per UX prenotazione | No in v1 |

### 4.2 Capabilities richieste

Indipendentemente dal provider scelto, l'integrazione deve supportare:

- ✅ Lettura disponibilità in range data + timezone
- ✅ Creazione booking con timezone-aware
- ✅ Reschedule / cancel via API
- ✅ Webhook su events (booking_created, rescheduled, cancelled, no_show)
- ✅ Custom fields nel form di booking (per passare context Segmenta MCP)
- ✅ Multi-host (assegnazione automatica al sales rep correto)
- ✅ Email di conferma personalizzabile
- ✅ Videocall provider integrato (Zoom / Google Meet / Cal Video)

### 4.3 Contratto API target

Wrapper interno `integrations/booking.py` espone questa interfaccia, indipendentemente dal provider sottostante:

```python
from typing import Protocol
from datetime import datetime

class BookingProvider(Protocol):
    """Interfaccia astratta per provider di booking."""

    async def get_availability(
        self,
        from_iso: datetime,
        to_iso: datetime,
        timezone: str,
        event_type_id: str,
        limit: int = 5,
    ) -> list[Slot]:
        """Restituisce slot disponibili nel range."""

    async def create_booking(
        self,
        slot_iso: datetime,
        timezone: str,
        attendee_email: str,
        attendee_name: str,
        event_type_id: str,
        custom_fields: dict[str, str],
        idempotency_key: str,
    ) -> BookingResult:
        """Crea booking. Idempotente via idempotency_key."""

    async def cancel_booking(
        self,
        booking_id: str,
        reason: str = "",
    ) -> bool:
        """Cancella booking esistente."""

    async def get_booking(self, booking_id: str) -> Booking | None:
        """Recupera dettagli booking."""
```

`Slot`, `BookingResult`, `Booking` sono Pydantic models definiti in `integrations/models.py`.

### 4.4 Implementazione Cal.com (target)

**Endpoint base**: `https://api.cal.com/v2/`

**Autenticazione**: API key in header `Authorization: Bearer <CALCOM_API_KEY>`. Key in Fly.io secrets (`flyctl secrets set CALCOM_API_KEY=...`).

**Endpoint usati**:

| Operazione | Method | Path |
|---|---|---|
| Get availability | GET | `/slots/available?start={iso}&end={iso}&eventTypeSlug={slug}&timeZone={tz}` |
| Create booking | POST | `/bookings` |
| Cancel booking | DELETE | `/bookings/{id}` |
| Get booking | GET | `/bookings/{id}` |

**Esempio create_booking**:

```http
POST /v2/bookings
Authorization: Bearer cal_live_xxx
Idempotency-Key: hash(email, slot_iso)
Content-Type: application/json

{
  "eventTypeId": 12345,
  "start": "2026-05-20T14:00:00.000Z",
  "timeZone": "America/Mexico_City",
  "attendee": {
    "name": "Carlos Mendoza",
    "email": "ceo@startup.mx",
    "language": "es"
  },
  "metadata": {
    "source": "mcp_segmenta",
    "tool": "agendar_auditoria_gratuita",
    "url_sitio": "https://techstartup.mx",
    "sector": "tecnologia",
    "objetivo_call": "Escalar adquisición B2B SaaS",
    "request_id": "req_01..."
  }
}
```

**Response 201 Created**:

```json
{
  "data": {
    "id": 78910,
    "uid": "bk_01JXVGT3ZA7K5HQ2W",
    "status": "ACCEPTED",
    "title": "Auditoría Segmenta - Carlos Mendoza",
    "start": "2026-05-20T14:00:00.000Z",
    "end": "2026-05-20T14:30:00.000Z",
    "videoCallUrl": "https://meet.cal.com/abc-defg-hij",
    "host": {
      "id": 999,
      "email": "merari@segmentamarketing.com",
      "name": "Merari Montoya"
    }
  }
}
```

**Response 409 Conflict** (slot occupato):

```json
{
  "error": {
    "code": "SLOT_NOT_AVAILABLE",
    "message": "The requested time slot is not available."
  }
}
```

### 4.5 Retry e timeout

| Operazione | Timeout connect | Timeout total | Retry | Idempotente |
|---|---|---|---|---|
| `get_availability` | 3s | 5s | 2x exponential (1s, 2s) | Sì (read-only) |
| `create_booking` | 5s | 10s | **0 retry** (D-T2-015) | Sì via Idempotency-Key |
| `cancel_booking` | 3s | 5s | 1 retry (1s) | Sì |
| `get_booking` | 3s | 5s | 2 retry | Sì |

Razionale `0 retry` su `create_booking`: doppi appuntamenti sono peggio che falliti. Idempotency-Key copre i retry safe (stesso utente che ritriova nello stesso slot ottiene stessa response). Network failure dopo create → utente vede errore, ritriova manualmente, idempotency previene doppia prenotazione.

### 4.6 Fallback se Cal.com down

Definito in `05-TOOLS-TIER2.md` sez. 6.6 e standardizzato qui:

```python
async def create_booking_with_fallback(...) -> BookingResult:
    try:
        return await calcom.create_booking(...)
    except (TimeoutError, IntegrationError) as e:
        # Fallback queue
        request_id = await save_to_fallback_queue(
            queue="booking",
            payload={"slot_iso": ..., "email": ..., "details": ...},
            error=str(e),
        )
        # Slack alert
        await slack_alert("#alerts-mcp", f"Booking fallback queue +1, request {request_id}")
        # Email alert a Claudio
        await send_alert_email(
            subject="Cal.com integration down — manual booking required",
            body=f"Request: {request_id}\nDetails: {payload}"
        )
        # Response onesta utente
        return BookingResult(
            estado="queued",
            booking_id=None,
            videocall_link=None,
            notas=(
                "Sistema de calendarios temporalmente con problemas. "
                "Tu solicitud está siendo procesada manualmente. "
                "Recibirás confirmación en máximo 4 horas. "
                "Para urgencia, contáctanos en hola@segmentamarketing.com."
            )
        )
```

### 4.7 Webhook handling (incoming da Cal.com)

Cal.com può notificarci su events del booking. Endpoint:

`POST /webhooks/calcom`

Validation:
- Header `X-Cal-Signature-256` con HMAC SHA-256 del body con `CALCOM_WEBHOOK_SECRET`.
- Reject se signature non match.

Events gestiti in v1:
- `BOOKING_CREATED`: log + push CRM (se non già pushato — idempotency).
- `BOOKING_CANCELLED`: log + flag CRM lead.
- `BOOKING_RESCHEDULED`: log + update CRM.
- `BOOKING_NO_SHOW` (M3+): flag CRM lead come "no_show", workflow re-engagement.

In v1: webhook è "nice to have", non required (l'app può funzionare senza). I Cal events sono fonte di verità per analytics, non per il flow primario.

### 4.8 Costo atteso

Free tier Cal.com (al 2026-05): 1 utente, 1 event type, unlimited bookings. Per uso v1 (1 sales rep, 1 evento "Auditoría Segmenta") sufficiente.

Quando aggiungiamo > 1 sales rep (M3+): Cal.com Teams plan ~$15/seat/mese. Budget previsto: $15-45/mese in M4.

---

## 5. CRM

> 🔧 **Adapter Pattern v1** (HC-004 v1.1): il CRM è dietro un Pydantic `Protocol` (`CrmProvider`). Default v1 = **HubSpot** (vedi sez. 5.4 per implementazione). Se DECISION-OPEN-003 chiude su Pipedrive o Zoho, sostituire solo `integrations/crm_<provider>.py`. Custom properties Segmenta (sez. 5.5) restano concettualmente uguali — cambia solo il mapping API. Tool layer (`solicitar_propuesta_personalizada`, `agendar_auditoria_gratuita`) invariato.

### 5.1 Provider scelto

DECISION-OPEN-003 di `00-MASTER-PLAN.md` rimane aperta. Merari deve confermare quale CRM usa già Segmenta. Comparativa:

| Provider | Pro | Contro | Fit Segmenta |
|---|---|---|---|
| **HubSpot** | Standard di settore, ricco di feature, marketing automation integrata, free tier potente | Costo crescente con volume, vendor lock-in | **Probabile**: HubSpot è dominante nel marketing agency space |
| **Pipedrive** | Sales-focused, semplice, prezzo accessibile | Marketing automation più limitata | Possibile |
| **Zoho CRM** | Ecosistema completo (CRM + email + analytics) | UX dated | Backup |
| **Custom DB** | Flessibilità totale, no costo subscription | Lavoro di mantenimento, no automation gratis | No in v1 |

Default ipotetico: **HubSpot** (probabilmente già in uso). I contratti API target sotto sono basati su HubSpot v3 API.

### 5.2 Capabilities richieste

- ✅ Create / update contact (lead) con custom fields
- ✅ Tag o lifecycle stage management
- ✅ Custom properties per `mcp_*` (mcp_request_id, mcp_tool, mcp_tier, mcp_source)
- ✅ Note/activity log per ogni lead
- ✅ Webhook outbound (per Slack alert downstream)
- ✅ Search per email (idempotency: se lead esiste, update invece di duplicare)
- ✅ Pipeline assignment (sales rep auto-routing)

### 5.3 Contratto API target

```python
class CRMProvider(Protocol):

    async def upsert_contact(
        self,
        email: str,
        properties: dict[str, str],
        tags: list[str],
        idempotency_key: str,
    ) -> ContactResult:
        """Crea o aggiorna contact. Idempotente per email."""

    async def add_activity(
        self,
        contact_email: str,
        activity_type: str,         # "note" | "tool_call" | "magic_link_used"
        content: str,
        metadata: dict,
    ) -> bool:
        """Aggiunge activity log al contact."""

    async def assign_owner(
        self,
        contact_email: str,
        owner_id: str,
    ) -> bool:
        """Assegna sales rep al lead."""
```

### 5.4 HubSpot v3 implementation (target)

**Endpoint base**: `https://api.hubapi.com/`

**Autenticazione**: Private App Access Token (not deprecated API key) in header `Authorization: Bearer <HUBSPOT_TOKEN>`.

**Esempio upsert_contact**:

```http
POST /crm/v3/objects/contacts/batch/upsert
Authorization: Bearer pat-xxx
Content-Type: application/json

{
  "inputs": [
    {
      "idProperty": "email",
      "id": "ceo@startup.mx",
      "properties": {
        "email": "ceo@startup.mx",
        "firstname": "Carlos",
        "lastname": "Mendoza",
        "company": "TechStartup MX",
        "country": "Mexico",
        "lifecyclestage": "lead",
        "mcp_request_id": "req_01...",
        "mcp_tool": "agendar_auditoria_gratuita",
        "mcp_tier": "2",
        "mcp_source": "mcp_segmenta",
        "mcp_first_interaction": "2026-05-10T15:42:18Z",
        "url_sitio": "https://techstartup.mx",
        "sector": "tecnologia",
        "objetivo_principal": "leads"
      }
    }
  ]
}
```

**Response 200 OK**:

```json
{
  "results": [
    {
      "id": "67890",
      "properties": {...},
      "createdAt": "2026-05-10T15:42:19Z",
      "updatedAt": "2026-05-10T15:42:19Z"
    }
  ]
}
```

### 5.5 Custom properties Segmenta (HubSpot setup)

Da configurare manualmente in HubSpot pre M2 (one-time setup):

| Property | Tipo | Cosa contiene |
|---|---|---|
| `mcp_request_id` | string | ID della prima interazione MCP |
| `mcp_tool` | string | Quale tool ha generato il lead (es. `solicitar_propuesta_personalizada`) |
| `mcp_tier` | enumeration | "1", "2", "3" |
| `mcp_source` | string | Sempre `"mcp_segmenta"` (filtro analytics) |
| `mcp_first_interaction` | datetime | Timestamp prima call |
| `mcp_last_interaction` | datetime | Timestamp ultima call |
| `mcp_total_calls` | number | Counter totale chiamate MCP |
| `mcp_tools_used` | string (CSV) | Lista tool chiamati |
| `mcp_client_origin` | string | `claude.ai` / `chatgpt.com` / altro |
| `mcp_user_country` | string | ISO country code |

### 5.6 Tags / Lifecycle stage mapping

| Tool | HubSpot tag/lifecycle |
|---|---|
| `diagnostico_seo_express` | `lead`, tag `mcp_diagnostico_seo` |
| `calcular_presupuesto` | `lead`, tag `mcp_presupuesto` |
| `agendar_auditoria_gratuita` | `marketingqualifiedlead` (MQL), tag `mcp_call_agendada`, priority `alta` |
| `solicitar_propuesta_personalizada` | `salesqualifiedlead` (SQL), tag `mcp_propuesta`, priority `critica` |
| `analizar_competencia` | tag `mcp_competitive_intel` aggiunto a contact esistente |

Oggetto naming HubSpot tags: snake_case con prefisso `mcp_` per filtraggio facile.

### 5.7 Retry e timeout

| Operazione | Timeout | Retry | Idempotente |
|---|---|---|---|
| `upsert_contact` | 8s total | 3x exponential (1s, 2s, 4s) | Sì (idProperty=email) |
| `add_activity` | 5s | 3x | Sì via idempotency_key |
| `assign_owner` | 5s | 2x | Sì |

### 5.8 Fallback se HubSpot down

Standard fallback queue + email alert:

```python
async def upsert_contact_with_fallback(...) -> ContactResult:
    try:
        return await crm.upsert_contact(...)
    except IntegrationError as e:
        await save_to_fallback_queue(
            queue="crm",
            payload={...},
            error=str(e),
        )
        await send_alert_email(
            subject=f"CRM fallback: {payload['email']}",
            body=...
        )
        # Lead non perso — il dato è in Redis 7 giorni
        return ContactResult(status="queued", contact_id=None)
```

In v1 il flush della queue è manuale (Claudio o team controllano `scripts/process_fallback_queue.py` 1-2 volte/giorno). In v2: background worker.

### 5.9 Costo atteso

HubSpot Free CRM: 1 milione contacts gratis. Marketing Hub Starter $20/mese aggiunge automation (necessario M3+).

Budget v1: $0/mese (free tier). M3+: $20-50/mese.

---

## 6. Email transactional

> 🔧 **Adapter Pattern v1** (HC-004 v1.1): l'invio email resta dietro Pydantic `Protocol` (`EmailProvider`) con metodi `send_magic_link(email, token)` e `send_diagnostic_report(email, report_url)`. Provider scelto v1 = **Resend** (DECISION-OPEN-004 chiusa 2026-05-11). Eventuale swap futuro (SendGrid/Mailgun) = un solo file `integrations/email_<provider>.py`.

### 6.1 Provider scelto: Resend (chiuso v1.2)

**DECISION-OPEN-004 chiusa 2026-05-11**. Provider canonico: **Resend free tier** (100 email/giorno = ~3000/mese, sufficiente M1-M3 dato volume previsto).

Comparativa che ha portato alla decisione:

| Provider | Pro | Contro | Deliverability LATAM | Decisione |
|---|---|---|---|---|
| **Resend** | Developer-friendly, API moderna REST + Python SDK, **free tier 100/giorno = $0/mese**, dashboard chiara, supporto DKIM/SPF/DMARC nativo | Più giovane, brand reputation in costruzione | Buona (da validare in M2 con test pratico) | ✅ **SCELTO v1.2** |
| SendGrid | Standard di settore, deliverability solida globale | UI dated, free tier solo 100/giorno (paro a Resend ma con overhead UX) | Ottima | Backup se Resend fallisce M2 deliverability test |
| Mailgun | Forza in deliverability EU | Free tier limitato (5k/mese poi paid) | Buona | Backup 2 |
| Postmark | Eccellente deliverability transactional | No free tier persistente | Ottima | Alternativa premium se Resend insufficiente in M3+ |
| AWS SES | Costo molto basso a scala | Setup complesso, no UX | Variabile | No in v1 (overhead) |

**Razionale scelta Resend**:
1. Coerente con target costo $0/mese (D-MP-002 v1.3, D-DE-020 v1.2).
2. API pulita, ecosystem Python ufficialmente supportato.
3. Free tier sufficiente per M1-M3 (volume previsto < 50 email/giorno).
4. Switch path chiaro grazie ad adapter pattern (HC-004).

**Test deliverability obbligatorio in M2.3.10** (M2): inviare 100 email a domini MX/AR/CO/CL/PE comuni (gmail.com, hotmail.com, outlook.com, yahoo.com.mx) e verificare inbox vs spam. Se < 90% inbox rate → escalation a SendGrid o Postmark e re-bump DECISION-OPEN-004.

### 6.2 Capabilities richieste

- ✅ Send transactional via API REST
- ✅ Template HTML + plain text
- ✅ Variable interpolation (Handlebars o equiv.)
- ✅ Sender reputation management
- ✅ Bounce handling (inbox cleanup)
- ✅ Delivery webhook (per audit log)
- ✅ Custom domain (dkim, spf, dmarc)
- ✅ Attachment support (per report PDF in M3+)
- ✅ Idempotency via custom header

### 6.3 Contratto API target

```python
class EmailProvider(Protocol):

    async def send_transactional(
        self,
        to: str,
        subject: str,
        template_id: str | None = None,
        template_vars: dict | None = None,
        html_body: str | None = None,
        text_body: str | None = None,
        from_name: str = "Segmenta MCP",
        from_email: str = "noreply@mcp.segmentamarketing.com",
        reply_to: str = "hola@segmentamarketing.com",
        idempotency_key: str | None = None,
        tags: list[str] | None = None,
    ) -> EmailResult:
        """Invia email transactional. Restituisce delivery_id."""

    async def get_delivery_status(self, delivery_id: str) -> EmailStatus:
        """Stato consegna: queued, sent, delivered, bounced, complained."""
```

### 6.4 Resend implementation (target)

**Endpoint base**: `https://api.resend.com/`

**Autenticazione**: API key Bearer `Authorization: Bearer re_xxx`.

**Esempio send_transactional**:

```http
POST /emails
Authorization: Bearer re_xxx
Idempotency-Key: hash(to, template, request_id)
Content-Type: application/json

{
  "from": "Segmenta MCP <noreply@mcp.segmentamarketing.com>",
  "to": ["doctor@miclinica.mx"],
  "reply_to": "hola@segmentamarketing.com",
  "subject": "Tu enlace de acceso a Segmenta MCP",
  "html": "<!DOCTYPE html>...",
  "text": "Hola,\n\nRecibimos una solicitud...",
  "tags": [
    {"name": "type", "value": "magic_link"},
    {"name": "tier", "value": "auth"}
  ]
}
```

**Response 200 OK**:

```json
{
  "id": "deliv_01JXVZL5HQNT...",
  "from": "Segmenta MCP <noreply@mcp.segmentamarketing.com>",
  "to": ["doctor@miclinica.mx"],
  "created_at": "2026-05-10T15:42:19.123Z"
}
```

### 6.5 Templates email v1

Lista template necessari per M2:

| Template ID | Scopo | Tool consumatore |
|---|---|---|
| `magic_link_es_latam` | Magic link OAuth (default) | Auth flow |
| `magic_link_es_es` | Magic link OAuth (variante ES) | Auth flow (locale-aware) |
| `magic_link_en_us` | Magic link OAuth (EN) | Auth flow (US-anglo) |
| `diagnostico_seo_report` | Report SEO completo HTML | `diagnostico_seo_express` |
| `auditoria_confirmation` | Conferma booking + pre-call info | `agendar_auditoria_gratuita` |
| `propuesta_recibida` | Conferma ricezione propuesta brief | `solicitar_propuesta_personalizada` |
| `research_publicado` | Notifica utenti che hanno contribuito a research pubblicato | `share_research` (M3+) |

I template HTML sono in `templates/email/*.html`, gestiti via Resend dashboard o file locali.

### 6.6 Domain setup (DKIM, SPF, DMARC)

DECISION-OPEN-004 risolta in M2 richiede setup DNS:

```
; SPF record
mcp.segmentamarketing.com. TXT  "v=spf1 include:_spf.resend.com ~all"

; DKIM (provider-specific, esempio Resend)
resend._domainkey.mcp.segmentamarketing.com. TXT  "k=rsa; p=MIGfMA0..."

; DMARC
_dmarc.mcp.segmentamarketing.com. TXT  "v=DMARC1; p=quarantine; rua=mailto:dmarc@segmentamarketing.com; pct=100"
```

Validazione: `dig TXT _dmarc.mcp.segmentamarketing.com` + tool come [mxtoolbox.com](https://mxtoolbox.com) per check completo.

### 6.7 Retry e timeout

| Operazione | Timeout | Retry | Idempotente |
|---|---|---|---|
| `send_transactional` | 5s | 3x exponential (1s, 2s, 4s) | Sì via Idempotency-Key |
| `get_delivery_status` | 3s | 2x | Sì (read-only) |

### 6.8 Fallback se Resend down

Critico per magic link (auth flow): senza email l'utente non può autenticarsi. Strategia:

```python
async def send_with_fallback(...):
    try:
        return await resend.send(...)
    except ResendDownError:
        # Try secondary provider (configurato in M3+)
        try:
            return await sendgrid_backup.send(...)
        except:
            # Both down: alert critico + queue
            await save_to_fallback_queue("email", payload)
            await alert_email_critical("Email infrastructure DOWN")
            # Per magic link specificamente: invalidate flow, ask user to retry later
            raise EmailUnavailableError(
                "Sistema de email temporalmente no disponible. Reintenta en 5 minutos."
            )
```

In v1: solo Resend, no secondary provider. Down = magic link non inviato. Utente vede errore esplicito (no silent fail).

### 6.9 Costo atteso

Resend free tier: 100 email/giorno (3,000/mese). Sufficiente per M1-M2.

M3+ con scala (50+ lead/mese × multiple email per lead): Resend Pro ~$20/mese (50,000/mese).

Budget M1: $0/mese. M3+: $20/mese.

---

## 7. Slack webhook (alerts interni)

### 7.1 Scopo

Notifiche real-time al team Segmenta su events critici: lead capture Tier 2/3, fallback queue spike, errori production.

### 7.2 Setup

Slack Incoming Webhook URL configurato in Fly.io secrets: `SLACK_WEBHOOK_URL_LEADS_MCP`, `SLACK_WEBHOOK_URL_ALERTS_MCP`.

Channel target:
- `#leads-mcp`: lead capture (silent during off-hours, ma notifica visible)
- `#alerts-mcp`: errori production, fallback queue, integration down (ping immediato)

### 7.3 Contratto

```python
class SlackNotifier:

    async def notify_lead_captured(
        self,
        channel: str,
        tool: str,
        email: str,
        priority: Literal["normal", "alta", "critica"],
        details: dict,
    ) -> None:
        """Notifica nuovo lead al team."""

    async def notify_alert(
        self,
        channel: str,
        severity: Literal["info", "warning", "critical"],
        title: str,
        message: str,
        request_id: str | None = None,
    ) -> None:
        """Notifica errore o anomalia."""
```

### 7.4 Esempio payload

```json
{
  "blocks": [
    {
      "type": "header",
      "text": {"type": "plain_text", "text": "🎯 Nuevo lead MCP — Tier 2"}
    },
    {
      "type": "section",
      "fields": [
        {"type": "mrkdwn", "text": "*Tool:* `solicitar_propuesta_personalizada`"},
        {"type": "mrkdwn", "text": "*Priority:* `crítica`"},
        {"type": "mrkdwn", "text": "*Empresa:* BigEcommerce LATAM"},
        {"type": "mrkdwn", "text": "*Email:* cmo@bigecommerce.com"},
        {"type": "mrkdwn", "text": "*Sector:* ecommerce"},
        {"type": "mrkdwn", "text": "*País:* MX"},
        {"type": "mrkdwn", "text": "*Presupuesto:* $8,000 USD/mes"},
        {"type": "mrkdwn", "text": "*SLA:* 48h"}
      ]
    },
    {
      "type": "actions",
      "elements": [
        {
          "type": "button",
          "text": {"type": "plain_text", "text": "Abrir en HubSpot"},
          "url": "https://app.hubspot.com/contacts/{contact_id}"
        }
      ]
    }
  ]
}
```

### 7.5 Retry e timeout

| Operazione | Timeout | Retry |
|---|---|---|
| Slack webhook POST | 3s | 1x (retry minimo, è solo notifica) |

Slack down = notifica perduta. Non è critico (lead salvato comunque in CRM). Log warning solo.

### 7.6 Costo

Zero. Webhook standard.

---

## 8. WhatsApp link generation

### 8.1 Scopo

Genera URL `wa.me/{numero}?text={message}` per `whatsapp_directo`. **Niente API call esterna in v1** — l'utente clicca il link e WhatsApp gestisce il resto.

### 8.2 Pattern

```python
def generate_whatsapp_link(
    numero: str,                # E.164 senza '+' (es. "5215512345678")
    mensaje: str,
) -> str:
    """Genera wa.me link con messaggio URL-encoded."""
    encoded = urllib.parse.quote(mensaje)
    return f"https://wa.me/{numero}?text={encoded}"
```

### 8.3 Mapping numeri

Vedi `06-TOOLS-TIER3.md` sez. 5.6. DECISION-OPEN-T3-001 da chiudere con Merari (numeri specifici per país).

### 8.4 WhatsApp Business API (futuro v2)

In v2 valuteremo integrazione attiva con WhatsApp Business API per:
- Tracking effettivo dei messaggi inviati (analytics)
- Auto-reply iniziale
- Lead capture automatico nel CRM

Provider candidati: Twilio, MessageBird, 360dialog. DECISION-OPEN-008 di MASTER-PLAN.

### 8.5 Costo v1

Zero (link generation puramente client-side). v2: $0.005-0.05 per messaggio inviato (Twilio pricing 2026).

---

## 9. SEO data API (Tier 3)

> 🔧 **Adapter Pattern v1** (HC-004 v1.1): provider SEO data dietro Pydantic `Protocol` (`SeoDataProvider`) con metodi `get_keyword_rankings(domain, country)`, `get_backlink_profile(domain)`, `get_paid_keywords(domain)`. Default v1 = **DataForSEO**. Se DECISION-OPEN-T3-002 chiude su SEMrush/Ahrefs, sostituire `integrations/seo_data_<provider>.py`. Cost cap (sez. 9.5) è enforce dal middleware adapter, indipendente dal provider.

### 9.1 Scopo

Per `analizar_competencia` modo `completo`. Fornisce dati di posizionamento SEO + paid stima del competitor.

### 9.2 Provider scelto

DECISION-OPEN-T3-002 di `06-TOOLS-TIER3.md` aperta. Comparativa:

| Provider | Pro | Contro | Cost/call (stima) |
|---|---|---|---|
| **DataForSEO** | API REST semplice, ricca, pay-as-you-go | Volume basso = cost per call alto | $0.05-0.30 |
| **SEMrush API** | Brand riconoscibile, dataset profondo | Subscription required, alta soglia entry | $200/mese minimo + per call |
| **Ahrefs API** | Backlink data eccellente | Subscription required | $500/mese minimo |
| **SERPAPI** | Specifico per SERP scraping, semplice | Limitato (solo serp, no full SEO) | $0.02-0.05 |

**Default candidato**: DataForSEO (pay-as-you-go aligned con cost cap di Tier 3).

### 9.3 Capabilities richieste

- ✅ Top organic keywords del competitor (con position, search volume, difficulty)
- ✅ Estimated organic traffic mensile
- ✅ Top paid keywords + budget stimato
- ✅ Backlink summary (DA, top referring domains)
- ✅ Country-specific data (MX, US, ES, CO, AR)

### 9.4 Contratto API target

```python
class SEODataProvider(Protocol):

    async def get_competitor_overview(
        self,
        url: str,
        country: str,    # ISO codes
    ) -> CompetitorOverview:
        """Overview SEO + paid stima."""

    async def get_top_keywords(
        self,
        url: str,
        country: str,
        limit: int = 20,
    ) -> list[Keyword]:
        """Top keywords con position e volume."""
```

### 9.5 Cost cap implementation

```python
CAP_USD_MENSILE = 20  # D-T3-003

async def call_seo_api(...) -> Result:
    current_spend = await redis.get(f"seo_api_spend:{current_month}")
    if float(current_spend or 0) >= CAP_USD_MENSILE:
        # Cap raggiunto: degrade automatico
        await alert_email("SEO API cap reached, degrading to basic mode")
        raise CapExceededError("Cap mensual alcanzado")

    result = await provider.call(...)

    # Track spend
    cost_usd = estimate_cost(result)
    await redis.incrbyfloat(f"seo_api_spend:{current_month}", cost_usd)

    return result
```

### 9.6 Retry e timeout

| Operazione | Timeout | Retry |
|---|---|---|
| `get_competitor_overview` | 15s | 2x exponential (2s, 4s) |
| `get_top_keywords` | 15s | 2x |

SEO data API è **lentissima** rispetto al resto (15s+ è normale per query profonde). Latency budget di `analizar_competencia` `completo` è < 8s p95: usiamo il modo `basico` come timeout fallback automatico se l'API non risponde in 5s.

### 9.7 Costo atteso

Pay-as-you-go DataForSEO: $0.10-0.30 per chiamata `competitor_overview` + $0.02-0.05 per chiamata `top_keywords`.

Budget mensile: $20 (D-T3-003) = ~50-150 chiamate `completo` mensili. Sufficiente per soft credit system (3 gratis/utente/mese × ~50 utenti attivi).

---

## 10. Geo IP

### 10.1 Scopo

Risolve country/city da IP per:
- Logging `user_country` nei tool calls
- Risk scoring auth flow (geo anomalo)
- Localizzazione default UI form OAuth

### 10.2 Provider scelto

DECISION-OPEN-AU-008 di `07-AUTH-OAUTH.md` aperta. Comparativa:

| Provider | Pro | Contro | Cost |
|---|---|---|---|
| **ipinfo.io** | Free tier 50k/mese, accurate | Free tier limit | $0 v1 |
| **ip-api.com** | Free tier 45/min unlimited | Senza HTTPS in free | $0 |
| **MaxMind GeoLite2** | Database scaricabile, no rate limit | Setup self-hosted, update mensili | $0 |

**Default**: ipinfo.io free tier sufficiente per v1 (anche con 1000 chiamate/giorno restiamo sotto limit).

### 10.3 Implementation

```python
async def get_geo(ip: str) -> GeoResult:
    # Cache 24h per IP (geo non cambia frequentemente)
    cached = await redis.get(f"geo:{ip}")
    if cached:
        return GeoResult.parse_raw(cached)

    response = await httpx.get(
        f"https://ipinfo.io/{ip}/json",
        params={"token": IPINFO_TOKEN},
        timeout=2.0,
    )
    data = response.json()
    result = GeoResult(
        ip=ip,
        country=data.get("country"),  # ISO 2-letter
        region=data.get("region"),
        city=data.get("city"),
        timezone=data.get("timezone"),
    )
    await redis.setex(f"geo:{ip}", 86400, result.json())
    return result
```

### 10.4 Fallback se geo down

Geo è **non-critical**: log con `geo: null` se fallisce. Niente alert, niente fallback queue.

### 10.5 Costo

ipinfo.io free tier $0/mese fino a 50k requests/mese. Sufficiente.

---

## 11. Decisioni canoniche integrazioni (locked)

| ID | Decisione | Motivazione |
|---|---|---|
| **D-IN-001** | Ogni integrazione dietro Protocol astratto in `integrations/` | Sostituibilità, test isolati, no vendor lock-in. |
| **D-IN-002** | Idempotency-Key end-to-end propagato a tutti i provider | Retry safe, no duplicati. |
| **D-IN-003** | Timeout aggressivi per ogni operation (3-15s) | Fail fast, mai chiamate infinite. |
| **D-IN-004** | Retry 0x per writes critiche (booking creation), 3x per upsert idempotenti | Doppi appuntamenti peggio che falliti. |
| **D-IN-005** | Fallback queue Redis per ogni write critica | Mai perdere un lead (SR-005). |
| **D-IN-006** | Slack webhook per alert team su lead capture e fallback queue spike | Visibilità real-time. |
| **D-IN-007** | Booking platform default Cal.com (aperta a Calendly se Segmenta lo usa già) | Free tier, API moderna, self-host opzionale. |
| **D-IN-008** | CRM default HubSpot (aperta a Pipedrive se Segmenta lo usa già) | Standard agency space, automation integrata. |
| **D-IN-009** | Email transactional default Resend (aperta a SendGrid post-deliverability test M2) | Developer-friendly, free tier 100/giorno. |
| **D-IN-010** | DKIM + SPF + DMARC obbligatori prima di production go-live | Deliverability LATAM critica. |
| **D-IN-011** | Custom HubSpot properties con prefisso `mcp_*` per filtraggio analytics | Identificabilità lead da MCP vs altri canali. |
| **D-IN-012** | Webhook entrante validato via HMAC SHA-256 con secret in env | Sicurezza, no spoofing eventi. |
| **D-IN-013** | Cap mensile $20 USD per SEO data API (Tier 3) | Cost control. Degrade automatico se raggiunto. |
| **D-IN-014** | WhatsApp v1: link generation client-side, no API call | Semplicità, zero cost. API attiva v2. |
| **D-IN-015** | Geo IP via ipinfo.io free tier, cache 24h Redis | Sufficient v1, no rate limit issue. |
| **D-IN-016** | Tutte le integration calls loggate con stessa struttura JSON | Observability uniforme. |
| **D-IN-017** | Fallback queue flush manuale via script in v1 | Semplicità v1, automation v2. |
| **D-IN-018** | Email template multi-locale (es-LATAM, es-MX, es-ES, en-US) | Coerente con D-MP-016 mercati target e D-AU-021. |
| **D-IN-019** | Test deliverability obbligatorio M2: 100 email a domini MX/AR/CO/CL/PE | Validazione provider scelto prima di production. |
| **D-IN-020** | Niente secondary provider in v1 (solo Resend per email) | Semplicità; secondary in v2 se serve robustezza. |

---

## 12. Decisioni aperte integrazioni

| ID | Decisione | Bloccare entro | Owner |
|---|---|---|---|
| **DECISION-OPEN-IN-001** | Conferma provider booking effettivo (Cal.com vs Calendly se già in Segmenta) | M2 | Merari |
| **DECISION-OPEN-IN-002** | Conferma provider CRM (HubSpot vs Pipedrive vs altro) | M2 | Merari |
| **DECISION-OPEN-IN-003** | Resend vs SendGrid vs Mailgun: scelta definitiva post-deliverability test | M2 | Claudio |
| **DECISION-OPEN-IN-004** | DataForSEO vs SEMrush API vs Ahrefs API per `analizar_competencia` | M4 | Claudio |
| **DECISION-OPEN-IN-005** | Background worker per fallback queue: introdurre v1 o v2? | M3 | Claudio |
| **DECISION-OPEN-IN-006** | Sentry o equivalente per error tracking aggregato | M3 | Claudio |
| **DECISION-OPEN-IN-007** | WhatsApp Business API: quale provider e quando attivarla | M4 | Claudio + Merari |
| **DECISION-OPEN-IN-008** | Aggiungere secondary email provider per disaster recovery? | M5 | Claudio |
| **DECISION-OPEN-IN-009** | Geo IP: passare a MaxMind self-hosted se traffico cresce > 50k req/mese? | M5 | Claudio |
| **DECISION-OPEN-IN-010** | Cal.com Teams plan ($15/seat) o restare su Free? Dipende numero sales rep. | M3 | Merari |

---

## 13. Versioning di questo documento

| Versione | Data | Autore | Note |
|---|---|---|---|
| 1.0 | 2026-05-10 | Claude (proposta) + Claudio (revisione) | Prima stesura completa: booking (Cal.com), CRM (HubSpot), email (Resend), Slack webhook, WhatsApp link, SEO data API (DataForSEO), geo IP. Contratti API target, retry/fallback strategies, cost caps. |
| 1.1 | 2026-05-11 | Claude (harmony pass M0.3) + Claudio (review) | **HC-004**: aggiunti disclaimer "Adapter Pattern v1" all'inizio di sez. 4 (booking), 5 (CRM), 6 (email), 9 (SEO data). Chiarisce che provider "default candidato" sono dietro Pydantic Protocol — sostituire 1 file = swap completo, tool layer invariato. DECISION-OPEN-002/003/004/T3-002 restano aperte ma non bloccano coding M2 grazie ad adapter pattern. |
| 1.2 | 2026-05-11 | Claude + Claudio (chiusura M0.2.1) | **DECISION-OPEN-004 chiusa**: Resend confermato come email provider v1 (free tier 100/giorno = $0/mese, coerente con D-MP-002 v1.3 target costo $0). Sez. 6.1 riscritta con razionale e test deliverability obbligatorio in M2.3.10. DECISION-OPEN-002 (Cal.com vs Calendly) e -003 (HubSpot vs Pipedrive) restano aperte — gestite da adapter pattern, decisione differita a M2 con Merari. |

---

## Note per il changelog

Harmony pass M0.3 (2026-05-11): chiarita strategia adapter pattern. Chiusura M0.2.1 (2026-05-11): DECISION-OPEN-004 chiusa (Resend). Le 20 decisioni canoniche D-IN-001 → D-IN-020 restano locked.

---

**Fine 08-INTEGRATIONS.md v1.2.**
