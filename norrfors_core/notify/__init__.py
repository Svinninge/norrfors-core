# File version: v0.01
# Description: Public API for outbound notifications — Telegram and SMTP e-mail
# Author: Per Norrfors
# Created: 2026-09-20
# Modified: 2026-09-20 - Initial implementation (Claude)
"""Outbound notifications: Telegram and SMTP e-mail.

Replaces three near-identical implementations (finance/notify.py,
dubblaren/src/notify.py, ai-trading/src/notifications/telegram.py).

    from norrfors_core.notify import NotifyConfig, notify

    config = NotifyConfig.from_env()
    notify("Nightly job finished.", config=config, subject="Finance: nightly run")

Nothing here raises: a notification problem must never crash the job that sent it.
Every sender returns a bool and logs why it returned False.
"""

from __future__ import annotations

import logging

from .config import ENV_KEYS, NotifyConfig
from .format import html_email_wrapper, md_to_html, split_message
from . import mail
from .mail import recipients, send_email
from .telegram import send_telegram

log = logging.getLogger(__name__)

__all__ = [
    "ENV_KEYS",
    "NotifyConfig",
    "html_email_wrapper",
    "mail",
    "md_to_html",
    "notify",
    "recipients",
    "send_email",
    "send_telegram",
    "split_message",
]


def notify(
    text: str,
    *,
    config: NotifyConfig,
    subject: str | None = None,
    html: str | None = None,
    to: str | list[str] | tuple[str, ...] | None = None,
    chat_ids: str | list[str] | tuple[str, ...] | None = None,
    telegram: bool = True,
    email: bool = True,
) -> bool:
    """Send the same message over every channel that is configured.

    Returns True when at least one channel delivered it. That is the useful answer
    for a nightly job: the operator was reached. A channel that is simply not
    configured is not a failure — it is a choice the project made.
    """
    delivered = False
    if telegram and config.telegram_configured():
        delivered |= send_telegram(text, config=config, chat_ids=chat_ids)
    if email and config.smtp_configured():
        delivered |= send_email(
            subject or text.strip().splitlines()[0][:120] or "Notification",
            text, config=config, html=html, to=to)
    if not delivered:
        log.warning("notify() reached nobody — no channel configured or all failed")
    return delivered
