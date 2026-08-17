# Werkplek Wijzer — geautomatiseerde affiliate-contentsite

Een systeem dat elke dag automatisch een concept-artikel schrijft voor een
affiliate-koopgidsensite, het als pull request klaarzet voor jouw controle,
en na goedkeuring automatisch publiceert via GitHub Pages. Alles draait op
gratis lagen: geen hosting-kosten, geen creditcard nodig om te beginnen.

**Lees eerst dit stuk hieronder voordat je begint — het bepaalt of dit
voor jou de moeite waard is.**

## Eerlijke verwachtingen

- **Het risico zit in tijd, niet in geld.** Je stopt er geen kapitaal in
  (geen advertentiebudget, geen voorraad), dus je kunt er ook geen geld op
  verliezen. Je *kunt* wel tijd verliezen aan een niche die niet aanslaat.
- **Dit is geen passief inkomen vanaf dag één.** Amazon accepteert je pas
  na beoordeling, en eist daarna 3 verkopen binnen 180 dagen om je account
  actief te houden. Zoekverkeer opbouwen kost meestal maanden, niet dagen.
- **Volledig automatisch artikelen de wereld in sturen is een slecht idee.**
  Google's spam-beleid ("scaled content abuse") straft sites die massaal
  ongecontroleerde AI-content publiceren actief af — recente core updates
  in 2026 hebben sites met 50-80% verkeersverlies hard geraakt. Daarom
  publiceert dit systeem NIETS automatisch: elk artikel wordt een pull
  request die jij leest en zelf goedkeurt.
- **Winst is niet gegarandeerd.** Hoeveel dit oplevert hangt af van je
  niche, hoe goed je de content bijschaaft, en of je het promoot. Dit
  script automatiseert het schrijfwerk en de publicatie — niet het
  vinden van een winnende niche of het aantrekken van bezoekers.

Als je hiermee kunt leven: hieronder de setup.

## Wat je nodig hebt (allemaal gratis)

1. Een GitHub-account
2. Een gratis Gemini API-key via [Google AI Studio](https://aistudio.google.com/app/apikey)
   (geen creditcard nodig; de gratis laag is ruim voldoende voor één
   artikel per dag — check bij twijfel je actuele limiet in AI Studio zelf,
   want Google past deze weleens aan)
3. Later, zodra er content staat: een Amazon Associates-account (zie
   onderaan dit document)

## Setup

1. Maak een nieuwe **publieke** GitHub-repository aan (publiek = gratis en
   onbeperkte GitHub Actions-minuten; privé werkt ook maar dan tellen de
   minuten mee met je gratis maandquotum).
2. Upload alle bestanden uit dit project naar die repository.
3. Ga naar **Settings → Secrets and variables → Actions** en voeg twee
   repository secrets toe:
   - `GEMINI_API_KEY` — je Gemini API-key
   - `AFFILIATE_TAG` — je Amazon-affiliate-tag (mag je voorlopig een
     placeholder laten, zoals `jouwtag-21`, totdat je bent goedgekeurd)
4. Ga naar **Settings → Pages**, kies bij "Source" voor **Deploy from a
   branch**, branch `main`, map **`/docs`**, en klik Save. Na een minuut
   staat je site live op `https://jouwgebruikersnaam.github.io/jouwrepo/`.
5. Open het **Actions**-tabblad, kies de workflow "Nieuw artikel
   genereren", en klik **Run workflow** om een eerste testartikel te
   genereren. Er verschijnt een pull request — lees die door.
6. Merge de pull request. Binnen een minuut staat het artikel live.

Vanaf nu draait de workflow vanzelf elke dag (in te stellen via de cron-
regel in `.github/workflows/generate-content.yml`), en hoef jij alleen
nog binnenkomende pull requests te beoordelen.

## Aanpassen naar jouw eigen niche

- **`config.py`** — sitenaam, niche-omschrijving, taal, Amazon-domein.
- **`topics.txt`** — de wachtrij met onderwerpen. Vervang de voorbeelden
  door onderwerpen waar jij zelf verstand van hebt. Dat is niet alleen
  prettiger te controleren, het is ook precies wat Google's kwaliteits-
  systemen proberen te herkennen: originele kennis versus generieke opvulling.
- **Taal**: staat nu op Nederlands, zodat je zelf goed kunt beoordelen of
  de output klopt. Engels (`LANGUAGE = "en"`, `AMAZON_DOMAIN = "amazon.com"`)
  geeft een veel groter bereik en betere tarieven, maar dan moet jij (of
  iemand anders) fouten in het Engels kunnen spotten voordat je merget.

## Waarom een pull request en geen directe publicatie

Zie "Eerlijke verwachtingen" hierboven. Praktisch betekent dit: lees elk
artikel echt door voordat je merget. Check op verzonnen feiten, rare
herhalingen, en of de affiliate-links naar iets logisch verwijzen. Voeg
gerust je eigen ervaring of een correctie toe voordat je merget — hoe meer
eigen inbreng, hoe geloofwaardiger (en hoe kleiner de kans dat Google het
als "scaled content" bestempelt).

## Amazon Associates aanvragen

Wacht tot je minimaal een stuk of 10 artikelen live hebt staan (Amazon
beoordeelt de kwaliteit van je site bij aanmelding) en meld je dan aan op
[associates.amazon.nl](https://associates.amazon.nl) (of `.com` voor de
VS-markt). Let op de huidige regels:

- Je krijgt na aanmelding **180 dagen om 3 kwalificerende verkopen** te
  realiseren. Lukt dat niet, dan sluit Amazon het account automatisch.
- Verkopen via betaalde advertenties tellen sinds april 2026 niet meer mee
  — het moet organisch verkeer zijn.
- Elke pagina met affiliate links moet een zichtbare disclosure hebben
  ("Bevat affiliate links…") — die staat al in de template.
- Je hebt een zichtbaar privacybeleid nodig — `docs/privacy.html` is een
  startpunt, geen waterdicht juridisch document. Laat dit bij twijfel
  nakijken; ik ben geen jurist.

Zodra je bent goedgekeurd, vervang je de `AFFILIATE_TAG`-secret door je
echte tag. Oudere artikelen gebruiken 'm automatisch mee (de tag wordt pas
ingevuld op het moment dat de link wordt gebouwd, niet hardcoded per
artikel — al moet je bij een nieuwe tag wel de al-live artikelen die vóór
de wijziging gegenereerd zijn handmatig vervangen, want die links liggen
al vast in de gepubliceerde HTML).

## Kosten — wat blijft gratis, en wanneer niet meer

- **GitHub Pages + Actions**: gratis en onbeperkt zolang de repo publiek is.
- **Gemini API**: gratis tier zonder verlooptijd, ruim genoeg voor één
  artikel per dag. Bij een 429-foutmelding (rate limit) probeert het
  script het automatisch een paar keer opnieuw; blijft dat mislukken,
  wacht dan tot de volgende dag of zet `GEMINI_MODEL` in `config.py` op
  `gemini-2.5-flash-lite` (hogere gratis limieten).
- **Amazon Associates**: altijd gratis om aan mee te doen.
- Dit hele project kan dus draaien zonder ooit geld uit te geven — het
  enige dat je investeert is de tijd om artikelen te reviewen en de site
  onder de aandacht te brengen.

## Problemen oplossen

- **PR bevat rare of verzonnen content** → sluit de PR zonder te mergen.
  Het onderwerp staat al als "gedaan" in `topics.txt`; haal het `#`-teken
  weg voor dat onderwerp als je het later opnieuw wilt proberen.
- **Workflow faalt met een Gemini-foutmelding** → check of de
  `GEMINI_API_KEY`-secret correct staat, en of je niet je dagquotum hebt
  bereikt (zichtbaar in Google AI Studio).
- **Site laadt niet** → controleer of Pages echt op map `/docs` staat
  ingesteld en of de laatste Actions-run geslaagd is.
