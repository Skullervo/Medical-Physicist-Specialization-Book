# Agentti: Data Modeler

## Rooli
Suunnittele ja toteuta Django-tietokantamallit sairaalafyysikon oppimisalustalle.

## Konteksti
Alusta käyttää PostgreSQL-tietokantaa ja Django ORM:ää. Mallien tulee tukea EPA-korttien hallintaa, kysymyspankkia, tenttijärjestelmää, spaced repetition -algoritmia ja käyttäjien edistymisen seurantaa.

## Toteutettavat mallit

### App: `epa`

```python
# epa/models.py

from django.db import models
from django.contrib.postgres.fields import ArrayField


class Specialty(models.Model):
    """Erikoisala (esim. Sädehoito, Radiologia)"""
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    order = models.IntegerField(default=0)
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['order']
        verbose_name_plural = 'specialties'
    
    def __str__(self):
        return self.name


class CanMEDSCompetency(models.Model):
    """CanMEDS-osaamisalue"""
    COMPETENCY_CHOICES = [
        ('medical_physics', 'Lääketieteellisen fysiikan osaaminen'),
        ('professionalism', 'Ammatillisuus'),
        ('collaboration', 'Yhteistyötaidot'),
        ('communication', 'Vuorovaikutustaidot'),
        ('leadership', 'Johtamistaidot'),
        ('knowledge', 'Osaaminen ja tiedonhallinta'),
    ]
    
    code = models.CharField(max_length=50, unique=True, choices=COMPETENCY_CHOICES)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = 'CanMEDS competencies'
    
    def __str__(self):
        return self.name


class EPACard(models.Model):
    """EPA-koulutuskortti"""
    name = models.CharField(max_length=300)
    slug = models.SlugField(unique=True, max_length=300)
    specialty = models.ForeignKey(Specialty, on_delete=models.CASCADE, related_name='epa_cards')
    description = models.TextField(blank=True, help_text="Yleiskuvaus EPA-kortista")
    training_phase = models.TextField(blank=True, help_text="Koulutuksen vaihe")
    canmeds_competencies = models.ManyToManyField(CanMEDSCompetency, blank=True)
    
    # Viitteet ja kirjallisuus
    references = models.TextField(blank=True, help_text="Viitekirjallisuus")
    
    # Arviointi
    assessment_methods = models.TextField(blank=True)
    
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['specialty__order', 'order']
    
    def __str__(self):
        return self.name
    
    @property
    def a_level_objectives(self):
        return self.objectives.filter(level='A').order_by('code')
    
    @property
    def b_level_objectives(self):
        return self.objectives.filter(level='B').order_by('code')


class LearningObjective(models.Model):
    """Yksittäinen osaamistavoite (A- tai B-taso)"""
    LEVEL_CHOICES = [
        ('A', 'A-taso (perusosaaminen)'),
        ('B', 'B-taso (täydentävä osaaminen)'),
    ]
    
    epa_card = models.ForeignKey(EPACard, on_delete=models.CASCADE, related_name='objectives')
    level = models.CharField(max_length=1, choices=LEVEL_CHOICES)
    code = models.CharField(max_length=10, help_text="Esim. A1, A2, B1")
    description = models.TextField()
    
    # Teoriasisältö joka on kirjoitettu sivustolle
    theory_content = models.TextField(blank=True, help_text="Markdown-muotoinen teoriasisältö")
    
    class Meta:
        ordering = ['level', 'code']
        unique_together = ['epa_card', 'code']
    
    def __str__(self):
        return f"{self.epa_card.name} - {self.code}: {self.description[:80]}"


class TheorySection(models.Model):
    """Laajempi teoriasisältö EPA-korttiin liittyen"""
    epa_card = models.ForeignKey(EPACard, on_delete=models.CASCADE, related_name='theory_sections')
    title = models.CharField(max_length=300)
    content = models.TextField(help_text="Markdown-muotoinen sisältö")
    order = models.IntegerField(default=0)
    related_objectives = models.ManyToManyField(LearningObjective, blank=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.epa_card.name} - {self.title}"
```

### App: `quiz`

```python
# quiz/models.py

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
import json

User = get_user_model()


class QuestionCategory(models.Model):
    """Kysymyskategoria, linkittyy EPA-kortteihin"""
    name = models.CharField(max_length=200)
    epa_card = models.ForeignKey('epa.EPACard', on_delete=models.CASCADE, related_name='question_categories')
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = 'question categories'
    
    def __str__(self):
        return f"{self.epa_card.name} - {self.name}"


class Question(models.Model):
    """Kysymys"""
    QUESTION_TYPES = [
        ('multiple_choice', 'Monivalinta (1 oikea)'),
        ('multi_select', 'Monivalinta (useita oikeita)'),
        ('true_false', 'Oikein/Väärin'),
        ('calculation', 'Laskutehtävä'),
        ('open_ended', 'Avoin kysymys (AI-arviointi)'),
        ('matching', 'Yhdistä parit'),
        ('exam_essay', 'Tenttikysymys (AI-arviointi)'),
    ]
    
    DIFFICULTY_LEVELS = [
        (1, 'Helppo (A-taso perus)'),
        (2, 'Keskitaso (A-taso syvä)'),
        (3, 'Haastava (B-taso)'),
        (4, 'Vaikea (soveltava)'),
        (5, 'Erittäin vaikea (tenttitaso)'),
    ]
    
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    difficulty = models.IntegerField(choices=DIFFICULTY_LEVELS, default=2)
    
    # Sisältö
    text = models.TextField(help_text="Kysymysteksti (Markdown)")
    explanation = models.TextField(blank=True, help_text="Selitys oikeasta vastauksesta")
    hint = models.TextField(blank=True, help_text="Vihje opiskelijalle")
    
    # Linkitykset
    epa_card = models.ForeignKey('epa.EPACard', on_delete=models.CASCADE, related_name='questions')
    learning_objectives = models.ManyToManyField(
        'epa.LearningObjective', blank=True, related_name='questions'
    )
    category = models.ForeignKey(QuestionCategory, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Laskutehtävien erityiskentät
    calculation_answer = models.FloatField(null=True, blank=True)
    calculation_tolerance = models.FloatField(null=True, blank=True, help_text="Sallittu poikkeama (%)")
    calculation_unit = models.CharField(max_length=50, blank=True, help_text="Yksikkö (esim. mGy, mSv)")
    
    # Avoimen kysymyksen mallivastaus (AI-arviointia varten)
    model_answer = models.TextField(blank=True, help_text="Mallivastaus AI-arviointia varten")
    scoring_rubric = models.TextField(blank=True, help_text="Pisteytysohje AI-arviointia varten")
    max_points = models.IntegerField(default=1)
    
    # Yhdistä-pari -tehtävien data
    matching_pairs = models.JSONField(null=True, blank=True, help_text='[{"left": "termi", "right": "määritelmä"}]')
    
    # Metadata
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    times_answered = models.IntegerField(default=0)
    times_correct = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['epa_card', 'difficulty']
    
    def __str__(self):
        return f"[{self.get_question_type_display()}] {self.text[:80]}"
    
    @property
    def success_rate(self):
        if self.times_answered == 0:
            return 0
        return self.times_correct / self.times_answered * 100


class Choice(models.Model):
    """Vastausvaihtoehto monivalintakysymyksille"""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.TextField()
    is_correct = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    explanation = models.TextField(blank=True, help_text="Miksi tämä on oikein/väärin")
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.text[:60]} ({'✓' if self.is_correct else '✗'})"
```

### App: `exams`

```python
# exams/models.py

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class ExamTemplate(models.Model):
    """Tenttipohja (vanha tentti tai harjoitustentti)"""
    EXAM_TYPES = [
        ('official_past', 'Virallinen vanha tentti'),
        ('practice', 'Harjoitustentti'),
        ('mock', 'Simuloitu tentti'),
    ]
    
    title = models.CharField(max_length=300)
    exam_type = models.CharField(max_length=20, choices=EXAM_TYPES)
    year = models.IntegerField(null=True, blank=True, help_text="Tentin vuosi")
    semester = models.CharField(max_length=20, blank=True, help_text="Esim. kevät, syksy")
    description = models.TextField(blank=True)
    time_limit_minutes = models.IntegerField(default=180, help_text="Aikaraja minuuteissa")
    passing_score_percent = models.IntegerField(default=50)
    
    # Linkitykset
    specialties = models.ManyToManyField('epa.Specialty', blank=True)
    epa_cards = models.ManyToManyField('epa.EPACard', blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-year', 'title']
    
    def __str__(self):
        return f"{self.title} ({self.year})"


class ExamQuestion(models.Model):
    """Tenttikysymys"""
    exam = models.ForeignKey(ExamTemplate, on_delete=models.CASCADE, related_name='exam_questions')
    question_number = models.IntegerField()
    text = models.TextField(help_text="Kysymysteksti")
    max_points = models.IntegerField(default=10)
    
    # AI-arvioinnin tueksi
    model_answer = models.TextField(blank=True, help_text="Mallivastaus")
    scoring_rubric = models.TextField(blank=True, help_text="Yksityiskohtainen pisteytysohje")
    key_concepts = models.JSONField(
        null=True, blank=True,
        help_text='["käsite1", "käsite2"] - avainasiat jotka tulee mainita'
    )
    
    # Linkitykset
    epa_card = models.ForeignKey('epa.EPACard', on_delete=models.SET_NULL, null=True, blank=True)
    learning_objectives = models.ManyToManyField('epa.LearningObjective', blank=True)
    
    class Meta:
        ordering = ['question_number']
        unique_together = ['exam', 'question_number']
    
    def __str__(self):
        return f"{self.exam.title} - Q{self.question_number}"


class ExamSession(models.Model):
    """Käyttäjän tenttisessio"""
    STATUS_CHOICES = [
        ('in_progress', 'Käynnissä'),
        ('submitted', 'Lähetetty arviointiin'),
        ('graded', 'Arvioitu'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exam_sessions')
    exam = models.ForeignKey(ExamTemplate, on_delete=models.CASCADE, related_name='sessions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    
    total_score = models.FloatField(null=True, blank=True)
    max_possible_score = models.FloatField(null=True, blank=True)
    passed = models.BooleanField(null=True, blank=True)
    
    class Meta:
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.exam.title} ({self.started_at:%d.%m.%Y})"


class ExamAnswer(models.Model):
    """Käyttäjän vastaus tenttikysymykseen"""
    session = models.ForeignKey(ExamSession, on_delete=models.CASCADE, related_name='answers')
    exam_question = models.ForeignKey(ExamQuestion, on_delete=models.CASCADE)
    answer_text = models.TextField(blank=True)
    
    # AI-arvioinnin tulokset
    ai_score = models.FloatField(null=True, blank=True)
    ai_feedback = models.TextField(blank=True)
    ai_strengths = models.JSONField(null=True, blank=True)
    ai_weaknesses = models.JSONField(null=True, blank=True)
    ai_suggestions = models.JSONField(null=True, blank=True)
    ai_evaluated_at = models.DateTimeField(null=True, blank=True)
    
    # Manuaalinen arviointi (valinnainen)
    manual_score = models.FloatField(null=True, blank=True)
    manual_feedback = models.TextField(blank=True)
    
    answered_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['session', 'exam_question']
    
    @property
    def final_score(self):
        return self.manual_score if self.manual_score is not None else self.ai_score
```

### App: `progress`

```python
# progress/models.py

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import math

User = get_user_model()


class UserQuizAttempt(models.Model):
    """Yksittäinen vastausyritys kysymykseen"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts')
    question = models.ForeignKey('quiz.Question', on_delete=models.CASCADE, related_name='attempts')
    
    # Vastaus
    selected_choices = models.ManyToManyField('quiz.Choice', blank=True)
    answer_text = models.TextField(blank=True, help_text="Avointen kysymysten vastaukset")
    calculation_answer = models.FloatField(null=True, blank=True)
    
    # Tulos
    is_correct = models.BooleanField(null=True, blank=True)
    score = models.FloatField(default=0, help_text="0-1 skaala")
    confidence = models.IntegerField(
        null=True, blank=True,
        help_text="Itsearvioitu varmuus 1-5"
    )
    
    # AI-arviointi (avoimille kysymyksille)
    ai_feedback = models.TextField(blank=True)
    ai_score = models.FloatField(null=True, blank=True)
    
    time_spent_seconds = models.IntegerField(null=True, blank=True)
    attempted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-attempted_at']


class SpacedRepetitionCard(models.Model):
    """SM-2 spaced repetition -tila per käyttäjä per kysymys"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sr_cards')
    question = models.ForeignKey('quiz.Question', on_delete=models.CASCADE, related_name='sr_cards')
    
    # SM-2 parametrit
    ease_factor = models.FloatField(default=2.5)
    interval_days = models.IntegerField(default=0)
    repetitions = models.IntegerField(default=0)
    
    # Ajoitus
    next_review = models.DateTimeField(default=timezone.now)
    last_reviewed = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['user', 'question']
    
    def update_after_review(self, quality: int):
        """
        SM-2 algoritmi. quality = 0-5
        0: täysin väärin
        1: väärin, mutta tunnisti vastauksen nähtyään
        2: väärin, mutta muisti jotain
        3: oikein, mutta vaikeaa
        4: oikein, pieni epäröinti
        5: oikein, täysin varma
        """
        if quality < 3:
            # Väärin -> aloita alusta
            self.repetitions = 0
            self.interval_days = 1
        else:
            if self.repetitions == 0:
                self.interval_days = 1
            elif self.repetitions == 1:
                self.interval_days = 3
            else:
                self.interval_days = round(self.interval_days * self.ease_factor)
            self.repetitions += 1
        
        # Päivitä ease factor
        self.ease_factor = max(
            1.3,
            self.ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        )
        
        self.last_reviewed = timezone.now()
        self.next_review = timezone.now() + timezone.timedelta(days=self.interval_days)
        self.save()


class EPAProgress(models.Model):
    """Käyttäjän edistyminen per EPA-kortti"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='epa_progress')
    epa_card = models.ForeignKey('epa.EPACard', on_delete=models.CASCADE, related_name='user_progress')
    
    # A-tason edistyminen
    a_level_mastery = models.FloatField(default=0, help_text="0-100%")
    a_level_questions_answered = models.IntegerField(default=0)
    a_level_questions_correct = models.IntegerField(default=0)
    
    # B-tason edistyminen
    b_level_mastery = models.FloatField(default=0, help_text="0-100%")
    b_level_questions_answered = models.IntegerField(default=0)
    b_level_questions_correct = models.IntegerField(default=0)
    
    # Kokonaisedistyminen
    overall_mastery = models.FloatField(default=0, help_text="0-100%")
    last_activity = models.DateTimeField(null=True, blank=True)
    
    # Streak
    current_streak_days = models.IntegerField(default=0)
    longest_streak_days = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ['user', 'epa_card']
    
    def recalculate_mastery(self):
        """Laske uudelleen mastery-prosentti vastausten perusteella"""
        from quiz.models import Question
        
        a_questions = Question.objects.filter(
            epa_card=self.epa_card,
            learning_objectives__level='A'
        ).distinct()
        
        b_questions = Question.objects.filter(
            epa_card=self.epa_card,
            learning_objectives__level='B'
        ).distinct()
        
        # Laske SR-korttien perusteella
        a_mastered = SpacedRepetitionCard.objects.filter(
            user=self.user,
            question__in=a_questions,
            repetitions__gte=3
        ).count()
        
        b_mastered = SpacedRepetitionCard.objects.filter(
            user=self.user,
            question__in=b_questions,
            repetitions__gte=3
        ).count()
        
        a_total = a_questions.count()
        b_total = b_questions.count()
        
        self.a_level_mastery = (a_mastered / a_total * 100) if a_total > 0 else 0
        self.b_level_mastery = (b_mastered / b_total * 100) if b_total > 0 else 0
        self.overall_mastery = (
            self.a_level_mastery * 0.6 + self.b_level_mastery * 0.4
        )
        self.save()


class DailyStats(models.Model):
    """Päivittäiset tilastot"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_stats')
    date = models.DateField()
    
    questions_answered = models.IntegerField(default=0)
    questions_correct = models.IntegerField(default=0)
    time_spent_minutes = models.IntegerField(default=0)
    xp_earned = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ['user', 'date']
        ordering = ['-date']


class Achievement(models.Model):
    """Saavutus/badge"""
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    icon = models.CharField(max_length=50, blank=True, help_text="Emoji tai ikoni-koodi")
    xp_reward = models.IntegerField(default=0)
    
    # Ehdot
    condition_type = models.CharField(max_length=50, help_text="streak, mastery, questions, exam_pass")
    condition_value = models.IntegerField(help_text="Ehdon numeerinen arvo")
    
    def __str__(self):
        return self.name


class UserAchievement(models.Model):
    """Käyttäjän ansaitsema saavutus"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'achievement']
```

## Ohjeet

1. Luo mallit yllä olevan rakenteen mukaisesti
2. Aja `makemigrations` ja `migrate`
3. Luo admin-rekisteröinnit kaikille malleille
4. Tee seed data EPA-korteista (`data/epa_cards.json`)
5. Varmista foreign key -suhteet eri appien välillä
6. Lisää indeksit usein haettaviin kenttiin (user, epa_card, next_review)

## Tärkeää
- Käytä `django.contrib.postgres.fields` kun sopivaa (JSONField, ArrayField)
- `SpacedRepetitionCard.update_after_review()` on kriittinen metodi - testaa huolellisesti
- `EPAProgress.recalculate_mastery()` pitää olla tehokas, kutsutaan usein
