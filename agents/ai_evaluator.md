# Agentti: AI Evaluator

## Rooli
Toteuta AI-pohjainen vastausten arviointi avoimille kysymyksille ja tenttikysymyksille käyttäen Anthropic Claude API:a.

## Arkkitehtuuri

```
ai_evaluator/
├── __init__.py
├── models.py          # EvaluationLog
├── services.py        # Core evaluation logic
├── prompts.py         # Prompt templates
├── tasks.py           # Celery tasks
├── views.py           # API endpoints
└── tests.py
```

## Toteutus

### services.py - Arvioinnin ydinlogiikka

```python
# ai_evaluator/services.py

from anthropic import Anthropic
from django.conf import settings
from epa.models import EPACard, LearningObjective
import json
import logging

logger = logging.getLogger(__name__)


class AIEvaluator:
    """AI-pohjainen vastausten arvioija"""
    
    def __init__(self):
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = "claude-sonnet-4-5-20250929"
    
    def evaluate_open_answer(
        self,
        question_text: str,
        student_answer: str,
        model_answer: str,
        scoring_rubric: str,
        epa_card: EPACard,
        learning_objectives: list[LearningObjective],
        max_points: int = 5,
    ) -> dict:
        """
        Arvioi avoin vastaus.
        
        Returns:
            {
                'score': float (0 - max_points),
                'score_percent': float (0-100),
                'feedback': str,
                'strengths': list[str],
                'weaknesses': list[str],
                'suggestions': list[str],
                'key_concepts_covered': list[str],
                'key_concepts_missing': list[str],
                'referenced_objectives': list[str],
            }
        """
        objectives_text = "\n".join([
            f"- {obj.code}: {obj.description}"
            for obj in learning_objectives
        ])
        
        prompt = f"""Olet kokenut sairaalafysiikan arvioija. Arvioi opiskelijan vastaus seuraavaan kysymykseen.

## Kysymys
{question_text}

## EPA-kortti: {epa_card.name}
Erikoisala: {epa_card.specialty.name}

## Relevantit osaamistavoitteet
{objectives_text}

## Mallivastaus
{model_answer}

## Pisteytysohje
{scoring_rubric}

## Opiskelijan vastaus
{student_answer}

## Tehtävä
Arvioi vastaus asteikolla 0-{max_points}. Palauta JSON:

{{
    "score": <pisteet 0-{max_points}, voi olla desimaaliluku>,
    "feedback": "<yleinen palaute suomeksi, 2-4 lausetta>",
    "strengths": ["<vahvuus 1>", "<vahvuus 2>"],
    "weaknesses": ["<puute 1>", "<puute 2>"],
    "suggestions": ["<parannusehdotus 1>", "<parannusehdotus 2>"],
    "key_concepts_covered": ["<mainittu käsite>"],
    "key_concepts_missing": ["<puuttuva käsite>"],
    "referenced_objectives": ["A1", "B2"]
}}

ARVIOINNIN PERIAATTEET:
1. Anna reilu ja rakentava palaute
2. Tunnista osittaiset vastaukset - älä anna 0 pistettä jos jotain oikein
3. Huomioi terminologian käyttö (oikeat suomenkieliset termit)
4. Viittaa konkreettisiin osaamistavoitteisiin
5. Älä penalisoi ylimääräisestä oikeasta tiedosta
6. Varmista että palaute on hyödyllistä oppimisen kannalta
7. Jos kysymys koskee säteilylainsäädäntöä, tarkista STUK-viittausten oikeellisuus
"""
        
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = message.content[0].text
            
            # Parse JSON
            if '```json' in response_text:
                json_str = response_text.split('```json')[1].split('```')[0]
            elif '```' in response_text:
                json_str = response_text.split('```')[1].split('```')[0]
            else:
                json_str = response_text
            
            result = json.loads(json_str)
            result['score_percent'] = (result['score'] / max_points) * 100
            return result
            
        except Exception as e:
            logger.error(f"AI evaluation failed: {e}")
            return {
                'score': None,
                'score_percent': None,
                'feedback': 'AI-arviointi epäonnistui. Vastaus tallennettu manuaalista arviointia varten.',
                'strengths': [],
                'weaknesses': [],
                'suggestions': [],
                'key_concepts_covered': [],
                'key_concepts_missing': [],
                'referenced_objectives': [],
                'error': str(e),
            }
    
    def evaluate_exam_answer(
        self,
        exam_question,  # ExamQuestion instance
        student_answer: str,
    ) -> dict:
        """Arvioi tenttivastaus - käyttää laajempaa kontekstia"""
        
        epa_card = exam_question.epa_card
        learning_objectives = exam_question.learning_objectives.all()
        
        return self.evaluate_open_answer(
            question_text=exam_question.text,
            student_answer=student_answer,
            model_answer=exam_question.model_answer,
            scoring_rubric=exam_question.scoring_rubric,
            epa_card=epa_card,
            learning_objectives=learning_objectives,
            max_points=exam_question.max_points,
        )
    
    def generate_study_tips(
        self,
        user_progress: dict,
        weak_areas: list,
    ) -> str:
        """Generoi personoituja opiskeluvinkkejä heikkojen alueiden perusteella"""
        
        prompt = f"""Olet sairaalafysiikan opettaja. Opiskelija valmistautuu erikoistumistenttiin.

Opiskelijan tilanne:
{json.dumps(user_progress, indent=2, ensure_ascii=False)}

Heikot osa-alueet:
{json.dumps(weak_areas, indent=2, ensure_ascii=False)}

Anna 3-5 konkreettista opiskeluvihjettä suomeksi. Keskity:
1. Miten parantaa heikkoja osa-alueita
2. Mitä lukea seuraavaksi
3. Miten yhdistää teoriaa ja käytäntöä
"""
        
        message = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return message.content[0].text
```

### tasks.py - Celery-tehtävät

```python
# ai_evaluator/tasks.py

from celery import shared_task
from .services import AIEvaluator


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def evaluate_open_answer_task(self, attempt_id):
    """Arvioi avoin vastaus taustalla"""
    from progress.models import UserQuizAttempt
    from quiz.models import Question
    
    try:
        attempt = UserQuizAttempt.objects.get(id=attempt_id)
        question = attempt.question
        
        evaluator = AIEvaluator()
        result = evaluator.evaluate_open_answer(
            question_text=question.text,
            student_answer=attempt.answer_text,
            model_answer=question.model_answer,
            scoring_rubric=question.scoring_rubric,
            epa_card=question.epa_card,
            learning_objectives=list(question.learning_objectives.all()),
            max_points=question.max_points,
        )
        
        attempt.ai_score = result.get('score')
        attempt.ai_feedback = result.get('feedback', '')
        attempt.is_correct = result.get('score_percent', 0) >= 60
        attempt.score = (result.get('score', 0) / question.max_points) if question.max_points > 0 else 0
        attempt.save()
        
        return result
        
    except Exception as exc:
        self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def evaluate_exam_session_task(self, session_id):
    """Arvioi koko tenttisessio taustalla"""
    from exams.models import ExamSession, ExamAnswer
    from django.utils import timezone
    
    try:
        session = ExamSession.objects.get(id=session_id)
        evaluator = AIEvaluator()
        
        total_score = 0
        max_score = 0
        
        for answer in session.answers.select_related('exam_question'):
            if answer.answer_text:
                result = evaluator.evaluate_exam_answer(
                    exam_question=answer.exam_question,
                    student_answer=answer.answer_text,
                )
                
                answer.ai_score = result.get('score')
                answer.ai_feedback = result.get('feedback', '')
                answer.ai_strengths = result.get('strengths', [])
                answer.ai_weaknesses = result.get('weaknesses', [])
                answer.ai_suggestions = result.get('suggestions', [])
                answer.ai_evaluated_at = timezone.now()
                answer.save()
                
                if answer.ai_score is not None:
                    total_score += answer.ai_score
            
            max_score += answer.exam_question.max_points
        
        session.total_score = total_score
        session.max_possible_score = max_score
        session.passed = (total_score / max_score * 100) >= session.exam.passing_score_percent if max_score > 0 else False
        session.status = 'graded'
        session.save()
        
    except Exception as exc:
        self.retry(exc=exc)
```

## Konfigurointi

```python
# settings.py lisäykset

ANTHROPIC_API_KEY = env('ANTHROPIC_API_KEY')

# Celery
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_TASK_ALWAYS_EAGER = env.bool('CELERY_TASK_ALWAYS_EAGER', default=False)  # True kehityksessä

# AI Evaluation
AI_EVAL_MAX_RETRIES = 3
AI_EVAL_TIMEOUT = 30  # sekuntia
```

## Tärkeät huomiot

1. **Rate limiting**: Rajoita API-kutsuja per käyttäjä (esim. max 50 arviointia/päivä)
2. **Fallback**: Jos AI-arviointi epäonnistuu, tallenna vastaus manuaalista arviointia varten
3. **Kustannukset**: Seuraa API-käyttöä ja kustannuksia, loggaa jokainen kutsu
4. **Turvallisuus**: Älä sisällytä API-avainta koodiin, käytä ympäristömuuttujia
5. **Prompt injection**: Validoi opiskelijan vastaus ennen API-kutsua
