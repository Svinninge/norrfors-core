# LESSONS — norrfors-core

Lärdomar, nyast överst.

## 2026-09-20 — Tom sträng i secrets.env måste räknas som osatt, annars ser en blank rad ut som konfiguration

Ärvt från dubblaren: `os.environ.get("SMTP_HOST")` returnerar `""` för en blank
rad, vilket är sant nog för ett `if` och gör att koden försöker skicka mot en tom
server. `NotifyConfig.from_env` behandlar tomt som saknat.

## 2026-09-20 — Bilder i mail måste bäddas in som `cid:`, inte länkas

Mätt 2026-08-31: appen låg bakom en autentiserande reverse proxy, så en länkad
bild svarar 302 till en inloggningssida för en mailklient utan session och
mottagaren ser en bruten ikon. `data:`-URI:er duger inte heller — Gmail, Outlook
och Yahoo blockerar dem, alltså precis de tre tjänster mottagarna använder.

## 2026-09-20 — En UTV-instans som delar SMTP-uppgifter med prod mailar skarpa larm vid varje lokal testkörning

Per 2026-08-08. Därför finns `enabled`/`disabled_reason` i `NotifyConfig` och inte
bara "konfigurerad eller inte". Spärren är opt-in för projektet att sätta, för
core kan inte veta vad som är prod i just det projektet.
