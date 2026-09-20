# File version: v0.01
# Description: Telegram sender — chunking, HTML parse mode, never raises
# Author: Per Norrfors
# Created: 2026-09-20
# Modified: 2026-09-20 - Initial implementation (Claude)
"""Send a Telegram message.

Uses ``urllib`` rather than ``httpx`` so the package stays dependency-free and
installs unchanged on the NAS and in slim images. The call is synchronous with a
short timeout: a notification is a side effect of a job, never its critical path.

Never raises. A notification that blows up would take the caller — a nightly job
or a daemon — down with it, which is the opposite of the point.
"""

from __future__ import annotations

import json
import logging
import urllib.error
import urllib.parse
import urllib.request

from .config import NotifyConfig
from .format import split_message

log = logging.getLogger(__name__)

TELEGRAM_API = "https://api.telegram.org"
#: Telegram caps a message at 4096 characters; leave headroom for HTML escaping.
MAX_MESSAGE_LEN = 4000


def _call(token: str, method: str, params: dict, timeout: float) -> dict:
    url = f"{TELEGRAM_API}/bot{token}/{method}"
    data = urllib.parse.urlencode(params).encode()
    request = urllib.request.Request(url, data=data)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read())


def send_telegram(
    text: str,
    *,
    config: NotifyConfig,
    chat_ids: str | list[str] | tuple[str, ...] | None = None,
    parse_mode: str = "HTML",
    disable_notification: bool = False,
    timeout: float = 10.0,
) -> bool:
    """Send ``text`` to every configured chat.

    ``chat_ids`` overrides the config, which is how a project with per-user
    recipients feeds in the addresses it resolved from its own database.

    Returns True when every chunk reached every recipient. False means missing
    configuration or a failed send — both logged, neither raised.
    """
    allowed, reason = config.sending_enabled()
    if not allowed:
        log.info("Skipping Telegram send: %s", reason)
        return False

    if chat_ids is None:
        recipients = config.telegram_chat_ids
    elif isinstance(chat_ids, str):
        recipients = tuple(part.strip() for part in chat_ids.split(",") if part.strip())
    else:
        recipients = tuple(str(c).strip() for c in chat_ids if str(c).strip())

    if not config.telegram_configured():
        log.info("Telegram not configured (TELEGRAM_BOT_TOKEN missing) — skipping send")
        return False
    if not recipients:
        log.info("Telegram has no recipients — skipping send")
        return False

    success = True
    for chat_id in recipients:
        for chunk in split_message(text, MAX_MESSAGE_LEN):
            params = {
                "chat_id": chat_id,
                "text": chunk,
                "parse_mode": parse_mode,
                "disable_notification": str(bool(disable_notification)).lower(),
            }
            try:
                _call(config.telegram_bot_token, "sendMessage", params, timeout)
            except Exception as exc:    # noqa: BLE001 — log, never crash the caller
                log.warning("Telegram send failed for chat %s: %s", chat_id, exc)
                success = False
    if success:
        log.info("Telegram sent to %s recipient(s)", len(recipients))
    return success
