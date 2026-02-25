"""Seed default achievements into the database."""
from django.core.management.base import BaseCommand

from progress.models import Achievement

ACHIEVEMENTS = [
    {
        'code': 'first_question',
        'name': 'Ensimmäinen askel',
        'description': 'Vastasit ensimmäiseen kysymykseen.',
        'icon': 'fa-shoe-prints',
        'xp_reward': 10,
        'condition_type': 'questions',
        'condition_value': 1,
    },
    {
        'code': 'ten_questions',
        'name': 'Kymmenen vastausta',
        'description': 'Vastasit kymmeneen kysymykseen.',
        'icon': 'fa-list-ol',
        'xp_reward': 25,
        'condition_type': 'questions',
        'condition_value': 10,
    },
    {
        'code': 'fifty_questions',
        'name': 'Puoli sataa',
        'description': 'Vastasit 50 kysymykseen.',
        'icon': 'fa-star-half-alt',
        'xp_reward': 50,
        'condition_type': 'questions',
        'condition_value': 50,
    },
    {
        'code': 'hundred_questions',
        'name': 'Sata vastausta',
        'description': 'Vastasit 100 kysymykseen.',
        'icon': 'fa-star',
        'xp_reward': 100,
        'condition_type': 'questions',
        'condition_value': 100,
    },
    {
        'code': 'five_hundred_questions',
        'name': 'Viisisataa',
        'description': 'Vastasit 500 kysymykseen.',
        'icon': 'fa-crown',
        'xp_reward': 250,
        'condition_type': 'questions',
        'condition_value': 500,
    },
    {
        'code': 'streak_3',
        'name': 'Kolmen päivän putki',
        'description': 'Harjoittelit 3 peräkkäisenä päivänä.',
        'icon': 'fa-fire',
        'xp_reward': 30,
        'condition_type': 'streak',
        'condition_value': 3,
    },
    {
        'code': 'streak_7',
        'name': 'Viikon putki',
        'description': 'Harjoittelit 7 peräkkäisenä päivänä.',
        'icon': 'fa-fire-alt',
        'xp_reward': 75,
        'condition_type': 'streak',
        'condition_value': 7,
    },
    {
        'code': 'streak_30',
        'name': 'Kuukauden putki',
        'description': 'Harjoittelit 30 peräkkäisenä päivänä.',
        'icon': 'fa-meteor',
        'xp_reward': 300,
        'condition_type': 'streak',
        'condition_value': 30,
    },
    {
        'code': 'correct_streak_5',
        'name': 'Viisi peräkkäin oikein',
        'description': 'Vastasit viiteen kysymykseen peräkkäin oikein.',
        'icon': 'fa-bolt',
        'xp_reward': 40,
        'condition_type': 'correct_streak',
        'condition_value': 5,
    },
    {
        'code': 'correct_streak_10',
        'name': 'Kymmenen peräkkäin oikein',
        'description': 'Vastasit kymmeneen kysymykseen peräkkäin oikein.',
        'icon': 'fa-bolt',
        'xp_reward': 100,
        'condition_type': 'correct_streak',
        'condition_value': 10,
    },
    {
        'code': 'first_exam',
        'name': 'Ensimmäinen tenttiharjoitus',
        'description': 'Suoritit ensimmäisen AI-arvioidun tenttiharjoituksen.',
        'icon': 'fa-file-alt',
        'xp_reward': 50,
        'condition_type': 'exam_pass',
        'condition_value': 1,
    },
    {
        'code': 'epa_mastery',
        'name': 'EPA hallinnassa',
        'description': 'Saavutit 80%+ hallinnan yhdessä EPA-kortissa.',
        'icon': 'fa-graduation-cap',
        'xp_reward': 150,
        'condition_type': 'mastery',
        'condition_value': 80,
    },
]


class Command(BaseCommand):
    help = 'Seed default achievements into the database'

    def handle(self, *args, **options):
        created = 0
        for data in ACHIEVEMENTS:
            _, was_created = Achievement.objects.update_or_create(
                code=data['code'],
                defaults=data,
            )
            if was_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(
            f'Seeded {created} new achievements ({len(ACHIEVEMENTS)} total defined).'
        ))
