"""
Site- en automatiseringsinstellingen.

Dit is het EERSTE bestand om aan te passen. Alles hier bepaalt waar de site
over gaat en hoe de gegenereerde artikelen eruitzien.
"""
import os

# --- Site-identiteit -------------------------------------------------------
SITE_NAME = "Werkplek Wijzer"
NICHE_DESCRIPTION = "thuiskantoor-spullen en productiviteitstools voor thuiswerkers"

# --- Taal --------------------------------------------------------------
# "nl" = Nederlandse markt, kleiner bereik maar jij kan de kwaliteit goed
#   controleren. "en" = veel groter bereik en betere affiliate/advertentie-
#   tarieven, maar dan moet je zelf (of iemand anders) de output kunnen
#   beoordelen op fouten/onzin in het Engels.
LANGUAGE = "nl"                # taalcode voor de HTML lang-attribute
LANGUAGE_NAME = "Nederlands"   # taalnaam die naar het AI-model gaat

# --- Affiliate -----------------------------------------------------------
# amazon.nl voor de Nederlandse markt, amazon.com voor de VS/wereldwijd.
AMAZON_DOMAIN = "amazon.nl"
# Wordt normaal overschreven door de AFFILIATE_TAG GitHub secret.
AFFILIATE_TAG = os.environ.get("AFFILIATE_TAG", "jouwtag-21")

# --- AI-model --------------------------------------------------------------
# gemini-2.5-flash zit ruim in de gratis tier van Google AI Studio.
# Kom je rate limits tegen, probeer dan gemini-2.5-flash-lite (nog hogere
# gratis limieten, iets minder verfijnde tekst).
GEMINI_MODEL = "gemini-3.6-flash"
