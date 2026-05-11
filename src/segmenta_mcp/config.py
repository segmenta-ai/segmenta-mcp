"""Pydantic Settings per env vars (D-C-009, D-DE-012).

Caricamento e validazione di tutte le env vars al boot del server.
Fail fast: se manca una var required, il server non parte.
"""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurazione globale del server, caricata da env vars o `.env`."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # === Server core ===
    env: str = Field(default="local", pattern="^(local|staging|production)$")
    log_level: str = Field(default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR)$")
    port: int = Field(default=8000, ge=1, le=65535)
    host: str = Field(default="0.0.0.0")
    issuer_url: str = Field(default="http://localhost:8000")

    # === OAuth / JWT (M2+) ===
    jwt_private_key: str = Field(default="")
    jwt_public_key: str = Field(default="")
    jwt_key_id: str = Field(default="key-dev")
    oauth_allowed_redirect_hosts: str = Field(default="claude.ai,chatgpt.com,cursor.so")

    # === Redis (M1.5+) ===
    redis_url: str = Field(default="redis://localhost:6379")
    redis_tls: bool = Field(default=False)

    # === Email (M2+) ===
    resend_api_key: str = Field(default="")
    resend_from_email: str = Field(default="hola@mcp.segmentamarketing.com")

    # === CRM (M2+) ===
    hubspot_private_token: str = Field(default="")

    # === Booking (M2+) ===
    calcom_api_key: str = Field(default="")
    calcom_username: str = Field(default="segmenta")
    calcom_webhook_secret: str = Field(default="")

    # === Slack ===
    slack_webhook_url_leads_mcp: str = Field(default="")
    slack_webhook_url_alerts_mcp: str = Field(default="")
    slack_webhook_url_deploys: str = Field(default="")

    # === Geo IP ===
    ipinfo_token: str = Field(default="")

    # === SEO data (M4+) ===
    dataforseo_login: str = Field(default="")
    dataforseo_password: str = Field(default="")


settings = Settings()
