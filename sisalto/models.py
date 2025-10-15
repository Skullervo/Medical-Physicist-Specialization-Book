from django.db import models

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
	user_answer = models.TextField()
	gpt_evaluation = models.TextField(blank=True)  # GPT:n arviointi
	score = models.FloatField(null=True, blank=True)  # Pistemäärä 0-10
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"Answer to Q{self.question.question_number} ({self.session_id})"


class Specialty(models.Model):
	name = models.CharField(max_length=100, unique=True)

	def __str__(self):
		return self.name


class EPA(models.Model):
	specialty = models.ForeignKey(Specialty, on_delete=models.CASCADE, related_name='epas')
	title = models.CharField(max_length=200)
	content = models.TextField(blank=True)
	last_modified = models.DateTimeField(auto_now=True)

	# Natiivikuvantaminen-erikoiskenttä
	natiivikuvantaminen_content = models.TextField(blank=True, default="")

	def __str__(self):
		return f"{self.specialty.name}: {self.title}"


# Uusi Section-malli
class Section(models.Model):
    PROFICIENCY_CHOICES = [
        ('1', '1 — Aihe on uusi/tuntematon/vieras'),
        ('2', '2 — Yleistason/teoreettinen ymmärrys'),
        ('3', '3 — Ymmärtää ja osaa soveltaa käytännössä'),
    ]
    
    epa = models.ForeignKey(EPA, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(max_length=200)
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
