# LESSONS — norrfors-core

Lärdomar, nyast överst.

## 2026-09-20 — Ett konsumentprojekt som hämtar core som GIT-källa kräver git i sin runtime-image

ai-tradings image-bygge failade efter migreringen: `cause: Git executable not
found`. `python:3.12-slim` har ingen git, och `uv sync` skalar ut till git för ett
git-beroende — CI passerade eftersom runnern har git, så felet syntes först i
image-bygget efter merge till main.

Använd en **tagg-pinnad tarball** i konsumenterna, inte en git-källa:
`https://github.com/Svinninge/norrfors-core/archive/refs/tags/vX.YY.tar.gz`
(uv: `[tool.uv.sources] norrfors-core = { url = "..." }`). Fungerar utan
git-binär och är pinnad likadant. Alla tre konsumenterna gör så nu.

## 2026-09-20 — Ett delat bibliotek utan `py.typed` får mypy att ge upp i varje typad konsument

Hittades vid första migreringen (ai-trading): `error: Skipping analyzing
"norrfors_core.notify": module is installed, but missing library stubs or py.typed
marker`. Paketet var fullt annoterat hela tiden — markören är det som säger åt mypy
att tro på annoteringarna. Kräver både filen `norrfors_core/py.typed` och
`[tool.setuptools.package-data]`, annars följer den inte med i bygget.

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
