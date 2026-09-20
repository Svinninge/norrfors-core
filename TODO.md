# TODO — norrfors-core

## Aktivt arbete (WIP)

Inget pågående.

## Backlog — migrering av konsumenter

Ordningen är medveten: minst risk först, så flödet (installation, versionspinning,
uppdatering på två datorer) är bevisat innan något större flyttar.

1. ~~**ai-trading**~~ — klart 2026-09-20 (v0.02). `telegram.py` är nu en adapter:
   `config_resolver` stannar kvar, transporten är core:s. Signaturen oförändrad,
   alla ~10 anropare orörda.
2. **dubblaren** — `src/notify.py`. Behåller `job_failed()` och `send_test()`
   lokalt (projektspecifik dedupe och UI-text), anropar core för transporten.
   `sending_enabled()` blir `enabled=auth.is_production()`.
3. **finance** — `notify.py`, störst och mest sammanvävd. `TelegramMessage`,
   `read_gmail()` och `family_users`-upplösningen stannar i finance.

## Backlog — nästa modul

- **Börsdata-klient** (`ai-trading/src/data/borsdata_client.py`,
  `dubblaren/src/borsdata*.py`, hitta-kursvinnare). Störst vinst efter notify:
  rate limiting och cache är precis den kod som blir subtilt olika i varje kopia.
  Väntar tills notify-migreringen är gjord och mönstret är bevisat.

<!-- ISSUES:START -->
<!-- Genereras av sync-todo-issues.py — redigera inte för hand. -->
<!-- ISSUES:END -->
