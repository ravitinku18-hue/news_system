# ============================================================
# FILE 3: classifier.py (GROQ VERSION - BILINGUAL FIX)
# PURPOSE: Classifies articles AND generates full bilingual content
# FIXES: Direct news style, full 200 word translation, bilingual
# ============================================================

from groq import Groq
import json
import re
import time
from config import GEMINI_API_KEY

# Create Groq client
client = Groq(api_key=GEMINI_API_KEY)


def detect_language(text):
    """
    Detects whether article is Telugu, Hindi, or English
    by counting Unicode characters of each script.
    """
    # Telugu Unicode range
    telugu_chars = len(re.findall(r'[\u0C00-\u0C7F]', text))

    # Hindi/Devanagari Unicode range
    hindi_chars = len(re.findall(r'[\u0900-\u097F]', text))

    total = len(text)

    if telugu_chars / max(total, 1) > 0.1:
        return "Telugu"
    elif hindi_chars / max(total, 1) > 0.1:
        return "Hindi"
    else:
        return "English"


def classify_and_translate(article_text, source_name):
    """
    Sends article to Groq and gets:
    - Classification (law_and_order / political / other)
    - Full original language text (200+ words)
    - Full English translation (200+ words)
    - Direct news-style headlines (no 'this article discusses')
    """

    lang = detect_language(article_text)

    prompt = f"""You are a senior Telangana police news editor writing for the DGP office.

Analyze this newspaper article and respond ONLY with a valid JSON object.
No explanation, no markdown, no extra text — just the JSON.

IMPORTANT WRITING RULES:
- Write headlines and content in DIRECT NEWS STYLE
- NEVER start with phrases like "This article", "The article discusses",
  "This report", "The news", "According to"
- Start directly with the subject: "CM Revanth Reddy visited...",
  "Police arrested 5 persons...", "BRS leaders protested..."
- Write minimum 150 words for each content field
- Be factual and specific — include names, places, numbers from the article

{{
  "category": "law_and_order" OR "political" OR "other",
  "is_telangana": true OR false,
  "language": "{lang}",

  "headline_original": "Direct headline in {lang} language, max 15 words, no intro phrases",
  "headline_english": "Direct headline in English, max 15 words, no intro phrases",

  "content_original": "Full news content in {lang} language, minimum 150 words.
                       Write in direct journalistic style. Include all names,
                       places, events, numbers from the article.
                       Do NOT start with This article or The article.",

  "content_english": "Full English translation, minimum 150 words.
                      Write in direct journalistic style. Include all names,
                      places, events, numbers from the article.
                      Do NOT start with This article or The article.",

  "location": "specific district or city name mentioned in article, else Telangana"
}}

Classification rules:
- law_and_order: crime, murder, theft, arrests, police raids, court orders,
                 riots, road accidents, communal incidents, drug busts
- political: elections, government orders, ministers, political parties,
             protests, rallies, appointments, assembly, governance
- other: sports, business, weather, entertainment, technology, international
- is_telangana: true ONLY if article is specifically about Telangana state

Article from newspaper: {source_name}
Detected language: {lang}
Article text:
---
{article_text[:2000]}
---"""

    try:
        # 1 second delay between calls to avoid rate limiting
        time.sleep(1)

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a professional news editor for Telangana Police DGP office. "
                        "Always write in direct journalistic style. "
                        "Never use phrases like 'This article discusses' or 'The article reports'. "
                        "Always respond with valid JSON only, no extra text."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="llama-3.3-70b-versatile",
            max_tokens=1200,  # increased for 150+ word content
            temperature=0
        )

        raw = chat_completion.choices[0].message.content.strip()

        # Remove markdown fences if present
        raw = re.sub(r'```json|```', '', raw).strip()

        result = json.loads(raw)
        return result

    except json.JSONDecodeError as e:
        print(f"    JSON parse error: {e}")
        return None

    except Exception as e:
        print(f"    Groq API error: {e}")
        return None