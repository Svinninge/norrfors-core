# TODO — norrfors-core

## Aktivt arbete (WIP)

Inget pågående.

## Backlog — migrering av konsumenter

Ordningen är medveten: minst risk först, så flödet (installation, versionspinning,
uppdatering på två datorer) är bevisat innan något större flyttar.

1. ~~**ai-trading**~~ — klart 2026-09-20 (v0.02). `telegram.py` är nu en adapter:
   `config_resolver` stannar kvar, transporten är core:s. Signaturen oförändrad,
   alla ~10 anropare orörda.
2. ~~**dubblaren**~~ — klart 2026-09-20 (PR #129). `notify.py` äger policyn,
   core äger transporten. Publika ytan oförändrad.
3. ~~**finance**~~ — klart 2026-09-20 (v0.03). `TelegramMessage`, `EmailMessage`,
   `read_gmail()`, Svinninge-mallen och `family_users`-upplösningen stannade kvar.
   Avslöjade att core saknade html-only-utskick.

## Utredda och avskrivna

### Börsdata-klienten — NEJ (utrett 2026-09-20)

Klarar inte inflyttningsregeln. Regelns andra halva — *har behövt ändras på båda
ställena* — är inte uppfylld:

| | Rader | Commits som rört filen |
|---|---|---|
| `dubblaren/src/borsdata.py` | 1681 | 47 |
| `ai-trading/src/data/borsdata_client.py` | 192 | **1** |

ai-tradings klient skrevs en gång (Sprint 19) och har aldrig rörts. De 47
commitarna i dubblaren gäller `_listing_rank`, KPI-feeder och cache-tak — alltså
just det som inte ska hit. Koderna är inte heller samma sort: `urllib` med
budgetvakt och fillås mot `httpx` mot bulk-endpoints. Gemensam yta: bas-URL,
`authKey`, 120 ms pacing, 429/403-backoff — ca 40 rader.

Ingen tredje konsument finns: `hitta-kursvinnare` har noll `.py` (dubblaren *är*
Hitta Kursvinnare) och `finance/Backtest/borsdata_loader.py` läser SQLite.

**Ta upp igen om** ai-tradings klient börjar ändras, eller en tredje konsument
dyker upp.

### Den verkliga Börsdata-frågan ligger inte här

`BORSDATA_API_KEY` i `shared.env` är **samma nyckel** i dubblaren, ai-trading och
finance (fingeravtryck verifierade 2026-09-20). Börsdatas gränser gäller per
nyckel, så dubblarens budgetvakt är blind för de andra två och pacingen är per
process. Mätt: dubblaren ~497 anrop/dygn mot ett tak på ~10 000, alltså gott om
marginal — latent, inte brinnande. En korrekt delad liggare kräver delat
filsystem mellan containrar, alltså infrastruktur och inte ett pip-paket.

<!-- ISSUES:START -->
<!-- Genereras av sync-todo-issues.py — redigera inte för hand. -->
<!-- ISSUES:END -->
