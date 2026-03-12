# Sairaalafyysikko-alustan sisältötehtävät

> **Käyttö**: Aseta tämä tiedosto projektihakemistoon. Suorita tehtävät järjestyksessä. Jokainen tehtävä on itsenäinen kokonaisuus — tee yksi kerrallaan, varmista laatu, ja siirry seuraavaan.

---

## Edistymisen yhteenveto (päivitetty 2026-03-12)

| Tehtävä | Kuvaus | Tila |
|---------|--------|------|
| Tehtävä 1 | EPA-korttien teoriasisällön täydentäminen | ✅ Valmis (KNF 6/6, Isotooppi 7/7, Radiologia 9/9, Fysiologia 5/5, Sädehoito 7/7) |
| Tehtävä 2 | Vanhojen tenttikysymysten analyysi | ✅ Valmis |
| Tehtävä 3 | Monivalintakysymysten luominen (tavoite 600+) | ✅ Valmis (601 uutta MCQ:ta, 698 yhteensä) |
| Tehtävä 4 | Kaikkien MCQ:ien tarkistus | ✅ Valmis (698 tarkistettu, 12 faktavirhettä, 28 EPA-korjausta, 30 vaikeustasoa, 27 kirjoitusvirhettä, 36 duplikaattia deaktivoitu) |
| Tehtävä 5 | 246 mallivastauksen täydentäminen + faktatarkistus | ✅ Valmis (246 mallivastausta + 241 faktatarkistettu, loki: data/model_answer_review_log.md) |
| Tehtävä 6 | Edistymisen seuranta: Quiz→Progress-integraatio | ✅ Valmis (2026-02-19) |
| Tehtävä 7 | Käyttäjärekisteröinti + kirjautuminen | ✅ Valmis (2026-02-19) |
| Tehtävä 8 | AI-arviointi tenttiharjoitteluun (OpenAI GPT-4o) | ✅ Valmis (2026-02-19) |
| Tehtävä 9 | Hakutoiminto EPA-sisällöstä | ✅ Valmis (2026-02-19) |
| Tehtävä 10 | Saavutusjärjestelmän aktivointi (12 saavutusta) | ✅ Valmis (2026-02-19) |
| Tehtävä 11 | Heikkojen alueiden tunnistus + tenttivalmius | ✅ Valmis (2026-02-19) |
| Tehtävä 12 | Tenttisimulaatio (aikarajalla + AI-arviointi) | ✅ Valmis (2026-02-19) |
| Tehtävä 13 | Teoriakuvien lisääminen modaliteettisivuille | ✅ Valmis (2026-03-02) — 99 slottia 5 modaliteetissa |
| Tehtävä 14 | Isotooppi.html teoriasisällön laajennus Duodecim-lähteistä | ✅ Valmis (2026-03-09) — Sisältö jo kattava: SPET (sydän, kilpirauhanen, keuhkot, aivot, DAT, vartijaimusolmuke, lisäkilpirauhaset), PET (sydän, aivot FDG/amyloidi, eturauhassyöpä), radionuklidihoidot (jodi, PRRT, PSMA, SIRT, radiosynoviorthesis) |
| Tehtävä 15 | Usean kysymystyypin tuki teoriaquiziin | ✅ Valmis (2026-03-04) — MC, TF, calculation, matching kaikilla modaliteettisivuilla |
| Tehtävä 16 | Text-to-Speech (kuuntele-ominaisuus) | ✅ Valmis (2026-03-04) — OpenAI TTS, 5 modaliteettia, välimuisti |
| Tehtävä 17 | KNF-sivun quiz-osiot | ✅ Valmis (2026-03-04) — 6 välilehteä + tyyppivalitsimet |
| Tehtävä 18 | .env + python-dotenv -tuki | ✅ Valmis (2026-03-04) — API-avainten hallinta |
| Tehtävä 19 | Kysymysten merkitseminen + muistiinpanot | ✅ Valmis (2026-03-04) — FlaggedQuestion (3 tyyppiä) + QuestionNote, UI kaikissa quiz-tiloissa |
| Tehtävä 20 | Teoria ↔ Kysymys -ristiviittaus | ✅ Valmis (2026-03-04) — Teorialinkit vääriin vastauksiin, kysymysmäärä-badget tab-painikkeissa |
| Tehtävä 21 | Aukkotehtävät (Cloze deletion) | ✅ Valmis (2026-03-04) — `{{cN::answer::hint}}` -syntaksi, backend + frontend kaikissa quiz-tiloissa |
| Tehtävä 22 | SM-2 → FSRS algoritmipäivitys | ✅ Valmis (2026-03-05) — py-fsrs 6.3.0, 4-tasoinen arviointi, predicted intervals, retrievability |
| Tehtävä 23 | AI-muistikortit (Flashcards) | ✅ Valmis (2026-03-05) — GPT-4o generoi termi→selitys -kortit Section-sisällöstä, flip-card UI, FSRS-kertaus |
| Tehtävä 24 | AI-tutor/copilot — Tekoälypohjainen oppimisavustaja | ✅ Valmis (2026-03-06) — GPT-4o palvelinpuolella, chatbot-widget päivitetty, EPA-kontekstituki |
| Tehtävä 25 | Timed vs Tutor -moodi — Ajastettu tenttivalmistelu vs. välitön palaute | ✅ Valmis (2026-03-06) — moodinvalinta quiz_homessa, countdown-timer, per-kysymys tulossivu |
| Tehtävä 26 | Parannettu analytiikka — Trendikaaviot, aika/kysymys, ennustettu tenttipisteet | ✅ Valmis (2026-03-06) — 30-pv trendikaavio, 90-pv heatmap, vaikeimmat kysymykset, time_spent_seconds tallennus |
| Tehtävä 27 | Oppimispolut — Rakenteelliset opiskelusuunnitelmat erikoisaloittain | ✅ Valmis (2026-03-06) — /progress/paths/ yleiskatsaus + detailsivu per erikoisala, dashboard-widget |
| Tehtävä 28 | PWA ja offline-tuki — Asennettava verkkosovellus välimuistilla | ✅ Valmis (2026-03-06) — manifest.json, service worker, offline-sivu, SW-rekisteröinti base-templateen |
| Tehtävä 29 | Anki-vienti — Flashcardien vienti .apkg-muotoon | ✅ Valmis (2026-03-06) |
| Tehtävä 30 | Kysymyskohtaiset kommentit — Käyttäjien kommentit ja keskustelu per kysymys | ✅ Valmis (2026-03-06) |
| Tehtävä 31 | Adaptiivinen vaikeus — Automaattinen vaikeustason säätö suorituksen mukaan | ✅ Valmis (2026-03-06) |
| Tehtävä 32 | CKEditor-kuvien lataus inline-editoriin | ✅ Valmis (2026-03-12) — CKEditor integraatio teoria-inline-editoriin, kuvien upload/poisto |
| Tehtävä 33 | Inline-editorin auto-tallennuksen korjaus | ✅ Valmis (2026-03-12) — Auto-tallentaa kaikki avoimet välilehdet kun painetaan "Lopeta muokkaus" |
| Tehtävä 34 | TTS-äänivalinta | ✅ Valmis (2026-03-12) — 5 ääntä (nova♀, shimmer♀, echo♂, onyx♂, fable♂), localStorage-tallennus, äänenvaihto pysäyttää toiston |
| Tehtävä 35 | AI-chatbot-virheenkorjaus | ✅ Valmis (2026-03-12) — Lisätty puuttuva chatbot-status -elementti, korjattu ReferenceErrorit, chatbot toimii nyt luotettavasti |
| Tehtävä 36 | AI-chatbot laajennusmoodi | ✅ Valmis (2026-03-12) — Expand-painike laajentaa chatbotin 680px leveäksi (80vh), puristetaan takaisin samalla painikkeella |
| Tehtävä 37 | AI-chatbot äänikeskustelu | ✅ Valmis (2026-03-12) — Mikrofoninappi (Web Speech API STT fi-FI), botti vastaa Onyx-äänellä (TTS), mikrofonipainike pysäyttää botin puheen |
| Tehtävä 38 | Otsikoiden AI-kyselypainikkeet | ✅ Valmis (2026-03-12) — Kaksi robotti-painiketta jokaisessa h2/h3-otsikossa teoriastivuilla: teksti- ja äänivastausversio, kontekstina modaliteetti+välilehti+yläotsikko+tekstikatkelma |
| Tehtävä 39 | Sädehoito-sivun teoria Sädehoito-kansion PDF-materiaalista | ✅ Valmis (2026-03-12) — IMRT (sliding window/dMLC vs step-and-shoot), VMAT (jaw tracking, coplanar/non-coplanar), SRS/SBRT, fiducial markerit, IORT, BNCT, FLASH RT, Paddick CI + GI-kaavat, käyttötekijätaulukko NCRP 151 |
| Tehtävä 40 | Virheellisten erikoisalatietojen poistaminen | ✅ Valmis (2026-03-12) — Poistettu 4 virheellistä Specialty-tietuetta (Yleiset, raportoi_ongelma, Isotooppi, Yleinen) + niiden EPAt ja 10 kysymystä tietokannasta |

---

## Tilannekuva (helmikuu 2026)

### EPA-korttien sisältötilanne

| Erikoisala | EPA-kortteja | Sektioita | Tyhjät sektiot | Puutteellisuus |
|---|---|---|---|---|
| Radiologia | 9 | 129 | 0 (0%) | ✅ Valmis |
| KNF | 6 | 109 | 0 (0%) | ✅ Valmis |
| Fysiologia | 5 | 64 | 0 (0%) | ✅ Valmis |
| Sädehoito | 7 | 101 | 0 (0%) | ✅ Valmis |
| Isotooppilääketiede | 7 | 76 | 0 (0%) | ✅ Valmis |

### Tenttikysymysten mallivastaukset

| Erikoisala | Kysymyksiä | Mallivastauksia | Puuttuu |
|---|---|---|---|
| Anatomia | 87 | 87 | 0 ✅ |
| Radiologia | 108 | 108 | 0 ✅ |
| Sädehoito | 95 | 95 | 0 ✅ |
| Isotooppilääketiede | 82 | 82 | 0 ✅ |
| KNF | 50 | 50 | 0 ✅ |
| Kliininen fysiologia | 65 | 65 | 0 ✅ |

### Monivalintakysymykset (quiz)

698 kysymystä + 2784 vastausvaihtoehtoa (601 uutta luotu 2026-02-18). Kaikki 34 EPAa katettu tasaisesti (13–36 MCQ:ta per EPA).

---

## Tehtävä 1: EPA-korttien teoriasisällön täydentäminen

### Tavoite
T�ydennä tyhjät ja puutteelliset EPA-korttien sektiot kattavalla teoriasisällöllä.

### Prioriteettijärjestys ja tarkistuslista

**KNF (94% tyhjä — 103/109 sektiota):**
- [x] EEG — perusteet, elektrodiasettelut, normaalit rytmit, poikkeavuudet (20/20 sektiota täydennetty)
- [x] Herätepotentiaali ja ENMG — SEP, VEP, BAEP, EMG, hermonjohtuminen (20/20 sektiota täydennetty)
- [x] Sarja-TMS — rTMS-protokollat, turvallisuus, käyttöaiheet (17/17 sektiota täydennetty)
- [x] Uni — polysomnografia, signaalit, uniluokittelu (19/19 sektiota täydennetty)
- [x] IOM — intraoperatiivinen neuromonitorointi, menetelmät (20/20 sektiota täydennetty)
- [x] Laite- ja sähköturvallisuus — IEC 60601, mittaukset, huolto (13/13 sektiota täydennetty)

**Isotooppilääketiede (0% tyhjä — 0/76 sektiota) ✅:**
- [x] Gammakamera — rakenne, laadunvalvonta (16/16 sektiota täydennetty)
- [x] PET-kamera — rakenne, kalibrointi, suorituskyky (15/15 sektiota täydennetty)
- [x] Annostelu ja radiofarmasia — radiolääkkeet, laadunvalvonta (10/10 sektiota täydennetty)
- [x] Gammakuvaus ja SPET — kuvausprotokollat, rekonstruktio (4/4 sektiota täydennetty)
- [x] PET-tutkimukset — FDG, muut merkkiaineet, kvantifiointi (4/4 sektiota täydennetty)
- [x] Radionuklidihoidot — I-131, Lu-177, Ra-223, annosmittaus (10/10 sektiota täydennetty)
- [x] Säteilybiologia ja suojelu — annokset, kontaminaatio, jätehuolto (17/17 sektiota täydennetty)

**Kliininen fysiologia (0% tyhjä — 0/64 sektiota) ✅:**
- [x] EKG — kirjallisuus, tiedonhaku (2/2 sektiota korjattu)
- [x] GI-kanavan tutkimukset — kirjallisuus, henkilökunnan ohjaus, tiedonhaku (3/3 sektiota korjattu)
- [x] Keuhkofunktiotutkimukset — kaikki 8 sektiota: otsikot korjattu (PET/SPECT → keuhkofunktio), sisältö kirjoitettu (8/8 sektiota korjattu)
- [x] Luuston mineraalitiheys (DXA) — kaikki 14 sektiota: tekniikka, ROI, kalibraatio, laadunvarmistus, raportointi (14/14 sektiota korjattu)
- [x] Verenkiertotutkimukset — kaikki 14 sektiota: fysiologia, oskillometria, ABPM, ABI, PPG, validointi (14/14 sektiota korjattu)

**Radiologia (0% tyhjä — 0/129 sektiota) ✅:**
- [x] Natiivikuvantaminen — kirjallisuus, potilasannos, laadunvarmistus, kliiniset tutkimukset (4/4 korjattu)
- [x] Magneettikuvaus — kaikki 16 sektiota: laitteisto, turvallisuus, sekvenssit, artefaktit, kliiniset tutkimukset (16/16 korjattu)
- [x] Mammografia — kirjallisuus, erikoistutkimukset (3/3 korjattu)
- [x] Ultraääni — kirjallisuus ja bioturvallisuus (1/1 korjattu)
- [x] Säteilybiologia ja suojelu — kaikki 15 sektiota: lainsäädäntö, biologia, riskit, annossuureet, tilasuunnittelu, auditointi (15/15 korjattu)
- [x] Hammaskuvantaminen — kirjallisuus (2/2 korjattu)
- [x] Läpivalaisu ja angiografia — kaikki 16 sektiota: laitteisto, annos, artefaktit, varjoaineet, kliiniset tutkimukset (16/16 korjattu)
- [x] Tietokonetomografia — kirjallisuus, digitaalinen kuva, kliiniset ja erikoistutkimukset (5/5 korjattu)
- [x] Kuvankatselunäytöt — kirjallisuus ja standardit (2/2 korjattu)

**Sädehoito (0% tyhjä — 0/101 sektiota) ✅:**
- [x] Peruskäsitteet — kirjallisuus MSO korjattu (1/1 korjattu)
- [x] Kuvantaminen ja suunnittelu — kirjallisuus MSO korjattu (1/1 korjattu)
- [x] Ulkoinen sädehoito — 2 kirjallisuus-MSO korjattu (2/2 korjattu)
- [x] Sisäinen sädehoito — kirjallisuus MSO korjattu (1/1 korjattu)
- [x] Dosimetria — 2 kirjallisuus-MSO korjattu + STUK-laitetarkastus kirjoitettu (3/3 korjattu)
- [x] Laitteet — 2 kirjallisuus-MSO + lineaarikiihdyttimen QA + laitehankintaprosessi (4/4 korjattu)
- [x] Säteilybiologia — normaalikudostoleranssi uudelleenkirjoitettu + 2 kirjallisuus-MSO + kliininen auditointi (4/4 korjattu)

### Kirjallisuuslähteet joista sinun tulee ammentaa

**KNF:**
- Malmivuo: Bioelectromagnetism (http://www.bem.fi/book/index.htm — vapaasti verkossa)
- Nunez & Srinivasan: Electric Fields of the Brain, 2nd ed., Oxford 2006
- Rubin & Daube: Clinical Neurophysiology, Oxford
- Webster: Medical Instrumentation, 4th ed., Wiley 2010
- Ilmoniemi & Sarvas: Brain Signals, MIT Press 2019
- IEC 60601-1 -standardi (pääperiaatteet)

**Sädehoito:**
- Khan: The Physics of Radiation Therapy, 6th ed., Lippincott Williams & Wilkins
- ICRU-raportit
- STUK S/5/2019 (säteilyturvallisuus)
- STUK-STO-TR1 (annosmittaukset)
- IAEA TRS-483 (pienten kenttien dosimetria)

**Radiologia:**
- Webb's: Physics of Medical Imaging, 2nd ed., CRC Press 2012
- Dowsett: The Physics of Diagnostic Imaging, CRC Press 2006
- Kalender: Computed Tomography, 3rd ed., Publicis 2011
- McRobbie: MRI from Picture to Proton, 3rd ed., Cambridge 2017
- STUK-oppaat (mammografia, röntgenlaitteiden laadunvalvonta, KKTT, kardiologia)

**Isotooppilääketiede:**
- Cherry, Sorenson, Phelps: Physics in Nuclear Medicine, 4th ed., Elsevier 2012
- Bushberg: The Essential Physics of Medical Imaging, 3rd ed., Lippincott 2012
- EANM-suositukset (www.eanm.org)
- STUK: Isotooppitutkimuslaitteiden laadunvalvontaopas 2010

**Fysiologia:**
- Malmivuo: Bioelectromagnetism
- Kligfield et al: Recommendations for the standardization and interpretation of the electrocardiogram, Circulation 115(10), 2007
- Alpert et al: Oscillometric blood pressure, J Am Soc Hypertens 8(12), 2014
- Käypä hoito -suositukset (kohonnut verenpaine ym.)
- ISCD Official Positions 2019

### Työtapa

1. Lue ensin EPA-kortin koulutuskortin kuvaus (A- ja B-osaamistasot) tiedostosta `Erikoistuvan_-sairaalafyysikon_koulutuskortit_Neuvottelukunta_2021__1_.pdf`
2. Tarkista tietokannasta nykyinen sisältö: `python manage.py dumpdata sisalto.section --indent 2 | python -c "import sys,json; [print(f'{s[\"fields\"][\"title\"]}: {len(s[\"fields\"][\"content\"])} chars') for s in json.load(sys.stdin) if s['fields']['epa']==EPA_ID]"`
3. Kirjoita sisältö HTML-muodossa (CKEditor5-yhteensopiva): käytä `<h3>`, `<p>`, `<ul>`, `<table>`, `<strong>`, `<em>` -tageja
4. Päivitä tietokantaan Django shellissä tai management commandilla
5. Sisällön tulee kattaa koulutuskortin A- ja B-osaamistavoitteet kattavasti
6. Matemaattiset kaavat MathJax-muodossa: `\( kaava \)` inline, `\[ kaava \]` display

### Sisällön vaatimukset

- **Laajuus**: Jokaisen ei-tyhjän sektion tulee olla vähintään 500 merkkiä, tyypillisesti 1000-3000 merkkiä
- **Tarkkuus**: Fysiikan kaavat, yksiköt ja arvot oikein. Varmista SI-yksiköt.
- **Käytännönläheisyys**: Yhdistä teoria kliiniseen käytäntöön (miten fyysikko soveltaa tätä sairaalassa)
- **Kieli**: Suomi. Tieteelliset termit suomeksi, englanninkielinen termi suluissa ensimmäisellä mainintakerralla.
- **Rakenne**: Jokaisella sektiolla on yksi selkeä aihe. Älä toista samaa asiaa eri sektioissa.

### Tietokantaoperaatiot

```python
# Päivitä yksittäinen sektio
from sisalto.models import Section
section = Section.objects.get(epa__id=EPA_ID, title__startswith="A1.")
section.content = "<h3>Otsikko</h3><p>Sisältö...</p>"
section.save()

# Tai bulk-päivitys
sections_data = {
    "A1. ...": "<h3>...</h3><p>...</p>",
    "A2. ...": "<h3>...</h3><p>...</p>",
}
for title_start, content in sections_data.items():
    Section.objects.filter(epa__id=EPA_ID, title__startswith=title_start[:20]).update(content=content)
```

---

## Tehtävä 2: Vanhojen tenttikysymysten analyysi

### Tavoite
Analysoi kaikki 487 vanhaa tenttikysymystä ja luo raportti.

### Tarkistuslista

- [x] Hae ja luokittele kaikki 487 tenttikysymystä erikoisaloittain
- [x] Analysoi aihepiirijakauma (mitkä teemat toistuvat useimmin)
- [x] Arvioi vaikeustasot (perus / soveltava / vaativa)
- [x] Tunnista puuttuvat aihealueet suhteessa EPA-osaamistavoitteisiin
- [x] Tallenna raportti: `data/exam_analysis.md`
- [x] Validoi raportti vertaamalla EPA-korttien kattavuuteen

### Työtapa

1. Hae kaikki tenttikysymykset: `ExamQuestion.objects.all().order_by('subject_area', 'year')`
2. Luo raportti jossa:
   - Aihepiirijakauma erikoisaloittain
   - Toistuvat teemat (mitkä aiheet kysytään useimmiten)
   - Vaikeustason arvio (perus/soveltava/vaativa)
   - Puuttuvat aihealueet suhteessa EPA-korttien osaamistavoitteisiin
3. Tallenna raportti: `data/exam_analysis.md`

### Hyödyntäminen
Raportti ohjaa tehtäviä 3 ja 5 — monivalintakysymykset tulee kohdistaa tenteissä toistuviin teemoihin, ja mallivastaukset priorisoidaan yleisimpien aiheiden mukaan.

---

## Tehtävä 3: Monivalintakysymysten luominen tenttikysymyksistä

### Tavoite
Luo jokaisesta tenttikysymyksestä 5-15 monivalintakysymystä (quiz.Question, quiz.Choice) jotka testaavat samaa aihetta eri näkökulmista.

### Nykyinen tilanne
- 487 tenttikysymystä, 97 olemassa olevaa monivalintakysymystä
- Tavoite: vähintään 600 uutta monivalintakysymystä

### Tarkistuslista (erikoisaloittain)

- [x] **Radiologia** — 152 MCQ:ta (EPA 1,2,3,4,18,19,20,21,22)
- [x] **Sädehoito** — 110 MCQ:ta (EPA 16,17,23,24,25,26,27)
- [x] **Isotooppilääketiede** — 89 MCQ:ta (EPA 28,29,30,31,32,33,34)
- [x] **Anatomia / yleisfysiikka** — 86 MCQ:ta (EPA 4,8,9,14,19,22,30,31,32,33,34)
- [x] **Kliininen fysiologia** — 81 MCQ:ta (EPA 11,12,13,14,15)
- [x] **KNF** — 83 MCQ:ta (EPA 5,6,7,8,9,10)
- [x] EPA-mapping validointi — kaikki 34 EPAa katettu (13–36 MCQ:ta per EPA)

### Kysymysten laatu

Jokainen kysymys tarvitsee:
- `question_text`: Selkeä, yksiselitteinen kysymys suomeksi
- `question_type`: "multiple_choice" (4 vaihtoehtoa, 1 oikea)
- `difficulty`: 1-5 (1=perus, 3=tenttitaso, 5=erittäin vaativa)
- `explanation`: Miksi oikea vastaus on oikea (2-4 lausetta)
- `epa`: Linkitä oikeaan EPA-korttiin (käytä alla olevaa mappingia)
- 4 vastausvaihtoehtoa (Choice):
  - 1 oikea (`is_correct=True`) + selitys miksi oikea
  - 3 väärää (`is_correct=False`) + selitys miksi väärä
  - Väärät vaihtoehdot tulee olla uskottavia (eivät ilmiselvän vääriä)

### EPA-mapping tenttikysymyksistä

```python
# Tenttikysymyksen subject_area → sopiva EPA (id)
AREA_TO_EPAS = {
    'Radiologia': {
        'CT': 21,          # Tietokonetomografia
        'MRI': 2,          # Magneettikuvaus
        'UÄ': 4,           # Ultraääni
        'mammografia': 3,  # Mammografia
        'natiivi': 1,      # Natiivikuvantaminen
        'läpivalaisu': 7,  # Läpivalaisu ja angiografia
        'näyttö': 9,       # Kuvankatselunäytöt
        'hammas': 6,       # Hammaskuvantaminen
        'säteilybiologia': 5,  # Säteilybiologia radiologiassa
        'default': 1,
    },
    'Sädehoito': {
        'dosimetria': 25,    # Dosimetria
        'ulkoinen': 23,      # Ulkoinen sädehoito
        'sisäinen': 24,      # Sisäinen sädehoito
        'laitteet': 26,      # Laitteet
        'biologia': 27,      # Säteilybiologia
        'kuvantaminen': 22,  # Kuvantaminen ja suunnittelu
        'default': 16,       # Peruskäsitteet
    },
    'Isotooppilääketiede': {
        'gamma': 28,     # Gammakamera
        'PET': 29,       # PET-kamera
        'SPET': 31,      # Gammakuvaus ja SPET
        'hoito': 33,     # Radionuklidihoidot
        'farmasia': 30,  # Annostelu ja radiofarmasia
        'default': 28,
    },
    'KNF': {
        'EEG': 10,     # EEG
        'ENMG': 11,    # Herätepotentiaali ja ENMG
        'TMS': 15,     # TMS
        'uni': 14,     # Uni
        'IOM': 12,     # IOM
        'default': 10,
    },
    'Kliininen fysiologia': {
        'EKG': 16,          # EKG-tutkimukset
        'verenkierto': 20,  # Verenkiertotutkimukset
        'keuhko': 18,       # Keuhkofunktiotutkimukset
        'GI': 17,           # GI-kanavan tutkimukset
        'DXA': 19,          # Luuston mineraalitiheys
        'default': 16,
    },
    'Anatomia': {
        'default': 16,  # EKG (lähin)
    },
}
```

### Työtapa

Käytä management commandia `generate_exam_quiz.py` pohjana. Paranna:

1. Hae tenttikysymys ja sen mahdollinen mallivastaus kontekstiksi
2. Hae linkitetyn EPA-kortin teoriasisältö kontekstiksi
3. Generoi 2-4 monivalintakysymystä per tenttikysymys
4. Varmista ettei duplikaatteja synny (tarkista question_text similariteetti)
5. Aseta vaikeus tenttikysymyksen luonteen mukaan

### Tietokantaoperaatiot

```python
from quiz.models import Question, Choice
from sisalto.models import EPA, ExamQuestion

q = Question.objects.create(
    question_type='multiple_choice',
    question_text='Kysymysteksti',
    explanation='Selitys',
    difficulty=3,
    epa=EPA.objects.get(id=21),
    source_exam_question=exam_question,  # jos kenttä on olemassa
)
Choice.objects.create(question=q, text='Oikea vastaus', is_correct=True, explanation='Miksi oikea')
Choice.objects.create(question=q, text='Väärä 1', is_correct=False, explanation='Miksi väärä')
Choice.objects.create(question=q, text='Väärä 2', is_correct=False, explanation='Miksi väärä')
Choice.objects.create(question=q, text='Väärä 3', is_correct=False, explanation='Miksi väärä')
```

---

## Tehtävä 4: Olemassa olevien monivalintakysymysten tarkistus

### Tavoite
Käy läpi kaikki nykyiset monivalintakysymykset ja vastausvaihtoehdot. Tarkista ja korjaa virheet.

### Tarkistuslista

- [x] **Radiologia** MCQ:t tarkistettu (213 kpl: 5 kriittistä, 9 kohtalaista, 6 pieniä, 11 EPA, 11 duplikaattia)
- [x] **Sädehoito** MCQ:t tarkistettu (131 kpl: 3 kriittistä, 11 kohtalaista, 7 pieniä, 3 EPA, 8 duplikaattia)
- [x] **Isotooppilääketiede** MCQ:t tarkistettu (133 kpl: 2 kriittistä, 9 kohtalaista, 8 pieniä, 6 EPA, 6 duplikaattia)
- [x] **KNF** MCQ:t tarkistettu (110 kpl: 3 kriittistä, 11 kohtalaista, 6 pieniä, 4 EPA, 9 duplikaattia)
- [x] **Kliininen fysiologia** MCQ:t tarkistettu (111 kpl: 3 kriittistä, 12 kohtalaista, 8 pieniä, 10 EPA, 2 duplikaattia)
- [x] EPA-mapping tarkistettu ja korjattu kaikille kysymyksille (28 korjausta)
- [x] Korjaukset kirjattu lokiin: `data/quiz_review_log.md`

### Tarkistettavat asiat

1. **Faktavirheet**: Onko oikea vastaus oikeasti oikea? Ovatko väärät oikeasti vääriä?
2. **Yksiselitteisyys**: Onko kysymyksessä vain yksi oikea vastaus? Voiko väärästä vaihtoehdosta argumentoida oikeaksi?
3. **Selitykset**: Onko explanation-kenttä informatiivinen ja täsmällinen?
4. **Vaikeusaste**: Onko difficulty realistinen (1=perus, 5=vaativa)?
5. **Kieliasu**: Suomen kieli oikein, termit johdonmukaisia
6. **Kattavuus**: Ovatko väärät vaihtoehdot uskottavia mutta selkeästi vääriä?

### Työtapa

1. Hae kaikki kysymykset: `Question.objects.prefetch_related('choices').all()`
2. Käy läpi erikoisaloittain
3. Tarkista jokainen kysymys EPA-kortin teoriasisältöä ja kirjallisuutta vasten
4. Korjaa suoraan tietokannassa: `question.question_text = "..."; question.save()`
5. Kirjaa muutokset lokiin: `data/quiz_review_log.md`

### Erityishuomiot

- Sädehoidon kysymykset: Varmista annosten yksiköt (Gy, cGy), energiat (MeV, keV) ja etäisyydet oikein
- Radiologian kysymykset: TT-numerot (HU), kuvausparametrit (kV, mAs)
- Isotooppilääketieteen kysymykset: Puoliintumisajat, energiat, radionuklidit oikein
- KNF: EEG-taajuuskaistat (delta, theta, alpha, beta), amplitudit

---

## Tehtävä 5: Tenttikysymysten mallivastausten täydentäminen ja tarkistus

### Tavoite
1. Tarkista olemassa olevat mallivastausta — korjaa virheet
2. Kirjoita puuttuvat mallivastaukset

### Tarkistuslista (puuttuvat mallivastaukset)

- [x] **Anatomia** — 87 mallivastausta (3 erää, 2026-02-18/19)
- [x] **Sädehoito** — 43 mallivastausta (2026-02-19)
- [x] **Isotooppilääketiede** — 42 mallivastausta (2 erää, 2026-02-19)
- [x] **Radiologia** — 34 mallivastausta (2 erää, 2026-02-19)
- [x] **KNF** — 22 mallivastausta (2026-02-19)
- [x] **Kliininen fysiologia** — 18 mallivastausta (2026-02-19)
- [x] Olemassa olevien mallivastausten faktatarkistus (241 kpl, 2026-02-19)
- [x] Korjaukset kirjattu lokiin: `data/model_answer_review_log.md` (65 löydöstä, 13 kriittistä)

### Prioriteettijärjestys (puuttuvat)
1. **Anatomia** — nämä ovat poikkitieteellisiä, kirjoita lääketieteellisen fysiikan näkökulmasta
2. **Sädehoito**
3. **Isotooppilääketiede** 
4. **Radiologia**
5. **KNF** 
6. **Kliininen fysiologia**

### Mallivastauksen laatu

- **Laajuus**: 400-1000 sanaa riippuen kysymyksen laajuudesta
- **Rakenne**: Aloita ytimekkäällä vastauksella, sitten perustele ja syvennä
- **Kaavat**: MathJax-muoto, selitä muuttujat
- **Kliininen relevanssi**: Yhdistä teoria käytäntöön
- **Viittaukset**: Mainitse relevantti lähde/standardi kun mahdollista (esim. "IAEA TRS-398 mukaan...")
- **Pisteytysohje**: Mallivastaus toimii AI-arvioinnin referenssinä — sen tulee olla riittävän kattava että AI voi verrata opiskelijan vastausta siihen

### Työtapa

```python
from sisalto.models import ExamQuestion

# Puuttuvat mallivastaukset
missing = ExamQuestion.objects.filter(model_answer='').order_by('subject_area', 'year')

# Päivitä mallivastaus
eq = ExamQuestion.objects.get(id=123)
eq.model_answer = "Mallivastaus tähän..."
eq.save()
```

### Olemassa olevien mallivastausten tarkistus

1. Lue mallivastaus ja vertaa EPA-kortin teoriaan ja kirjallisuuteen
2. Tarkista faktat: kaavat, arvot, yksiköt, prosessikuvaukset
3. Tarkista kattavuus: vastaako kaikki kysymyksen osa-alueet
4. Tarkista kieli: selkeä suomi, johdonmukainen terminologia
5. Kirjaa korjaukset: `data/model_answer_review_log.md`

---

## Tehtävä 6: Edistymisen seuranta — Quiz → Progress -integraatio

### Tavoite
Kytke quiz-vastaukset progress-tietokantamalleihin, toteuta toimiva dashboard ja spaced repetition -kertausjärjestelmä.

### Tarkistuslista

- [x] **Quiz → Progress -integraatio** (`quiz/views.py`)
  - [x] `_persist_quiz_progress()` helper: tallentaa UserQuizAttempt, päivittää SpacedRepetitionCard (SM-2), DailyStats, EPAProgress
  - [x] `api_check_answer()` kutsuu persistointiä kirjautuneille käyttäjille
  - [x] Kirjautumattomat käyttäjät: quiz toimii edelleen session-pohjaisesti
- [x] **Älykäs kysymysvalinta** (`quiz/views.py: api_get_question()`)
  - [x] 35% todennäköisyydellä valitsee kysymyksen johon käyttäjä on aiemmin vastannut väärin (matala ease_factor < 2.2)
  - [x] 65% satunnainen valinta kuten ennen
- [x] **Spaced repetition -kertaus** (`quiz/views.py` + `quiz/templates/quiz/spaced_review.html`)
  - [x] `spaced_review()` view: näyttää due-korttien määrän
  - [x] `api_get_review_question()` GET: palauttaa seuraavan kerattavan kortin JSON:ina
  - [x] `api_submit_review()` POST: tarkistaa vastauksen ja päivittää SR-kortin
  - [x] Täysi kertaus-UI: AJAX-pohjainen flow, SM-2 info, "kaikki tehty" -tila
  - [x] URL-patterit: `/quiz/api/review/question/`, `/quiz/api/review/answer/`
- [x] **Progress dashboard** (`progress/views.py` + `progress/templates/progress/progress_home.html`)
  - [x] `progress_home()`: oikeat kyselyt tietokannasta (UserQuizAttempt, DailyStats, EPAProgress, SpacedRepetitionCard)
  - [x] `_calculate_streak()`: peräkkäiset aktiiviset päivät
  - [x] 4 tilastokorttia: vastattuja, oikein-%, putki, XP
  - [x] Viikkokaavio: 7 päivän pylväskaavio (CSS-pohjainen, `{% widthratio %}`)
  - [x] EPA-edistyminen erikoisaloittain: progress bar + answered/total
  - [x] Kertaus-painike: "X kysymystä kerattävänä" → `/quiz/spaced-review/`
  - [x] Tyhjä tila uusille käyttäjille
- [x] **Quiz-harjoittelun lopetuspainike** (`quiz/templates/quiz/quiz_practice.html`)
  - [x] "Lopeta" -painike tulospalkkiin
  - [x] Yhteenveto-tila: näyttää tulokset (vastattuja, oikein, prosentti)
  - [x] Navigaatiolinkit: Kysymyspankki + Edistyminen
  - [x] JavaScript-handler kytketty
- [x] **Asetukset** (`sivusto/settings.py`)
  - [x] `LOGIN_URL = '/admin/login/'` (ei erillistä kirjautumissivua)

### Tekniset tiedot

- SM-2-algoritmi: `SpacedRepetitionCard.update_after_review(quality)` — quality 0-5, ease_factor mukautuu
- Oikein → quality 5, intervalli kasvaa (1→3→7→14→30→60+ pv)
- Väärin → quality 1, intervalli palautuu 1 päivään
- XP: 10 oikeasta, 2 väärästä vastauksesta
- Kaikki toimii vain kirjautuneille — @login_required tai `request.user.is_authenticated` tarkistus

---

## Tehtävä 7: Käyttäjärekisteröinti + kirjautuminen (2026-02-19)

### Tavoite
Lisää erillinen kirjautumis- ja rekisteröintisivu (ei pelkästään admin-kirjautuminen).

### Tarkistuslista

- [x] **Settings**: `LOGIN_URL = '/login/'`, `LOGIN_REDIRECT_URL = '/'`, `LOGOUT_REDIRECT_URL = '/'`
- [x] **URLs** (`sivusto/urls.py`): `login/`, `logout/`, `register/`
- [x] **RegistrationForm** (`sisalto/forms.py`): UserCreationForm + email, suomenkieliset labelit
- [x] **register_view** (`sisalto/views.py`): POST → validoi → luo käyttäjä → auto-login → redirect
- [x] **Login-template** (`sisalto/templates/registration/login.html`): Nordic Observatory -tyyli
- [x] **Register-template** (`sisalto/templates/registration/register.html`): Nordic Observatory -tyyli
- [x] **Header-linkit** (`base_summereditor.html`): `{% if user.is_authenticated %}` → kirjaudu ulos / kirjaudu sisään

---

## Tehtävä 8: AI-arviointi tenttiharjoitteluun (2026-02-19)

### Tavoite
Kytke OpenAI GPT-4o tenttikysymysten esseearvioihin. Pisteytys 0-5, sanallinen palaute.

### Tarkistuslista

- [x] **openai SDK** asennettu (`pip install openai` → openai-2.21.0)
- [x] **ai_evaluator.py** (`sisalto/ai_evaluator.py`): GPT-4o, `response_format={"type": "json_object"}`, 5s rate limit per user
- [x] **ExamAnswer-malli** (`sisalto/models.py`): lisätty user FK, ai_score, ai_feedback, ai_strengths, ai_weaknesses, ai_suggestions, ai_evaluated_at, self_score
- [x] **Migraatio**: `0011_examanswer_ai_evaluated_at_...` luotu ja ajettu
- [x] **API-endpoint** (`sisalto/views.py: ai_evaluate_exam_answer()`): POST `/exam/ai-evaluate/`
- [x] **exam_practice.html**: AI-painike, latausanimaatio, tulososio, JS `{% block extra_js %}`-blokissa
- [x] **Ympäristömuuttuja**: `OPENAI_API_KEY` tarvitaan

---

## Tehtävä 9: Hakutoiminto EPA-sisällöstä (2026-02-19)

### Tavoite
Lisää hakutoiminto jolla käyttäjä voi etsiä sisältöä EPA-sektioista ja tenttikysymyksistä.

### Tarkistuslista

- [x] **search_view** (`sisalto/views.py`): `icontains`-haku Section + ExamQuestion, max 50 tulosta per tyyppi
- [x] **URL**: `/search/` (`sisalto/urls.py`)
- [x] **search_results.html**: kaksi tulosryhmää (EPA-sisältö + tenttikysymykset), snippet-korostus
- [x] **Header-hakukenttä** (`base_summereditor.html`): form nav-linkkien jälkeen

---

## Tehtävä 10: Saavutusjärjestelmän aktivointi (2026-02-19)

### Tavoite
Aktivoi 12 saavutusta, kytke tarkistus vastausfloweihin ja näytä UI:ssa.

### Tarkistuslista

- [x] **seed_achievements** (`progress/management/commands/seed_achievements.py`): 12 saavutusta (questions, streak, correct_streak, exam_pass, mastery)
- [x] **achievement_checker.py** (`progress/achievement_checker.py`): `check_achievements(user)` → tarkistaa kaikki ehdot
- [x] **Quiz-integraatio** (`quiz/views.py: api_check_answer()`): kutsuu check_achievements, palauttaa JSON:issa
- [x] **SR-integraatio** (`quiz/views.py: api_submit_review()`): kutsuu check_achievements
- [x] **Exam-integraatio** (`sisalto/views.py: ai_evaluate_exam_answer()`): kutsuu check_achievements
- [x] **Toast-ilmoitukset**: quiz_practice.html, spaced_review.html, exam_practice.html — `showAchievementToast()`
- [x] **Achievements-sivu** (`progress/templates/progress/achievements.html`): earned/locked grid
- [x] **Viimeisimmät saavutukset** (`progress/templates/progress/progress_home.html`): viimeiset 5 dashboardissa
- [x] **Seeded**: `python manage.py seed_achievements` → 12 saavutusta tietokannassa

### 12 saavutusta

| Koodi | Tyyppi | Ehto | XP |
|---|---|---|---|
| first_question | questions | 1 | 10 |
| ten_questions | questions | 10 | 25 |
| fifty_questions | questions | 50 | 50 |
| hundred_questions | questions | 100 | 100 |
| five_hundred_questions | questions | 500 | 250 |
| streak_3 | streak | 3 | 30 |
| streak_7 | streak | 7 | 75 |
| streak_30 | streak | 30 | 300 |
| correct_streak_5 | correct_streak | 5 | 40 |
| correct_streak_10 | correct_streak | 10 | 100 |
| first_exam | exam_pass | 1 | 50 |
| epa_mastery | mastery | 80 | 150 |

---

## Tehtävä 11: Heikkojen alueiden tunnistus + tenttivalmius (2026-02-19)

### Tavoite
Tunnista käyttäjän heikoimmat EPAt ja näytä tenttivalmiusarvio dashboardissa.

### Tarkistuslista

- [x] **Weak EPAs** (`progress/views.py`): matalin oikein-% (min 5 vastausta) → top 5
- [x] **Erikoisalavalmius** (`progress/views.py`): accuracy × coverage per erikoisala
- [x] **Tenttivalmius** (`progress/views.py`): painotettu kokonaisarvio
- [x] **"Harjoittele näitä"** -osio (`progress_home.html`): 5 heikointa EPAa + linkki quiziin
- [x] **"Tenttivalmius"** -osio (`progress_home.html`): kokonaisprosentti + erikoisalapalkit
- [x] Näkyy vain kun käyttäjällä on >20 vastausta

---

## Tehtävä 12: Tenttisimulaatio (2026-02-19)

### Tavoite
Aikarajallinen tenttisimulaatio jossa käyttäjä vastaa esseekysymyksiin ja AI arvioi jokaisen.

### Tarkistuslista

- [x] **simulation_setup** (`exams/views.py`): erikoisalan, kysymysmäärän (3-10) ja aikarajan (30-180 min) valinta
- [x] **simulation_start** (`exams/views.py`): satunnaisten ExamQuestion-kysymysten valinta, session-tallennus
- [x] **simulation_active** (`exams/views.py` + template): kysymykset + JS-ajastin + auto-submit
- [x] **Sekventiaali AI-arviointi**: JS kutsuu `/exam/ai-evaluate/` per kysymys, X-Simulation-Session header
- [x] **simulation_results** (`exams/views.py` + template): kokonaispistemäärä, hyväksytty/hylätty, per-kysymys palaute
- [x] **exams_home.html**: simulaatio-CTA + Nordic Observatory -tyyli
- [x] **URLs** (`exams/urls.py`): 5 patternia (home, setup, start, active, results)

### Flow
```
/exams/simulation/ → valitse erikoisala + kysymysmäärä + aikaraja
→ /exams/simulation/start/ (POST) → valitsee satunnaiset kysymykset
→ /exams/simulation/active/ → kirjoita vastaukset, ajastin
→ Submit → JS arvioi kysymykset 1/N yksitellen (/exam/ai-evaluate/)
→ /exams/simulation/<session_id>/results/ → tulokset
```

---

## Yleisiä ohjeita Claude Codelle

### Kieli ja terminologia
- Kaikki sisältö suomeksi
- Tieteelliset termit: suomeksi, englanninkielinen vastine suluissa ensimmäisellä kerralla
- Johdonmukainen terminologia läpi koko alustan (esim. aina "tietokonetomografia" eikä sekaisin "TT" / "CT" / "tietokonetomografia")

### Tietokanta
- Tee aina `python manage.py dumpdata` ennen ja jälkeen muutosten (varmuuskopiointi)
- Käytä transaktioita bulk-operaatioissa
- Testaa muutokset: `python manage.py runserver` ja tarkista selaimessa

### Sisällön formaatti
- EPA-korttien sektiot: HTML (CKEditor5-yhteensopiva)
- Mallivastaukset: plaintext tai kevyt HTML
- Monivalintakysymykset: plaintext (ei HTML:ää question_text-kentässä)
- Kaavat: MathJax (`\( ... \)` inline, `\[ ... \]` display)

### Versionhallinta
- Commitoi jokaisen tehtävän jälkeen erikseen
- Commit-viesti: "Content: [tehtävä] - [kuvaus]"
  - Esim: "Content: Task 1 - KNF EPA sections complete"
  - Esim: "Content: Task 3 - 150 new MCQs for Radiologia"
  - Esim: "Content: Task 5 - Model answers for Anatomia complete"

---

## Tehtävä 13: Teoriakuvien lisääminen modaliteettisivuille (✅ Valmis 2026-03-02)

### Tavoite
Lisää kuvanhallinnan mahdollisuus kaikkiin modaliteettiteoriasivuihin. Superuser voi ladata kuvia teoriakuvapaikkoihin (theory-image-slot), jotka näkyvät oikeassa sivupalkissa tekstin vieressä.

### Toteutettu

**Malli ja migraatiot:**
- `TheoryImage` malli (`sisalto/models.py`): kentät `modality`, `tab_id`, `slot_id`, `image`, `caption`, `alt_text`, `display_size`
- Migraatiot: `0012_theoryimage`, `0013_theoryimage_display_size`

**API-endpointit** (`sisalto/urls.py` + `sisalto/views.py`):
- `GET /modaliteetit/api/theory-images/<modality>/` — palauttaa kaikki kuvat modaliteetille
- `POST /modaliteetit/api/theory-images/upload/` — lataa uuden kuvan slottiin
- `POST /modaliteetit/api/theory-images/delete/` — poistaa kuvan slotista

**HTML-kuvio** (jokaisessa html-tiedostossa):
```html
<div class="theory-image-slot" data-slot="SLOT_ID" data-tab="TAB_ID" data-default-caption="Kuvan otsikko"></div>
```
Sijoitussääntö: h3-osion ALUSSA ennen ensimmäistä p/ul-elementtiä. EI koskaan suoraan ennen `<h2>`:ta (sillä on `clear:right` CSS).

**Views.py-kuvio** (jokaisessa view-funktiossa):
```python
return render(request, 'sisalto/modaliteetit/X.html', {
    'modality_id': 'X',
    'is_superuser': request.user.is_superuser,
    ...
})
```

**JavaScript**: Aina `{% block extra_js %}` -blokissa (ei `{% block content %}` -blokissa), koska `getCookie()` on määritelty vasta rivillä 508 pohjatemplatessa.

### Slottimäärät modaliteeteittain

| Modaliteetti | Slotteja | Välilehdet |
|---|---|---|
| radiologia | 24 | läpivalaisu, mri, mammografia, natiivi, tt, us, naytot, hammas, sateilybiologia |
| isotooppi | 22 | gammakamera, pet, radiofarmasia, spet, pet-tutkimukset, radionuklidihoidot, sateilybiologia |
| knf | 18 | eeg, heratepotentiaali, iom, uni, tms, laiteturvallisuus |
| fysiologia | 14 | ekg, verenkierto, keuhkofunktio, gi, dxa |
| sadehoito | 21 | peruskasitteet, kuvantaminen, ulkoinen, sisainen, dosimetria, laitteet, sateilybiologia |
| **Yhteensä** | **99** | |

---

## Tehtävä 14: Isotooppi.html teoriasisällön laajennus Duodecim-lähteistä (✅ Valmis — 2026-03-09)

### Tavoite
Laajenna `isotooppi.html`:n kolmen välilehden (SPET, PET-tutkimukset, Radionuklidihoidot) teoriasisältöä käyttäen 7 Duodecim-kirjasta kopioitua tekstitiedostoa projektin juuressa.

### Tila
Isotooppi.html (3455 riviä) sisältää jo kattavasti kaiken oleellisen sisällön 7 Duodecim-lähteestä. Kaikki suunnitellut operaatiot A–F oli jo toteutettu aiemmissa sessioissa.

### Toteutettu sisältö (6 operaatiota — kaikki valmiit)

- [x] **A** — SPET: 2.2 Sydänperfuusio (merkkiaineet, protokolla, bull's eye, MUGA, MIBG) + 2.3 Kilpirauhaskuvaus (123I/perteknetaatti, esivalmistelut, tulkinta)
- [x] **B** — SPET: 2.5 Keuhkot (MAA, Technegas vs DTPA, PISA-PED-kriteerit taulukko, preop FEV1)
- [x] **C** — SPET: 3.1 Aivoperfuusio + 3.1b DAT-SPET ([123I]FP-CIT, Parkinson/LBD, tauotukset) + 3.2 Vartijaimusolmuke + 3.7 Lisäkilpirauhaset
- [x] **D** — PET: 2.2 Sydän (Rb-82/N-13/O-15, kvantifiointi ml/g/min, viabiliteetti FDG, sarkoidoosi/endokardiitti) + 2.3 Aivot FDG-PET + amyloidikuvaus taulukko
- [x] **E** — PET: 3.1 Eturauhassyöpä (koliini/flusikloviini/68Ga-PSMA-11/18F-PSMA-1007/Na18F, PSA-relapsi, staging)
- [x] **F** — Radionuklidihoidot: jodihoidot, PRRT, PSMA-PRLT, radiosynoviorthesis, SIRT, lymfooma-immunosädehoito

### HTML-konventiot

```html
<!-- Info-laatikoille -->
<div class="theory-info"><strong>Muista:</strong> ...</div>
<!-- Varoituksille -->
<div class="theory-warning"><strong>Huomio:</strong> ...</div>
<!-- Isotooppimerkinnät -->
<sup>99m</sup>Tc, <sup>18</sup>F, <sup>123</sup>I, <sup>177</sup>Lu
<!-- Kuvauspaikoille -->
<div class="theory-image-slot" data-slot="slot-id" data-tab="tab-id"></div>
```

---

## Tehtävä 24: AI-tutor/copilot (⬜ Tekemättä — KORKEA PRIORITEETTI)

### Tavoite
Toteuta tekoälypohjainen oppimisavustaja joka osaa vastata opiskelijan kysymyksiin EPA-teoriasisällön ja kontekstin perusteella. Käyttäjä voi kysyä minkä tahansa EPA:n tai kysymyksen aiheesta, saada selityksiä, pyytää esimerkkejä ja jatkaa keskustelua.

### Ominaisuudet
- Kelluvaa chat-paneeli joka on käytettävissä koko alustalla (quiz, teoria, tenttiharjoittelu)
- Kontekstitietoisuus: tietää minkä EPA:n tai kysymyksen parissa käyttäjä työskentelee
- Backend-endpoint käyttää OpenAI GPT-4o (sama kuin `sisalto/ai_evaluator.py`)
- Viestihistoria tallennettuna session-pohjaisesti tai tietokantaan
- Syöte: käyttäjän kysymys + EPA-konteksti (teoriateksti, nykyinen kysymys)
- EPA-teoria haetaan automaattisesti kontekstiksi

### Toteutussuunnitelma

**Backend:**
- Uusi endpoint: `POST /api/tutor/chat/` (`sisalto/views.py`)
- Parametrit: `{message, epa_id, question_id, conversation_id}`
- Vastaus: `{reply, conversation_id, usage}`
- Kontekstin kokoaminen: `EPA.title + Section.content[:3000]`
- OpenAI GPT-4o, `temperature=0.7`, `max_tokens=1500`
- Conversation history: max 10 viestiparia (sliding window)

**Frontend:**
- Kelluva chat-widget (`position: fixed; bottom: right`) — kaikissa sivupohjissa
- Avautuu painikkeesta (pyöreä sininen nappi, kuplaikkoni)
- Chat-paneeli: viestit, syötekenttä, lähetä-nappi
- Tuki pikanäppäimille: Enter = lähetä, Escape = sulje
- Markdown-renderöinti vastauksille (bold, listat, koodit)
- Latausindikaattori API-kutsun aikana

**Tiedostot:**
- `sisalto/views.py` — uusi `ai_tutor_chat()` view
- `sisalto/urls.py` — uusi URL-pattern
- `sisalto/static/sisalto/js/ai-tutor.js` — chat-widget JS
- `sisalto/static/sisalto/css/ai-tutor.css` — widgetin tyyli
- `sisalto/templates/sisalto/base_summereditor.html` — widget + skriptit footer-alueelle

### Priorisointi
Tämä on tärkein puuttuva ominaisuus (UWorld AI Tutor, AMBOSS Ask AMBOSS -verrokit). Toteuta ensin.

---

## Tehtävä 25: Timed vs Tutor -moodi (⬜ Tekemättä — KORKEA PRIORITEETTI)

### Tavoite
Lisää quiz-harjoitteluun kaksi eri moodia: **Tutor-moodi** (nykyinen: välitön palaute jokaisen vastauksen jälkeen) ja **Timed-moodi** (ajastettu tenttiharjoittelu ilman välitöntä palautetta).

### Timed-moodi
- Käyttäjä valitsee ennen harjoittelun aloitusta: kysymysmäärä (10/25/50) + aikaraja (minuutteina)
- Näyttää ajastimen (countdown timer) sivun yläosassa
- Ei näytä oikeaa vastausta tai selitystä kysymyksen jälkeen
- Kun aika loppuu tai kaikki vastattu → tulossivu
- Tulossivu: oikein/väärin per kysymys + selitykset kootusti lopussa

### Toteutus
- `quiz_home.html`: moodin valinta UI (radio-buttons tai toggle)
- `quiz_practice.html`: uusi `timed-mode` JS-logiikka
- `api_get_question()`: lisää `session_id`-tuki timed-moodille (ryhmittely per istunto)
- `api_check_answer()`: palauta tulos mutta ei selitystä jos `mode=timed`
- Session-pohjainen tallenne: `quiz_session_{id}` → lista question_id + user_answer

---

## Tehtävä 26: Parannettu analytiikka (✅ Valmis — 2026-03-06)

### Tavoite
Laajenna progress-dashboardia konkreettisemmilla oppimisanalytiikoilla jotka auttavat käyttäjää ymmärtämään edistymistään paremmin.

### Uudet visualisoinnit
1. **Trendikaavio** — 30 päivän tarkkuusprosentti (line chart, Chart.js tai CSS-pohjainen)
2. **Aika per kysymys** — keskimääräinen vastaamisaika (tallennettava frontend-aika) + jakauma
3. **Ennustettu tenttipisteet** — lasketaan accuracy × coverage × difficulty, skaalataan 0-5
4. **Heatmap** — viimeisen 3 kuukauden aktiivisuus (GitHub-tyylinen päiväkohtainen heatmap)
5. **Vaikeimmmat kysymykset** — top 10 eniten väärin vastattu (suora linkki kysymykseen)

### Toteutus
- `UserQuizAttempt`-malliin: `time_spent_seconds` IntegerField (optional)
- Progress-dashboard API: uusi `GET /progress/api/stats/` → JSON-data kaavioille
- Chart.js CDN — yksinkertaiset, kevyet kaaviot
- Mobiiliresponsiiivisuus: kaaviot skrollaantuvat vaakasuunnassa

---

## Tehtävä 27: Oppimispolut (✅ Valmis — 2026-03-06)

### Tavoite
Strukturoidut opiskelusuunnitelmat jotka ohjaavat käyttäjän EPA-alueiden läpi järjestyksessä erikoisalakohtaisesti.

### Rakenne
- Viisi oppimispolkua (yksi per erikoisala): Radiologia, Sädehoito, Isotooppilääketiede, KNF, Kliininen fysiologia
- Jokainen polku: EPA-kortit järjestyksessä (perusteet ensin, erikoisosaaminen myöhemmin)
- Edistyminen: % EPA-korteista "hallussa" (mastery threshold)
- Seuraava askel -suositus: mikä EPA kannattaa opiskella seuraavaksi

### Toteutus
- Uusi sivu: `/progress/learning-path/` tai `/modaliteetit/polku/<specialty>/`
- `LearningPath` -malli tai staattiset konfiguraatiot (dict-pohjainen riittää alussa)
- Dashboard-integraatio: "Jatka polkua" -kortti

---

## Tehtävä 28: PWA ja offline-tuki (✅ Valmis — 2026-03-06)

### Tavoite
Tee alustasta asennettava progressiivinen verkkosovellus (PWA) joka toimii rajoitetusti myös offline-tilassa.

### Toteutus
- `manifest.json` — sovelluksen metadata (nimi, ikoni, värit)
- `service-worker.js` — välimuististrategi (Cache-first EPA-sisällölle, Network-first API:lle)
- iOS/Android-asennettavuus
- Offline-fallback: "Olet offline-tilassa, tässä viimeksi katsomasi sisältö"

---

## Tehtävä 29: Anki-vienti (✅ Valmis — 2026-03-06)

### Tavoite
Mahdollista AI-generoitujen flashcardien vienti Anki-yhteensopivaan `.apkg`-muotoon.

### Toteutus
- Endpoint: `GET /quiz/flashcards/export/anki/?epa_id=X` tai kaikki
- Python-kirjasto: `genanki` (`pip install genanki`)
- Deck: EPA-nimi, kortit: front/back, tagit: erikoisala + EPA
- Käyttöliittymä: "Vie Ankiin" -painike flashcard-sivulla

---

## Tehtävä 30: Kysymyskohtaiset kommentit (✅ Valmis — 2026-03-06)

### Tavoite
Mahdollista käyttäjien välinen kommentointi yksittäisissä kysymyksissä (erityishyödyllinen virheellisten selitysten tai epäselvien muotoilujen ilmoittamiseen).

### Toteutus
- Uusi malli: `QuestionComment(question, user, text, created_at, is_resolved)`
- Moderointi: superuser voi merkata kommentit ratkaistuiksi
- UI: "Kommentit" -osio jokaisen kysymyksen selitysosiossa
- Admin-integraatio: kommentit admin-paneelissa

---

## Tehtävä 31: Adaptiivinen vaikeus (✅ Valmis — 2026-03-06)

### Tavoite
Kysymysten automaattinen vaikeustason säätö käyttäjän suorituksen perusteella, niin että harjoittelu pysyy sopivan haastavana (Goldilocks-vyöhyke).

### Toteutus
- Tavoiteoikein-prosentti: 75–85% (liian helppo → vaikeampi, liian vaikea → helpompi)
- `api_get_question()`: suodata kysymykset käyttäjäkohtaisen difficulty-kohteen perusteella
- Liukuva ikkuna: viimeiset 20 vastausta → laske accuracy → säädä difficulty_target
- Tallennus: `UserProfile`-malliin tai sessio-muuttujaan
