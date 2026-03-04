from django.db import models
from django.utils.text import slugify


class FrontPage(models.Model):
	title = models.CharField(max_length=200, default="Etusivu")
	content = models.TextField(blank=True)
	last_modified = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.title


class ExamQuestion(models.Model):
	exam_date = models.CharField(max_length=20, default="")  # Esim. "4/29/2016" tai "touko 2019"
	question_number = models.IntegerField(default=1)
	question_text = models.TextField(default="")
	subject_area = models.CharField(max_length=100, blank=True, default="")  # Esim. "Anatomia & fysiologia"
	year = models.IntegerField(null=True, blank=True)  # Vuosiluku parsittuna
	semester = models.CharField(max_length=20, blank=True, default="")  # "kevät", "syksy", "touko" jne.
	model_answer = models.TextField(blank=True, default="")  # Mallivastaus Word-dokumenteista
	created_at = models.DateTimeField(auto_now_add=True)
	last_modified = models.DateTimeField(auto_now=True)

	def __str__(self):
		return f"{self.exam_date} Q{self.question_number}: {self.question_text[:50]}..."

	class Meta:
		ordering = ['-year', 'exam_date', 'question_number']


class ExamAnswer(models.Model):
	"""Käyttäjän vastaukset tenttikysymyksiin"""
	session_id = models.CharField(max_length=100)  # Uniikki tunniste tenttikerralle
	question = models.ForeignKey(ExamQuestion, on_delete=models.CASCADE)
	user = models.ForeignKey(
		'auth.User', on_delete=models.SET_NULL, null=True, blank=True
	)
	user_answer = models.TextField()
	gpt_evaluation = models.TextField(blank=True)
	score = models.FloatField(null=True, blank=True)
	# AI evaluation fields
	ai_score = models.IntegerField(null=True, blank=True)
	ai_feedback = models.TextField(blank=True)
	ai_strengths = models.JSONField(null=True, blank=True)
	ai_weaknesses = models.JSONField(null=True, blank=True)
	ai_suggestions = models.JSONField(null=True, blank=True)
	ai_evaluated_at = models.DateTimeField(null=True, blank=True)
	self_score = models.IntegerField(null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"Answer to Q{self.question.question_number} ({self.session_id})"


class Specialty(models.Model):
	name = models.CharField(max_length=100, unique=True)
	slug = models.SlugField(unique=True, max_length=150, blank=True)
	order = models.IntegerField(default=0)
	description = models.TextField(blank=True)

	class Meta:
		ordering = ['order']
		verbose_name_plural = 'specialties'

	def __str__(self):
		return self.name

	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = slugify(self.name, allow_unicode=True)
		super().save(*args, **kwargs)


class EPA(models.Model):
	specialty = models.ForeignKey(Specialty, on_delete=models.CASCADE, related_name='epas')
	title = models.CharField(max_length=200)
	slug = models.SlugField(unique=True, max_length=300, blank=True)
	content = models.TextField(blank=True)
	description = models.TextField(blank=True, help_text="Yleiskuvaus EPA-kortista")
	references = models.TextField(blank=True, help_text="Viitekirjallisuus")
	order = models.IntegerField(default=0)
	last_modified = models.DateTimeField(auto_now=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True)

	# Natiivikuvantaminen-erikoiskenttä
	natiivikuvantaminen_content = models.TextField(blank=True, default="")

	class Meta:
		ordering = ['specialty__order', 'order']

	def __str__(self):
		return f"{self.specialty.name}: {self.title}"

	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = slugify(self.title, allow_unicode=True)
		super().save(*args, **kwargs)

	@property
	def a_level_objectives(self):
		return self.learning_objectives.filter(level='A').order_by('code')

	@property
	def b_level_objectives(self):
		return self.learning_objectives.filter(level='B').order_by('code')


class LearningObjective(models.Model):
	"""Yksittäinen osaamistavoite (A- tai B-taso)"""
	LEVEL_CHOICES = [
		('A', 'A-taso (perusosaaminen)'),
		('B', 'B-taso (täydentävä osaaminen)'),
	]

	epa = models.ForeignKey(EPA, on_delete=models.CASCADE, related_name='learning_objectives')
	level = models.CharField(max_length=1, choices=LEVEL_CHOICES)
	code = models.CharField(max_length=10, help_text="Esim. A1, A2, B1")
	description = models.TextField()
	theory_content = models.TextField(blank=True, help_text="Markdown-muotoinen teoriasisältö")

	class Meta:
		ordering = ['level', 'code']
		unique_together = ['epa', 'code']

	def __str__(self):
		return f"{self.epa.title} - {self.code}: {self.description[:80]}"


# Uusi Section-malli
class Section(models.Model):
    PROFICIENCY_CHOICES = [
        ('1', '1 — Aihe on uusi/tuntematon/vieras'),
        ('2', '2 — Yleistason/teoreettinen ymmärrys'),
        ('3', '3 — Ymmärtää ja osaa soveltaa käytännössä'),
    ]

    epa = models.ForeignKey(EPA, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(max_length=500)  # Increased from 200 to 500
    content = models.TextField(blank=True)
    proficiency_level = models.CharField(
        max_length=2,
        choices=PROFICIENCY_CHOICES,
        default='1',
        verbose_name="Osaamisen taso"
    )
    order = models.PositiveIntegerField(default=0)
    last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.title} ({self.epa.title}) - {self.proficiency_level}"


class TheoryImage(models.Model):
    """Image slot for theory pages (modaliteetit). Each slot is a predefined
    placeholder in a theory template that a superuser can fill with an image."""

    modality = models.CharField(max_length=50, db_index=True)
    tab_id = models.CharField(max_length=50)
    slot_id = models.CharField(max_length=100)
    SIZE_CHOICES = [
        ('small',  'Pieni (40 %)'),
        ('medium', 'Normaali (65 %)'),
        ('large',  'Suuri (85 %)'),
        ('full',   'Täysleveys (100 %)'),
    ]

    image = models.ImageField(upload_to='theory/', blank=True, null=True)
    caption = models.CharField(max_length=500, blank=True)
    alt_text = models.CharField(max_length=300, blank=True)
    display_size = models.CharField(max_length=10, choices=SIZE_CHOICES, default='medium')
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('modality', 'tab_id', 'slot_id')
        ordering = ['modality', 'tab_id', 'order']

    def __str__(self):
        return f"{self.modality}/{self.tab_id}/{self.slot_id}"
