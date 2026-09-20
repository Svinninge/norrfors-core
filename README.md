# norrfors-core

Delade byggstenar som återanvänds i Pers projekt. Ett privat pip-installerbart
paket — ingen PyPI, ingen ceremoni.

## Vad

| Modul | Ersätter |
|---|---|
| `norrfors_core.notify` | `finance/notify.py`, `dubblaren/src/notify.py`, `ai-trading/src/notifications/telegram.py` |

## Stack

Ren stdlib. Inga runtime-beroenden — paketet ska installeras oförändrat på NAS:en,
på en Pi och i slimmade Docker-images. `markdown` används om det råkar finnas
installerat, annars faller `md_to_html` tillbaka på en inbyggd konverterare.

Python ≥ 3.10.

## Status

v0.01 — `notify` är första modulen. Ingen konsument har migrerats ännu.

## Snabbstart

```bash
pip install git+ssh://git@github.com/Svinninge/norrfors-core@v0.01
```

```python
from norrfors_core.notify import NotifyConfig, notify, send_email

config = NotifyConfig.from_env()
notify("Nattjobbet är klart.", config=config, subject="Finance: nattkörning")
```

Pinna versionen per projekt (`@v0.01`) och bumpa medvetet. Ett delat paket som
följer main automatiskt går sönder i det projekt du inte tittade på.

### Konfiguration

Läses från miljön med samma variabelnamn som projekten redan använder, så
`secrets.env` behöver inte röras:

`SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_SSL`, `EMAIL_FROM`,
`EMAIL_TO`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `NOTIFY_ENABLED`.

Tom sträng räknas som osatt. Projekt med egen secret-store skickar in en getter:

```python
import secrets_store
config = NotifyConfig.from_env(secrets_store.get)
```

Projekt som delar SMTP-uppgifter mellan UTV och PROD stänger av i UTV:

```python
config = NotifyConfig.from_env(enabled=auth.is_production(),
                               disabled_reason="Utvecklingsläge — mail går bara från prod.")
```

## Struktur

```
norrfors_core/
  notify/
    __init__.py   publikt API: notify(), send_email(), send_telegram()
    config.py     NotifyConfig — credentials, mottagare, av/på
    mail.py       SMTP, text+HTML-alternativ, inbäddade bilder (cid:)
    telegram.py   sendMessage, chunkning vid 4000 tecken
    format.py     split_message, md_to_html, html_email_wrapper
tests/
```

## Vad som INTE hör hemma här

Affärslogik, UI och datamodeller. De ser lika ut mellan projekten och driver isär
— en delad kopia blir en boll av flaggor. Detsamma gäller mottagarupplösning ur
databas (`family_users` i finance, per-användar-adresser i dubblaren): det är
projektens datamodell, inte en gemensam.

En modul flyttar hit först när **två projekt redan använder den och den har behövt
ändras på båda ställena minst en gång**.
