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
    """FSRS spaced repetition -tila per käyttäjä per kysymys"""
    FSRS_STATES = [
        (0, 'New'),
        (1, 'Learning'),
        (2, 'Review'),
        (3, 'Relearning'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sr_cards')
    question = models.ForeignKey(
        'quiz.Question', on_delete=models.CASCADE, related_name='sr_cards'
    )

    # FSRS parameters
    stability = models.FloatField(default=0, help_text="FSRS: muistin vahvuus (päiviä)")
    difficulty = models.FloatField(default=0, help_text="FSRS: vaikeusaste 1-10")
    fsrs_state = models.IntegerField(
        default=0, choices=FSRS_STATES, help_text="FSRS: kortin tila"
    )
    lapses = models.IntegerField(default=0, help_text="FSRS: unohduskerrat")
    elapsed_days = models.IntegerField(default=0, help_text="FSRS: päiviä edellisestä kertauksesta")

    # Kept from SM-2 (still used for display + mastery)
    ease_factor = models.FloatField(default=2.5)  # Deprecated, kept for migration
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

    def _build_fsrs_card(self):
        """Reconstruct a py-fsrs Card object from DB fields."""
        from fsrs import Card, State
        from datetime import datetime, timezone as dt_tz

        if self.fsrs_state == 0:
            # Never reviewed — return a fresh card
            return Card()

        card = Card()
        card.stability = self.stability
        card.difficulty = self.difficulty
        card.state = State(self.fsrs_state)
        now = datetime.now(dt_tz.utc)
        card.due = self.next_review.astimezone(dt_tz.utc) if self.next_review else now
        card.last_review = (
            self.last_reviewed.astimezone(dt_tz.utc) if self.last_reviewed else None
        )
        return card

    def _get_scheduler(self):
        """Return configured FSRS scheduler."""
        from fsrs import Scheduler
        from datetime import timedelta

        return Scheduler(
            desired_retention=0.9,
            learning_steps=(timedelta(days=1),),
            relearning_steps=(timedelta(days=1),),
            maximum_interval=365,
        )

    def update_after_review(self, rating: int) -> None:
        """
        FSRS algorithm. rating = 1-4:
        1: Again (unohdin)
        2: Hard (vaikea muistaa)
        3: Good (muistin epäröiden)
        4: Easy (helppo muistaa)
        """
        from fsrs import Rating as FSRSRating
        from datetime import datetime, timezone as dt_tz

        scheduler = self._get_scheduler()
        card = self._build_fsrs_card()

        fsrs_rating = FSRSRating(rating)
        card, _review_log = scheduler.review_card(card, fsrs_rating)

        now = datetime.now(dt_tz.utc)

        # Write back to model
        self.stability = card.stability or 0
        self.difficulty = card.difficulty or 0
        self.fsrs_state = card.state.value if hasattr(card.state, 'value') else card.state
        self.repetitions += 1
        if rating == 1:  # Again
            self.lapses += 1
        delta = (card.due - now).total_seconds() / 86400
        self.interval_days = max(0, round(delta))
        self.next_review = card.due
        self.last_reviewed = now
        self.save()

    def get_predicted_intervals(self) -> dict:
        """Return predicted intervals (days) for all 4 ratings without updating."""
        from fsrs import Card, Rating as FSRSRating

        scheduler = self._get_scheduler()
        card = self._build_fsrs_card()

        from datetime import datetime, timezone as dt_tz

        now = datetime.now(dt_tz.utc)
        intervals = {}
        for r in [FSRSRating.Again, FSRSRating.Hard, FSRSRating.Good, FSRSRating.Easy]:
            card_copy = Card.from_json(card.to_json())
            updated, _ = scheduler.review_card(card_copy, r)
            delta = (updated.due - now).total_seconds() / 86400
            intervals[r.value] = max(0, round(delta))
        return intervals

    def get_retrievability(self) -> float:
        """Return current recall probability (0-100%)."""
        scheduler = self._get_scheduler()
        card = self._build_fsrs_card()
        return round(scheduler.get_card_retrievability(card) * 100)


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

        # Calculate based on SR cards — FSRS: stable Review cards
        a_mastered = SpacedRepetitionCard.objects.filter(
            user=self.user,
            question__in=a_questions,
            stability__gte=14,
            fsrs_state=2,  # Review state
        ).count()

        b_mastered = SpacedRepetitionCard.objects.filter(
            user=self.user,
            question__in=b_questions,
            stability__gte=14,
            fsrs_state=2,  # Review state
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


class FlaggedQuestion(models.Model):
    """User-flagged question for later review."""
    FLAG_TYPES = [
        ('wrong', 'Väärin vastattu'),
        ('guess', 'Arvaus'),
        ('important', 'Tärkeä'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='flagged_questions')
    question = models.ForeignKey(
        'quiz.Question', on_delete=models.CASCADE, related_name='flags'
    )
    flag_type = models.CharField(max_length=20, choices=FLAG_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'question']
        indexes = [
            models.Index(fields=['user', 'flag_type']),
        ]

    def __str__(self):
        return f"{self.user.username} -> Q{self.question_id} ({self.flag_type})"


class QuestionNote(models.Model):
    """Personal note attached to a question."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='question_notes')
    question = models.ForeignKey(
        'quiz.Question', on_delete=models.CASCADE, related_name='notes'
    )
    note_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'question']

    def __str__(self):
        return f"{self.user.username} note on Q{self.question_id}"


class QuestionComment(models.Model):
    """Public comment on a question, visible to all users."""
    question = models.ForeignKey(
        'quiz.Question', on_delete=models.CASCADE, related_name='comments'
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='question_comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False, help_text="Superuser marks as resolved")

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['question', 'is_resolved']),
        ]

    def __str__(self):
        return f"{self.user.username} on Q{self.question_id}: {self.text[:50]}"
