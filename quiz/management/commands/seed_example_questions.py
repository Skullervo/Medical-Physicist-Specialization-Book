"""
Seed example questions for the three new question types: true_false, calculation, matching.

These are hardcoded, medically accurate examples — no API key needed.
Useful for immediate UI testing and demonstrating the new question types.

Usage:
    python manage.py seed_example_questions          # Add all examples
    python manage.py seed_example_questions --clear  # Remove existing examples first
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from sisalto.models import EPA
from quiz.models import Question, Choice


# --- TRUE/FALSE EXAMPLES ---
# Format: (epa_id, difficulty, text, is_true, explanation)
TRUE_FALSE_DATA = [
    # Isotooppilääketiede — radionuklidit
    (28, 2, "Teknetium-99m:n fyysinen puoliintumisaika on noin 6 tuntia.", True,
     "Tc-99m:n T½ = 6,02 h. Se on yleisin isotooppilääketieteen diagnosointinuklidi juuri sopivan puoliintumisajan ja 140 keV gamma-energian vuoksi."),
    (28, 2, "Fluori-18:n puoliintumisaika on noin 110 minuuttia.", True,
     "F-18 T½ = 109,7 min (~110 min). PET-kuvantamisen tärkein positroniemitteri."),
    (28, 3, "Gallium-68:n puoliintumisaika on 78 minuuttia.", False,
     "Ga-68:n T½ = 68 minuuttia (ei 78). Muisti: luku vastaa massalukua 68."),
    (28, 2, "Jodi-131 on beetaemitteri, jota käytetään kilpirauhasen radiojodihoitoon.", True,
     "I-131 emittoi beetasäteilyä (E_max 606 keV) ja gammasäteilyä (364 keV). T½ = 8,02 vrk."),
    (28, 3, "Lu-177-PSMA-617 -hoidossa syljen eritysrauhaset ovat kriittiset elimet.", True,
     "PSMA-proteiinia ekspressoidaan voimakkaasti syljeneritysrauhasissa. Kylmäpakkaukset rauhasten kohdalla vähentävät säteilykertymää."),

    # Radiologia — TT
    (21, 2, "Tietokonetomografiassa veden Hounsfield-yksikköarvo on 0 HU.", True,
     "HU-asteikko on kalibroitu: vesi = 0 HU, ilma = -1000 HU. Muut kudokset suhteessa näihin."),
    (21, 3, "TT-kuvauksessa käytetty CTDI_vol kuvaa potilaan saaman absorboituneen annoksen tarkasti.", False,
     "CTDIvol kuvaa skannerin dosimetrista suorituskykyä standardifantomilla — ei yksittäisen potilaan annosta. Potilasannos riippuu myös kuvauksen pituudesta (DLP) ja potilaan koosta."),

    # Sädehoito — annosyksiköt
    (23, 2, "Sädehoidossa ulkoisen säteilyhoidon absorboitunut annos ilmoitetaan yksikössä Gray (Gy).", True,
     "1 Gy = 1 J/kg. Tyypillinen fraktioannos ulkoisessa sädehoidossa on 1,8–2,0 Gy."),
    (16, 3, "Fotonit ja elektronit omaavat saman säteilypainokeron (w_R = 1) ionisoivassa säteilyssä.", True,
     "Fotonit, elektronit ja positronit: w_R = 1. Protonit: w_R = 2. Alfasäteily: w_R = 20."),

    # KNF — EEG
    (5, 2, "EEG:ssä alfarytymin taajuusalue on 8–13 Hz.", True,
     "Alfarytymin taajuus on 8–13 Hz (tyypillisesti ~10 Hz). Se dominoi rentoutuneessa valvetilassa silmät suljettuna."),
    (5, 3, "Deltaaaltojen taajuusalue EEG:ssä on 4–8 Hz.", False,
     "Delta: < 4 Hz. Theta: 4–8 Hz. Delta-aallot esiintyvät syvässä unessa ja patologisissa tiloissa."),

    # Kliininen fysiologia — EKG
    (11, 2, "Normaalissa sinusrytmissä PR-intervalli on alle 120 ms.", False,
     "Normaali PR-intervalli on 120–200 ms. Alle 120 ms viittaa esi-eksitaatioon (WPW-oireyhtymä). Yli 200 ms = I-asteen AV-blokki."),
    (11, 2, "QRS-kompleksin normaali kesto aikuisella on alle 120 ms (3 pientä ruutua).", True,
     "Normaali QRS < 120 ms. Yli 120 ms viittaa haarakatkokseen tai kammioperäiseen rytmiin."),
]


# --- CALCULATION EXAMPLES ---
# Format: (epa_id, difficulty, text, answer, tolerance_pct, unit, explanation)
CALCULATION_DATA = [
    # Tc-99m aktiivisuuden lasku
    (28, 3,
     "Tc-99m-radiofarmakkoa kalibroitiin aamulla klo 8:00 aktiivisuudella 800 MBq. "
     "Lääke injektoidaan potilaalle klo 14:00. Mikä on aktiivisuus injektiohetkellä? "
     "(T½ = 6 h, käytä kaavaa A = A₀ × 2^(−t/T½))",
     400.0, 5.0, "MBq",
     "t = 6 h = 1 × T½. A = 800 × 2^(−6/6) = 800 × 0,5 = 400 MBq."),

    # Efektiivinen annos
    (28, 3,
     "Potilas saa I-131 radiojodihoitona 600 MBq. Jos efektiivinen annoskertymä on "
     "0,22 mSv/MBq, mikä on potilaan kokonaisefektiivinen annos?",
     132.0, 5.0, "mSv",
     "E = 600 MBq × 0,22 mSv/MBq = 132 mSv."),

    # TT-annos DLP-muunnos
    (21, 4,
     "TT-pään kuvauksen DLP on 900 mGy·cm. Efektiivisen annoksen muunnoskerroin on "
     "k = 0,0023 mSv/(mGy·cm). Laske efektiivinen annos.",
     2.07, 5.0, "mSv",
     "E = DLP × k = 900 × 0,0023 = 2,07 mSv."),

    # Puoliintumisajan laskeminen
    (28, 3,
     "Radionuklidin aktiivisuus on aluksi 512 MBq. Kahdeksan tunnin kuluttua aktiivisuus "
     "on 64 MBq. Mikä on nukliidin puoliintumisaika? (T½ = t / log₂(A₀/A))",
     2.667, 5.0, "h",
     "A₀/A = 512/64 = 8 = 2³ → kolme puoliintumisaikaa. T½ = 8/3 ≈ 2,67 h."),

    # Sädehoidon BED
    (23, 4,
     "Laske biologinen ekvivalenttiannos (BED) kun kokonaisannos D = 50 Gy, "
     "fraktioannos d = 2 Gy ja α/β = 10 Gy. Kaava: BED = D × (1 + d/(α/β))",
     60.0, 2.0, "Gy",
     "BED = 50 × (1 + 2/10) = 50 × 1,2 = 60 Gy."),

    # EEG elektrodimäärä
    (5, 2,
     "Kansainvälinen 10-20 järjestelmä käyttää standardia elektrodimäärää. "
     "Montaako elektrodia standardijärjestelmässä on (ilman korva-elektrodeita)?",
     19.0, 0.0, "kpl",
     "10-20-järjestelmässä on 19 päänahkaelektrodia + 2 korvaelektrodia (A1, A2). Ilman korvaelektrodeja: 19 kpl."),

    # Säteilysuojelu efektiivinen annos
    (8, 3,
     "Röntgenhoitaja saa työpäivässä 3 µSv/h. Hän työskentelee 8 h/vrk, 220 vrk/v. "
     "Laske vuosiannos mikrosieverteissä.",
     5280.0, 2.0, "µSv",
     "Vuosiannos = 3 µSv/h × 8 h/vrk × 220 vrk = 5280 µSv = 5,28 mSv (alle 20 mSv rajaa)."),
]


# --- MATCHING EXAMPLES ---
# Format: (epa_id, difficulty, text, explanation, pairs)
# pairs = [(left, right), ...]
MATCHING_DATA = [
    # Radionuklidit ja puoliintumisajat
    (28, 2,
     "Yhdistä radionuklidit niiden fyysisiin puoliintumisaikoihin.",
     "Puoliintumisajat ovat keskeinen tieto isotooppilääketieteessä — ne ohjaavat protokollan suunnittelua.",
     [
         ("Tc-99m", "6,0 tuntia"),
         ("F-18", "110 minuuttia"),
         ("I-131", "8,02 vuorokautta"),
         ("Ga-68", "68 minuuttia"),
     ]),

    # SPET-merkkiaineet ja indikaatiot
    (31, 3,
     "Yhdistä SPET-merkkiaineet niiden pääasiallisiin kliinisiin käyttöaiheisiin.",
     "Jokainen merkkiaine akkumuloituu kudokseen spesifin biologisen mekanismin kautta.",
     [
         ("⁹⁹ᵐTc-MIBI / tetrofosmiini", "Sydänperfuusio-SPET"),
         ("[¹²³I]FP-CIT (DaTSCAN)", "Dopaminerginen hermopääte (Parkinson/LBD)"),
         ("⁹⁹ᵐTc-MAA", "Keuhkoperfuusiokuvaus"),
         ("⁹⁹ᵐTc-HMPAO", "Aivoperfuusio-SPET"),
     ]),

    # EEG-rytmit ja taajuudet
    (5, 2,
     "Yhdistä EEG-rytmit niiden taajuusalueisiin.",
     "EEG-rytmien taajuusalueet ovat kansainvälisesti standardoituja.",
     [
         ("Delta", "< 4 Hz"),
         ("Theta", "4–8 Hz"),
         ("Alfa", "8–13 Hz"),
         ("Beta", "> 13 Hz"),
     ]),

    # Säteilysuureet ja yksiköt
    (5, 2,
     "Yhdistä säteilysuureet niiden SI-yksiköihin.",
     "Säteilyannosten yksiköt ovat kansainvälisesti yhtenäisiä ICRP:n suositusten mukaan.",
     [
         ("Absorboitunut annos", "Gray (Gy)"),
         ("Ekvivalenttiannos", "Sievert (Sv)"),
         ("Aktiivisuus", "Becquerel (Bq)"),
         ("Efektiivinen annos", "Sievert (Sv)"),
     ]),

    # MRI-sekvenssit ja käyttötarkoitukset
    (2, 2,
     "Yhdistä MRI-sekvenssit niiden tyypillisiin käyttötarkoituksiin.",
     "MRI-sekvenssit perustuvat erilaisiin relaksaatioaikoihin ja signaalikontrasteihin.",
     [
         ("T1-painotteinen", "Anatominen rakennekuva, rasva kirkas"),
         ("T2-painotteinen", "Patologia ja turvotus, neste kirkas"),
         ("FLAIR", "Supprimoi CSF-signaali, periventrilulaarinen patologia"),
         ("DWI", "Diffuusiorajoittuma — akuutti infarkti"),
     ]),

    # Radionuklidihoidot ja kohdenuklidi/sairaus
    (33, 3,
     "Yhdistä radionuklidihoidot niiden kohdistusmolekyyleihin tai käyttöaiheisiin.",
     "Jokainen hoito perustuu nukliidin kohdennettuun kulkeutumiseen kasvainkudokseen.",
     [
         ("¹³¹I (radiojodi)", "Kilpirauhaselle natriumi-jodidi-symportteri (NIS)"),
         ("¹⁷⁷Lu-PSMA-617", "Eturauhassyövän PSMA-proteiini"),
         ("¹⁷⁷Lu-DOTA-oktreotaatti", "Neuroendokriiniset kasvaimet (SSTR)"),
         ("²²³Ra-kloridi", "Osteolyyttiset luustometastaasit"),
     ]),

    # TT: Hounsfield-yksikköarvot
    (21, 2,
     "Yhdistä kudostyypit tyypillisiin Hounsfield-yksikköarvoihinsa (HU).",
     "HU-asteikko on kalibroitu veden (0 HU) ja ilman (-1000 HU) suhteen.",
     [
         ("Ilma", "-1000 HU"),
         ("Rasva", "-80 … -100 HU"),
         ("Pehmytkudos / lihas", "+30 … +60 HU"),
         ("Luu (kortikaalinen)", "+400 … +1000 HU"),
     ]),

    # Sädehoidon fraktiointi: α/β-arvot
    (27, 4,
     "Yhdistä kudostyypit tyypillisiin α/β-arvoihinsa sädehoidossa.",
     "α/β-arvo kuvaa kudoksen herkkyyttä fraktiokoon muutokselle.",
     [
         ("Eturauhassyöpä", "~1,5–2 Gy"),
         ("Pienisolulinen keuhkosyöpä", "~10 Gy"),
         ("Aivoselkäydinjatkos (late)", "~2 Gy"),
         ("Limakalvo (early)", "~8–12 Gy"),
     ]),
]


class Command(BaseCommand):
    help = 'Seed example true_false, calculation, and matching questions for UI testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Delete existing seeded example questions before adding new ones',
        )

    def handle(self, *args, **options):
        # Build EPA cache
        epa_cache = {}
        for epa in EPA.objects.all():
            epa_cache[epa.id] = epa

        if options['clear']:
            deleted, _ = Question.objects.filter(
                hint='seeded_example'
            ).delete()
            self.stdout.write(self.style.WARNING(f"Cleared {deleted} existing example questions."))

        created_tf = 0
        created_calc = 0
        created_matching = 0

        with transaction.atomic():
            # --- TRUE/FALSE ---
            for epa_id, difficulty, text, is_true, explanation in TRUE_FALSE_DATA:
                epa = epa_cache.get(epa_id)
                if not epa:
                    self.stdout.write(self.style.WARNING(f"EPA {epa_id} not found, skipping."))
                    continue

                # Avoid duplicate seeds
                if Question.objects.filter(text=text, question_type='true_false').exists():
                    continue

                q = Question.objects.create(
                    question_type='true_false',
                    difficulty=difficulty,
                    text=text,
                    explanation=explanation,
                    hint='seeded_example',
                    epa=epa,
                )
                Choice.objects.create(
                    question=q, text='Oikein', is_correct=is_true, order=0,
                    explanation=explanation if is_true else '',
                )
                Choice.objects.create(
                    question=q, text='Väärin', is_correct=not is_true, order=1,
                    explanation='' if is_true else explanation,
                )
                created_tf += 1

            # --- CALCULATION ---
            for epa_id, difficulty, text, answer, tol, unit, explanation in CALCULATION_DATA:
                epa = epa_cache.get(epa_id)
                if not epa:
                    continue

                if Question.objects.filter(text=text[:60], question_type='calculation').exists():
                    continue

                Question.objects.create(
                    question_type='calculation',
                    difficulty=difficulty,
                    text=text,
                    explanation=explanation,
                    hint='seeded_example',
                    calculation_answer=answer,
                    calculation_tolerance=tol,
                    calculation_unit=unit,
                    epa=epa,
                )
                created_calc += 1

            # --- MATCHING ---
            for epa_id, difficulty, text, explanation, pairs in MATCHING_DATA:
                epa = epa_cache.get(epa_id)
                if not epa:
                    continue

                if Question.objects.filter(text=text[:60], question_type='matching').exists():
                    continue

                Question.objects.create(
                    question_type='matching',
                    difficulty=difficulty,
                    text=text,
                    explanation=explanation,
                    hint='seeded_example',
                    matching_pairs=[{'left': l, 'right': r} for l, r in pairs],
                    epa=epa,
                )
                created_matching += 1

        self.stdout.write(self.style.SUCCESS(
            f"Seeded: {created_tf} true_false, {created_calc} calculation, "
            f"{created_matching} matching questions."
        ))
        self.stdout.write(
            "Hint field 'seeded_example' marks these — use --clear to remove them."
        )
