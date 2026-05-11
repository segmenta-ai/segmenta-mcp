# 07 — AUTH & OAUTH

| Campo | Valore |
|---|---|
| **Progetto** | Segmenta MCP Server |
| **Versione documento** | 1.0 |
| **Data** | 2026-05-10 |
| **Status** | Draft (in revisione) |
| **File n.** | 07 di 12 numerati |
| **Documento padre** | `00-MASTER-PLAN.md` v1.3, `01-ARCHITECTURE.md` v1.2 |
| **File correlati** | `05-TOOLS-TIER2.md`, `06-TOOLS-TIER3.md`, `08-INTEGRATIONS.md`, `09-DEPLOYMENT.md` |

---

## 1. Scopo del documento

Questo file specifica **come autenticare gli utenti** che chiamano i tool Tier 2 e Tier 3 del server MCP Segmenta. Risponde a quattro domande:

1. *"Quale standard di autenticazione usiamo e perché?"* — sezioni 2, 3
2. *"Come si svolge il flow OAuth dynamic dal punto di vista del client e del server?"* — sezioni 4, 5, 6
3. *"Come gestiamo magic link, sessioni, token, refresh, rate limit?"* — sezioni 7, 8, 9, 10
4. *"Come ci difendiamo da attacchi (token replay, session hijack, brute force)?"* — sezione 11

Le specifiche dei tool che usano questo auth sono in `05-TOOLS-TIER2.md` e `06-TOOLS-TIER3.md`. Le decisioni canoniche sono in sezione 14.

> **Nota tecnica**: questo file presuppone familiarità con OAuth 2.0 (RFC 6749), Dynamic Client Registration (RFC 7591), Authorization Server Metadata (RFC 8414), e PKCE (RFC 7636). Riferimenti esplicitati dove necessario.

---

## 2. Principi guida

Cinque principi che governano tutte le decisioni auth:

### 2.1 Standard-first

Niente protocolli proprietari. Usiamo **OAuth 2.0** come definito dalla specifica MCP, che a sua volta segue gli RFC standard. Questo garantisce compatibilità nativa con Claude e ChatGPT senza configurazione extra lato utente.

### 2.2 Email-only, no password

L'unico fattore di autenticazione è **possesso di una casella email** (magic link). Niente password, niente OTP via SMS, niente social login. Motivazioni:
- **Riduce attrito** in conversazione AI: l'utente non vuole creare un nuovo account.
- **Niente rischio password leak**: se non c'è password, non c'è breach possibile.
- **Allineato con audience B2B**: utenti decision-maker hanno una sola email professionale.
- **Compliance LFPDPPP/GDPR**: email è dato minimo, no biometrici, no dati sensibili.

### 2.3 Short-lived tokens

Access token ha vita breve (7 giorni). Refresh token vita media (30 giorni). Niente token "eterni". Questo limita l'impatto di un eventuale leak.

### 2.4 Stateless validation, stateful revocation

JWT firmati permettono validazione **stateless** (no DB lookup ad ogni call). Ma manteniamo **una blocklist Redis** per revocation immediata di token compromessi. Trade-off: validation veloce + sicurezza in incidenti.

### 2.5 Defense in depth

L'auth non è solo la verifica del token. È un sistema a strati:
- TLS obbligatorio (intercettazione)
- HSTS abilitato (downgrade)
- Rate limit aggressivo (brute force)
- IP risk scoring (anomalie geo)
- Sessioni isolate per origin (cross-origin abuse)
- Logging strutturato (audit trail)

---

## 3. Standard di riferimento

### 3.1 RFC e specifiche applicate

| RFC / Spec | Cosa | Quando applicato |
|---|---|---|
| RFC 6749 — OAuth 2.0 | Authorization framework base | Sempre |
| RFC 7591 — Dynamic Client Registration | Permette ai client (Claude, ChatGPT) di registrarsi automaticamente senza configurazione manuale | Endpoint `/oauth/register` |
| RFC 8414 — Authorization Server Metadata | Discovery delle capacità del server via `/.well-known/oauth-authorization-server` | Discovery iniziale del client MCP |
| RFC 7636 — PKCE | Proof Key for Code Exchange, mitiga authorization code interception | Obbligatorio per *tutti* i flow |
| RFC 9068 — JWT Profile for OAuth | Standardizza struttura JWT come access token | Formato access token |
| RFC 6750 — Bearer Token Usage | Come passare il token nelle request | Header `Authorization: Bearer <token>` |
| RFC 7009 — Token Revocation | Endpoint per revocare token | `/oauth/revoke` |
| RFC 8252 — OAuth 2.0 for Native Apps | Best practice per native client (alcuni client MCP sono native) | Linee guida implementazione |
| MCP Authorization Spec (2025-06-18) | Specifica auth ufficiale del protocollo MCP | Conformità MCP |

### 3.2 Specifica MCP

L'autorizzazione MCP è definita nel documento [Model Context Protocol Authorization](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization). Punti chiave per Segmenta:

- Server MCP che richiedono auth devono **rispondere 401** con header `WWW-Authenticate: Bearer resource_metadata="..."` per indicare dove trovare la metadata OAuth.
- I client MCP (Claude.ai, ChatGPT, Cursor) implementano **automaticamente** il flow OAuth dynamic se il server lo annuncia correttamente. Niente configurazione manuale dell'utente.
- Lo scope deve essere descritto in modo human-readable, mostrato all'utente in fase di consent.

---

## 4. Architettura del flow OAuth

### 4.1 Visione d'insieme

```
                            ┌──────────────────────────────────┐
                            │  CLIENT MCP (Claude.ai, ...)     │
                            └──────────────────────────────────┘
                                          │
                                  Tier 2/3 tool call
                                          │
                            ┌─────────────▼────────────────────┐
                            │  401 + WWW-Authenticate          │
                            │  + resource_metadata URL         │
                            └─────────────┬────────────────────┘
                                          │
                              GET .well-known/oauth-...
                                          │
                            ┌─────────────▼────────────────────┐
                            │  Authorization Server Metadata   │
                            │  (RFC 8414)                      │
                            └─────────────┬────────────────────┘
                                          │
                            POST /oauth/register (RFC 7591)
                                          │
                            ┌─────────────▼────────────────────┐
                            │  client_id, client_secret        │
                            └─────────────┬────────────────────┘
                                          │
                                  redirect user a
                                  /oauth/authorize
                                          │
                            ┌─────────────▼────────────────────┐
                            │  Form: inserisci email           │
                            └─────────────┬────────────────────┘
                                          │
                                  invio magic link
                                          │
                            ┌─────────────▼────────────────────┐
                            │  user clicca magic link in email │
                            └─────────────┬────────────────────┘
                                          │
                            redirect ─▶ client con auth_code
                                          │
                            POST /oauth/token (con PKCE)
                                          │
                            ┌─────────────▼────────────────────┐
                            │  access_token (JWT) + refresh    │
                            └─────────────┬────────────────────┘
                                          │
                            retry tool call con
                            Authorization: Bearer
                                          │
                                  ✅ tool eseguito
```

### 4.2 Componenti del sistema auth

Tutti vivono in `src/segmenta_mcp/auth/`:

| Componente | File | Responsabilità |
|---|---|---|
| Discovery endpoint | `discovery.py` | Espone `/.well-known/oauth-authorization-server` (metadata) |
| Client registration | `registration.py` | Endpoint `/oauth/register` (RFC 7591) |
| Authorization endpoint | `authorize.py` | `/oauth/authorize` — UI form email + magic link send |
| Magic link handler | `magic_link.py` | Generazione, send via email, callback `/oauth/callback` |
| Token endpoint | `token.py` | `/oauth/token` — scambia auth_code per access+refresh, gestisce refresh |
| Revocation | `revocation.py` | `/oauth/revoke` (RFC 7009) |
| JWT handler | `jwt_handler.py` | Sign + verify, claims standard |
| Rate limiter | `rate_limit.py` | Sliding window Redis-backed |
| Middleware | `middleware.py` | Estrae Bearer, valida, popola `request.user` |
| Storage | `storage.py` | Wrapper Redis per state (codes, sessions, blocklist) |

### 4.3 Storage layout (Redis)

Convenzione: prefisso `oauth:` per tutto auth-related.

| Key pattern | Tipo Redis | TTL | Contenuto |
|---|---|---|---|
| `oauth:client:{client_id}` | hash | nessuno | Metadata client registrato (issued_at, redirect_uris, ...) |
| `oauth:auth_code:{code}` | hash | 10 min | code_challenge, redirect_uri, email, scope, used flag |
| `oauth:magic_link:{token}` | hash | 15 min | email, request_id, ip_origin, device_fingerprint |
| `oauth:session:{session_id}` | hash | 24h | email, jti_access, jti_refresh, created_at, last_seen |
| `oauth:refresh:{jti}` | string | 30 days | session_id (per lookup inverso) |
| `oauth:blocklist:{jti}` | string | until token natural expiry | "revoked" reason |
| `oauth:rate_limit:{key}` | sorted set | 1 min sliding | timestamps di chiamate |
| `oauth:ip_risk:{ip}` | hash | 24h | failure count, geo, reasons |

Tutti gli accessi a Redis vanno tramite `auth/storage.py` (wrapper tipizzato).

---

## 5. Discovery endpoint

### 5.1 Endpoint

`GET /.well-known/oauth-authorization-server`

### 5.2 Response (JSON)

```json
{
  "issuer": "https://mcp.segmentamarketing.com",
  "authorization_endpoint": "https://mcp.segmentamarketing.com/oauth/authorize",
  "token_endpoint": "https://mcp.segmentamarketing.com/oauth/token",
  "registration_endpoint": "https://mcp.segmentamarketing.com/oauth/register",
  "revocation_endpoint": "https://mcp.segmentamarketing.com/oauth/revoke",
  "jwks_uri": "https://mcp.segmentamarketing.com/.well-known/jwks.json",
  "response_types_supported": ["code"],
  "grant_types_supported": ["authorization_code", "refresh_token"],
  "code_challenge_methods_supported": ["S256"],
  "token_endpoint_auth_methods_supported": ["client_secret_post", "none"],
  "scopes_supported": [
    "tier2:lead_capture",
    "tier2:diagnostic",
    "tier2:booking",
    "tier3:competitive_intel",
    "tier3:research_share"
  ],
  "service_documentation": "https://segmentamarketing.com/mcp",
  "ui_locales_supported": ["es-MX", "es-LATAM", "es-ES", "en-US"]
}
```

### 5.3 Note

- `jwks_uri` è dinamico: il server espone la chiave pubblica per validazione asimmetrica RS256 (vedi DECISION-OPEN-T-002 risolta in M2).
- `scopes_supported` riflette i permessi granulari (vedi sez. 9.1).
- `ui_locales_supported` annuncia che la pagina `/oauth/authorize` supporta multi-locale.
- Il client MCP riconosce questo endpoint e configura tutto automaticamente.

---

## 6. Client registration (RFC 7591)

### 6.1 Endpoint

`POST /oauth/register`

### 6.2 Request body

```json
{
  "client_name": "Claude.ai MCP Client",
  "redirect_uris": [
    "https://claude.ai/api/mcp/auth/callback"
  ],
  "grant_types": ["authorization_code", "refresh_token"],
  "response_types": ["code"],
  "token_endpoint_auth_method": "client_secret_post",
  "application_type": "web"
}
```

### 6.3 Response

```json
{
  "client_id": "cl_01JXVZK8M7NQ3RT",
  "client_secret": "cs_8a3f...redacted",
  "client_id_issued_at": 1746893421,
  "redirect_uris": ["https://claude.ai/api/mcp/auth/callback"],
  "grant_types": ["authorization_code", "refresh_token"],
  "response_types": ["code"],
  "token_endpoint_auth_method": "client_secret_post",
  "registration_access_token": "rat_...",
  "registration_client_uri": "https://mcp.segmentamarketing.com/oauth/clients/cl_01JXVZK8M7NQ3RT"
}
```

### 6.4 Validation

- `redirect_uris`: lista hostname pre-approvati. **Per Segmenta v1 accettiamo solo `claude.ai`, `chatgpt.com`, `localhost` (dev)**. Hostname non in lista → 400 Bad Request.
- `client_name`: max 100 caratteri, sanitizzato.
- `application_type`: deve essere `web` o `native` (no `service`).
- Rate limit: 10 registrazioni/IP/giorno (vedi sez. 10).

### 6.5 Lifecycle del client

- `client_id`: ULID prefissato `cl_`. Pattern stabile.
- `client_secret`: 256 bit randomico, prefissato `cs_`. **Memorizzato hash bcrypt** in Redis (`oauth:client:{client_id}`).
- Validità: indefinita finché non revoked.
- Re-registration: l'utente che cancella il connector e lo aggiunge di nuovo crea un nuovo `client_id`. I client_id vecchi restano validi finché il refresh_token non scade.

### 6.6 Revoca client

DELETE `/oauth/clients/{client_id}` con `Authorization: Bearer {registration_access_token}`. Esegue:
1. Blocklist tutti i refresh token associati a quel client.
2. Marca client come `revoked` in Redis.
3. Le richieste future con quel client_id rispondono 401.

---

## 7. Authorization flow + Magic link

Questa è la sezione critica: cuore dell'auth Segmenta.

### 7.1 Authorization request

Il client MCP redirige l'utente a:

```
GET /oauth/authorize?
    response_type=code
    &client_id=cl_01JXVZK8M7NQ3RT
    &redirect_uri=https://claude.ai/api/mcp/auth/callback
    &scope=tier2:lead_capture+tier2:booking
    &state=randomized_csrf_token
    &code_challenge=SHA256(code_verifier)
    &code_challenge_method=S256
    &ui_locales=es-MX
```

### 7.2 Validation step (server)

Il server `/oauth/authorize`:
1. Valida `client_id` esiste e non revoked.
2. Valida `redirect_uri` esattamente match con quelli registrati.
3. Valida `response_type = "code"`.
4. Valida `code_challenge_method = "S256"` (PKCE obbligatorio, no "plain").
5. Valida `scope` contiene almeno uno scope valido.
6. Salva il context in Redis con TTL 15 min: `oauth:authz_request:{state}` → tutti i parametri.
7. Renderizza HTML form: "Inserisci la tua email per accedere a Segmenta MCP".

### 7.3 UI form (HTML statica server-side rendered)

Pagina semplice, brand Segmenta, locale-aware basato su `ui_locales`.

```html
<!DOCTYPE html>
<html lang="es-MX">
<head>
  <title>Accede a Segmenta MCP</title>
  <!-- ... -->
</head>
<body>
  <header>
    <img src="/static/segmenta-logo.svg" alt="Segmenta" />
  </header>
  <main>
    <h1>Accede al MCP de Segmenta Marketing</h1>
    <p>Para usar las herramientas avanzadas (auditoría, presupuesto, agenda),
    verifica tu email. Te enviaremos un enlace mágico.</p>
    <p><strong>Permisos solicitados:</strong></p>
    <ul>
      <li>Recibir reportes y propuestas en tu email</li>
      <li>Reservar slots de videocall en nuestro calendario</li>
    </ul>
    <form method="POST" action="/oauth/magic-link">
      <input type="hidden" name="state" value="..." />
      <input type="email" name="email" required
             placeholder="tu@email.com"
             autocomplete="email" />
      <button type="submit">Enviar enlace mágico</button>
    </form>
    <footer>
      <p><a href="https://segmentamarketing.com/mcp/privacy">Política de privacidad</a> ·
         <a href="https://segmentamarketing.com/mcp">¿Qué es esto?</a></p>
    </footer>
  </main>
</body>
</html>
```

Stile minimale, accessibility WCAG 2.1 AA, responsive mobile-first.

### 7.4 Magic link generation

Quando l'utente submitta l'email:

```python
async def send_magic_link(email: str, state: str, ip: str) -> None:
    # 1. Validazioni
    validate_email_format(email)
    check_ip_risk(ip)  # vedi sez. 11
    check_rate_limit(f"magic_link:{email}", limit=3, window_min=15)

    # 2. Genera magic link token (256-bit random)
    magic_token = secrets.token_urlsafe(32)  # 43 char

    # 3. Salva in Redis con TTL 15 min
    await redis.hset(f"oauth:magic_link:{magic_token}", mapping={
        "email": email,
        "state": state,
        "ip_origin": ip,
        "issued_at": now_iso(),
        "used": "false",
    })
    await redis.expire(f"oauth:magic_link:{magic_token}", 900)  # 15 min

    # 4. Costruisci URL
    callback_url = f"{ISSUER_URL}/oauth/callback?token={magic_token}"

    # 5. Invia email transactional
    await send_email(
        to=email,
        subject="Tu enlace de acceso a Segmenta MCP",
        template="magic_link.html",
        context={
            "callback_url": callback_url,
            "expires_minutes": 15,
            "ip_origin": ip,
            "geo": geo_from_ip(ip),
        }
    )

    # 6. Log evento
    log.info(
        "magic_link_sent",
        email_hash=hash_email(email),
        state=state,
        ip=ip,
    )
```

### 7.5 Email template (highlights)

```
Asunto: Tu enlace de acceso a Segmenta MCP

Hola,

Recibimos una solicitud para acceder a las herramientas de Segmenta MCP
desde Claude.ai (o ChatGPT).

🔗 Tu enlace de acceso:
{callback_url}

Este enlace:
- Expira en 15 minutos
- Solo puede usarse una vez
- Fue solicitado desde IP: {ip_origin} ({geo})

Si no solicitaste este acceso, ignora este email. No se concedió ningún
permiso sin que hagas click en el enlace.

¿Preguntas? Escribe a privacidad@segmentamarketing.com

— Equipo Segmenta
https://segmentamarketing.com/mcp
```

Email plain-text + HTML version. Sender: `noreply@mcp.segmentamarketing.com`. SPF/DKIM/DMARC configurati per dominio (vedi `09-DEPLOYMENT.md`).

### 7.6 Magic link callback

L'utente clicca il link → arriva a `/oauth/callback?token=...`:

```python
@router.get("/oauth/callback")
async def magic_link_callback(token: str, request: Request):
    # 1. Recupera dal Redis
    magic_data = await redis.hgetall(f"oauth:magic_link:{token}")
    if not magic_data:
        return error_page("Enlace expirado o inválido. Solicita uno nuevo.")

    if magic_data.get("used") == "true":
        return error_page("Este enlace ya fue usado. Solicita uno nuevo.")

    # 2. Marca come usato (idempotency)
    await redis.hset(f"oauth:magic_link:{token}", "used", "true")

    # 3. Recupera authorization request originale
    state = magic_data["state"]
    authz_req = await redis.hgetall(f"oauth:authz_request:{state}")
    if not authz_req:
        return error_page("Sesión expirada. Reintenta el flujo desde Claude.")

    # 4. Verifica IP consistency (security check soft)
    if request.client.host != magic_data["ip_origin"]:
        log.warning("magic_link_ip_mismatch",
                    email=hash_email(magic_data["email"]),
                    original_ip=magic_data["ip_origin"],
                    callback_ip=request.client.host)
        # Soft check: warn ma permetti (mobile + WiFi switch è normale)

    # 5. Genera authorization code (one-time-use, TTL 10 min)
    auth_code = secrets.token_urlsafe(32)
    await redis.hset(f"oauth:auth_code:{auth_code}", mapping={
        "client_id": authz_req["client_id"],
        "redirect_uri": authz_req["redirect_uri"],
        "scope": authz_req["scope"],
        "code_challenge": authz_req["code_challenge"],
        "email": magic_data["email"],
        "used": "false",
    })
    await redis.expire(f"oauth:auth_code:{auth_code}", 600)  # 10 min

    # 6. Redirect al client con auth_code
    callback_uri = f"{authz_req['redirect_uri']}?code={auth_code}&state={state}"
    return redirect(callback_uri)
```

A questo punto il client MCP riceve `code` e procede al token endpoint.

---

## 8. Token endpoint

### 8.1 Endpoint

`POST /oauth/token`

### 8.2 Grant: authorization_code

Request:
```
POST /oauth/token
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code
&code=auth_code_from_callback
&redirect_uri=https://claude.ai/api/mcp/auth/callback
&client_id=cl_01JXVZK8M7NQ3RT
&client_secret=cs_8a3f...
&code_verifier=original_verifier_for_PKCE
```

Server logic:
1. Estrae `code` da Redis (`oauth:auth_code:{code}`).
2. Validations:
   - Code esiste, non scaduto, `used=false`.
   - `client_id` + `client_secret` match (bcrypt verify).
   - `redirect_uri` match esatto.
   - `code_verifier` hashato in S256 == `code_challenge` (PKCE check).
3. Marca code come `used=true` (one-time-use).
4. Genera **access_token** (JWT) e **refresh_token**.
5. Salva session in Redis.
6. Risponde 200 OK con token.

Response:
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "Bearer",
  "expires_in": 604800,
  "refresh_token": "rt_01JXVZL2K8MNT...",
  "scope": "tier2:lead_capture tier2:booking"
}
```

### 8.3 Grant: refresh_token

Request:
```
POST /oauth/token

grant_type=refresh_token
&refresh_token=rt_01JXVZL2K8MNT...
&client_id=cl_...
&client_secret=cs_...
```

Server logic:
1. Lookup `oauth:refresh:{rt}` → ottiene `session_id`.
2. Validations:
   - Refresh non in blocklist.
   - Client match.
   - Session non scaduta.
3. Genera nuovo access_token (JWT, 7 giorni).
4. **Refresh token rotation**: genera anche un nuovo refresh_token, blocklist quello vecchio.
5. Update session in Redis con nuovi `jti`.
6. Risponde con nuovi token.

**Razionale rotation**: se un attaccante intercetta un refresh, può usarlo una sola volta. Se l'utente legittimo lo usa dopo, scopriamo il theft (refresh non più valido) e possiamo invalidare l'intera sessione. Pattern raccomandato da OAuth Security Topics (RFC 9700).

### 8.4 Error response

```json
{
  "error": "invalid_grant",
  "error_description": "Authorization code expired or already used."
}
```

Codici errore conformi a RFC 6749:
- `invalid_request`: parametri mancanti o malformati
- `invalid_client`: client_id/secret invalidi
- `invalid_grant`: code/refresh invalido o scaduto
- `unsupported_grant_type`: grant non supportato
- `invalid_scope`: scope richiesto non valido

---

## 9. Token format e claims

### 9.1 Access token (JWT, RS256)

```json
{
  "iss": "https://mcp.segmentamarketing.com",
  "sub": "user_email_hash_or_ulid",
  "aud": "mcp.segmentamarketing.com",
  "exp": 1747498221,
  "iat": 1746893421,
  "jti": "jt_01JXVZL5HQNT...",
  "scope": "tier2:lead_capture tier2:booking",
  "client_id": "cl_01JXVZK8M7NQ3RT",
  "email": "user@example.com",
  "session_id": "ss_01JXVZL2K8MNT..."
}
```

Claims spiegati:
- `iss`: issuer, sempre uguale al dominio del server.
- `sub`: subject, hash dell'email o ULID stabile dell'utente.
- `aud`: audience, sempre il server stesso.
- `exp`: expiration timestamp Unix.
- `iat`: issued at.
- `jti`: JWT ID, univoco per token, usato per blocklist.
- `scope`: permessi granulari (vedi sez. 9.4).
- `client_id`: quale client MCP ha richiesto il token.
- `email`: email plaintext (necessaria per il tool dispatch — alternativa più privacy: encryption del campo).
- `session_id`: per correlare con session Redis.

**Decisione su `email` plaintext nel JWT**: la specifica MCP richiede che il server identifichi l'utente per CRM e booking. Memorizzarlo nel JWT evita lookup Redis ad ogni call. Il JWT è criptato in transito (TLS) e firmato (RS256) — non è leggibile da terzi. Trade-off accettato in v1.

### 9.2 Firma RS256 (asymmetric)

DECISION-OPEN-T-002 risolta: usiamo RS256, non HS256.

Motivazioni:
- Repo pubblico (D-MP-008): chiave pubblica può essere esposta safely via JWKS, evitiamo di leak il secret.
- JWKS endpoint permette key rotation senza downtime.
- Standard industriale per produzione.

Configurazione:
- Key pair generato all'avvio del server o pre-provisioned in Fly.io env.
- Private key in Fly.io env var `JWT_PRIVATE_KEY` (PEM format).
- Public key esposta via `/.well-known/jwks.json`.
- Rotation key ogni 90 giorni (manuale in v1, automatica in v2).

### 9.3 Refresh token

Format: opaque random string prefixed `rt_`. **Non è JWT**. Solo un identificatore.

Lookup in Redis: `oauth:refresh:{rt}` → `session_id`.

Lunghezza: 256 bit base64url-encoded (43 caratteri visibili).

### 9.4 Scope granulari

Niente "scope: full_access". Granularità per tier e funzione:

| Scope | Cosa permette | Tool che lo richiedono |
|---|---|---|
| `tier2:lead_capture` | Tool che generano lead in CRM | `calcular_presupuesto`, `solicitar_propuesta_personalizada` |
| `tier2:diagnostic` | Tool che analizzano siti | `diagnostico_seo_express` |
| `tier2:booking` | Tool che prenotano slot | `agendar_auditoria_gratuita`, `consultar_disponibilidad` |
| `tier3:competitive_intel` | Tool competitive intelligence | `analizar_competencia` |
| `tier3:research_share` | Tool che pubblicano research | `share_research` |

Il client richiede solo gli scope necessari per il tool che sta per chiamare. Questo limita il blast radius di un eventuale token leak.

### 9.5 Verifica del token nel middleware

```python
# auth/middleware.py (estratto)

async def verify_jwt(token: str) -> TokenClaims:
    # 1. Decode header per ottenere kid (key ID)
    header = jwt.get_unverified_header(token)
    kid = header.get("kid")

    # 2. Fetch JWKS (cached 5 min)
    jwks = await get_jwks_cached()
    key = next((k for k in jwks["keys"] if k["kid"] == kid), None)
    if not key:
        raise InvalidTokenError("Unknown key ID")

    # 3. Verifica firma + claims standard
    try:
        claims = jwt.decode(
            token,
            key=key,
            algorithms=["RS256"],
            audience="mcp.segmentamarketing.com",
            issuer="https://mcp.segmentamarketing.com",
        )
    except jwt.ExpiredSignatureError:
        raise InvalidTokenError("Token expired")
    except jwt.InvalidTokenError as e:
        raise InvalidTokenError(f"Invalid token: {e}")

    # 4. Check blocklist
    if await redis.exists(f"oauth:blocklist:{claims['jti']}"):
        raise InvalidTokenError("Token revoked")

    # 5. Check session active
    session_id = claims["session_id"]
    if not await redis.exists(f"oauth:session:{session_id}"):
        raise InvalidTokenError("Session expired")

    # 6. Update last_seen
    await redis.hset(f"oauth:session:{session_id}", "last_seen", now_iso())

    return TokenClaims(**claims)
```

Latency budget: < 5ms p95 (cache JWKS + Redis exists).

---

## 10. Rate limiting

### 10.1 Strategia

Sliding window log algorithm su Redis sorted set. Per ogni `(key, window)`:
1. ZADD timestamp_now timestamp_now
2. ZREMRANGEBYSCORE 0 (now - window)
3. ZCARD → count attuale
4. Compare con limit.

Atomicità via Lua script per evitare race conditions.

### 10.2 Limiti per endpoint

| Endpoint / Operation | Limite | Window | Key |
|---|---|---|---|
| `/oauth/register` | 10 | 24h | per IP |
| `/oauth/authorize` | 30 | 1h | per IP |
| `/oauth/magic-link` POST | 3 | 15 min | per email |
| `/oauth/magic-link` POST | 30 | 1h | per IP |
| `/oauth/callback` (clic magic link) | 5 | 5 min | per token (anti-replay) |
| `/oauth/token` | 60 | 1h | per client_id |
| Tool Tier 1 | 60 | 1 min | per IP |
| Tool Tier 2 | 10 | 1 min | per user_email |
| Tool Tier 3 | 10 | 1 min | per user_email |
| Globale (DOS protection) | 1000 | 1 min | per IP |

### 10.3 Response a rate limit hit

```
HTTP/1.1 429 Too Many Requests
Retry-After: 47
Content-Type: application/json

{
  "error": "rate_limit_exceeded",
  "error_description": "Demasiadas solicitudes. Reintenta en 47 segundos.",
  "retry_after_seconds": 47
}
```

### 10.4 Soft block escalation

Se un IP triggera rate limit > 10 volte in 1h:
- Soft block per 24h (tutti gli endpoint rispondono 429 anche sotto limite normale).
- Alert email a Claudio.
- Log strutturato per analisi.

---

## 11. Threat model + difese

Threat model dettagliato per il layer auth. Coerente con `01-ARCHITECTURE.md` sez. 8.1 ma più granulare.

### 11.1 Tabella minacce → contromisure

| Minaccia | Vector | Probabilità | Impatto | Contromisura |
|---|---|---|---|---|
| Magic link interception | Email account compromesso | Bassa | Alto | TTL 15 min, one-time-use, IP consistency check soft |
| Authorization code interception | Browser MITM, history leak | Bassa | Alto | PKCE obbligatorio (S256), TTL 10 min, one-time-use |
| Token replay | Token leak via log/screenshot | Media | Alto | Short TTL (7gg), blocklist su revocation, session revoke se device anomalo |
| Refresh token theft | Storage compromise client | Bassa | Alto | Rotation obbligatoria, blocklist su rotation gap |
| Credential stuffing | Email validate per spam | Media | Basso | Rate limit 3/15min per email, captcha dopo 5 fails (v2) |
| OAuth client impersonation | redirect_uri permissive | Bassa | Alto | Allowlist hostname stretto, exact match |
| CSRF attack | Browser cross-site form | Bassa | Medio | `state` parameter obbligatorio, validato server-side |
| Token forgery | JWT signing key leak | Bassissima | Critico | Key in env, rotation 90gg, JWKS pubblico per validation |
| Session fixation | Pre-set session ID | Bassa | Medio | Session ID generato server-side, mai accettato dal client |
| Phishing → magic link | Fake email "click here" | Media | Alto | Email contiene IP origine + geo, user può rifiutare se sospetto |
| Email enumeration | Probe per scoprire utenti registrati | Media | Basso | Response sempre uguale ("se l'email esiste, riceverà link") |
| Brute force code | Probing auth_code random | Bassa | Alto | Code 256-bit random, TTL 10min, rate limit |

### 11.2 Email enumeration prevention

L'endpoint `/oauth/magic-link` POST risponde **sempre** con la stessa response, indipendentemente dal fatto che l'email esista già nel sistema:

```json
{
  "ok": true,
  "message": "Si la dirección es válida, recibirás un email con el enlace de acceso en breve."
}
```

Niente dare hint che l'email è "già registrata" o "non esiste".

### 11.3 IP risk scoring (basico, v1)

Funzione `check_ip_risk(ip)` che valuta:
- Geo IP via free service (ipinfo.io free tier o equivalente).
- Se geo cambiata drasticamente in < 1h dalla stessa session: warning log.
- Se IP in lista pubblica di proxy/VPN noti: warning log (in v1 non blocca, solo logga).
- Se IP ha causato > 10 fail negli ultimi 7gg: soft block.

In v2: integrazione con servizi più sofisticati (Stytch, Auth0 risk engine).

### 11.4 Audit log

Ogni evento auth genera log strutturato con campi minimi:

```json
{
  "timestamp": "2026-05-10T15:42:18.453Z",
  "level": "INFO",
  "event": "magic_link_sent" | "token_issued" | "token_revoked" | "auth_failed" | ...,
  "request_id": "req_01...",
  "client_id": "cl_01...",
  "user_email_hash": "sha256:abc123...",
  "ip": "203.0.113.42",
  "geo_country": "MX",
  "user_agent_brief": "claude.ai/1.5",
  "outcome": "success" | "failure",
  "failure_reason": null | "rate_limited" | "token_expired" | ...
}
```

Email loggata sempre come hash SHA-256, mai plaintext. Coerente con D-T3-009.

Audit log retention: 90 giorni (compliance LFPDPPP/GDPR).

---

## 12. Privacy & compliance

### 12.1 Dati raccolti dall'auth

| Dato | Storage | Retention | Base legale (LFPDPPP/GDPR) |
|---|---|---|---|
| Email plaintext | JWT (in-flight) + Redis session | 30gg dopo last_seen | Consenso esplicito (magic link click = consent) |
| Email hash (SHA-256) | Audit log | 90gg | Legitimate interest (security audit) |
| IP address | Audit log + Redis ip_risk | 24h (ip_risk) / 90gg (audit) | Legitimate interest (security) |
| User agent | Audit log | 90gg | Legitimate interest (security) |
| Tool calls history per session | Log | 90gg | Legitimate interest (analytics) |
| Geo derivata da IP | Audit log | 90gg | Legitimate interest (security) |

### 12.2 User rights

Cf. LFPDPPP art. 16 e GDPR art. 15-22.

Endpoint dedicati (M2):
- `GET /privacy/data-request` con OAuth → restituisce JSON con tutti i dati associati alla email autenticata.
- `POST /privacy/data-deletion` con OAuth → cancella session, blocklist token, anonymize log.

In v1: tutto manuale via email a `privacidad@segmentamarketing.com`. SLA risposta: 7 giorni.

### 12.3 Cross-border transfer

Server hostato Fly.io US. Utenti EU che usano i tool gated → loro dati transitano US.

Coperto da:
- Privacy policy MCP esplicita su questo punto.
- Standard Contractual Clauses (SCC) con Fly.io (auto-applicate dal loro Terms).
- Consenso esplicito utente al primo magic link click (informativa pre-form).

### 12.4 Notifica violazione

In caso di data breach (token leak, Redis compromise, ecc.):
- Notifica INAI entro 72h (LFPDPPP).
- Notifica utenti impattati entro 72h.
- Public incident report su `https://segmentamarketing.com/mcp/security`.

Procedura interna: vedi SR-009 di `00-MASTER-PLAN.md` (freeze immediato + sprint privacy).

---

## 13. Esempio end-to-end

Per fissare le idee, un flusso completo dell'auth dal punto di vista di tutti gli attori.

**Scenario**: utente in CDMX su Claude.ai chiede al modello "agéndame una auditoría con Segmenta".

```
T+0s:   Utente: "Agéndame una auditoría con Segmenta"
        Claude.ai: pensa → deve chiamare agendar_auditoria_gratuita

T+0.1s: Claude.ai → POST mcp.segmentamarketing.com/mcp/tools/call
        Body: { "name": "agendar_auditoria_gratuita", "args": {...} }
        Headers: NO Authorization

T+0.2s: Server → 401 Unauthorized
        Headers: WWW-Authenticate: Bearer resource_metadata="https://mcp.segmentamarketing.com/.well-known/oauth-authorization-server"

T+0.3s: Claude.ai → GET .well-known/oauth-authorization-server
        Server → JSON metadata (sez. 5.2)

T+0.4s: Claude.ai → POST /oauth/register
        Body: { client_name: "Claude.ai MCP Client", redirect_uris: [...] }
        Server → { client_id: cl_01..., client_secret: cs_... }

T+0.5s: Claude.ai genera code_verifier (random) + code_challenge = SHA256(verifier)
        Apre browser tab al user con URL:
        /oauth/authorize?client_id=cl_01...&code_challenge=...&...

T+1s:   Utente vede form HTML di Segmenta:
        "Inserisci la tua email per accedere..."
        Inserisce: doctor@miclinica.mx
        Submit.

T+1.1s: Server → POST /oauth/magic-link
        Validazioni: format email OK, IP non in soft block, rate limit OK.
        Genera magic_token = abc123...
        Salva in Redis con TTL 15 min.
        Invia email a doctor@miclinica.mx con link
        https://mcp.segmentamarketing.com/oauth/callback?token=abc123...

T+1.2s: Server → response: "Si la dirección es válida, recibirás email."

T+30s:  Utente apre email su mobile, vede:
        "Tu enlace de acceso a Segmenta MCP — IP origen: 187.250.x.x (CDMX)"
        Click sul link.

T+31s:  Browser mobile → GET /oauth/callback?token=abc123...
        Server:
        - Lookup magic_link in Redis: trovato, used=false.
        - Marca used=true.
        - Recupera authorization request originale via state.
        - IP check: callback IP = 187.250.x.y (mobile), original = 187.250.x.x (desktop).
          Stessa /24, accettato.
        - Genera auth_code = xyz789...
        - Salva in Redis TTL 10 min.
        - Redirect a https://claude.ai/api/mcp/auth/callback?code=xyz789&state=...

T+31.5s: Claude.ai riceve auth_code.
         POST /oauth/token con grant=authorization_code, code=xyz789,
         code_verifier=originale, client_id, client_secret.
         Server:
         - Lookup auth_code: trovato, used=false.
         - Marca used=true.
         - Verifica PKCE: SHA256(code_verifier) == code_challenge ✓
         - Verifica client credentials ✓
         - Verifica redirect_uri match ✓
         - Genera access_token (JWT 7gg) + refresh_token (rt_01...).
         - Crea session in Redis con jti, email, etc.
         - Response: { access_token, refresh_token, expires_in, scope }

T+32s:   Claude.ai retry POST /mcp/tools/call con
         Authorization: Bearer eyJhbGc... e args originali.

T+32.5s: Server middleware:
         - Estrae Bearer token.
         - JWKS fetch (cached) → public key.
         - Verifica firma RS256 ✓
         - Verifica claims (iss, aud, exp, scope contiene tier2:booking) ✓
         - Verifica jti non in blocklist ✓
         - Verifica session attiva in Redis ✓
         - Update last_seen.
         - Popola request.user con email = doctor@miclinica.mx.

T+32.6s: Tool agendar_auditoria_gratuita esegue normalmente:
         - Idempotency check OK.
         - Chiama Cal.com API.
         - Webhook CRM con email = doctor@miclinica.mx.
         - Slack alert al team.
         - Response.

T+33s:   Claude.ai compone risposta naturale all'utente con conferma slot.

# In parallelo:
T+33.1s: Audit log:
         - magic_link_sent, magic_link_callback_success, token_issued, tool_call_success.
         Tutti correlati via request_id e session_id.
```

Total elapsed: ~33 secondi dal momento dell'utterance utente alla conferma slot. La maggior parte del tempo (29s) è il delay umano del lettura email + click.

Il flow è 100% automatico per l'utente: lui inserisce email una volta, clicca link una volta, fatto. Tutto il resto del meccanismo OAuth è invisibile.

---

## 14. Decisioni canoniche auth (locked)

| ID | Decisione | Motivazione |
|---|---|---|
| **D-AU-001** | OAuth 2.0 con Dynamic Client Registration (RFC 7591) | Standard MCP, supportato nativamente da Claude/ChatGPT, no config manuale utente. |
| **D-AU-002** | Magic link email come unico fattore (no password, no SMS, no social) | Riduce attrito B2B, no password leak risk, allineato LFPDPPP/GDPR data minimization. |
| **D-AU-003** | PKCE obbligatorio (S256, no `plain`) per ogni authorization code flow | Mitigazione code interception. Standard 2026 anche per server-side clients. |
| **D-AU-004** | JWT RS256 con JWKS pubblico per access token | Repo pubblico (D-MP-008), key rotation possibile, no shared secret. |
| **D-AU-005** | Access token TTL 7 giorni | Bilancia UX (no re-auth frequente) e sicurezza (blast radius limitato). |
| **D-AU-006** | Refresh token TTL 30 giorni con rotation obbligatoria | Pattern raccomandato OAuth Security Topics RFC 9700. Detection di theft. |
| **D-AU-007** | Magic link TTL 15 min, one-time-use, hash IP origine | Mitigazione interception, replay. |
| **D-AU-008** | Authorization code TTL 10 min, one-time-use | Standard OAuth. |
| **D-AU-009** | Allowlist hostname per redirect_uri: claude.ai, chatgpt.com, localhost | Mitigazione client impersonation. Espansione gestita esplicitamente. |
| **D-AU-010** | Scope granulari per tier+funzione (no "full_access") | Principio least privilege, blast radius minimo se token leak. |
| **D-AU-011** | Email enumeration prevention: response uniforme | Privacy + sicurezza. |
| **D-AU-012** | Audit log con email come hash SHA-256, mai plaintext | Coerente con D-T3-009 e LFPDPPP minimization. |
| **D-AU-013** | Token revocation via blocklist Redis (stateful), validation stateless via JWT | Bilanciamento performance + sicurezza in incident response. |
| **D-AU-014** | Rate limit aggressivo: 3 magic link/email/15min, 30/IP/h, 60 token/client/h | Mitigazione brute force, credential stuffing. |
| **D-AU-015** | IP risk scoring basico (geo, proxy, history fail) — log only in v1, blocking in v2 | Detection precoce senza falsi positivi su mobile + WiFi switch. |
| **D-AU-016** | Audit log retention 90gg, Redis session 24h dopo last_seen | LFPDPPP compliance, evita dati ridondanti. |
| **D-AU-017** | Rotation chiave JWT signing ogni 90gg (manuale v1, automatica v2) | Standard sicurezza, riduce impatto compromise teoretico. |
| **D-AU-018** | Endpoint `/privacy/data-request` e `/privacy/data-deletion` (M2). In v1: email manuale | LFPDPPP/GDPR right of access e right to erasure. |
| **D-AU-019** | Cross-border transfer EU → US coperto da SCC + privacy policy esplicita | GDPR art. 46. |
| **D-AU-020** | Email plaintext nel JWT (criptato in transit via TLS) per evitare lookup Redis ad ogni call | Performance vs minimization tradeoff accettato in v1. |
| **D-AU-021** | UI form locale-aware (es-MX/es-LATAM/es-ES/en-US) | Coerente con D-MP-016 mercati target. |
| **D-AU-022** | Soft block 24h dopo > 10 rate limit hit/h da stesso IP | Auto-mitigation senza intervento umano. |
| **D-AU-023** | Email IP origine + geo nel template magic link | Anti-phishing: utente vede da dove la richiesta è partita. |
| **D-AU-024** | Notifica INAI + utenti entro 72h in caso di data breach | LFPDPPP art. 20 e SR-009 compliance. |
| **D-AU-025** | OAuth metadata UI in `ui_locales_supported` per multi-locale awareness | Client MCP avanzati possono passare lingua preferita utente. |

---

## 15. Decisioni aperte auth

| ID | Decisione | Bloccare entro | Owner |
|---|---|---|---|
| **DECISION-OPEN-AU-001** | Email transactional provider per magic link: Resend / SendGrid / Mailgun (deliverability LATAM/MX) | M2 | Claudio |
| **DECISION-OPEN-AU-002** | IP risk scoring v2: integrazione Stytch / Auth0 risk engine? Cost vs valore? | M5 | Claudio |
| **DECISION-OPEN-AU-003** | Captcha (hCaptcha) dopo X failed magic link da stesso IP? Cost cognitive vs security | M3 | Claudio |
| **DECISION-OPEN-AU-004** | Endpoint `/privacy/data-request` automatizzato via OAuth o manual review? | M2 | Merari + Claudio |
| **DECISION-OPEN-AU-005** | Encryption del campo `email` nel JWT (al posto di plaintext) per privacy stricter? | M3 | Claudio |
| **DECISION-OPEN-AU-006** | Implementare DPoP (Demonstrating Proof-of-Possession) per token? Sicurezza++ ma complexity++ | v2 | Claudio |
| **DECISION-OPEN-AU-007** | Sessione "remember me" (refresh TTL 90gg invece 30gg) opt-in via UI form? | M4 | Claudio |
| **DECISION-OPEN-AU-008** | Provider geo IP: ipinfo.io free (50k/mese) vs ip-api.com vs MaxMind | M2 | Claudio |
| **DECISION-OPEN-AU-009** | Auto-rotation chiave JWT (cron job) o manuale con alert? | M5 | Claudio |
| **DECISION-OPEN-AU-010** | Multi-device session management: l'utente vede device attivi e revoca? | v2 | Claudio |

---

## 16. Versioning di questo documento

| Versione | Data | Autore | Note |
|---|---|---|---|
| 1.0 | 2026-05-10 | Claude (proposta) + Claudio (revisione) | Prima stesura completa: OAuth 2.0 dynamic, magic link email, JWT RS256, scope granulari, rate limit, threat model, privacy compliance LFPDPPP/GDPR. |

---

## Note per il changelog

*(Sezione vuota in v1.0 — verrà popolata se emergono incongruenze nei file successivi che richiedono retrofitting in questo AUTH-OAUTH.)*

---

**Fine 07-AUTH-OAUTH.md v1.0.**
