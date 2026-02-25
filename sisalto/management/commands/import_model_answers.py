"""
Import model answers from Word documents to ExamQuestion.model_answer field
"""
import re
import sys
from pathlib import Path
from django.core.management.base import BaseCommand
from sisalto.models import ExamQuestion
import docx


class Command(BaseCommand):
    help = 'Import model answers from Word documents to ExamQuestion.model_answer field'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear all existing model_answer fields before importing',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        clear = options['clear']

        # Map Word doc files to subject areas in database
        doc_files = {
            'Radiologia_mallivastaukset.docx': 'Radiologia',
            'Sadehoito_mallivastaukset.docx': 'Sädehoito',
            'Isotooppilaaketieteen_mallivastaukset.docx': 'Isotooppilääketiede',
            'Kliinisen_fysiologian_mallivastaukset.docx': 'Kliininen fysiologia',
            'Kliinisen_neurofysiologian_mallivastaukset.docx': 'KNF',
        }

        if clear:
            if dry_run:
                count = ExamQuestion.objects.exclude(model_answer='').count()
                self.stdout.write(f'Would clear {count} existing model answers')
            else:
                ExamQuestion.objects.update(model_answer='')
                self.stdout.write(self.style.SUCCESS('Cleared all existing model answers'))

        total_imported = 0
        total_matched = 0

        for filename, subject_area in doc_files.items():
            self.stdout.write(f'\nProcessing {filename} ({subject_area})...')

            file_path = Path(filename)
            if not file_path.exists():
                self.stdout.write(self.style.WARNING(f'  File not found: {filename}'))
                continue

            try:
                doc = docx.Document(filename)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  Error opening document: {e}'))
                continue

            # Parse the document for questions and answers
            questions_found = self.parse_document(doc)
            self.stdout.write(f'  Found {len(questions_found)} questions in document')

            # Match with database and update
            for q_data in questions_found:
                year = q_data['year']
                title = q_data['title']
                answer = q_data['answer']

                # Try to find matching question in database
                # First try exact match on subject_area and year
                candidates = ExamQuestion.objects.filter(
                    year=year,
                    subject_area=subject_area
                )

                if not candidates.exists():
                    # Try without subject_area filter (for unclassified questions)
                    candidates = ExamQuestion.objects.filter(year=year)

                # Find best match based on question text similarity
                best_match = None
                best_score = 0

                for candidate in candidates:
                    # Simple similarity: count common words
                    title_words = set(title.lower().split())
                    question_words = set(candidate.question_text.lower().split())
                    common = len(title_words & question_words)
                    score = common / max(len(title_words), len(question_words), 1)

                    if score > best_score:
                        best_score = score
                        best_match = candidate

                # If we have a reasonable match (>30% word overlap)
                if best_match and best_score > 0.3:
                    total_matched += 1
                    # Sanitize title for console output (remove non-ASCII for Windows compatibility)
                    safe_title = title[:60].encode('ascii', 'replace').decode('ascii')
                    if dry_run:
                        self.stdout.write(f'  Would update Q{best_match.id}: {safe_title}... (match: {best_score:.2f})')
                    else:
                        best_match.model_answer = answer
                        best_match.save()
                        self.stdout.write(f'  [OK] Updated Q{best_match.id}: {safe_title}...')
                else:
                    safe_title = title[:60].encode('ascii', 'replace').decode('ascii')
                    self.stdout.write(self.style.WARNING(
                        f'  [SKIP] No match for [{year}] {safe_title}... (best score: {best_score:.2f})'
                    ))

            total_imported += len(questions_found)

        self.stdout.write(self.style.SUCCESS(
            f'\n{"[DRY RUN] " if dry_run else ""}Total: {total_imported} answers parsed, {total_matched} matched to database'
        ))

    def parse_document(self, doc):
        """
        Parse a Word document to extract questions and model answers.

        Expected structure:
        - "Kysymys X (year)" - heading
        - Question text in italics (skipped in parsing)
        - "Mallivastaus (6 p):"
        - Question title (repeat of question text)
        - Answer paragraphs...
        - Separator line (────────...)
        - Next question...
        """
        questions = []
        current_question = None
        in_answer = False
        answer_lines = []

        for para in doc.paragraphs:
            text = para.text.strip()

            # Skip empty lines
            if not text:
                continue

            # Check for separator line (horizontal rule with repeated special chars)
            # This marks the end of current question - save it
            if len(text) > 20 and len(set(text)) <= 3:
                if current_question and answer_lines:
                    current_question['answer'] = '\n\n'.join(answer_lines)
                    questions.append(current_question)
                    # Reset for next question
                    current_question = None
                    in_answer = False
                    answer_lines = []
                continue

            # Check for question start: "Kysymys X (year)"
            match = re.match(r'Kysymys\s+(\d+)\s*\((\d{4})', text)
            if match:
                # Save previous question if exists (in case separator was missing)
                if current_question and answer_lines:
                    current_question['answer'] = '\n\n'.join(answer_lines)
                    questions.append(current_question)

                # Start new question
                question_num = int(match.group(1))
                year = int(match.group(2))
                current_question = {
                    'number': question_num,
                    'year': year,
                    'title': '',
                    'answer': ''
                }
                answer_lines = []
                in_answer = False
                continue

            # Check for answer start: "Mallivastaus (6 p):"
            if re.match(r'Mallivastaus\s*\(.*?\):', text):
                in_answer = True
                continue

            # If we're in a question context
            if current_question:
                # The line after "Mallivastaus" is the title (if title not set)
                if in_answer and not current_question['title']:
                    current_question['title'] = text
                    continue

                # Everything else is answer content
                if in_answer and current_question['title']:
                    answer_lines.append(text)

        # Don't forget the last question (if no final separator)
        if current_question and answer_lines:
            current_question['answer'] = '\n\n'.join(answer_lines)
            questions.append(current_question)

        return questions
