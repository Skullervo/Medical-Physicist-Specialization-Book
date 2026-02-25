"""AI evaluation service for exam answers using OpenAI GPT-4o."""
import json
import logging
import os
import re
import time
from typing import Optional

logger = logging.getLogger(__name__)

# Rate limiting: track last call time per user
_last_call_times: dict[int, float] = {}
RATE_LIMIT_SECONDS = 5

EVALUATION_SYSTEM_PROMPT = """Olet sairaalafysiikan asiantuntija ja arvioija. Tehtävänäsi on arvioida
opiskelijan vastausta tenttikysymykseen. Arvioi vastaus mallivastaukseen verraten.

Palauta arviointi JSON-muodossa:
{
    "score": <kokonaisluku 0-5>,
    "feedback": "<yleinen sanallinen palaute>",
    "strengths": ["vahvuus1", "vahvuus2"],
    "weaknesses": ["heikkous1", "heikkous2"],
    "suggestions": ["ehdotus1", "ehdotus2"]
}

Pisteytysasteikko:
0 = Täydellisesti väärin tai ei vastausta
1 = Hyvin puutteellinen, vain yksittäisiä oikeita mainintoja
2 = Osittain oikein, mutta merkittäviä puutteita
3 = Kohtuullinen vastaus, peruskäsitteet hallussa
4 = Hyvä vastaus, pieniä puutteita
5 = Erinomainen, kattava ja oikea vastaus

Palauta VAIN JSON, ei muuta tekstiä."""


def evaluate_exam_answer(
    question_text: str,
    model_answer: str,
    user_answer: str,
    subject_area: str = "",
    user_id: Optional[int] = None,
) -> dict:
    """
    Evaluate a user's exam answer using OpenAI GPT-4o.

    Returns dict with keys: score, feedback, strengths, weaknesses, suggestions
    On error, returns dict with 'error' key.
    """
    # Rate limiting
    if user_id is not None:
        now = time.time()
        last_call = _last_call_times.get(user_id, 0)
        if now - last_call < RATE_LIMIT_SECONDS:
            return {
                'error': f'Odota {RATE_LIMIT_SECONDS} sekuntia ennen seuraavaa arviointia.',
                'rate_limited': True,
            }
        _last_call_times[user_id] = now

    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        return {'error': 'AI-arviointi ei ole käytössä (API-avain puuttuu).'}

    prompt = f"""Tenttikysymys ({subject_area}):
{question_text}

Mallivastaus:
{model_answer}

Opiskelijan vastaus:
{user_answer}

Arvioi opiskelijan vastaus mallivastaukseen verraten."""

    try:
        import openai

        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            max_tokens=2048,
            messages=[
                {"role": "system", "content": EVALUATION_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        )

        response_text = response.choices[0].message.content.strip()
        result = json.loads(response_text)

        # Validate required fields
        result.setdefault('score', 0)
        result.setdefault('feedback', '')
        result.setdefault('strengths', [])
        result.setdefault('weaknesses', [])
        result.setdefault('suggestions', [])
        result['score'] = max(0, min(5, int(result['score'])))

        return result

    except json.JSONDecodeError:
        logger.error("Failed to parse AI response as JSON")
        return {'error': 'AI-vastauksen jäsennys epäonnistui.'}
    except Exception as e:
        logger.error(f"AI evaluation error: {e}")
        return {'error': 'AI-arvioinnissa tapahtui virhe. Yritä myöhemmin.'}
