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

    # Links to existing models
    specialties = models.ManyToManyField('sisalto.Specialty', blank=True)
    epa_cards = models.ManyToManyField('sisalto.EPA', blank=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-year', 'title']

    def __str__(self):
        return f"{self.title} ({self.year})"


class ExamTemplateQuestion(models.Model):
    """Tenttikysymys (laajennettu versio, linkittyy ExamTemplate:en)"""
    exam = models.ForeignKey(
        ExamTemplate, on_delete=models.CASCADE, related_name='exam_questions'
    )
    question_number = models.IntegerField()
    text = models.TextField(help_text="Kysymysteksti")
    max_points = models.IntegerField(default=10)

    # AI evaluation support
    model_answer = models.TextField(blank=True, help_text="Mallivastaus")
    scoring_rubric = models.TextField(blank=True, help_text="Yksityiskohtainen pisteytysohje")
    key_concepts = models.JSONField(
        null=True, blank=True,
        help_text='["käsite1", "käsite2"] - avainasiat jotka tulee mainita'
    )

    # Links to existing models
    epa = models.ForeignKey(
        'sisalto.EPA', on_delete=models.SET_NULL, null=True, blank=True
    )
    learning_objectives = models.ManyToManyField(
        'sisalto.LearningObjective', blank=True
    )

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
        indexes = [
            models.Index(fields=['user', 'status']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.exam.title} ({self.started_at:%d.%m.%Y})"


class ExamSessionAnswer(models.Model):
    """Käyttäjän vastaus tenttikysymykseen"""
    session = models.ForeignKey(
        ExamSession, on_delete=models.CASCADE, related_name='answers'
    )
    exam_question = models.ForeignKey(ExamTemplateQuestion, on_delete=models.CASCADE)
    answer_text = models.TextField(blank=True)

    # AI evaluation results
    ai_score = models.FloatField(null=True, blank=True)
    ai_feedback = models.TextField(blank=True)
    ai_strengths = models.JSONField(null=True, blank=True)
    ai_weaknesses = models.JSONField(null=True, blank=True)
    ai_suggestions = models.JSONField(null=True, blank=True)
    ai_evaluated_at = models.DateTimeField(null=True, blank=True)

    # Manual evaluation (optional)
    manual_score = models.FloatField(null=True, blank=True)
    manual_feedback = models.TextField(blank=True)

    answered_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['session', 'exam_question']

    @property
    def final_score(self) -> float | None:
        return self.manual_score if self.manual_score is not None else self.ai_score
