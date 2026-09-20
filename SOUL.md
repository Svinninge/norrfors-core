# SOUL.md — norrfors-core

## Personlighet & Arbetssätt

Ett bibliotek som flera projekt hänger på. Det gör konservatism till dygd här,
till skillnad från i apparna: en ändring som är "bara en förbättring" kan gå
sönder i ett projekt ingen tittade på den dagen.

## Autonomi & Godkännande

| Åtgärd | Utan att fråga |
|---|---|
| Ny modul, nytt publikt API | **Nej** — kräver att två projekt redan använder koden |
| Bugfix inom befintligt API | Ja |
| Nytt valfritt kwarg med default | Ja |
| Ändrad signatur / borttaget argument | **Nej** — bryter konsumenter |
| Nytt runtime-beroende | **Nej** — paketet ska förbli stdlib |
| Tester, dokumentation | Ja |

## Plan-läge & Komplexitetsbedömning

Migrering av en konsument är plan-värd: den rör produktionskod i ett annat repo.
Ändring inom det här repot är det sällan.

## Elegans-pausen

Innan en modul flyttas hit: kan projekten leva med två kopior en runda till?
Om koden inte har behövt ändras på båda ställena ännu vet du inte vilket det
gemensamma gränssnittet är — då bygger du ett ramverk för en gissning.

## Lessons-loop

Varje gång en ändring här går sönder i ett konsumentprojekt: skriv raden i
`LESSONS.md` innan fixen committas.

## Kod & Skript

- Ren stdlib. Ett beroende som råkar finnas (`markdown`) används bara bakom
  `try: import`, aldrig som krav.
- All kod och alla kommentarer på **engelska** — filerna läses av projekt som är
  både svenska och engelska.
- Filhuvuden enligt det globala regelverket.

## Felhantering

**Ingenting här får kasta.** En notis är en sidoeffekt av ett jobb, aldrig dess
kritiska väg — en larmfunktion som exploderar tar daemonen med sig, vilket är
raka motsatsen till poängen. Returnera `False` och logga varför. Aldrig tyst.

## Testning

`pytest`, inget nät. Testa det de tre ursprungliga implementationerna gjorde fel:
tomma env-värden som läste som konfigurerade, meddelanden som klipptes mitt i en
tabellrad, sändningar som kastade i stället för att returnera `False`.

## Säkerhet

Inga credentials i repot. Inga default-mottagare i koden — en hårdkodad
e-postadress i ett delat bibliotek är fel adress i minst ett projekt.

## Versionskontroll (Git)

`main`, taggar `vX.YY` enligt det globala regelverket. **Konsumenter pinnar
taggen.** En bump här är inte klar förrän det står i `TODO.md` vilka projekt som
ska följa med upp.

## Dokumentation

`README.md` är gränssnittskontraktet — ändras API:t ändras README i samma commit.

## Outputformat

Svenska i `.md`, engelska i koden.

## Ton

Rakt på. Säg när en modul inte borde flytta hit.
