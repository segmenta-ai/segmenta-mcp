"""Layer 5b — Integrations: chiamate API esterne, retry, fallback queue.

Provider in v1 (`Docs/blueprint/08-INTEGRATIONS.md` v1.3):
- Booking: Cal.com (DECISION-OPEN-002, adapter pattern HC-004)
- CRM: HubSpot (DECISION-OPEN-003, adapter pattern)
- Email: Resend (chiusa M0.2.1)
- Slack: webhook leads + alerts + deploys
- WhatsApp: link generation client-side (no API in v1)
- Geo IP: ipinfo.io free tier
- SEO data: DataForSEO (Tier 3 M4+)

Ogni integrazione è dietro un Pydantic Protocol per facilitare swap.
"""
