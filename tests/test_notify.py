# File version: v0.01
# Description: Tests for config resolution, chunking, formatting and send guards
# Author: Per Norrfors
# Created: 2026-09-20
# Modified: 2026-09-20 - Initial implementation (Claude)
"""Tests for :mod:`norrfors_core.notify`.

Nothing here touches the network. What is worth testing is the behaviour the three
original implementations kept getting subtly wrong: blank env values reading as
configured, messages split mid-row, and a send that raises instead of returning
False.
"""

from __future__ import annotations

import norrfors_core.notify as notify
from norrfors_core.notify import NotifyConfig, split_message


def test_blank_env_value_counts_as_unset():
    """A blank line in secrets.env must not read as configured."""
    config = NotifyConfig.from_env({"SMTP_HOST": "   ", "EMAIL_FROM": ""})
    assert not config.smtp_configured()


def test_from_env_reads_recipients_and_port():
    config = NotifyConfig.from_env({
        "SMTP_HOST": "smtp.example.com",
        "SMTP_PORT": "465",
        "SMTP_SSL": "1",
        "EMAIL_FROM": "bot@example.com",
        "EMAIL_TO": "a@example.com, b@example.com , ",
        "TELEGRAM_BOT_TOKEN": "token",
        "TELEGRAM_CHAT_ID": "111,222",
    })
    assert config.smtp_configured() and config.telegram_configured()
    assert config.smtp_port == 465 and config.smtp_ssl is True
    assert config.email_to == ("a@example.com", "b@example.com")
    assert config.telegram_chat_ids == ("111", "222")


def test_bad_port_falls_back_to_587():
    config = NotifyConfig.from_env({"SMTP_PORT": "not-a-number"})
    assert config.smtp_port == 587


def test_disabled_config_blocks_every_send():
    """Dev instances share credentials with prod; the guard is what stops a local
    test run from mailing live alerts to the whole family."""
    config = NotifyConfig.from_env(
        {"SMTP_HOST": "smtp.example.com", "EMAIL_FROM": "bot@example.com",
         "EMAIL_TO": "a@example.com", "TELEGRAM_BOT_TOKEN": "t",
         "TELEGRAM_CHAT_ID": "1"},
        enabled=False, disabled_reason="Development mode.")
    allowed, reason = config.sending_enabled()
    assert not allowed and reason == "Development mode."
    assert notify.send_email("subject", "body", config=config) is False
    assert notify.send_telegram("text", config=config) is False


def test_notify_enabled_env_can_disable():
    config = NotifyConfig.from_env({"NOTIFY_ENABLED": "0"})
    assert config.sending_enabled()[0] is False


def test_unconfigured_send_returns_false_without_raising():
    config = NotifyConfig.from_env({})
    assert notify.send_email("subject", "body", config=config) is False
    assert notify.send_telegram("text", config=config) is False
    assert notify.notify("text", config=config) is False


def test_telegram_without_recipients_returns_false():
    config = NotifyConfig.from_env({"TELEGRAM_BOT_TOKEN": "token"})
    assert notify.send_telegram("text", config=config) is False


def test_recipients_normalises_string_and_list():
    config = NotifyConfig.from_env({"EMAIL_TO": "fallback@example.com"})
    assert notify.recipients(None, config) == ["fallback@example.com"]
    assert notify.recipients("a@x.se, b@x.se", config) == ["a@x.se", "b@x.se"]
    assert notify.recipients(["a@x.se", " "], config) == ["a@x.se"]


def test_split_message_prefers_newline_cut():
    text = "\n".join(f"row {i}" for i in range(100))
    chunks = split_message(text, limit=50)
    assert all(len(chunk) <= 50 for chunk in chunks)
    assert "".join(chunks).replace("\n", "") == text.replace("\n", "")
    assert not any(chunk.startswith("ow ") for chunk in chunks)


def test_split_message_handles_text_without_newlines():
    chunks = split_message("x" * 120, limit=50)
    assert [len(c) for c in chunks] == [50, 50, 20]


def test_md_to_html_renders_table_and_marks():
    html = notify.md_to_html("# Rubrik\n\n| A | B |\n|---|---|\n| 1 | 2 |\n\n**fet**")
    assert "<h1>" in html and "<table>" in html and "<strong>" in html


def test_html_email_wrapper_carries_branding_not_a_project_name():
    html = notify.html_email_wrapper(
        "<p>hej</p>", title="Mower", subtitle="Nattkörning", accent="#065f46")
    assert "<title>Mower</title>" in html
    assert "#065f46" in html and "<p>hej</p>" in html
    assert "Family Office" not in html
