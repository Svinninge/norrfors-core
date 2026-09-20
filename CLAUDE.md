# CLAUDE.md — norrfors-core

**Kärnprincip:** det här paketet får bara innehålla sådant som redan bevisat sig
i två projekt. Varje ny modul här är en framtida synkroniseringsskuld — tveka.

## Bas-kontext (läs vid sessionsstart)

- `README.md` — vad paketet är, hur det installeras, vad som inte hör hemma här
- `SOUL.md` — arbetssätt, autonomi, vad som får ändras utan att fråga
- Paketet har **inga runtime-beroenden** och ska inte få några

## Läs on-demand

- `LESSONS.md` — innan du ändrar i `notify/`
- `TODO.md` — pågående arbete och backlog
- Konsumenternas nuvarande kod när en migrering ska göras:
  `finance/notify.py`, `dubblaren/src/notify.py`,
  `ai-trading/src/notifications/telegram.py`

## Kodkarta (kort)

- `norrfors_core/notify/__init__.py` — publikt API, `notify()` som skickar på alla
  konfigurerade kanaler
- `norrfors_core/notify/config.py` — `NotifyConfig`, env-läsning, av/på-spärren
- `norrfors_core/notify/mail.py` — SMTP, `cid:`-inbäddade bilder
- `norrfors_core/notify/telegram.py` — sendMessage + chunkning
- `norrfors_core/notify/format.py` — `split_message`, `md_to_html`,
  `html_email_wrapper`

## Kör & testa

```bash
python -m pytest tests -q
pip install -e ".[dev]"
```

Inga tester får röra nätet. En sändning mot en okonfigurerad `NotifyConfig` ska
returnera `False` — testa det, inte SMTP-servern.

## Uppgifter — GitHub Issues är SSoT

Uppgifter lever som GitHub Issues i `Svinninge/norrfors-core` och speglas i
`TODO.md` mellan `<!-- ISSUES:START -->` och `<!-- ISSUES:END -->`. Redigera aldrig
det blocket för hand:

```
python "C:\Users\perno\OneDrive\Dokument\Claude\scripts\sync-todo-issues.py" norrfors-core
```

## Planer

Inga aktiva PLAN-filer. Migreringsordningen står i `TODO.md`.
