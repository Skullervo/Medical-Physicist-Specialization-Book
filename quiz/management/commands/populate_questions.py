"""
Populate quiz database with multiple choice questions based on EPA theory content.

Usage:
    python manage.py populate_questions
    python manage.py populate_questions --clear  # Clear existing questions first
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from sisalto.models import EPA
from quiz.models import Question, Choice


# Questions organized by EPA ID
# Each question: (type, difficulty, text, explanation, [(choice_text, is_correct, explanation), ...])
QUESTIONS = {
    # ===== RADIOLOGIA - Tietokonetomografia (EPA 21) =====
    21: [
        (
            "multiple_choice", 2,
            "Mikä on TT-laitteen gantry-yksikön päätehtävä?",
            "Gantry sisältää röntgenputken ja detektorijärjestelmän, jotka kiertävät potilaan ympärillä mahdollistaen säteilyn mittaamisen useista kulmista.",
            [
                ("Sisältää röntgenputken ja detektorit, jotka kiertävät potilaan ympärillä", True, "Gantry on TT-laitteen keskeisin komponentti, jossa röntgenputki ja detektorit kiertävät potilasta."),
                ("Ohjaa potilaspöydän liikettä", False, "Potilaspöydän liike ohjataan erillisellä järjestelmällä."),
                ("Tallentaa kuvadatan PACS-järjestelmään", False, "Tiedon tallennus tapahtuu ohjaus- ja tietojenkäsittelyjärjestelmässä."),
                ("Tuottaa varjoaineen injektion", False, "Varjoaineen injektio tehdään erillisellä injektorilaitteella."),
            ],
        ),
        (
            "multiple_choice", 2,
            "Mikä matemaattinen muunnos on TT-kuvantamisen teoreettinen perusta?",
            "Radon-muunnos esittää funktion integraalit kaikilla mahdollisilla suorilla, ja sen käänteismuunnos mahdollistaa kuvan rekonstruoinnin projektioista.",
            [
                ("Radon-muunnos", True, "Radon-muunnos kuvaa säteilymittauksia eri kulmista ja etäisyyksiltä, ja sen inversio on TT-rekonstruktion perusta."),
                ("Fourier-muunnos", False, "Fourier-muunnosta käytetään apuna rekonstruktiossa, mutta se ei ole TT:n teoreettinen perusta."),
                ("Laplace-muunnos", False, "Laplace-muunnosta käytetään säätötekniikassa, ei TT-kuvantamisessa."),
                ("Hilbert-muunnos", False, "Hilbert-muunnosta ei käytetä suoraan TT-rekonstruktiossa."),
            ],
        ),
        (
            "multiple_choice", 1,
            "Mikä on CTDIvol-suureen yksikkö?",
            "CTDIvol (volume Computed Tomography Dose Index) ilmoitetaan milligrayina (mGy).",
            [
                ("mGy", True, "CTDIvol ilmoitetaan milligrayina ja se kuvaa keskimääräistä annosta yksittäisessä leikkeessä."),
                ("mSv", False, "mSv on efektiivisen annoksen yksikkö, ei CTDIvol."),
                ("mGy·cm", False, "mGy·cm on DLP:n (Dose Length Product) yksikkö."),
                ("cGy", False, "cGy käytetään sädehoidossa, ei TT-annosten ilmoittamisessa."),
            ],
        ),
        (
            "multiple_choice", 3,
            "Miten CTDIw (painotettu CTDI) lasketaan?",
            "CTDIw on painotettu keskiarvo keskustan ja reunan CTDI-mittauksista.",
            [
                ("CTDIw = 1/3 × CTDI_center + 2/3 × CTDI_periphery", True, "Painotettu CTDI antaa suuremman painon reunamittauksille, koska fantomissa annos on suurempi reunoilla."),
                ("CTDIw = 1/2 × CTDI_center + 1/2 × CTDI_periphery", False, "Tasapaino ei ole oikea painotus."),
                ("CTDIw = 2/3 × CTDI_center + 1/3 × CTDI_periphery", False, "Painotus on päinvastainen: reunalle annetaan suurempi paino."),
                ("CTDIw = CTDI_center × pitch", False, "Pitch huomioidaan CTDIvol-laskennassa, ei CTDIw:ssä."),
            ],
        ),
        (
            "multiple_choice", 2,
            "Miten potilasannos (D) riippuu mAs-arvosta TT-kuvauksessa?",
            "Annos on likimain suoraan verrannollinen mAs-arvoon.",
            [
                ("D on suoraan verrannollinen mAs-arvoon", True, "Kaksinkertainen mAs tarkoittaa kaksinkertaista annosta."),
                ("D on kääntäen verrannollinen mAs-arvoon", False, "Annos kasvaa mAs:n kasvaessa."),
                ("D on verrannollinen mAs:n neliöjuureen", False, "Tämä pätee kohinaan, ei annokseen."),
                ("D ei riipu mAs-arvosta", False, "mAs on yksi tärkeimmistä annokseen vaikuttavista parametreista."),
            ],
        ),
        (
            "multiple_choice", 3,
            "Mikä aiheuttaa säteilyn kovettumisartefaktin (beam hardening) TT-kuvassa?",
            "Polykromaattinen röntgenspektri muuttuu kulkiessaan tiheän materiaalin läpi, kun matalaenergiset fotonit absorboituvat enemmän.",
            [
                ("Matalaenergiset fotonit absorboituvat tiheässä materiaalissa enemmän, jolloin spektri kovenee", True, "Tämä vääristää vaimennusprofiilia ja aiheuttaa tummia juovia kuvaan (cupping effect)."),
                ("Detektorin herkkyyserot eri energioilla", False, "Tämä aiheuttaa rengasartefakteja, ei beam hardening -efektiä."),
                ("Potilaan liike kuvauksen aikana", False, "Liike aiheuttaa liikeartefakteja, ei beam hardening -efektiä."),
                ("Liian suuri pitch-arvo", False, "Liian suuri pitch voi aiheuttaa aliasointia, ei beam hardening -efektiä."),
            ],
        ),
        (
            "multi_select", 3,
            "Mitkä seuraavista ovat TT-kuvauksen artefaktien pääluokkia?",
            "TT-artefaktit jaetaan viiteen pääluokkaan: fyysiset, liike-, laitetekniset, metalli- sekä osittaisvolyymi- ja aliasointiartefaktit.",
            [
                ("Fyysiset artefaktit (esim. beam hardening)", True, "Johtuvat säteilyn ja aineen vuorovaikutuksesta."),
                ("Potilasliikkeen artefaktit", True, "Aiheutuvat liikkeestä kuvauksen aikana."),
                ("Metalliartefaktit", True, "Johtuvat voimakkaasta vaimennuksesta tai sironnasta."),
                ("Magneettikenttäartefaktit", False, "Magneettikenttäartefaktit liittyvät MRI-kuvantamiseen, eivät TT:hen."),
            ],
        ),
        (
            "multiple_choice", 2,
            "Miten DLP (Dose Length Product) lasketaan?",
            "DLP kuvaa potilaan kokonaissäteilyannosta koko skannauksen pituudelta.",
            [
                ("DLP = CTDIvol × L (skannauksen pituus)", True, "DLP ottaa huomioon sekä annoksen tason (CTDIvol) että kuvauksen laajuuden."),
                ("DLP = CTDIw × pitch", False, "Tämä on CTDIvol:n laskentakaava, ei DLP:n."),
                ("DLP = mAs × kVp", False, "mAs ja kVp ovat kuvausparametreja, eivät suoraan DLP:n laskentakaava."),
                ("DLP = CTDI₁₀₀ × detektorin leveys", False, "CTDI₁₀₀ on eri suure kuin CTDIvol."),
            ],
        ),
        (
            "multiple_choice", 2,
            "Mikä on automaattisen putkivirran säädön (ATCM) tyypillinen annosssäästö?",
            "ATCM säätää putkivirtaa potilaan läpäisevyyden mukaan reaaliajassa.",
            [
                ("20–40 % ilman kuvanlaadun heikkenemistä", True, "ATCM on tehokas tapa vähentää annosta optimoimalla putkivirta potilaan koon mukaan."),
                ("5–10 %", False, "Säästö on huomattavasti suurempi kuin 5–10 %."),
                ("50–70 %", False, "Näin suurta säästöä ei tyypillisesti saavuteta pelkällä ATCM:llä."),
                ("ATCM ei vaikuta annokseen", False, "ATCM:n nimenomaisin tavoite on annosoptimointi."),
            ],
        ),
        (
            "multiple_choice", 3,
            "Miten putkijännite (kVp) vaikuttaa TT-kuvan kontrastiin ja annokseen?",
            "Matalampi kVp parantaa pehmytkudoskontrastia mutta annos kasvaa voimakkaasti kVp:n kasvaessa (D ∝ kVp²⁻³).",
            [
                ("Matalampi kVp parantaa kontrastia, annos kasvaa likimain kVp:n 2.–3. potenssiin", True, "Matalampi kVp lisää fotoabsorptiota ja parantaa kontrastia erityisesti varjoainekuvissa."),
                ("Korkeampi kVp parantaa kontrastia ja pienentää annosta", False, "Korkeampi kVp heikentää pehmytkudoskontrastia."),
                ("kVp ei vaikuta kontrastiin", False, "kVp on yksi tärkeimmistä kontrastiin vaikuttavista tekijöistä."),
                ("Annos pienenee lineaarisesti kVp:n kasvaessa", False, "Annos kasvaa, ei pienene, kVp:n kasvaessa."),
            ],
        ),
    ],

    # ===== RADIOLOGIA - Mammografia (EPA 3) =====
    3: [
        (
            "multiple_choice", 2,
            "Mikä on mammografian tyypillinen putkijännitealue?",
            "Mammografiassa käytetään matalia jännitteitä parhaan pehmytkudoskontrastin saavuttamiseksi.",
            [
                ("22–35 kV", True, "Mammografiassa käytetään matalaenergistä (17–25 keV) spektriä, jossa pehmytkudosten kontrasti korostuu."),
                ("80–120 kV", False, "Nämä jännitteet ovat tyypillisiä perinteiselle röntgenkuvantamiselle."),
                ("40–60 kV", False, "Tämä alue on liian korkea mammografialle."),
                ("5–15 kV", False, "Nämä jännitteet ovat liian matalia tuottamaan diagnostista kuvaa."),
            ],
        ),
        (
            "multiple_choice", 2,
            "Mikä anodimateriaalin ja suodattimen yhdistelmä sopii parhaiten ohuen ja pehmeän rinnan kuvaamiseen?",
            "Mo/Mo-yhdistelmä tuottaa parhaan kontrastin ohuille rinnoille.",
            [
                ("Mo/Mo (molybdeeni/molybdeeni)", True, "Mo/Mo tuottaa kapean matalaenergisen spektrin, joka antaa parhaan pehmytkudoskontrastin ohuelle rinnalle."),
                ("W/Rh (volframi/rodium)", False, "W/Rh sopii paremmin paksuille rinnoille digitaalisissa DR-laitteissa."),
                ("W/Ag (volframi/hopea)", False, "W/Ag tuottaa leveämmän spektrin ja sopii paksummille rinnoille."),
                ("Cu/Al (kupari/alumiini)", False, "Tätä yhdistelmää ei käytetä mammografiassa."),
            ],
        ),
        (
            "multiple_choice", 2,
            "Mikä on rinnan puristuksen (kompressio) tärkein merkitys mammografiassa?",
            "Puristus pienentää rinnan paksuutta, mikä vähentää annosta ja parantaa kuvanlaatua.",
            [
                ("Pienentää rinnan paksuutta, vähentää annosta ja parantaa kontrastia", True, "Puristus on tärkein yksittäinen tekijä annoksen ja kuvanlaadun kannalta."),
                ("Estää potilaan liikkumisen", False, "Immobilisaatio on sivuhyöty, ei päätehtävä."),
                ("Tasaa kudostiheyserot", False, "Puristus ei muuta kudostiheyksiä."),
                ("Lyhentää kuvausaikaa", False, "Kuvausaika riippuu mAs-arvosta, ei puristuksesta."),
            ],
        ),
        (
            "multiple_choice", 3,
            "Mikä detektorimateriaalista käytetään digitaalisessa CR-mammografiassa (Computed Radiography)?",
            "CR-mammografiassa käytetään fotostimulaatioluminenssilevyjä.",
            [
                ("BaFBr:Eu (bariumfluorobromidi)", True, "CR-levyt perustuvat fotostimulaatioluminesenssiin ja baesiumfluorobromidi-materiaaliin."),
                ("CsI:Tl (cesiumjodidi)", False, "CsI:Tl on tyypillinen DR-detektorimateriaali."),
                ("Gd₂O₂S:Tb (gadoliniumoksisulfidi)", False, "Tätä käytetään vanhoissa filmikasettien fosforeissa."),
                ("Se (seleeni)", False, "Seleeniä käytetään suorakonversion DR-detektoreissa."),
            ],
        ),
        (
            "multiple_choice", 1,
            "Mikä on mammografian tyypillinen fokus-detektori-etäisyys (SID)?",
            "Mammografiassa käytetään lyhyempää etäisyyttä kuin muussa radiologiassa.",
            [
                ("60–70 cm", True, "Mammografiassa fokus-detektori-etäisyys on tyypillisesti 60–70 cm."),
                ("100–120 cm", False, "Tämä on tyypillinen SID perinteisessä radiografiassa."),
                ("150–180 cm", False, "Tämä on liian pitkä mammografialle."),
                ("30–40 cm", False, "Tämä on liian lyhyt tuottamaan diagnostista kuvaa."),
            ],
        ),
        (
            "multi_select", 3,
            "Mitkä seuraavista röntgenputken anodimateriaaleista ovat käytössä mammografiassa?",
            "Mammografiassa käytetään useita anodimateriaaleja eri rintaominaisuuksille.",
            [
                ("Molybdeeni (Mo)", True, "Mo-anodi tuottaa karakteristisen säteilyn mammografian optimaalialueella."),
                ("Rodium (Rh)", True, "Rh-anodia käytetään paksumpien rintojen kuvauksessa."),
                ("Volframi (W)", True, "W-anodi on nykyaikaisten digitaalisten mammografialaitteiden yleinen valinta."),
                ("Kupari (Cu)", False, "Kuparia ei käytetä mammografian anodimateriaalina."),
            ],
        ),
    ],

    # ===== SÄDEHOITO - Ulkoinen sädehoito (EPA 23) =====
    23: [
        (
            "multiple_choice", 1,
            "Mikä on yleisin laite ulkoisessa sädehoidossa?",
            "Lineaarikiihdytin (LINAC) on nykyaikaisen sädehoidon peruslaite.",
            [
                ("Lineaarikiihdytin (LINAC)", True, "LINAC tuottaa korkeaenergisiä fotoni- ja elektronisäteitä ja on yleisin sädehoitolaite."),
                ("Kobolttilaite (Co-60)", False, "Kobolttilaite on vanhempi ja nykyään harvinainen."),
                ("Betatroni", False, "Betatronit ovat historiallisia laitteita, eivät enää kliinisessä käytössä."),
                ("Röntgenputki", False, "Perinteinen röntgenputki ei tuota riittävän energistä säteilyä syvähoitoon."),
            ],
        ),
        (
            "multiple_choice", 2,
            "Mikä suure kuvaa annoksen vaihtelua syvyyssuunnassa säteilykentän keskiakselilla?",
            "PDD (Percentage Depth Dose) ilmaisee annoksen suhteessa referenssisyvyyteen.",
            [
                ("PDD (Percentage Depth Dose, suhteellinen syväannos)", True, "PDD kuvaa annoksen heikkenemistä kudoksessa syvyyden funktiona."),
                ("MU (Monitor Unit)", False, "MU on lineaarikiihdyttimen mittayksikkö, ei annosjakauman kuvaaja."),
                ("SAD (Source-to-Axis Distance)", False, "SAD on geometrinen etäisyysparametri."),
                ("DVH (Dose Volume Histogram)", False, "DVH kuvaa annosjakaumaa tilavuudessa, ei syvyyssuunnassa."),
            ],
        ),
        (
            "multiple_choice", 2,
            "Mikä on monitoriyksikön (MU) määritelmä lineaarikiihdyttimessä?",
            "MU on kalibroitu tuottamaan tietty annos referenssiolosuhteissa.",
            [
                ("1 MU tuottaa 1 cGy referenssipisteessä standardiolosuhteissa", True, "Tyypillisesti 10×10 cm kenttä, 100 cm SSD, dmax-syvyydessä."),
                ("1 MU vastaa 1 sekunnin säteilytysaikaa", False, "MU ei ole aika vaan annosyksikkö."),
                ("1 MU tuottaa 1 Gy", False, "1 MU tuottaa 1 cGy, ei 1 Gy."),
                ("MU mitataan potilaan pinnalta", False, "MU mitataan laitteen ionisaatiokammiosta."),
            ],
        ),
        (
            "multiple_choice", 3,
            "Mitkä tekijät vaikuttavat PDD:hen (suhteellinen syväannos)?",
            "PDD:hen vaikuttavat säteilyenergia, kentän koko, SSD ja säteilyn tyyppi.",
            [
                ("Säteilyenergia, kentän koko, SSD ja säteilyn tyyppi", True, "Kaikki nämä muuttavat annoksen syvyysjakaumaa."),
                ("Vain säteilyenergia", False, "Energia on tärkein mutta ei ainoa tekijä."),
                ("Vain kentän koko ja SSD", False, "Myös energia ja säteilytyyppi vaikuttavat."),
                ("PDD on vakio kaikissa olosuhteissa", False, "PDD vaihtelee merkittävästi eri parametrien mukaan."),
            ],
        ),
        (
            "multiple_choice", 2,
            "Mikä on Bragg-huipun merkitys hadroniterapiassa?",
            "Raskaiden varattujen hiukkasten annos huipentuu tietyllä syvyydellä, mikä mahdollistaa tarkan annoskohdistuksen.",
            [
                ("Annos huipentuu tietyllä syvyydellä, mahdollistaen tarkan kohdistuksen", True, "Protonien ja hiili-ionien Bragg-huippu mahdollistaa kasvaimen tarkan säteilytyksen."),
                ("Annos jakautuu tasaisesti koko matkalle", False, "Tämä pätee fotonisäteilyyn, ei hadroneille."),
                ("Annos on suurin ihon pinnalla", False, "Fotonisäteilyssä build-up alue kasvaa pinnan jälkeen, mutta hadroneilla huippu on syvemmällä."),
                ("Bragg-huippu kuvaa säteilyn sirontaa", False, "Bragg-huippu kuvaa energian deponitoitumista, ei sirontaa."),
            ],
        ),
        (
            "multiple_choice", 2,
            "Mikä on fraktioinnin perustarkoitus sädehoidossa?",
            "Fraktioinnissa kokonaisannos jaetaan useisiin osiin hyödyntäen terveiden ja syöpäkudosten erilaista korjautumiskykyä.",
            [
                ("Hyödyntää terveiden kudosten parempaa korjautumiskykyä fraktioiden välillä", True, "Fraktiointi mahdollistaa terveiden kudosten palautumisen hoitokertojen välillä."),
                ("Lyhentää kokonaishoitoaikaa", False, "Fraktiointi itse asiassa pidentää hoitoaikaa."),
                ("Vähentää laitteen kuormitusta", False, "Fraktiointi perustuu biologisiin syihin, ei teknisiin."),
                ("Parantaa kuvanlaatua sädehoidossa", False, "Fraktiointi ei liity kuvanlaatuun."),
            ],
        ),
        (
            "multi_select", 3,
            "Mitkä säteilylajit ovat käytössä ulkoisessa sädehoidossa?",
            "Ulkoisessa sädehoidossa käytetään useita säteilylajeja eri käyttötarkoituksiin.",
            [
                ("Fotonisäteily (röntgen- ja gammasäteet)", True, "Yleisin säteilylaji ulkoisessa sädehoidossa."),
                ("Elektronisäteily", True, "Käytetään pinnallisten kasvainten hoitoon."),
                ("Protonisäteily", True, "Hadroniterapiassa käytettävä säteilylaji."),
                ("Ultraviolettisäteily", False, "UV-säteily ei ole ionisoivaa säteilyä eikä sitä käytetä sädehoidossa."),
            ],
        ),
        (
            "multiple_choice", 3,
            "Mikä on MLC:n (monilehtikollimaattori) tehtävä sädehoidossa?",
            "MLC muokkaa säteilykeilan muotoa vastaamaan kasvaimen muotoa.",
            [
                ("Muotoilla säteilykeila vastaamaan kasvaimen muotoa", True, "MLC:n lehdet liikkuvat itsenäisesti ja muokkaavat keilan geometriaa."),
                ("Mitata säteilyannosta", False, "Annos mitataan ionisaatiokammioilla."),
                ("Kiihdyttää elektroneja", False, "Elektronien kiihdytys tapahtuu lineaarikiihdyttimen putkessa."),
                ("Suodattaa matalaenergistä säteilyä", False, "Tämä on suodattimien, ei MLC:n tehtävä."),
            ],
        ),
    ],

    # ===== FYSIOLOGIA - EKG-tutkimukset (EPA 11) =====
    11: [
        (
            "multiple_choice", 1,
            "Mistä sydämen sähköinen impulssi normaalisti syntyy?",
            "Sinussolmuke (SA-solmuke) toimii sydämen luonnollisena tahdistimena.",
            [
                ("Sinussolmukkeessa (SA-solmuke)", True, "SA-solmuke sijaitsee oikeassa eteisessä ja aloittaa jokaisen sydämenlyönnin."),
                ("Eteis-kammiosolmukkeessa (AV-solmuke)", False, "AV-solmuke viivyttää impulssia, mutta ei ole ensisijainen tahdistin."),
                ("Hisin kimpussa", False, "Hisin kimppu johtaa impulssin, mutta ei ole tahdistin."),
                ("Purkinjen säikeissä", False, "Purkinjen säikeet välittävät aktivaation kammioihin."),
            ],
        ),
        (
            "multiple_choice", 2,
            "Mitä P-aalto edustaa EKG:ssä?",
            "P-aalto kuvaa eteisten depolarisaatiota.",
            [
                ("Eteisten depolarisaatiota", True, "P-aalto syntyy sinussolmukkeesta leviävän impulssin aiheuttamasta eteisten aktivaatiosta."),
                ("Kammioiden depolarisaatiota", False, "Kammioiden depolarisaatio näkyy QRS-kompleksina."),
                ("Kammioiden repolarisaatiota", False, "Kammioiden repolarisaatio näkyy T-aaltona."),
                ("Eteisten repolarisaatiota", False, "Eteisten repolarisaatio on yleensä peittynyt QRS-kompleksin alle."),
            ],
        ),
        (
            "multiple_choice", 2,
            "Kuinka monta kytkentää standardoidussa 12-kytkentäisessä EKG:ssä on?",
            "Standardi-EKG koostuu 12 kytkennästä.",
            [
                ("12 kytkentää (3 bipolaarista + 3 unipolaarista raajakytkentää + 6 rintakytkentää)", True, "Tämä on kansainvälinen standardi sydämen sähköisen toiminnan rekisteröintiin."),
                ("6 kytkentää", False, "6 kytkentää kattaisi vain raaja- tai rintakytkennät."),
                ("3 kytkentää", False, "3 kytkentää riittäisi vain bipolaarisiin raajakytkentöihin."),
                ("24 kytkentää", False, "24 kytkentää käytetään joissakin erikoistutkimuksissa, ei standardissa."),
            ],
        ),
        (
            "multiple_choice", 2,
            "Mikä on PR-intervallin (PQ-välin) fysiologinen merkitys?",
            "PR-intervalli kuvaa aikaa eteisten depolarisaatiosta kammioiden depolarisaation alkuun.",
            [
                ("AV-solmukkeessa tapahtuva viive, joka mahdollistaa eteisten supistumisen ennen kammioita", True, "PR-väli kuvaa aikaa, joka tarvitaan impulssin etenemiseen SA-solmukkeesta kammioihin."),
                ("Kammioiden supistumisaika", False, "Kammioiden supistumisaika näkyy QRS-kompleksissa."),
                ("Sydämen lepovaiheen kesto", False, "Lepovaihe näkyy T-P-intervallissa."),
                ("Eteisten täyttymisaika", False, "PR-intervalli liittyy sähköiseen johtumiseen, ei mekaaniseen täyttymiseen."),
            ],
        ),
        (
            "multiple_choice", 2,
            "Mikä on suositeltava ihon kontaktivastus EKG-mittauksessa?",
            "Pieni kontaktivastus parantaa signaalin laatua.",
            [
                ("Alle 5 kΩ", True, "Ihon impedanssia pienennetään alkoholilla tai hiontatyynyllä parhaan signaalilaadun saamiseksi."),
                ("Alle 1 MΩ", False, "1 MΩ on aivan liian suuri kontaktivastus EKG-mittaukseen."),
                ("Alle 100 Ω", False, "Näin pientä vastusta on vaikea saavuttaa ihon pinnalta."),
                ("Kontaktivastuksella ei ole merkitystä", False, "Kontaktivastus vaikuttaa suoraan signaalin laatuun ja kohinatasoon."),
            ],
        ),
        (
            "multi_select", 2,
            "Mitkä ovat yleisimpiä syitä EKG-tutkimukseen lähettämiselle?",
            "EKG-tutkimus tehdään monista sydämen toimintaan liittyvistä syistä.",
            [
                ("Rintakipu tai sepelvaltimotautiepäily", True, "Yksi yleisimmistä EKG:n indikaatioista."),
                ("Sydämen rytmihäiriöepäily", True, "Potilas kokee tykytystä, muljahduksia tai huimausta."),
                ("Ennen anestesiaa tai leikkausta", True, "Sydämen perustoiminta dokumentoidaan ennen toimenpidettä."),
                ("Päänsärkydiagnostiikka", False, "Päänsäryn diagnostiikassa käytetään muita tutkimuksia."),
            ],
        ),
        (
            "multiple_choice", 3,
            "Mikä EKG:n aaltomuoto vastaa kammioiden depolarisaatiota?",
            "QRS-kompleksi syntyy kammioiden depolarisaatiosta.",
            [
                ("QRS-kompleksi", True, "QRS edustaa sähköisen impulssin etenemistä Hisin kimpun ja Purkinjen säikeiden kautta kammioihin."),
                ("P-aalto", False, "P-aalto kuvaa eteisten depolarisaatiota."),
                ("T-aalto", False, "T-aalto kuvaa kammioiden repolarisaatiota."),
                ("U-aalto", False, "U-aalto on harvinainen ja sen mekanismi on epäselvä."),
            ],
        ),
    ],

    # ===== RADIOLOGIA - Ultraääni (EPA 4) =====
    4: [
        (
            "multiple_choice", 1,
            "Mikä on ultraäänen tyypillinen taajuusalue lääketieteellisessä kuvantamisessa?",
            "Diagnostisessa ultraäänitutkimuksessa käytetään 1–20 MHz taajuuksia.",
            [
                ("1–20 MHz", True, "Diagnostinen ultraääni käyttää megahertsitaajuuksia kudosten kuvantamiseen."),
                ("20 Hz – 20 kHz", False, "Tämä on ihmisen kuuloalue, ei ultraäänialue."),
                ("100–500 kHz", False, "Tämä alue on alle diagnostisen ultraäänen tyypillisen taajuuden."),
                ("100–1000 MHz", False, "Näin korkeita taajuuksia ei käytetä lääketieteellisessä kuvantamisessa."),
            ],
        ),
        (
            "multiple_choice", 2,
            "Miten ultraäänen taajuus vaikuttaa kuvanlaatuun?",
            "Korkeampi taajuus parantaa erottelukykyä mutta heikentää tunkeutumissyvyyttä.",
            [
                ("Korkeampi taajuus parantaa erottelukykyä mutta heikentää tunkeutumissyvyyttä", True, "Korkeampi taajuus tarkoittaa lyhyempää aallonpituutta ja parempaa resoluutiota, mutta vaimennus kasvaa."),
                ("Korkeampi taajuus parantaa sekä erottelukykyä että tunkeutumissyvyyttä", False, "Vaimennus kasvaa taajuuden kasvaessa."),
                ("Taajuus ei vaikuta kuvanlaatuun", False, "Taajuus on yksi tärkeimmistä kuvanlaadun parametreista."),
                ("Matalampi taajuus parantaa erottelukykyä", False, "Matalampi taajuus heikentää erottelukykyä."),
            ],
        ),
        (
            "multiple_choice", 2,
            "Mikä on pietsosähköisen ilmiön merkitys ultraäänikuvantamisessa?",
            "Pietsosähköinen ilmiö mahdollistaa sähköisen signaalin muuntamisen ultraääneksi ja päinvastoin.",
            [
                ("Muuntaa sähköenergian ääniaalloksi ja ääniaallon sähkösignaaliksi", True, "Ultraäänianturin pietsosähköinen kide toimii sekä lähettäjänä että vastaanottajana."),
                ("Vahvistaa ultraäänisignaalia kudoksissa", False, "Pietsosähköinen ilmiö ei vahvista signaalia kudoksissa."),
                ("Tuottaa lämpöä kudoksissa", False, "Lämpö on sivuvaikutus, ei pietsosähköisen ilmiön päätarkoitus."),
                ("Suodattaa kohinaa signaalista", False, "Kohinansuodatus tehdään elektronisesti."),
            ],
        ),
    ],

    # ===== RADIOLOGIA - Natiivikuvantaminen (EPA 1) =====
    1: [
        (
            "multiple_choice", 1,
            "Mikä on MRI-kuvantamisen fyysinen perusta?",
            "MRI perustuu ydinmagneettiseen resonanssiin, erityisesti vetyatomien käyttäytymiseen magneettikentässä.",
            [
                ("Ydinmagneettinen resonanssi (NMR) ja vetyatomien käyttäytyminen magneettikentässä", True, "Vetyatomien ydinspinit resonoivat radioaaltojen kanssa voimakkaassa magneettikentässä."),
                ("Röntgensäteilyn absorptio kudoksissa", False, "Tämä on röntgenkuvantamisen perusta, ei MRI:n."),
                ("Ultraääniaaltojen heijastuminen", False, "Tämä on ultraäänikuvantamisen perusta."),
                ("Radioaktiivisten isotooppien hajoaminen", False, "Tämä on isotooppikuvantamisen perusta."),
            ],
        ),
        (
            "multiple_choice", 2,
            "Mitkä ovat MRI-turvallisuuden kolme pääasiallista fyysistä riskiä?",
            "MRI-turvallisuudessa on huomioitava staattisen magneettikentän, gradienttikenttien ja RF-kenttien vaikutukset.",
            [
                ("Staattisen magneettikentän, gradienttikenttien ja RF-kenttien vaikutukset", True, "Nämä kolme kenttää muodostavat MRI:n fysikaaliset perusriskit."),
                ("Röntgensäteily, magneettikenttä ja kontrasti", False, "MRI ei käytä röntgensäteilyä."),
                ("Lämpö, tärinä ja ääni", False, "Nämä ovat oireita, eivät pääasiallisia fyysisiä riskejä."),
                ("Säteilyannos, allergiat ja klaustrofobia", False, "MRI ei aiheuta ionisoivaa säteilyaltistusta."),
            ],
        ),
    ],

    # ===== SÄDEHOITO - Peruskäsitteet (EPA 16) =====
    16: [
        (
            "multiple_choice", 1,
            "Mikä on Gray (Gy) yksikkönä?",
            "Gray on absorboituneen annoksen yksikkö.",
            [
                ("Absorboituneen annoksen yksikkö: 1 Gy = 1 J/kg", True, "Gray kuvaa kudokseen absorboituneen energian massayksikköä kohti."),
                ("Ekvivalenttiannoksen yksikkö", False, "Ekvivalenttiannoksen yksikkö on sievert (Sv)."),
                ("Aktiivisuuden yksikkö", False, "Aktiivisuuden yksikkö on becquerel (Bq)."),
                ("Altistuksen yksikkö", False, "Altistuksen yksikkö on coulombi/kilogramma (C/kg)."),
            ],
        ),
        (
            "multiple_choice", 2,
            "Mikä on lineaarikiihdyttimen (LINAC) tyypillinen fotonienergian alue?",
            "LINAC tuottaa korkeaenergisiä fotoneja sädehoidossa.",
            [
                ("4–25 MV", True, "Lineaarikiihdyttimet tuottavat fotonisäteitä tällä energia-alueella."),
                ("80–140 kV", False, "Tämä on diagnostisen TT-kuvantamisen jännitealue."),
                ("22–35 kV", False, "Tämä on mammografian jännitealue."),
                ("1–5 keV", False, "Tämä energia on aivan liian matala sädehoidolle."),
            ],
        ),
    ],

    # ===== ISOTOOPPILÄÄKETIEDE - Gammakamera (EPA 28) =====
    28: [
        (
            "multiple_choice", 2,
            "Mikä on gammakameran keskeinen detektorimateriaali?",
            "Gammakamerassa käytetään tuikeilmaisinkidettä gammasäteilyn havaitsemiseen.",
            [
                ("NaI(Tl) – natriumjodidi (tallium-aktivoitu)", True, "NaI(Tl) on yleisin gammakameran tuikeilmaisinkide."),
                ("CsI(Tl) – cesiumjodidi", False, "CsI käytetään joissakin digitaalisissa röntgendetektoreissa, ei tyypillisesti gammakameroissa."),
                ("BGO – bismuttimgermanium-oksidi", False, "BGO on PET-kameran detektorimateriaali."),
                ("CZT – kadmium-sinkkitelleridi", False, "CZT on uudempi detektorimateriaali erikoisgammakameroissa, mutta ei yleisin."),
            ],
        ),
        (
            "multiple_choice", 2,
            "Mikä on kollimaattorin tehtävä gammakamerassa?",
            "Kollimaattori rajoittaa detektorille pääsevän säteilyn suuntaa kuvan muodostamiseksi.",
            [
                ("Rajoittaa detektorille pääsevän säteilyn suuntaa paikkatiedon säilyttämiseksi", True, "Ilman kollimaattoria kaikki suunnista tuleva säteily osuisi detektoriin ilman paikkatietoa."),
                ("Vahvistaa gammasäteilyä", False, "Kollimaattori ei vahvista säteilyä vaan vaimentaa ei-halutun suuntaista säteilyä."),
                ("Muuttaa gammasäteilyn näkyväksi valoksi", False, "Tämä on tuikeilmaisinkiteen tehtävä."),
                ("Suodattaa matalaenergistä hajontasäteilyä", False, "Energiaikkunat hoitavat hajontasäteilyn suodatuksen."),
            ],
        ),
        (
            "multiple_choice", 1,
            "Mikä on yleisin gammakuvauksessa käytetty radioisotooppi?",
            "Teknetium-99m on ylivoimaisesti yleisin SPECT-isotooppi.",
            [
                ("Teknetium-99m (⁹⁹ᵐTc)", True, "Tc-99m:n lyhyt puoliintumisaika (6 h) ja sopiva gammaenergia (140 keV) tekevät siitä ideaalin."),
                ("Fluori-18 (¹⁸F)", False, "F-18 on yleisin PET-isotooppi, ei gammakuvauksen."),
                ("Jodi-131 (¹³¹I)", False, "I-131 käytetään pääasiassa kilpirauhashoidoissa."),
                ("Gallium-68 (⁶⁸Ga)", False, "Ga-68 on PET-isotooppi."),
            ],
        ),
    ],

    # ===== ISOTOOPPILÄÄKETIEDE - PET-kamera (EPA 29) =====
    29: [
        (
            "multiple_choice", 2,
            "Mikä fysikaalinen ilmiö on PET-kuvantamisen perusta?",
            "PET perustuu positronin annihilaatioon ja siitä syntyvien gammasäteiden koinsidenssihavainnointiin.",
            [
                ("Positronin annihilaatio ja kahden 511 keV gammasäteen koinsidenssihavainnointi", True, "Positroni kohtaa elektronin ja syntyy kaksi vastakkaisiin suuntiin lähtevää 511 keV gammasädettä."),
                ("Yksittäisten gammasäteiden havainnointi kollimaattorilla", False, "Tämä on SPECT/gammakameran periaate."),
                ("Röntgensäteilyn absorptio kudoksissa", False, "Tämä on TT-kuvantamisen periaate."),
                ("Ultraääniheijastukset kudosrajapinnoista", False, "Tämä on ultraäänikuvantamisen periaate."),
            ],
        ),
        (
            "multiple_choice", 2,
            "Mikä on PET-kuvantamisen yleisin merkkiaine?",
            "¹⁸F-FDG on yleisin PET-merkkiaine.",
            [
                ("¹⁸F-FDG (fluorideoksiglukooisi)", True, "FDG on glukoosinkaltainen merkkiaine, joka kertyy metabolisesti aktiivisiin soluihin."),
                ("⁹⁹ᵐTc-MDP", False, "Tämä on SPECT-luustokuvauksessa käytetty merkkiaine."),
                ("¹²³I-joflupane", False, "Tämä on SPECT-tutkimuksessa käytetty dopamiinkuljettajaligandi."),
                ("²⁰¹Tl-talliumkloridi", False, "Tämä on SPECT-sydäntutkimuksessa käytetty merkkiaine."),
            ],
        ),
        (
            "multiple_choice", 3,
            "Mikä on annihilaatiossa syntyvien gammasäteiden energia?",
            "Positroni-elektroni-annihilaatiossa syntyy kaksi 511 keV gammasädettä.",
            [
                ("511 keV", True, "Energia vastaa elektronin lepomassan energiaa (E = mc²), joten kumpikin fotoni saa 511 keV."),
                ("140 keV", False, "140 keV on Tc-99m:n gammaenergia."),
                ("662 keV", False, "662 keV on Cs-137:n gammaenergia."),
                ("1022 keV", False, "1022 keV on kokonaisenergia, mutta se jakautuu kahteen 511 keV fotoniin."),
            ],
        ),
    ],

    # ===== KNF - EEG (EPA 5) =====
    5: [
        (
            "multiple_choice", 1,
            "Mitä EEG mittaa?",
            "EEG mittaa aivojen sähköistä toimintaa päänahalta.",
            [
                ("Aivojen sähköistä toimintaa (kortikaalisia jännitevaihteluja)", True, "EEG rekisteröi aivokuoren hermosolujen synaptisia potentiaaleja päänahalle asetettujen elektrodien avulla."),
                ("Aivojen verenvirtausta", False, "Verenvirtausta mitataan fMRI:llä tai TCD:llä."),
                ("Aivojen metabolista aktiivisuutta", False, "Metabolista aktiivisuutta mitataan PET:llä."),
                ("Hermojen johtumisnopeutta", False, "Johtumisnopeutta mitataan ENMG-tutkimuksella."),
            ],
        ),
        (
            "multiple_choice", 2,
            "Mikä on kansainvälinen standardi EEG-elektrodien sijoitteluun?",
            "10-20-järjestelmä on kansainvälinen standardi EEG-elektrodien paikkojen määrittämiseen.",
            [
                ("Kansainvälinen 10-20-järjestelmä", True, "Elektrodit sijoitetaan 10 % ja 20 % välimatkan etäisyydellä anatomisista maamerkeistä."),
                ("Wilson-järjestelmä", False, "Wilson-elektrodit liittyvät EKG-mittaukseen."),
                ("Bipolaarinen raajajärjestelmä", False, "Tämä liittyy EKG-kytkentöihin."),
                ("Montrealin standardijärjestelmä", False, "Tällaista standardia ei ole EEG:ssä."),
            ],
        ),
    ],

    # ===== KNF - Heräteresponssit ja ENMG (EPA 6) =====
    6: [
        (
            "multiple_choice", 2,
            "Mikä on ENMG-tutkimuksen tarkoitus?",
            "ENMG tutkii hermojen ja lihasten sähköistä toimintaa.",
            [
                ("Tutkia ääreishermojen johtumisnopeutta ja lihasten sähköistä toimintaa", True, "ENMG (elektroneuromyografia) mittaa sekä hermojen johtumista (ENG) että lihasten sähköistä aktiivisuutta (EMG)."),
                ("Mitata aivojen sähköistä toimintaa", False, "Aivojen sähköistä toimintaa mitataan EEG:llä."),
                ("Kuvata lihasten rakennetta ultraäänellä", False, "Lihasten kuvantaminen tehdään ultraäänellä tai MRI:llä."),
                ("Rekisteröidä sydämen sähköistä toimintaa", False, "Sydämen sähköistä toimintaa mitataan EKG:llä."),
            ],
        ),
    ],

    # ===== FYSIOLOGIA - GI-kanavan tutkimukset (EPA 12) =====
    12: [
        (
            "multiple_choice", 2,
            "Mikä on manometrian mittausperiaate GI-kanavan tutkimuksissa?",
            "Manometria mittaa ruoansulatuskanavan paineolosuhteita.",
            [
                ("Mittaa ruoansulatuskanavan paineolosuhteita ja lihassupistusten voimaa", True, "Manometrialla voidaan arvioida ruokatorven, mahalaukun ja suoliston motiliteettia."),
                ("Mittaa mahalaukun happamuutta", False, "Happamuutta mitataan pH-metrialla."),
                ("Kuvaa suoliston rakennetta", False, "Rakenteen kuvantamiseen käytetään tähystyslaitteita tai röntgenkuvantamista."),
                ("Mittaa ruoansulatusentsyymien aktiivisuutta", False, "Entsyymiaktiivisuutta mitataan laboratorioanalyysillä."),
            ],
        ),
    ],

    # ===== RADIOLOGIA - Läpivalaisu ja angiografia (EPA 20) =====
    20: [
        (
            "multiple_choice", 2,
            "Mikä on läpivalaisun (fluoroskopian) erityispiirre verrattuna tavanomaiseen röntgenkuvantamiseen?",
            "Läpivalaisu mahdollistaa reaaliaikaisen kuvantamisen.",
            [
                ("Tuottaa reaaliaikaisen liikkuvan kuvan (jatkuva tai pulssitettu säteily)", True, "Läpivalaisu mahdollistaa toimenpiteiden ja liikkuvien rakenteiden seurannan reaaliajassa."),
                ("Tuottaa kolmiulotteisen kuvan", False, "Läpivalaisu tuottaa kaksiulotteisen projektiokuvan."),
                ("Käyttää ultrakorkeaa jännitettä", False, "Läpivalaisussa käytetään samankaltaisia jännitteitä kuin muussa röntgenkuvantamisessa."),
                ("Ei vaadi säteilyä", False, "Läpivalaisu käyttää röntgensäteilyä."),
            ],
        ),
        (
            "multiple_choice", 2,
            "Mikä on DAP-suureen (Dose Area Product) merkitys läpivalaisussa?",
            "DAP kuvaa potilaan kokonaissäteilyaltistusta huomioiden sekä annoksen että säteilytetyn alueen koon.",
            [
                ("Kuvaa kokonaissäteilyaltistusta huomioiden annoksen ja säteilytetyn alueen pinta-alan", True, "DAP (Gy·cm²) on tärkeä suure potilasannoksen seurannassa läpivalaisussa."),
                ("Mittaa vain ihon pinnan annosta", False, "DAP huomioi alueen koon, ei pelkkää piste-annosta."),
                ("Kuvaa säteilyn laatua", False, "Säteilyn laatua kuvataan HVL-arvolla."),
                ("On sama suure kuin CTDIvol", False, "CTDIvol on TT-kuvantamisen annossuure."),
            ],
        ),
    ],

    # ===== RADIOLOGIA - Hammaskuvantaminen (EPA 19) =====
    19: [
        (
            "multiple_choice", 2,
            "Mikä on KKTT:n (kartiokeilatomografia) erityispiirre hammaskuvantamisessa?",
            "KKTT tuottaa kolmiulotteisen kuvan kartiomaisella röntgenkeilalla.",
            [
                ("Tuottaa kolmiulotteisen kuvan kartiomaisella keilalla yhdellä kierrolla", True, "KKTT (CBCT) kuvaa koko tilavuuden yhdellä kierrolla ja on yleinen hammaskuvantamisessa."),
                ("Käyttää ultraääntä", False, "KKTT käyttää röntgensäteilyä."),
                ("Tuottaa vain kaksiulotteisen panoraamakuvan", False, "Panoraamakuva on eri kuvausmenetelmä kuin KKTT."),
                ("Käyttää magneettiresonanssia", False, "KKTT perustuu röntgensäteilyyn."),
            ],
        ),
    ],

    # ===== RADIOLOGIA - Kuvankatselunäytöt (EPA 22) =====
    22: [
        (
            "multiple_choice", 2,
            "Mikä on diagnostisen kuvankatselunäytön DICOM GSDF -standardin tarkoitus?",
            "GSDF varmistaa, että näyttö esittää harmaasävyt ihmisen visuaalisen havaintokyvyn kannalta optimaalisesti.",
            [
                ("Varmistaa harmaa-asteikon tasainen visuaalinen vaihtelevuus (JND-malli)", True, "GSDF (Grayscale Standard Display Function) perustuu ihmisen näkökyvyn JND-malliin."),
                ("Määrittää näytön fyysisen koon", False, "GSDF ei liity näytön kokoon."),
                ("Asettaa näytön väriavaruuden", False, "GSDF koskee harmaasävyesitystä, ei värinhallintaa."),
                ("Säätää näytön virkistystaajuutta", False, "GSDF ei liity virkistystaajuuteen."),
            ],
        ),
    ],

    # ===== SÄDEHOITO - Dosimetria (EPA 25) =====
    25: [
        (
            "multiple_choice", 2,
            "Mikä on absoluuttisen dosimetrian tarkoitus sädehoidossa?",
            "Absoluuttinen dosimetria määrittää säteilyannoksen tarkasti tunnetuissa olosuhteissa.",
            [
                ("Määrittää säteilykeilan absoluuttinen annos referenssiolosuhteissa kalibraation avulla", True, "Käytetään ionisaatiokammiota ja kansainvälisiä protokollia (IAEA TRS-398)."),
                ("Mitata säteilyn spektriä", False, "Spektrin mittaus ei ole dosimetrian päätehtävä."),
                ("Laskea potilaan kokonaisannos hoitojakson aikana", False, "Tämä on annossuunnittelun tehtävä."),
                ("Arvioida säteilyn biologisia vaikutuksia", False, "Biologiset vaikutukset kuuluvat sädebiologian alueelle."),
            ],
        ),
        (
            "multiple_choice", 3,
            "Mikä ionisaatiokammiotyyppi on standardi absoluuttisessa dosimetriassa sädehoidossa?",
            "Absoluuttisessa dosimetriassa käytetään kalibroitua sylinterikammiota.",
            [
                ("Farmer-tyyppinen sylinterikammio (0.6 cm³)", True, "Farmer-kammio on kansainvälinen standardi sädehoidon absoluuttisessa dosimetriassa."),
                ("Tasolevykammio", False, "Tasolevykammiota käytetään pienillä syvyyksillä ja elektronikenttien mittauksissa."),
                ("Geiger-Müller-putki", False, "GM-putkea käytetään säteilynsuojelussa, ei dosimetriassa."),
                ("Puolijohdeilmaisin", False, "Puolijohteet ovat relatiiviseen dosimetriaan, eivät absoluuttiseen."),
            ],
        ),
    ],

    # ===== SÄDEHOITO - Sädebiologia (EPA 27) =====
    27: [
        (
            "multiple_choice", 2,
            "Mikä on DNA:n kaksoisjuostekatkos (DSB) ja sen merkitys sädehoidossa?",
            "DSB on säteilyn aiheuttama DNA-vaurio, jossa molemmat juosteet katkeavat.",
            [
                ("Molemmat DNA-juosteet katkeavat lähellä toisiaan, mikä on vaikeasti korjattava ja soluja tuhoava vaurio", True, "DSB:t ovat sädehoidon vaikutusmekanismin kannalta kriittisimpiä DNA-vaurioita."),
                ("Yksi DNA-juoste katkeaa ja toinen pysyy ehjänä", False, "Tämä on yksittäisjuostekatkos (SSB), joka korjaantuu helpommin."),
                ("DNA-emäs muuttuu toiseksi emäkseksi", False, "Tämä on emäsmuutos, ei juostekatkos."),
                ("DNA-ketjuun syntyy ylimääräinen kopioituminen", False, "Tämä on duplikaatio, eri mekanismi kuin DSB."),
            ],
        ),
        (
            "multiple_choice", 3,
            "Mikä on LQ-malli (linear-quadratic) ja mihin sitä käytetään sädehoidossa?",
            "LQ-malli kuvaa säteilyannoksen ja solujen eloonjäämisen välistä suhdetta.",
            [
                ("Mallintaa solujen eloonjäämistä: S = exp(-αD - βD²), käytetään fraktioinnin suunnitteluun", True, "LQ-malli on sädehoidon biologisen annossuunnittelun perustyökalu."),
                ("Laskee potilaan efektiivisen annoksen", False, "Efektiivisen annoksen laskentaan käytetään kudospainotuskertoimia."),
                ("Kuvaa säteilykeilan intensiteettijakaumaa", False, "Intensiteettijakaumaa kuvaavat PDD ja profiilitiedot."),
                ("Arvioi laitteiden mekaanista tarkkuutta", False, "Laitetarkkuutta arvioidaan laadunvarmistusmittauksilla."),
            ],
        ),
    ],
}


class Command(BaseCommand):
    help = 'Populate quiz database with predefined questions based on EPA theory content'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear all existing questions before populating',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options['clear']:
            count = Question.objects.count()
            Question.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'Cleared {count} existing questions'))

        total_created = 0
        total_skipped = 0

        for epa_id, questions in QUESTIONS.items():
            try:
                epa = EPA.objects.get(id=epa_id)
            except EPA.DoesNotExist:
                self.stderr.write(self.style.ERROR(f'EPA {epa_id} not found, skipping'))
                continue

            self.stdout.write(f'\n{epa.specialty.name} > {epa.title}')

            for q_type, difficulty, text, explanation, choices_data in questions:
                # Check for duplicate
                if Question.objects.filter(text=text, epa=epa).exists():
                    total_skipped += 1
                    continue

                question = Question.objects.create(
                    question_type=q_type,
                    difficulty=difficulty,
                    text=text,
                    explanation=explanation,
                    epa=epa,
                    is_active=True,
                )

                for idx, (c_text, is_correct, c_explanation) in enumerate(choices_data):
                    Choice.objects.create(
                        question=question,
                        text=c_text,
                        is_correct=is_correct,
                        order=idx,
                        explanation=c_explanation,
                    )

                total_created += 1

            self.stdout.write(self.style.SUCCESS(
                f'  Created {sum(1 for q in questions)} questions'
            ))

        self.stdout.write(f'\n{"=" * 50}')
        self.stdout.write(self.style.SUCCESS(
            f'Total: {total_created} questions created, {total_skipped} skipped (duplicates)'
        ))
