# Agentti: Gamification

## Rooli
Toteuta pelillistämisen logiikka oppimisalustan motivointiin ja sitouttamiseen.

## Pelillistämisen elementit

### 1. XP-järjestelmä (Experience Points)

```python
# gamification/services.py

class XPService:
    """XP-pisteiden hallinta"""
    
    XP_REWARDS = {
        'question_correct': 10,
        'question_correct_streak_3': 5,   # bonus 3 oikein peräkkäin
        'question_correct_streak_5': 10,  # bonus 5 oikein peräkkäin
        'question_correct_streak_10': 25, # bonus 10 oikein peräkkäin
        'question_first_try': 5,          # oikein ensimmäisellä yrittämällä
        'daily_goal_complete': 50,        # päivätavoite saavutettu
        'epa_mastery_50': 100,            # EPA-kortti 50% hallinnassa
        'epa_mastery_80': 200,            # EPA-kortti 80% hallinnassa
        'epa_mastery_100': 500,           # EPA-kortti 100% hallinnassa
        'exam_passed': 300,               # tentti läpäisty
        'exam_excellent': 500,            # tentti yli 80%
        'streak_7_days': 100,             # 7 päivän putki
        'streak_30_days': 500,            # 30 päivän putki
        'hard_question_correct': 20,      # vaikea kysymys oikein
    }
    
    @classmethod
    def award_xp(cls, user, event_type, multiplier=1.0):
        base_xp = cls.XP_REWARDS.get(event_type, 0)
        xp = int(base_xp * multiplier)
        
        # Tallenna XP
        profile = user.profile
        profile.total_xp += xp
        profile.save()
        
        # Tarkista taso-nousu
        new_level = cls.calculate_level(profile.total_xp)
        if new_level > profile.level:
            profile.level = new_level
            profile.save()
            return {'xp': xp, 'level_up': True, 'new_level': new_level}
        
        return {'xp': xp, 'level_up': False}
    
    @staticmethod
    def calculate_level(total_xp):
        """Tasot: 1-50, eksponentiaalinen kasvu"""
        import math
        return min(50, 1 + int(math.sqrt(total_xp / 100)))
```

### 2. Tasojärjestelmä

| Taso | XP | Nimi |
|------|-----|------|
| 1-5 | 0-2500 | Aloittelija |
| 6-10 | 2500-10000 | Harjoittelija |
| 11-20 | 10000-40000 | Perehtyjä |
| 21-30 | 40000-90000 | Taitaja |
| 31-40 | 90000-160000 | Asiantuntija |
| 41-50 | 160000+ | Sairaalafyysikko |

Tasonimet voi muokata erikoisalakohtaisesti:
- Sädehoito: "Dosimetristi" → "Annossuunnittelija" → "Sädehoitofyysikko"
- Radiologia: "Kuvan tulkitsija" → "Optimoija" → "Kuvantamisfyysikko"

### 3. Saavutukset (Achievements)

```python
# data/achievements.json
{
    "achievements": [
        {
            "code": "first_question",
            "name": "Ensimmäinen askel",
            "description": "Vastasit ensimmäiseen kysymykseen",
            "icon": "🎯",
            "condition_type": "questions",
            "condition_value": 1,
            "xp_reward": 10
        },
        {
            "code": "century",
            "name": "Sata kysymystä",
            "description": "Vastasit 100 kysymykseen",
            "icon": "💯",
            "condition_type": "questions",
            "condition_value": 100,
            "xp_reward": 200
        },
        {
            "code": "streak_7",
            "name": "Viikkoputki",
            "description": "7 peräkkäistä päivää harjoittelua",
            "icon": "🔥",
            "condition_type": "streak",
            "condition_value": 7,
            "xp_reward": 100
        },
        {
            "code": "streak_30",
            "name": "Kuukausiputki",
            "description": "30 peräkkäistä päivää harjoittelua",
            "icon": "⚡",
            "condition_type": "streak",
            "condition_value": 30,
            "xp_reward": 500
        },
        {
            "code": "rt_master",
            "name": "Sädehoitoguru",
            "description": "Kaikki sädehoidon EPA-kortit 80%+ hallinnassa",
            "icon": "☢️",
            "condition_type": "specialty_mastery",
            "condition_value": 80,
            "xp_reward": 1000
        },
        {
            "code": "rad_master",
            "name": "Kuvantamisen mestari",
            "description": "Kaikki radiologian EPA-kortit 80%+ hallinnassa",
            "icon": "📷",
            "condition_type": "specialty_mastery",
            "condition_value": 80,
            "xp_reward": 1000
        },
        {
            "code": "exam_ace",
            "name": "Tenttiässä",
            "description": "Läpäisit harjoitustentin yli 90% tuloksella",
            "icon": "🏆",
            "condition_type": "exam_score",
            "condition_value": 90,
            "xp_reward": 500
        },
        {
            "code": "perfect_10",
            "name": "Täydellinen kymppi",
            "description": "10 oikeaa vastausta peräkkäin",
            "icon": "⭐",
            "condition_type": "correct_streak",
            "condition_value": 10,
            "xp_reward": 100
        },
        {
            "code": "night_owl",
            "name": "Yökyöpeli",
            "description": "Harjoittelit klo 23-05 välillä",
            "icon": "🦉",
            "condition_type": "time_based",
            "condition_value": 0,
            "xp_reward": 25
        },
        {
            "code": "all_specialties",
            "name": "Moniottelija",
            "description": "Vastasit kysymykseen jokaiselta erikoisalalta",
            "icon": "🌟",
            "condition_type": "specialty_coverage",
            "condition_value": 6,
            "xp_reward": 200
        }
    ]
}
```

### 4. Päivätavoitteet

```python
class DailyGoalService:
    DEFAULT_DAILY_GOAL = 20  # kysymystä
    
    @classmethod
    def get_daily_goal(cls, user):
        """Adaptiivinen päivätavoite käyttäjän historian perusteella"""
        from progress.models import DailyStats
        
        # Viimeisen 7 päivän keskiarvo
        recent = DailyStats.objects.filter(
            user=user
        ).order_by('-date')[:7]
        
        if recent.count() >= 3:
            avg = sum(s.questions_answered for s in recent) / recent.count()
            return max(10, min(50, int(avg * 1.1)))  # 10% enemmän kuin keskiarvo
        
        return cls.DEFAULT_DAILY_GOAL
```

### 5. Leaderboard (valinnainen)

```python
class LeaderboardService:
    @staticmethod
    def get_weekly_leaderboard(limit=20):
        """Viikon TOP käyttäjät"""
        from progress.models import DailyStats
        from django.db.models import Sum
        from django.utils import timezone
        
        week_ago = timezone.now() - timezone.timedelta(days=7)
        
        return DailyStats.objects.filter(
            date__gte=week_ago
        ).values(
            'user__username', 'user__first_name'
        ).annotate(
            total_xp=Sum('xp_earned'),
            total_questions=Sum('questions_answered'),
            total_correct=Sum('questions_correct'),
        ).order_by('-total_xp')[:limit]
```

### 6. Harjoittelumuodot

1. **Vapaa harjoittelu**: Valitse EPA-kortti ja vaikeustaso
2. **Spaced Repetition**: Algoritmi valitsee kertaavat kysymykset
3. **Haaste-moodi**: 10 kysymystä, aikarajoitus, pisteet
4. **Viikkokisa**: Kuka vastaa eniten oikein viikossa
5. **Tenttisimulaatio**: Vanhan tentin simulointi aikarajalla

## Notifikaatiot

```python
NOTIFICATION_TYPES = {
    'sr_due': 'Sinulla on {count} kertaavaa kysymystä!',
    'streak_warning': 'Putkesi katkeaa huomenna! Vastaa edes yhteen kysymykseen.',
    'achievement_earned': 'Ansaitsit saavutuksen: {name}! 🏆',
    'level_up': 'Nousi tasolle {level}! 🎉',
    'exam_graded': 'Tenttisi on arvioitu. Tulos: {score}%',
    'weekly_summary': 'Viikon yhteenveto: {questions} kysymystä, {correct}% oikein',
}
```

## Tärkeää
- Pelillistäminen on motivointikeino, ei itseisarvo
- XP ja tasot eivät saa korvata oikeaa osaamisen arviointia
- Leaderboard on valinnainen (ei kaikki halua kilpailla)
- Streakien ei pidä aiheuttaa stressiä - "freeze" mahdollisuus
