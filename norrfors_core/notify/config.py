# File version: v0.01
# Description: Credentials and toggles for outbound notifications, read from env
# Author: Per Norrfors
# Created: 2026-09-20
# Modified: 2026-09-20 - Initial implementation (Claude)
"""Configuration for :mod:`norrfors_core.notify`.

Read once with :meth:`NotifyConfig.from_env` and passed explicitly to the senders,
so a caller can hold several configs (prod vs test bot) without touching globals.

Recipients come from the config or from the call site. Resolving *who* should be
mailed from a database (``family_users`` in finance, per-user addresses in
dubblaren) stays in those projects — that is their data model, not a shared one.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Callable, Mapping

#: Environment variable names. Deliberately the ones the existing projects already
#: use, so adopting this package needs no change to secrets.env.
ENV_KEYS = (
    "SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASSWORD", "SMTP_SSL",
    "EMAIL_FROM", "EMAIL_TO",
    "TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID",
    "NOTIFY_ENABLED",
)


def _split(value: str | None) -> tuple[str, ...]:
    """Comma-separated string to a clean tuple. Blank entries drop out."""
    if not value:
        return ()
    return tuple(part.strip() for part in value.split(",") if part.strip())


@dataclass(frozen=True)
class NotifyConfig:
    """Everything the senders need. Missing values mean "not configured", which
    makes the matching sender return ``False`` instead of raising."""

    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_ssl: bool = False          # implicit TLS (port 465) vs STARTTLS
    email_from: str = ""
    email_to: tuple[str, ...] = ()
    telegram_bot_token: str = ""
    telegram_chat_ids: tuple[str, ...] = ()
    enabled: bool = True            # master switch, see sending_enabled()
    disabled_reason: str = ""

    @classmethod
    def from_env(
        cls,
        getter: Callable[[str], str | None] | Mapping[str, str] | None = None,
        *,
        enabled: bool = True,
        disabled_reason: str = "",
    ) -> "NotifyConfig":
        """Build a config from the environment.

        ``getter`` lets a project route the lookup through its own secret store —
        dubblaren reads ``secrets_store.get`` so a value an admin just saved in the
        UI applies without a restart. An empty string counts as unset, so a blank
        line in secrets.env does not read as configured.
        """
        if getter is None:
            get = os.environ.get
        elif isinstance(getter, Mapping):
            get = getter.get
        else:
            get = getter

        def value(key: str, default: str = "") -> str:
            try:
                raw = get(key)
            except Exception:       # noqa: BLE001 — a broken store must not crash startup
                raw = None
            if not raw:
                raw = os.environ.get(key)
            return (raw or default).strip()

        try:
            port = int(value("SMTP_PORT", "587") or "587")
        except ValueError:
            port = 587

        env_enabled = value("NOTIFY_ENABLED", "1")
        return cls(
            smtp_host=value("SMTP_HOST"),
            smtp_port=port,
            smtp_user=value("SMTP_USER"),
            smtp_password=value("SMTP_PASSWORD"),
            smtp_ssl=value("SMTP_SSL", "0") in ("1", "true", "True", "yes"),
            email_from=value("EMAIL_FROM"),
            email_to=_split(value("EMAIL_TO")),
            telegram_bot_token=value("TELEGRAM_BOT_TOKEN"),
            telegram_chat_ids=_split(value("TELEGRAM_CHAT_ID")),
            enabled=enabled and env_enabled not in ("0", "false", "False", "no"),
            disabled_reason=disabled_reason,
        )

    # -- readiness -----------------------------------------------------------
    def smtp_configured(self) -> bool:
        """True when the transport can send at all (server + sender). Says nothing
        about who the recipient is — that question belongs to the caller."""
        return bool(self.smtp_host and self.email_from)

    def telegram_configured(self) -> bool:
        return bool(self.telegram_bot_token)

    def sending_enabled(self) -> tuple[bool, str]:
        """``(may send, reason if not)``.

        Projects that share credentials between dev and prod should pass
        ``enabled=False`` here in dev — without that guard every local test run
        mails live alerts to the whole family (dubblaren, 2026-08-08).
        """
        if self.enabled:
            return True, ""
        return False, self.disabled_reason or "Notifications disabled by configuration."
