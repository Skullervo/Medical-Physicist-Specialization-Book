from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class QuestionCategory(models.Model):
    """Kysymyskategoria, linkittyy EPA-kortteihin"""
    name = models.CharField(max_length=200)
    epa = models.ForeignKey(
        'sisalto.EPA', on_delete=models.CASCADE, related_name='question_categories'
    )
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'question categories'

    def __str__(self):
        return f"{self.epa.title} - {self.name}"


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

    # Content
    text = models.TextField(help_text="Kysymysteksti (Markdown)")
    explanation = models.TextField(blank=True, help_text="Selitys oikeasta vastauksesta")
    hint = models.TextField(blank=True, help_text="Vihje opiskelijalle")

    # Links to existing EPA models
    epa = models.ForeignKey(
        'sisalto.EPA', on_delete=models.CASCADE, related_name='questions'
    )
    exam_question = models.ForeignKey(
        'sisalto.ExamQuestion', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='quiz_questions',
        help_text="Linkki tenttikysymykseen josta tämä monivalinta on johdettu"
    )
    learning_objectives = models.ManyToManyField(
        'sisalto.LearningObjective', blank=True, related_name='questions'
    )
    category = models.ForeignKey(
        QuestionCategory, on_delete=models.SET_NULL, null=True, blank=True
    )

    # Calculation-specific fields
    calculation_answer = models.FloatField(null=True, blank=True)
    calculation_tolerance = models.FloatField(
        null=True, blank=True, help_text="Sallittu poikkeama (%)"
    )
    calculation_unit = models.CharField(
        max_length=50, blank=True, help_text="Yksikkö (esim. mGy, mSv)"
    )

    # Model answer for AI evaluation
    model_answer = models.TextField(blank=True, help_text="Mallivastaus AI-arviointia varten")
    scoring_rubric = models.TextField(blank=True, help_text="Pisteytysohje AI-arviointia varten")
    max_points = models.IntegerField(default=1)

    # Matching pairs data
    matching_pairs = models.JSONField(
        null=True, blank=True,
        help_text='[{"left": "termi", "right": "määritelmä"}]'
    )

    # Metadata
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    times_answered = models.IntegerField(default=0)
    times_correct = models.IntegerField(default=0)

    class Meta:
        ordering = ['epa', 'difficulty']
        indexes = [
            models.Index(fields=['epa', 'question_type']),
            models.Index(fields=['difficulty']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"[{self.get_question_type_display()}] {self.text[:80]}"

    @property
    def success_rate(self) -> float:
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
        mark = '\u2713' if self.is_correct else '\u2717'
        return f"{self.text[:60]} ({mark})"
