"""
LLM-Based Smart Transliteration

Converts Urdu (Arabic script or Romanized) and mixed Urdu-English voice
transcriptions into clean English for the ticketing system.

Why LLM instead of phonetic rules:
  - Handles Urdu names correctly  (e.g. "محمد" → "Muhammad", not "Mhmd")
  - Understands context           (e.g. "system band ho gaya" → "system is down")
  - Handles code-switching        (mixed Urdu/English in one sentence)
  - Preserves technical terms     (error codes, system names, URLs)
"""
import json
import logging

logger = logging.getLogger(__name__)

# Languages where transliteration/translation is needed (ISO codes)
_NON_ENGLISH_LANGS = {'ur', 'hi', 'pa', 'ps', 'fa', 'ar', 'bn', 'sd', 'ks'}

# Groq Whisper sometimes returns full language names instead of ISO codes
_LANG_NAME_TO_ISO = {
    'urdu': 'ur', 'hindi': 'hi', 'punjabi': 'pa', 'pashto': 'ps',
    'farsi': 'fa', 'persian': 'fa', 'arabic': 'ar', 'bengali': 'bn',
    'sindhi': 'sd', 'kashmiri': 'ks', 'english': 'en',
}


def _normalize_lang(lang: str) -> str:
    """Normalise Whisper language output to a lowercase ISO code."""
    return _LANG_NAME_TO_ISO.get(lang.lower(), lang.lower())

_SYSTEM_PROMPT = """You are a transliteration assistant for a WhatsApp support system used in Pakistan.

Your task: Convert Urdu text into Roman Urdu (Urdu words written in Latin/English script). This is NOT a translation — keep the Urdu words but write them in Latin letters.

Rules:
1. Arabic-script Urdu → transliterate to Roman Urdu
   Example: "کام نہیں ہو رہا" → "kaam nahi ho raha"
   Example: "اسکرین فریز ہو گئی" → "screen freeze ho gayi"
2. Romanized Urdu already in Latin script → normalize/clean spelling only
3. Mixed Urdu-English → keep English words as-is; transliterate only the Urdu words
   Example: "mera login button kaam nahi kar raha" → keep as-is (already Roman Urdu)
4. Technical terms, system names, error codes, URLs → preserve exactly as written
5. Proper names → use standard Roman Urdu spelling (e.g. "مرشد" → "Murshid")
6. Do NOT translate meaning into English — only change the script

Examples:
  Input:  "مجھے بیک آفس میں لاگ ان نہیں ہو رہا"
  Output: "mujhe backoffice mein login nahi ho raha"

  Input:  "merchant directory ka page hang ho jata hai"
  Output: "merchant directory ka page hang ho jata hai"  (already Roman Urdu, leave as-is)

Respond ONLY with valid JSON:
{
  "roman_urdu": "the Roman Urdu transliteration",
  "names_detected": ["any proper names found"],
  "technical_terms": ["technical terms preserved verbatim"]
}"""


class SmartTransliterator:
    """
    LLM-powered transliterator for Urdu ↔ English voice transcriptions.
    Falls back to returning the original text if Groq is unavailable.
    """

    def __init__(self, groq_client=None):
        self.groq_client = groq_client

    def process(self, text: str, detected_language: str = 'unknown') -> dict:
        """
        Process transcribed text.

        Args:
            text:               Raw transcription from Whisper.
            detected_language:  ISO language code from Whisper (e.g. "en", "ur").

        Returns:
            {
                "text": str,                  # English-ready text
                "original_language": str,
                "names_detected": list,
                "technical_terms": list,
                "processed": bool             # True if LLM was actually used
            }
        """
        if not text or not text.strip():
            return {'text': text, 'processed': False, 'original_language': detected_language}

        iso_lang = _normalize_lang(detected_language)

        needs_processing = (
            iso_lang in _NON_ENGLISH_LANGS
            or self._contains_urdu_script(text)
        )

        if not needs_processing:
            return {
                'text': text,
                'processed': False,
                'original_language': 'english',
                'names_detected': [],
                'technical_terms': [],
            }

        if self.groq_client:
            return self._llm_process(text, iso_lang)

        logger.warning('SmartTransliterator: no Groq client, returning raw transcription')
        return {
            'text': text,
            'processed': False,
            'original_language': detected_language,
            'names_detected': [],
            'technical_terms': [],
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _contains_urdu_script(self, text: str) -> bool:
        """Detect Arabic/Urdu Unicode block (U+0600–U+06FF)."""
        return any('\u0600' <= ch <= '\u06FF' for ch in text)

    def _llm_process(self, text: str, detected_language: str) -> dict:
        try:
            response = self.groq_client.chat.completions.create(
                model='llama-3.3-70b-versatile',
                messages=[
                    {'role': 'system', 'content': _SYSTEM_PROMPT},
                    {
                        'role': 'user',
                        'content': (
                            f'Detected language: {detected_language}\n'
                            f'Text: {text}'
                        ),
                    },
                ],
                temperature=0.2,
                max_tokens=400,
                response_format={'type': 'json_object'},
            )

            result = json.loads(response.choices[0].message.content)
            return {
                'text': result.get('roman_urdu', text),
                'original_language': detected_language,
                'names_detected': result.get('names_detected', []),
                'technical_terms': result.get('technical_terms', []),
                'processed': True,
            }
        except Exception as e:
            logger.error('SmartTransliterator LLM error: %s', e)
            return {
                'text': text,
                'processed': False,
                'original_language': detected_language,
                'error': str(e),
            }
