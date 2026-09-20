# File version: v0.02
# Description: SMTP e-mail sender with plain/HTML alternatives and embedded images
# Author: Per Norrfors
# Created: 2026-09-20
# Modified: 2026-09-20 - body=None sends an HTML-only message (Claude)
"""Send one e-mail over SMTP.

Stdlib ``smtplib`` on purpose: it is the pattern finance, dubblaren and ai-trading
already share, and it keeps this package dependency-free.

Never raises. A failed notification is logged and reported as ``False`` — it must
not crash the scan or nightly job that triggered it.
"""

from __future__ import annotations

import logging
import smtplib
import ssl
from email.message import EmailMessage

from .config import NotifyConfig

log = logging.getLogger(__name__)


def recipients(
    to: str | list[str] | tuple[str, ...] | None,
    config: NotifyConfig,
) -> list[str]:
    """Normalise recipients: a (possibly comma-separated) string or a list becomes
    a clean list. ``None`` falls back to the configured ``EMAIL_TO``."""
    if to is None:
        return list(config.email_to)
    if isinstance(to, str):
        to = to.split(",")
    return [address.strip() for address in to if address and str(address).strip()]


def send_email(
    subject: str,
    body: str | None,
    *,
    config: NotifyConfig,
    html: str | None = None,
    to: str | list[str] | tuple[str, ...] | None = None,
    images: dict[str, tuple[bytes, str]] | None = None,
    timeout: float = 20.0,
) -> bool:
    """Send one e-mail. Returns True on success, False if e-mail is not configured
    or the send failed — both logged, never raised.

    ``body`` is the plain-text part. Pass ``None`` to send an HTML-only message —
    an empty text part makes a plain-text client render a blank mail. ``images``
    then has no effect, since there is no alternative part to relate them to.

    ``images`` embeds pictures IN the message: ``{cid: (bytes, subtype)}``,
    referenced as ``<img src="cid:name">`` in ``html``. That is the only thing that
    works behind an authenticating reverse proxy: a linked image answers 302 to a login
    page for a mail client with no session, and the recipient sees a broken icon
    (measured 2026-08-31). ``data:`` URIs are no better — Gmail, Outlook and Yahoo
    all block them, which is exactly the three services the recipients use.
    """
    allowed, reason = config.sending_enabled()
    if not allowed:
        log.info("Skipping e-mail %r: %s", subject, reason)
        return False

    addresses = recipients(to, config)
    if not config.smtp_configured():
        log.info("E-mail not configured (SMTP_HOST/EMAIL_FROM missing) — "
                 "skipping send: %s", subject)
        return False
    if not addresses:
        log.info("E-mail has no recipients — skipping send: %s", subject)
        return False

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = config.email_from
    message["To"] = ", ".join(addresses)
    if body is None:
        # HTML-only: an empty text/plain part is worse than none at all — a client
        # that prefers plain text would render a blank message rather than fall
        # back to the HTML it can also read.
        if not html:
            log.info("E-mail has neither body nor html — skipping send: %s", subject)
            return False
        message.set_content(html, subtype="html")
    else:
        message.set_content(body)
        if html:
            message.add_alternative(html, subtype="html")
    if html and body is not None:
        for cid, (data, subtype) in (images or {}).items():
            # add_related on the HTML part makes that part multipart/related, so the
            # image belongs to the alternative rather than to the message — a client
            # showing the text version never gets an attachment it cannot use.
            message.get_payload()[-1].add_related(
                data, maintype="image", subtype=subtype, cid=f"<{cid}>")

    context = ssl.create_default_context()
    try:
        if config.smtp_ssl:
            with smtplib.SMTP_SSL(config.smtp_host, config.smtp_port,
                                  context=context, timeout=timeout) as server:
                if config.smtp_user:
                    server.login(config.smtp_user, config.smtp_password)
                server.send_message(message)
        else:
            with smtplib.SMTP(config.smtp_host, config.smtp_port,
                              timeout=timeout) as server:
                server.starttls(context=context)
                if config.smtp_user:
                    server.login(config.smtp_user, config.smtp_password)
                server.send_message(message)
        log.info("E-mail sent to %s: %s", addresses, subject)
        return True
    except Exception as exc:    # noqa: BLE001 — log, never crash the caller
        log.error("E-mail send failed (%s:%s): %s",
                  config.smtp_host, config.smtp_port, exc)
        return False
