from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class UserQuizAttempt(models.Model):
    """Yksittäinen vastausyritys kysymykseen"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts')
    question = models.ForeignKey(
        'quiz.Question', on_delete=models.CASCADE, related_name='attempts'
    )

    # Answer data
    selected_choices = models.ManyToManyField('quiz.Choice', blank=True)
    answer_text = models.TextField(blank=True, help_text="Avointen kysymysten vastaukset")
    calculation_answer = models.FloatField(null=True, blank=True)

    # Result
    is_correct = models.BooleanField(null=True, blank=True)
    score = models.FloatField(default=0, help_text="0-1 skaala")
    confidence = models.IntegerField(
        null=True, blank=True,
        help_text="Itsearvioitu varmuus 1-5"
    )

    # AI evaluation (for open-ended questions)
    ai_feedback = models.TextField(blank=True)
    ai_score = models.FloatField(null=True, blank=True)

    time_spent_seconds = models.IntegerField(null=True, blank=True)
    attempted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-attempted_at']
        indexes = [
            models.Index(fields=['user', 'question']),
            models.Index(fields=['user', 'attempted_at']),
        ]


class SpacedRepetitionCard(models.Model):
    """SM-2 spaced repetition -tila per käyttäjä per kysymys"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sr_cards')
    question = models.ForeignKey(
        'quiz.Question', on_delete=models.CASCADE, related_name='sr_cards'
    )

    # SM-2 parameters
    ease_factor = models.FloatField(default=2.5)
    interval_days = models.IntegerField(default=0)
    repetitions = models.IntegerField(default=0)

    # Timing
    next_review = models.DateTimeField(default=timezone.now)
    last_reviewed = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['user', 'question']
        indexes = [
            models.Index(fields=['user', 'next_review']),
        ]

    def update_after_review(self, quality: int) -> None:
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
            # Wrong -> reset
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

        # Update ease factor
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
    epa = models.ForeignKey(
        'sisalto.EPA', on_delete=models.CASCADE, related_name='user_progress'
    )

    # A-level progress
    a_level_mastery = models.FloatField(default=0, help_text="0-100%")
    a_level_questions_answered = models.IntegerField(default=0)
    a_level_questions_correct = models.IntegerField(default=0)

    # B-level progress
    b_level_mastery = models.FloatField(default=0, help_text="0-100%")
    b_level_questions_answered = models.IntegerField(default=0)
    b_level_questions_correct = models.IntegerField(default=0)

    # Overall progress
    overall_mastery = models.FloatField(default=0, help_text="0-100%")
    last_activity = models.DateTimeField(null=True, blank=True)

    # Streak
    current_streak_days = models.IntegerField(default=0)
    longest_streak_days = models.IntegerField(default=0)

    class Meta:
        unique_together = ['user', 'epa']
        indexes = [
            models.Index(fields=['user', 'overall_mastery']),
        ]

    def recalculate_mastery(self) -> None:
        """Laske uudelleen mastery-prosentti vastausten perusteella"""
        from quiz.models import Question

        a_questions = Question.objects.filter(
            epa=self.epa,
            learning_objectives__level='A'
        ).distinct()

        b_questions = Question.objects.filter(
            epa=self.epa,
            learning_objectives__level='B'
        ).distinct()

        # Calculate based on SR cards
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
        indexes = [
            models.Index(fields=['user', 'date']),
        ]


class Achievement(models.Model):
    """Saavutus/badge"""
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    icon = models.CharField(max_length=50, blank=True, help_text="Emoji tai ikoni-koodi")
    xp_reward = models.IntegerField(default=0)

    # Conditions
    condition_type = models.CharField(
        max_length=50, help_text="streak, mastery, questions, exam_pass, correct_streak, specialty_mastery, exam_score, time_based, specialty_coverage"
    )
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
