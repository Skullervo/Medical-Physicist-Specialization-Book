"""Generate gamified quiz questions from old exam questions."""
import random

from django.core.management.base import BaseCommand

from sisalto.models import ExamQuestion, EPA
from quiz.models import Question, Choice


# Map subject areas to EPA IDs (first EPA of matching specialty)
AREA_TO_EPA = {
    'Radiologia': 1,           # Natiivikuvantaminen
    'Sädehoito': 16,           # Peruskäsitteet (Sädehoito)
    'Sädehoito/Kuvantaminen': 16,
    'Isotooppilääketiede': 28,  # Gammakamera
    'KNF': 5,                  # EEG
    'Fysiologia': 11,          # EKG-tutkimukset
    'Kliininen fysiologia': 11,
    'Anatomia': 11,
}

AREA_DISPLAY = {
    'Radiologia': 'Radiologia',
    'Sädehoito': 'Sädehoito',
    'Sädehoito/Kuvantaminen': 'Sädehoito',
    'Isotooppilääketiede': 'Isotooppilääketiede',
    'KNF': 'KNF',
    'Fysiologia': 'Fysiologia',
    'Kliininen fysiologia': 'Kliininen fysiologia',
    'Anatomia': 'Anatomia',
}

ALL_AREAS = list(AREA_DISPLAY.values())


class Command(BaseCommand):
    help = 'Generate gamified quiz questions from old exam questions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear', action='store_true',
            help='Delete previously generated exam quiz questions before creating new ones',
        )
        parser.add_argument(
            '--dry-run', action='store_true',
            help='Show what would be created without saving',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        if options['clear'] and not dry_run:
            deleted, _ = Question.objects.filter(
                text__startswith='[TENTTI]'
            ).delete()
            self.stdout.write(f'Deleted {deleted} previously generated exam quiz objects.')

        # Get exam questions with subject areas
        exam_qs = ExamQuestion.objects.exclude(subject_area='').order_by('?')
        if not exam_qs.exists():
            self.stderr.write('No classified exam questions found. Run import_exam_questions first.')
            return

        # Group by area
        by_area = {}
        for eq in exam_qs:
            area = eq.subject_area
            if area not in AREA_TO_EPA:
                continue
            by_area.setdefault(area, []).append(eq)

        self.stdout.write(f'Found {sum(len(v) for v in by_area.values())} classified exam questions in {len(by_area)} areas')

        questions_created = 0

        # --- Type 1: "Mihin aihealueeseen tama tenttikysymys kuuluu?" ---
        type1_count = 0
        for area, area_questions in by_area.items():
            # Pick up to 15 questions per area for this type
            sample = random.sample(area_questions, min(15, len(area_questions)))
            for eq in sample:
                epa_id = AREA_TO_EPA[area]
                correct_area = AREA_DISPLAY[area]

                # Build wrong answers (other areas, 3 distractors)
                wrong_areas = [a for a in set(ALL_AREAS) if a != correct_area]
                if len(wrong_areas) < 3:
                    continue
                distractors = random.sample(wrong_areas, 3)

                q_text = f'[TENTTI] Mihin aihealueeseen seuraava tenttikysymys kuuluu?\n\n"{eq.question_text}"'
                explanation = f'Tama kysymys on aihealueelta "{correct_area}". Se kysyttiin tentissa vuonna {eq.year or "tuntematon"}.'

                if not dry_run:
                    q = Question.objects.create(
                        question_type='multiple_choice',
                        difficulty=4,
                        text=q_text,
                        explanation=explanation,
                        epa_id=epa_id,
                        is_active=True,
                    )
                    choices = [correct_area] + distractors
                    random.shuffle(choices)
                    for i, choice_text in enumerate(choices):
                        Choice.objects.create(
                            question=q,
                            text=choice_text,
                            is_correct=(choice_text == correct_area),
                            order=i,
                            explanation=f'{"Oikein" if choice_text == correct_area else "Vaarin"} - oikea aihealue on {correct_area}.',
                        )
                type1_count += 1
                questions_created += 1

        self.stdout.write(f'  Type 1 (classify question): {type1_count} questions')

        # --- Type 2: "Mika seuraavista on tenttikysymys X-alueelta?" ---
        type2_count = 0
        for area, area_questions in by_area.items():
            if len(area_questions) < 2:
                continue
            correct_area = AREA_DISPLAY[area]
            epa_id = AREA_TO_EPA[area]

            # Get questions from other areas for distractors
            other_questions = []
            for other_area, oqs in by_area.items():
                if AREA_DISPLAY[other_area] != correct_area:
                    other_questions.extend(oqs)

            if len(other_questions) < 3:
                continue

            # Create up to 10 per area
            sample = random.sample(area_questions, min(10, len(area_questions)))
            for eq in sample:
                distractor_eqs = random.sample(other_questions, 3)

                q_text = f'[TENTTI] Mika seuraavista on vanha tenttikysymys {correct_area}-alueelta?'
                explanation = f'"{eq.question_text}" on {correct_area}-alueen tenttikysymys.'

                if not dry_run:
                    q = Question.objects.create(
                        question_type='multiple_choice',
                        difficulty=5,
                        text=q_text,
                        explanation=explanation,
                        epa_id=epa_id,
                        is_active=True,
                    )
                    all_choices = [
                        (eq.question_text[:120], True),
                    ] + [
                        (d.question_text[:120], False) for d in distractor_eqs
                    ]
                    random.shuffle(all_choices)
                    for i, (ctext, is_correct) in enumerate(all_choices):
                        Choice.objects.create(
                            question=q,
                            text=ctext,
                            is_correct=is_correct,
                            order=i,
                            explanation=f'Tama kysymys on alueelta {AREA_DISPLAY.get(eq.subject_area, correct_area) if is_correct else "eri aihealueelta"}.',
                        )
                type2_count += 1
                questions_created += 1

        self.stdout.write(f'  Type 2 (identify area question): {type2_count} questions')

        # --- Type 3: "Minka vuoden tentissa kysyttiin X?" ---
        type3_count = 0
        year_questions = [eq for eqs in by_area.values() for eq in eqs if eq.year]
        if year_questions:
            years = sorted(set(eq.year for eq in year_questions))

            sample = random.sample(year_questions, min(60, len(year_questions)))
            for eq in sample:
                epa_id = AREA_TO_EPA.get(eq.subject_area, 11)
                correct_year = eq.year

                # Pick 3 wrong years
                wrong_years = [y for y in years if y != correct_year]
                if len(wrong_years) < 3:
                    continue
                distractors = random.sample(wrong_years, 3)

                q_text = f'[TENTTI] Minka vuoden sairaalafyysikkotentissa kysyttiin:\n\n"{eq.question_text}"'
                explanation = f'Tama kysymys kysyttiin vuoden {correct_year} tentissa.'

                if not dry_run:
                    q = Question.objects.create(
                        question_type='multiple_choice',
                        difficulty=5,
                        text=q_text,
                        explanation=explanation,
                        epa_id=epa_id,
                        is_active=True,
                    )
                    all_choices = [correct_year] + distractors
                    random.shuffle(all_choices)
                    for i, yr in enumerate(all_choices):
                        Choice.objects.create(
                            question=q,
                            text=str(yr),
                            is_correct=(yr == correct_year),
                            order=i,
                            explanation=f'{"Oikein" if yr == correct_year else "Vaarin"} - oikea vuosi on {correct_year}.',
                        )
                type3_count += 1
                questions_created += 1

        self.stdout.write(f'  Type 3 (identify year): {type3_count} questions')

        action = 'Would create' if dry_run else 'Created'
        self.stdout.write(self.style.SUCCESS(
            f'\n{action} {questions_created} gamified exam quiz questions.'
        ))
