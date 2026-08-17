#!/usr/bin/env python3
"""
Genereert automatisch één nieuw artikel voor de site.

Gebruikt alleen Python-standaardbibliotheek (geen pip install nodig).
Wordt aangeroepen door .github/workflows/generate-content.yml, dat het
resultaat als pull request opent — er wordt NOOIT automatisch direct naar
de live site gepubliceerd. Zie README.md voor uitleg waarom dat zo is.
"""
import html
import json
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path
from urllib.parse import quote_plus

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import config  # noqa: E402  (moet na de sys.path-fix geïmporteerd worden)

import os  # noqa: E402

TOPICS_FILE = ROOT / "topics.txt"
ARTICLES_DIR = ROOT / "docs" / "articles"
INDEX_FILE = ROOT / "docs" / "index.html"
TEMPLATE_FILE = ROOT / "docs" / "article_template.html"

API_KEY = os.environ.get("GEMINI_API_KEY")
REQUIRED_KEYS = {"title", "meta_description", "intro", "sections", "conclusion"}


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")[:60] or "artikel"


def next_topic() -> str:
    lines = TOPICS_FILE.read_text(encoding="utf-8").splitlines()
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            lines[i] = f"# gedaan ({date.today().isoformat()}): {stripped}"
            TOPICS_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return stripped
    raise SystemExit(
        "Geen open onderwerpen meer in topics.txt — voeg nieuwe regels toe."
    )


def build_prompt(topic: str) -> str:
    return f"""Je bent een ervaren, kritische productjournalist die schrijft voor \
"{config.SITE_NAME}", een site over {config.NICHE_DESCRIPTION}. Schrijf in het \
{config.LANGUAGE_NAME}.

Schrijf een koopgids-artikel over: "{topic}"

Eisen:
- Concreet en bruikbaar, geen vage algemeenheden of opvulzinnen.
- Verzin GEEN specifieke productnamen, merken, prijzen of testresultaten en
  presenteer die niet als feit. Beschrijf productTYPES en waar iemand op moet
  letten, in plaats van specifieke modellen te verzinnen.
- Eerlijk over voor- en nadelen, geen overdreven marketingtaal.
- 700-1000 woorden, verdeeld over 3-5 secties met duidelijke tussenkoppen.
- 2-3 natuurlijke momenten waar een productCATEGORIE genoemd wordt (voor
  affiliate-links), niet meer secties dan sections in de output.

Antwoord ALLEEN met geldig JSON, exact in dit format, zonder markdown-
codeblok eromheen en zonder uitleg ervoor of erna:
{{
  "title": "...",
  "meta_description": "... (max 155 tekens)",
  "intro": "een openingsalinea",
  "sections": [
    {{"heading": "...", "paragraphs": ["...", "..."]}}
  ],
  "product_mentions": [
    {{"search_term": "generieke productcategorie om naar te linken", "verdict": "kort oordeel, max 4 woorden", "rating": 4}}
  ],
  "conclusion": "een slotalinea"
}}"""


def call_gemini(prompt: str) -> dict:
    if not API_KEY:
        raise SystemExit("GEMINI_API_KEY ontbreekt (zet 'm als GitHub secret).")

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{config.GEMINI_MODEL}:generateContent?key={API_KEY}"
    )
    body = json.dumps(
        {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0.8,
            },
        }
    ).encode("utf-8")

    delay = 5
    last_error = None
    for attempt in range(5):
        req = urllib.request.Request(
            url, data=body, headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(text)
        except urllib.error.HTTPError as e:
            last_error = e
            if e.code == 429 and attempt < 4:
                print(f"Rate limit (429), wacht {delay}s en probeer opnieuw...")
                time.sleep(delay)
                delay *= 2
                continue
            raise SystemExit(
                f"Gemini API-fout {e.code}: {e.read().decode('utf-8', 'ignore')}"
            )
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            raise SystemExit(f"Onverwacht antwoord van Gemini, kon niet verwerken: {e}")
    raise SystemExit(f"Kon geen antwoord krijgen na herhaalde pogingen: {last_error}")


def validate(article: dict) -> None:
    missing = REQUIRED_KEYS - article.keys()
    if missing:
        raise SystemExit(f"Antwoord van Gemini mist velden: {missing}")
    if not isinstance(article["sections"], list) or not article["sections"]:
        raise SystemExit("Antwoord van Gemini: 'sections' is leeg of ongeldig.")


def safe_rating(value) -> int:
    try:
        r = int(round(float(value)))
    except (TypeError, ValueError):
        r = 4
    return min(5, max(1, r))


def affiliate_link(search_term: str) -> str:
    return f"https://www.{config.AMAZON_DOMAIN}/s?k={quote_plus(search_term)}&tag={config.AFFILIATE_TAG}"


def render_body(article: dict) -> str:
    parts = [f"<p>{html.escape(article['intro'])}</p>"]
    stamps = article.get("product_mentions") or []

    for i, section in enumerate(article["sections"]):
        heading = section.get("heading", "").strip()
        if heading:
            parts.append(f"<h2>{html.escape(heading)}</h2>")
        for p in section.get("paragraphs", []):
            if p and p.strip():
                parts.append(f"<p>{html.escape(p)}</p>")

        if i < len(stamps):
            m = stamps[i]
            term = (m.get("search_term") or "").strip()
            if not term:
                continue
            link = affiliate_link(term)
            rating = safe_rating(m.get("rating", 4))
            stars = "★" * rating + "☆" * (5 - rating)
            verdict = html.escape(m.get("verdict") or "Bekijk opties")
            parts.append(
                f'<a class="verdict-stamp" href="{link}" target="_blank" '
                f'rel="nofollow sponsored noopener">'
                f"<strong>{verdict}</strong>{stars} · "
                f"{html.escape(term)} bekijken →</a>"
            )

    parts.append(f"<p>{html.escape(article['conclusion'])}</p>")
    return "\n".join(parts)


def estimate_minutes(article: dict) -> int:
    words = len(article["intro"].split()) + len(article["conclusion"].split())
    for s in article["sections"]:
        words += len(s.get("heading", "").split())
        for p in s.get("paragraphs", []):
            words += len(p.split())
    return max(1, round(words / 200))


def main() -> None:
    topic = next_topic()
    print(f"Onderwerp: {topic}")

    article = call_gemini(build_prompt(topic))
    validate(article)

    slug = slugify(article["title"])
    today = date.today().isoformat()
    minutes = estimate_minutes(article)

    template = TEMPLATE_FILE.read_text(encoding="utf-8")
    page = (
        template.replace("{{LANG}}", config.LANGUAGE)
        .replace("{{TITLE}}", html.escape(article["title"]))
        .replace("{{META_DESCRIPTION}}", html.escape(article["meta_description"]))
        .replace("{{DATE}}", today)
        .replace("{{READING_TIME}}", str(minutes))
        .replace("{{BODY}}", render_body(article))
    )

    ARTICLES_DIR.mkdir(parents=True, exist_ok=True)
    out_path = ARTICLES_DIR / f"{slug}.html"
    out_path.write_text(page, encoding="utf-8")
    print(f"Artikel geschreven: {out_path}")

    index_html = INDEX_FILE.read_text(encoding="utf-8")
    entry = f"""    <li>
      <p class="entry-meta">{today} · {minutes} min leestijd</p>
      <h2 class="entry-title"><a href="articles/{slug}.html">{html.escape(article['title'])}</a></h2>
      <p class="entry-dek">{html.escape(article['meta_description'])}</p>
    </li>
"""
    marker = "<!-- ARTICLES_START -->"
    if marker not in index_html:
        raise SystemExit("Kon de ARTICLES_START-marker niet vinden in index.html.")
    index_html = index_html.replace(marker, marker + "\n" + entry, 1)
    INDEX_FILE.write_text(index_html, encoding="utf-8")
    print("index.html bijgewerkt.")


if __name__ == "__main__":
    main()
