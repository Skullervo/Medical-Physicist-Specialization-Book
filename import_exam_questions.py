#!/usr/bin/env python
"""
Skripti tenttikysymysten tuomiseen tietokantaan
"""
import os
import sys
import django
import re

# Django setup
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sivusto.settings')
django.setup()

from sisalto.models import ExamQuestion

def parse_year_and_semester(date_str):
    """Parsii vuosiluvun ja lukukauden päivämäärästä"""
    date_str = date_str.strip()
    
    # Täydelliset päivämäärät (esim. "4/29/2016")
    date_match = re.search(r'(\d{1,2})/(\d{1,2})/(\d{4})', date_str)
    if date_match:
        year = int(date_match.group(3))
        month = int(date_match.group(1))
        semester = "kevät" if month <= 6 else "syksy"
        return year, semester
    
    # Kuukausi ja vuosi (esim. "touko 2019")
    month_year_match = re.search(r'(touko|kesäkuu|syksy|Feb|May|Oct)\s*(\d{4})', date_str)
    if month_year_match:
        year = int(month_year_match.group(2))
        month = month_year_match.group(1).lower()
        if month in ['touko', 'may', 'kesäkuu']:
            semester = "kevät"
        elif month in ['syksy', 'oct']:
            semester = "syksy"
        elif month in ['feb']:
            semester = "kevät"
        else:
            semester = ""
        return year, semester
    
    # Vuosi ja kuukausi (esim. "8.2.2019")
    euro_date_match = re.search(r'(\d{1,2})\.(\d{1,2})\.(\d{4})', date_str)
    if euro_date_match:
        year = int(euro_date_match.group(3))
        month = int(euro_date_match.group(2))
        semester = "kevät" if month <= 6 else "syksy"
        return year, semester
    
    # Pelkkä kuukausi ja lyhyt vuosi (esim. "Feb-20")
    short_match = re.search(r'(Feb|May|Oct|Mar)-(\d{2})', date_str)
    if short_match:
        year = 2000 + int(short_match.group(2))
        month = short_match.group(1)
        semester = "kevät" if month in ['Feb', 'May', 'Mar'] else "syksy"
        return year, semester
    
    return None, ""

def parse_subject_area(question_text):
    """Yrittää tunnistaa aihealueen kysymystekstistä"""
    question_lower = question_text.lower()
    
    if any(word in question_lower for word in ['anatomia', 'fysiologia', 'rakenne', 'toiminta', 'luun', 'sydämen', 'maksan']):
        return "Anatomia & fysiologia"
    elif any(word in question_lower for word in ['eeg', 'emg', 'enmg', 'herätepotentiaali', 'kliininen neurofysiologia', 'unihäiriö']):
        return "Kliininen neurofysiologia"
    elif any(word in question_lower for word in ['isotooppi', 'gammakuvaus', 'spet', 'pet', 'radionuklidi', 'merkkiaine']):
        return "Isotooppilääketiede"
    elif any(word in question_lower for word in ['magneetti', 'mri', 'tietokonetomografia', 'ttk', 'ultraääni', 'röntgen']):
        return "Radiologia"
    elif any(word in question_lower for word in ['sädehoito', 'lineaarikiihdytin', 'annosjakauma', 'brakyterapia', 'fraktio']):
        return "Sädehoito"
    elif any(word in question_lower for word in ['spirometria', 'keuhkofunktio', 'verenpaine', 'ekg']):
        return "Fysiologia"
    else:
        return "Muu"

# Tenttikysymysten data
exam_data = [
    {
        "date": "4/29/2016",
        "questions": [
            "Pitkän luun rakenne",
            "EKG:n pitkäaikaisrekisteröinnin (holter) laitteisto ja datan analyysi pääpiirteissään",
            "Gammakameran tekninen laadunvarmistus",
            "Rauhaskudosannoksen määritys mammografiassa",
            "Millaisilla menetelmillä voidaan mitata sädehoitoannosta hoidon aikana (=in vivo). A) ihon pinnalta b) kudoksesta/kehon ontelonsta c) potilaan läpimennyttä annosta",
            "Millaisilla testeillä voit todeta tarkkuustason jolla sädehoitolaitteeseen integroitu röntgenkuvaukseen perustuva kuvanohjausjärjestelmä kohdistaa hoidettavan kohteen varsinaiset (hoito)säteilyisosentrin suhteen?"
        ]
    },
    {
        "date": "2/12/2016", 
        "questions": [
            "Silmän akkomodaatio ja taittovirheet",
            "EEG-laitteen laadunvarmistusmittaukset. Mikä on tarpeellista, mikä turhaa ja miten kehittäisit sitä",
            "Potilaan isotooppitutkimuksesta saamaan säteilyannoksen arvioiminen",
            "Kuvavääristymät (artefaktat) magneettikuvissa",
            "Vertaile tyypillisiä säästävästi ja radikaalisti (ablaatiolla) leikatun rintasyövän sädehoitotekniikoita: A) annosjakaumat kohdealueella ja terveissa kudoksissa, erityisesti keuhkot ja sydän B) hoitotekniikan tekninen yksinkertaisuus C) mahdolliset lisämenetelmän terveen kudoksen annoksen pienentämiseksi",
            "Kerro kuvantamismahdollisuuksista sädehoitofraktion aikaisen liikkeen havaitsemiseksi"
        ]
    },
    {
        "date": "10/16/2015",
        "questions": [
            "Luukudos",
            "Jatkuvan verenpainemittauksen ei-invasiiviset mittausmenetelmät ja niiden käyttö kliinisen fysiologian laboratoriossa",
            "Keuhkojen isotooppitutkimukset. Käytettävät merkkiaineet, aktiivisuudet ja potilaalle aiheutuva säteilyannos",
            "Tietokonetomografiatutkimuksen optimointi. Käytettävät menetelmät ja niiden vaikutus potilaan säteilyaltistukseen ja kuvanlaatuun",
            "Mitä voit kertoa sädehoidon nykyisten annoslaskentamenetelmien suorituskyvystä a) vesiekvivalentissa materiaalissa lähellä kentän keskiakselia b) kentän ulkopuolella c) keuhkokudoksessa d) metallisen lonkaaproteesin vieressä",
            "Sädehoitoon tulevalla potilaalla on sydämentahdistin. Miten asia huomioidaan annossuunnittelumagneettikuvauksessa ja rintakehän alueen sädehoidon suunnittelussa ja toteutuksessa?"
        ]
    },
    {
        "date": "2/6/2015",
        "questions": [
            "Munuaisten rakenne ja toiminta",
            "Transkraniaalinen magneettistimulaatio: toimintaperiaate, laitteisto ja sovellusalueet",
            "Kilpirauhasen radioisotooppihoidot: menetelmän perusteet ja säteilysuojelutoimet",
            "UÄ-laitteiden laadunvarmistus. Mikä on tarpeellista, mikä turhaa, miten kehittäisin sitä?",
            "Miten toimit seuraavissa tilanteissa a) Epäilen vikaa sädehoidon absoluuttidosimetrian mittausketjussa b) Sädehoidon lineaarikiihdytin antaa hoitotilanteessa turvalukiskeskeytyksen (interlock), joka varoittaa kentän epätasaisuudesta c) sädehoidon lineaarikiihdyttimen annostaso on aamumittauksessa 5% suurempi, kuin referenssitaso",
            "Metalliartefaktat sädehoidon suunnittelukuvauksissa: Vaikutus annokseen ja korjausmahdollisuudet"
        ]
    },
    {
        "date": "touko 2019",
        "questions": [
            "Pyramidirata ja sen merkitys motoriikassa",
            "IOM, perusteet, virhelähteet, käyttöaiheet, jne.",
            "MR-PET, detektoritekniikka",
            "Keinot ja menetelmät nopeuttaa MRI-kuvausta VS. perinteinen SE-sekvenssi",
            "Brakyterapian laadunvarmistustoimenpiteet lähteen vaihdon jälkeen",
            "Hengityspidätys ja hengitystahdistus sädehoidossa"
        ]
    },
    {
        "date": "Feb-20",
        "questions": [
            "Potilaalla vasemmassa kyynärtaipeessa kanyyli, kuvaa varjoaineen kierto",
            "Video-EEG tutkimuksen valmistelu ja toteutus",
            "Vertaile tc99m ja I-131",
            "MRI-vierasesine selvittely: a) kuvauksesta luopuminen, b) kuvauksen suorittaminen varotoimenpiteineen, c) kuvaus normaalisti",
            "Pienien kenttien dosimetria, toteutus ja haasteet",
            "Sädetyksen paikan monitorointi hoidon aikana"
        ]
    },
    {
        "date": "Oct-22",
        "questions": [
            "Naisen sukuelimet ja niiden toiminta",
            "KNF-laitteiden laadunvarmistus",
            "Aivojen hermovälittäjäaineiden gammakuvaus",
            "Kaksoisenergia vs perinteinen TT",
            "Sädehoidon annosmittauksiin käytettävän mittalaitteiston laadunvarmistus",
            "Metalliartefaktit sädehoidon suunnittelukuvauksissa"
        ]
    }
]

def import_questions():
    """Tuodaan kysymykset tietokantaan"""
    print("Tuodaan tenttikysymyksiä tietokantaan...")
    
    # Tyhjennetään vanhat kysymykset
    ExamQuestion.objects.all().delete()
    
    for exam in exam_data:
        date_str = exam["date"]
        year, semester = parse_year_and_semester(date_str)
        
        for i, question_text in enumerate(exam["questions"], 1):
            subject_area = parse_subject_area(question_text)
            
            question = ExamQuestion.objects.create(
                exam_date=date_str,
                question_number=i,
                question_text=question_text,
                subject_area=subject_area,
                year=year,
                semester=semester
            )
            
            print(f"Luotu: {date_str} Q{i} - {subject_area}")
    
    print(f"\nTuotu yhteensä {ExamQuestion.objects.count()} kysymystä tietokantaan!")

if __name__ == "__main__":
    import_questions()