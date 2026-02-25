"""Generate real subject-matter MCQ questions from exam question topics."""
from django.core.management.base import BaseCommand
from quiz.models import Question, Choice
from sisalto.models import ExamQuestion


# Map subject areas to EPA IDs
AREA_EPA = {
    'Radiologia': 1,
    'Sädehoito': 16,
    'Isotooppilääketiede': 28,
    'KNF': 5,
    'Fysiologia': 11,
    'Kliininen fysiologia': 11,
    'Anatomia': 11,
}

# Each entry: (exam_question_id, question_text, explanation, [choices as (text, is_correct, explanation)])
QUESTIONS = [
    # ======================================================================
    # RADIOLOGIA - CT
    # ======================================================================
    (43, "Mikä on tietokonetomografian (CT) perusperiaate?",
     "CT:ssä röntgenputki kiertää potilaan ympäri ja detektori mittaa vaimentuneen säteilyn. Kuvat rekonstruoidaan matemaattisesti.",
     [
         ("Röntgenputki kiertää potilasta ja detektorit mittaavat säteilyn vaimenemisen eri kulmista, minkä jälkeen kuva rekonstruoidaan", True,
          "Tämä on CT:n perusperiaate - pyörivä röntgenputki ja takaisinprojektio."),
         ("Potilas altistetaan voimakkaalle magneettikentälle ja radioaalloille", False,
          "Tämä kuvaa MRI:n periaatetta, ei CT:tä."),
         ("Ultraäänikaikujen avulla muodostetaan poikkileikekuva", False,
          "Tämä on ultraäänitutkimuksen periaate."),
         ("Radioaktiivisen merkkiaineen jakautuminen kuvataan gammakameralla", False,
          "Tämä kuvaa isotooppikuvauksen periaatetta."),
     ]),
    (43, "Mikä matemaattinen menetelmä on CT-kuvien rekonstruktion perustana?",
     "Suodatettu takaisinprojektio (filtered back projection, FBP) on klassinen CT-rekonstruktiomenetelmä.",
     [
         ("Suodatettu takaisinprojektio (filtered back projection)", True,
          "FBP on perinteinen ja edelleen käytössä oleva CT-rekonstruktiomenetelmä."),
         ("Fourier-muunnos suoraan kuvadatasta", False,
          "Fourier-muunnosta käytetään osana prosessia, mutta se ei ole itse rekonstruktiomenetelmä."),
         ("Monte Carlo -simulaatio", False,
          "Monte Carlo on stokastinen simulointimenetelmä, jota käytetään annoslaskennassa."),
         ("Lineaarinen interpolointi", False,
          "Interpolointia käytetään kuvien käsittelyssä, mutta se ei ole CT:n rekonstruktiomenetelmä."),
     ]),
    (148, "Mikä seuraavista EI ole tyypillinen CT-artefakta?",
     "CT-kuvissa esiintyy tyypillisesti metalliartifakteja, liike-artifakteja ja kovettumisartefakteja.",
     [
         ("Kemiallisen siirtymän artefakta", True,
          "Kemiallisen siirtymän artefakta liittyy MRI-kuvantamiseen, ei CT:hen."),
         ("Metalliartefakta", False,
          "Metalliset implantit aiheuttavat tyypillisiä juova-artefaktoja CT-kuvissa."),
         ("Kovettumisartefakta (beam hardening)", False,
          "Röntgensäteilyn spektrin kovettuminen luun läpi kulkiessa aiheuttaa tyypillisen CT-artefaktan."),
         ("Liikeartefakta", False,
          "Potilaan liike kuvauksen aikana on yleinen CT-artefaktan aiheuttaja."),
     ]),

    # ======================================================================
    # RADIOLOGIA - MRI
    # ======================================================================
    (52, "Mikä aiheuttaa kontrastin T1-painotteisissa MRI-kuvissa?",
     "T1-painotteisissa kuvissa kontrasti perustuu kudosten erilaisiin T1-relaksaatioaikoihin.",
     [
         ("Kudosten erilaiset pitkittäisrelaksaatioajat (T1)", True,
          "T1 kuvaa protonien spin-hila -relaksaation nopeutta, joka vaihtelee kudostyypeittäin."),
         ("Kudosten erilaiset poikittaisrelaksaatioajat (T2)", False,
          "T2-relaksaatio tuottaa kontrastin T2-painotteisissa kuvissa."),
         ("Protonitiheyden erot kudosten välillä", False,
          "Protonitiheys vaikuttaa signaalin voimakkuuteen, mutta ei ole T1-painotuksen perusta."),
         ("Kudosten erilaiset sähkönjohtavuudet", False,
          "Sähkönjohtavuus ei ole keskeinen MRI-kontrastimekanismi."),
     ]),
    (52, "Miten T1-painotteinen MRI-kuva tuotetaan pulssijaksoparametreilla?",
     "T1-painotus saadaan käyttämällä lyhyttä TR:ää ja lyhyttä TE:tä.",
     [
         ("Lyhyt TR ja lyhyt TE", True,
          "Lyhyt TR korostaa T1-eroja ja lyhyt TE minimoi T2-vaikutuksen."),
         ("Pitkä TR ja pitkä TE", False,
          "Pitkä TR ja pitkä TE tuottaa T2-painotteisen kuvan."),
         ("Pitkä TR ja lyhyt TE", False,
          "Pitkä TR ja lyhyt TE tuottaa protonipainotteisen kuvan."),
         ("Lyhyt TR ja pitkä TE", False,
          "Tämä yhdistelmä ei ole käytännöllinen eikä tuota hyödyllistä kontrastia."),
     ]),
    (71, "Mikä näkyy kirkkaana T1-painotteisessa MRI-kuvassa?",
     "T1-painotteisissa kuvissa rasva on kirkas ja vesi tumma.",
     [
         ("Rasva", True,
          "Rasvan lyhyt T1-relaksaatioaika tekee siitä kirkkaan T1-painotteisessa kuvassa."),
         ("Aivo-selkäydinneste (likvor)", False,
          "Likvor on tumma T1-kuvissa pitkän T1-ajan vuoksi, mutta kirkas T2-kuvissa."),
         ("Luurankolihas", False,
          "Lihas näkyy keskiharmaan sävyisenä T1-kuvissa."),
         ("Ilma", False,
          "Ilma ei anna MRI-signaalia ja näkyy mustana."),
     ]),

    # ======================================================================
    # RADIOLOGIA - Digitaalinen kuvankäsittely
    # ======================================================================
    (95, "Mikä on ikkunoinnin (windowing) tarkoitus digitaalisessa röntgenkuvassa?",
     "Ikkunointi säätää näytettävää harmaasävyaluetta, jolloin haluttujen kudosten kontrasti paranee.",
     [
         ("Säätää näytettävää kontrastialuetta korostamaan haluttujen kudosten eroja", True,
          "Ikkunan leveys ja keskipiste määräävät, mitkä harmaasävyt näytetään."),
         ("Poistaa kuvasta satunnainen kohina", False,
          "Kohinan poistoon käytetään suodatusta, ei ikkunointia."),
         ("Pienentää kuvan tiedostokokoa", False,
          "Ikkunointi on vain näyttöoperaatio, ei vaikuta tiedostokokoon."),
         ("Korjaa potilaan liikkeestä aiheutuvat artefaktat", False,
          "Liikeartefaktojen korjaus vaatii erilaisia algoritmeja."),
     ]),
    (96, "Mikä seuraavista on digitaalisen kuvan suodatustekniikka?",
     "Digitaalisia kuvia voidaan käsitellä esim. konvoluutiosuodattimilla tai Fourier-suodatuksella.",
     [
         ("Konvoluutiosuodatus avaruudellisella maskilla", True,
          "Konvoluutio on perussuodatustekniikka, jossa pikseliarvoihin vaikutetaan naapuripikselien arvoilla."),
         ("DICOM-muunnos", False,
          "DICOM on kuvien tallennus- ja siirtostandardi, ei suodatustekniikka."),
         ("Hounsfield-kalibrointi", False,
          "Hounsfield-yksiköt liittyvät CT-kuvien harmaasävyasteikkoon."),
         ("Bremsstrahlung-korjaus", False,
          "Bremsstrahlung liittyy röntgensäteilyn tuottoon, ei kuvan käsittelyyn."),
     ]),

    # ======================================================================
    # RADIOLOGIA - DSA
    # ======================================================================
    (85, "Mikä on DSA:n (Digital Subtraction Angiography) perusperiaate?",
     "DSA:ssa vähennetään varjoaineen ruiskutusta edeltävä kuva varjoainekuvasta, jolloin verisuonet erottuvat selkeästi.",
     [
         ("Varjoainetta edeltävä maskikuva vähennetään varjoainekuvasta verisuonten korostamiseksi", True,
          "Subtraktio poistaa luiset ja pehmytkudosrakenteet, jolloin vain varjoaine näkyy."),
         ("Kaksi eri energian röntgenkuvaa vähennetään toisistaan", False,
          "Tämä kuvaa dual-energy-tekniikkaa, ei perinteistä DSA:ta."),
         ("Ultraäänen Doppler-signaali muunnetaan angiografiakuvaksi", False,
          "DSA perustuu röntgensäteilyyn, ei ultraääneen."),
         ("MRI-kontrastiaineen virtaus kuvataan reaaliaikaisesti", False,
          "Tämä kuvaa MRA-tekniikkaa, ei DSA:ta."),
     ]),

    # ======================================================================
    # RADIOLOGIA - Dosimetria
    # ======================================================================
    (107, "Mikä on absorboitunut annos ja sen SI-yksikkö?",
     "Absorboitunut annos on säteilyn aineeseen luovuttama energia massayksikköä kohden.",
     [
         ("Säteilyn aineeseen luovuttama energia massayksikköä kohden, yksikkö gray (Gy)", True,
          "D = dE/dm, 1 Gy = 1 J/kg."),
         ("Säteilyn ilmaan tuottama ionisaatio, yksikkö coulombi per kilogramma", False,
          "Tämä kuvaa ilmakerma-annosta tai altistusta, ei absorboitunutta annosta."),
         ("Biologisesti painotettu annos, yksikkö sievert (Sv)", False,
          "Sievert on ekvivalenttiannoksen yksikkö, jossa huomioidaan säteilylaji."),
         ("Säteilylähteen aktiivisuus, yksikkö becquerel (Bq)", False,
          "Becquerel mittaa radioaktiivista aktiivisuutta, ei annosta."),
     ]),
    (128, "Mikä on ionisaatiokammion toimintaperiaate?",
     "Ionisaatiokammiossa säteily ionisoi kaasun ja syntynyt varaus kerätään sähkökentän avulla.",
     [
         ("Säteily ionisoi kammion kaasun ja syntyneet ionit kerätään sähkökentällä, virta on verrannollinen annokseen", True,
          "Tämä on ionisaatiokammion perusperiaate."),
         ("Säteily aiheuttaa valosähköilmiön puolijohteessa, tuottaen mitattavan jännitepulssin", False,
          "Tämä kuvaa puolijohdedetektorin toimintaa."),
         ("Säteily aiheuttaa termoluminesenssin kidekiteessä", False,
          "Tämä on TLD-dosimetrin periaate."),
         ("Säteily muuttaa filmin tummuutta kemiallisesti", False,
          "Tämä on filmi-dosimetrin periaate."),
     ]),

    # ======================================================================
    # SÄDEHOITO - Lineaarikiihdytin ja peruskäsitteet
    # ======================================================================
    (256, "Mikä on lineaarikiihdyttimen rooli sädehoidossa?",
     "Lineaarikiihdytin kiihdyttää elektroneja suureen energiaan ja tuottaa hoitoon käytettävän fotoni- tai elektronisäteilyn.",
     [
         ("Kiihdyttää elektroneja ja tuottaa korkeaenergisen fotoni- tai elektronisäteilyn potilaan hoitoon", True,
          "Lineaarikiihdytin on modernin sädehoidon peruslaite."),
         ("Tuottaa radioaktiivisen koboltti-60 -säteilyn", False,
          "Co-60-säteilyä tuottaa radioaktiivinen lähde, ei kiihdytin."),
         ("Tuottaa protonisäteilyn hoitokäyttöön", False,
          "Protonien kiihdytykseen käytetään syklotronia tai synkrotronia."),
         ("Kuvaa potilaan hoitoalueen ultraäänellä", False,
          "Ultraääni on kuvantamismenetelmä, ei hoitolaite."),
     ]),
    (86, "Mitkä tekijät vaikuttavat syväannoskäyrän muotoon fotonisädehoidossa?",
     "Syväannoskäyrään vaikuttavat säteilyn energia, kenttäkoko, SSD ja kudoksen tiheys.",
     [
         ("Säteilyn energia, kenttäkoko, etäisyys lähteestä (SSD) ja kudoksen tiheys", True,
          "Nämä ovat keskeiset syväannoskäyrän muotoon vaikuttavat tekijät."),
         ("Ainoastaan säteilyn energia", False,
          "Energia on tärkeä tekijä, mutta ei ainoa."),
         ("Hoitohuoneen lämpötila ja ilmanpaine", False,
          "Nämä vaikuttavat ionisaatiokammion lukemiin, eivät suoraan syväannoskäyrään."),
         ("Potilaan paino ja pituus", False,
          "Potilaan koko ei suoraan vaikuta syväannoskäyrän muotoon."),
     ]),
    (93, "Mitä ICRU 50 -raportissa määritellyt GTV, CTV ja PTV tarkoittavat?",
     "GTV on näkyvä kasvain, CTV lisää mikroskooppisen leviämisen marginaalin, PTV lisää asettelun epävarmuusmarginaalin.",
     [
         ("GTV = näkyvä tuumori, CTV = kliininen kohdealue (sis. mikroskooppinen leviäminen), PTV = suunnittelukohdealue (sis. asettelumarginaalit)", True,
          "ICRU 50 määrittelee nämä kolme sisäkkäistä tilavuutta sädehoidon suunnitteluun."),
         ("GTV = koko potilaan kehon annos, CTV = kriittisten elinten annos, PTV = maksimiannos", False,
          "Nämä eivät ole ICRU 50:n tilavuusmääritelmiä."),
         ("GTV, CTV ja PTV ovat eri säteilylajeja", False,
          "Lyhenteet viittaavat hoitotilavuuksiin, eivät säteilylajeihin."),
         ("GTV = kokonaisannos gray-yksikössä, CTV = annos per fraktio, PTV = annos per viikko", False,
          "Nämä eivät liity ICRU 50:n tilavuusmääritelmiin."),
     ]),

    # ======================================================================
    # SÄDEHOITO - Fraktiointimallit
    # ======================================================================
    (171, "Mitä alfa/beta-suhde kuvaa lineaaris-kvadraattisessa mallissa?",
     "Alfa/beta on annos, jossa lineaarinen ja kvadraattinen solukuoleman komponentti ovat yhtä suuret.",
     [
         ("Annos jossa lineaarinen (alfa*d) ja kvadraattinen (beta*d²) solukuoleman komponentti ovat yhtä suuret", True,
          "Alfa/beta-suhde on tärkeä parametri fraktioinnin suunnittelussa."),
         ("Säteilyn maksimi-energia MeV:nä", False,
          "Säteilyn energia ei liity alfa/beta-suhteeseen."),
         ("Puoliintumisaika päivinä", False,
          "Puoliintumisaika on radioaktiivisen hajoamisen käsite."),
         ("Kudoksen happipitoisuus prosentteina", False,
          "Happipitoisuus vaikuttaa säteilyherkkyyteen, mutta ei ole alfa/beta-suhde."),
     ]),
    (171, "Mikä on tyypillinen alfa/beta-arvo nopeasti jakautuvalle kasvaimelle?",
     "Nopeasti jakautuvien kasvainten alfa/beta on tyypillisesti 10 Gy, hitaasti reagoivien normaalikudosten 3 Gy.",
     [
         ("Noin 10 Gy", True,
          "Useimpien kasvainten ja akuutisti reagoivien kudosten alfa/beta on noin 10 Gy."),
         ("Noin 1 Gy", False,
          "Tämä on liian alhainen kasvaimille."),
         ("Noin 3 Gy", False,
          "3 Gy on tyypillinen myöhäisreagoivalle normaalikudokselle, ei kasvaimelle."),
         ("Noin 50 Gy", False,
          "Tämä on epärealistisen korkea arvo."),
     ]),

    # ======================================================================
    # SÄDEHOITO - Bragg-Gray
    # ======================================================================
    (110, "Mikä on Bragg-Gray-onteloteorian perusidea?",
     "Bragg-Gray-teoria yhdistää kaasutäytteisen ontelon annoksen sitä ympäröivän aineen annokseen.",
     [
         ("Pienen kaasutäytteisen ontelon annoksesta voidaan päätellä ympäröivän aineen annos, kun ontelon läsnäolo ei häiritse hiukkaskantaa", True,
          "Tämä on Bragg-Gray-ehdon ydin - ontelon on oltava niin pieni ettei se muuta sekundäärielektronien kantaa."),
         ("Säteilyn annos pienenee eksponentiaalisesti aineen syvyyden funktiona", False,
          "Tämä kuvaa säteilyn vaimenemista, ei Bragg-Gray-teoriaa."),
         ("Protonisäteilyn annos on suurimmillaan kantaman lopussa (Bragg-piikki)", False,
          "Bragg-piikki on eri käsite kuin Bragg-Gray-onteloteoria."),
         ("Absorboitunut annos on sama kaikissa materiaaleissa", False,
          "Annos riippuu materiaalista, ja juuri tätä riippuvuutta Bragg-Gray-teoria käsittelee."),
     ]),

    # ======================================================================
    # SÄDEHOITO - Annossuunnittelu ja laadunvalvonta
    # ======================================================================
    (232, "Mikä on sädehoidon annossuunnitelman optimoinnin tavoite?",
     "Tavoitteena on maksimoida annos kohdealueelle samalla kun terveiden kudosten ja kriittisten elinten annokset minimoidaan.",
     [
         ("Riittävä ja tasainen annos kohdealueelle (PTV) samalla minimoiden kriittisten elinten annokset", True,
          "Tämä on annossuunnittelun perustavoite - hyvä kattavuus ja elinten suojaus."),
         ("Mahdollisimman suuri annos koko keholle", False,
          "Sädehoidon tavoite on kohdistaa annos tuumoriin, ei koko keholle."),
         ("Mahdollisimman nopea hoito riippumatta annoksen jakautumisesta", False,
          "Annoksen jakautuminen on oleellista, nopeus ei ole ensisijainen tavoite."),
         ("Saman annoksen antaminen kaikille potilaille", False,
          "Annossuunnitelma on aina yksilöllinen."),
     ]),
    (284, "Mitä sädehoitolaitteen päivittäiseen laadunvalvontaan tyypillisesti kuuluu?",
     "Päivittäisiin tarkistuksiin kuuluu annoksen tasaisuus, mekaanisten parametrien tarkistus ja turvatoimintojen testaus.",
     [
         ("Säteilyannoksen ulostulo, mekaaninen isosentrin tarkkuus ja turvalukitusten toiminta", True,
          "Nämä ovat päivittäisen QA:n perustarkistuksia."),
         ("Lineaarikiihdyttimen täydellinen purkaminen ja kokoaminen", False,
          "Tämä ei ole realistinen päivittäinen toimenpide."),
         ("Ainoastaan hoitohuoneen lämpötilan mittaus", False,
          "Lämpötila voi olla osa, mutta ei riitä yksinään laadunvalvonnaksi."),
         ("Potilastietokannan varmuuskopiointi", False,
          "IT-toimenpide, ei sädehoidon fysikaalista laadunvalvontaa."),
     ]),

    # ======================================================================
    # ISOTOOPPILÄÄKETIEDE - Gammakamera
    # ======================================================================
    (65, "Mikä on gammakameran pääasiallinen detektorikomponentti?",
     "Gammakameran detektori koostuu tyypillisesti NaI(Tl)-tuikekiteestä ja valomonistinputkista.",
     [
         ("NaI(Tl)-tuikekide yhdistettynä valomonistinputkiin (PMT)", True,
          "Natriumjodidi-talliumkide muuntaa gammasäteilyn valoksi, jonka PMT:t vahvistavat."),
         ("Puolijohdeilmaisin germaniumista", False,
          "Germaniumdetektoreita käytetään spektroskopiassa, ei kliinisessä gammakamerassa."),
         ("Filmikasetti lyijysuodattimella", False,
          "Gammakamerassa ei käytetä filmiä."),
         ("Piezoelektrinen kide", False,
          "Piezoelektrisiä kiteitä käytetään ultraäänilaitteissa, ei gammakameroissa."),
     ]),
    (65, "Mikä on kollimaattorin tehtävä gammakamerassa?",
     "Kollimaattori rajoittaa detektorille pääsevät gammakvantit vain tiettyyn suuntaan, mahdollistaen kuvan muodostuksen.",
     [
         ("Rajata detektorille pääsevät gammakvantit tiettyyn tulosuuntaan paikkainformaation säilyttämiseksi", True,
          "Ilman kollimaattoria detektori näkisi säteilyä kaikista suunnista eikä kuva muodostuisi."),
         ("Vahvistaa gammasäteilyn energiaa", False,
          "Kollimaattori ei vahvista säteilyä, vaan vaimentaa ei-toivotut suunnat."),
         ("Muuntaa gammasäteily näkyväksi valoksi", False,
          "Tämä on tuikekiteen tehtävä, ei kollimaattorin."),
         ("Suojata potilasta sironneelta säteilyltä", False,
          "Kollimaattorin päätehtävä on kuvan muodostus, ei potilaan suojaus."),
     ]),

    # ======================================================================
    # ISOTOOPPILÄÄKETIEDE - PET
    # ======================================================================
    (50, "Mikä fysikaalinen ilmiö on PET-kuvauksen perustana?",
     "PET perustuu positroniemission jälkeiseen annihilaatioon, joka tuottaa kaksi 511 keV fotonia vastakkaisiin suuntiin.",
     [
         ("Positronin ja elektronin annihilaatio, joka tuottaa kaksi 511 keV fotonia vastakkaisiin suuntiin (180°)", True,
          "Kahden fotonin koinsidenssimittaus mahdollistaa paikan määrityksen ilman kollimaattoria."),
         ("Gammasäteilyn Compton-sironta kudoksessa", False,
          "Compton-sironta on häiritsevä ilmiö, ei PET:n perusta."),
         ("Röntgensäteilyn vaimeneminen kehossa", False,
          "Tämä on CT:n periaate."),
         ("Protonien magneettinen resonanssi", False,
          "Tämä on MRI:n periaate."),
     ]),
    (50, "Mikä on yleisin PET-kuvantamisen radiofarmaseutti?",
     "18F-FDG (fluorodeoksiglukoosi) on ylivoimaisesti yleisin PET-merkkiaine.",
     [
         ("18F-FDG (fluorodeoksiglukoosi)", True,
          "FDG on glukoosianalogia, joka kertyy metabolisesti aktiivisiin soluihin kuten syöpäkasvaimiin."),
         ("99mTc-MDP", False,
          "Teknetium-99m-MDP on luuston gammakuvauksen merkkiaine, ei PET-aine."),
         ("131I (jodi)", False,
          "Jodi-131 käytetään kilpirauhashoidossa ja kuvantamisessa, mutta ei ole PET-aine."),
         ("201Tl (tallium)", False,
          "Tallium-201 on vanha sydänperfuusion SPET-merkkiaine."),
     ]),

    # ======================================================================
    # ISOTOOPPILÄÄKETIEDE - SPET ja sydänperfuusio
    # ======================================================================
    (63, "Miksi absorptiokorjaus on tärkeä SPET-kuvantamisessa?",
     "Gammasäteilyn vaimeneminen kehossa vääristää kuvaa, ellei sitä korjata.",
     [
         ("Koska kehon sisäosista tuleva gammasäteily vaimenee enemmän kuin pinnalta, mikä vääristää kuvaa", True,
          "Ilman korjausta syvällä olevat kohteet näyttävät vaimeammilta kuin ne todellisuudessa ovat."),
         ("Koska potilas liikkuu tutkimuksen aikana", False,
          "Liikeartefakta on eri ongelma kuin absorptiovääristymä."),
         ("Koska tuikekide ei toimi tasaisesti koko alueella", False,
          "Tämä on kameran uniformiteettiongelma, ei absorptiokorjaus."),
         ("Koska kollimaattori aiheuttaa kuvaan geometrisen vääristymän", False,
          "Kollimaattorin epäideaalisuus on eri korjattava tekijä."),
     ]),
    (59, "Mikä merkkiaine kertyy sydänlihaksen perfuusiotutkimuksessa iskeemiseen alueeseen vähemmän?",
     "Perfuusiotutkimuksessa verenvirtauksen mukana kulkeutuva merkkiaine kertyy huonommin iskeemisille alueille.",
     [
         ("99mTc-sestamibi tai 99mTc-tetrofosmiini", True,
          "Nämä teknetium-merkkiaineet kertyvät verenvirtauksen mukaan ja osoittavat perfuusiopuutokset."),
         ("18F-FDG", False,
          "FDG kertoo aineenvaihdunnasta, ei perfuusiosta - elävä mutta iskeeminen sydänlihas voi kertyttää FDG:tä."),
         ("131I-natriumjodidi", False,
          "Jodi-131 kertyy kilpirauhaseen, ei sydänlihakseen."),
         ("99mTc-MDP", False,
          "MDP kertyy luustoon, ei sydänlihakseen."),
     ]),

    # ======================================================================
    # ISOTOOPPILÄÄKETIEDE - Luusto ja keuhkot
    # ======================================================================
    (131, "Mikä merkkiaine on luuston gammakuvauksessa käytetty ja mihin se kertyy?",
     "99mTc-MDP kertyy osteoblastiaktiivisuuden mukaan luuston alueille joissa luuaineenvaihdunta on lisääntynyt.",
     [
         ("99mTc-MDP (metyylidi-fosfonaatti), kertyy luuston lisääntyneen aineenvaihdunnan alueille", True,
          "MDP kertyy osteoblastiaktiivisiin kohtiin kuten metastaaseihin, murtumiin ja infektioihin."),
         ("18F-FDG, kertyy luuston glukoosimetabolian mukaan", False,
          "FDG on PET-aine yleiseen onkologiaan, ei spesifinen luukuvaukselle."),
         ("99mTc-MAA, kertyy keuhkokapillaareihin", False,
          "MAA on keuhkoemboliatutkimuksen merkkiaine."),
         ("67Ga-sitraatti, kertyy infektiokohteisiin", False,
          "Gallium-67 on infektio/kasvain-merkkiaine, ei ensisijainen luuston kuvaukseen."),
     ]),
    (172, "Mitä tutkitaan keuhkoperfuusion gammakuvauksella?",
     "Keuhkoperfuusiokuvaus osoittaa keuhkojen verenkierron jakautumisen - puutosalueet voivat viitata keuhkoemboliaan.",
     [
         ("Keuhkojen verenkierron jakautuminen - perfuusiopuutokset voivat viitata keuhkoemboliaan", True,
          "99mTc-MAA-partikkelit kiilautuvat keuhkokapillaareihin verenkierron mukaisesti."),
         ("Keuhkokudoksen tulehdusaste", False,
          "Perfuusiokuvaus ei suoraan mittaa tulehdusta."),
         ("Keuhkojen hapenottokyky", False,
          "Hapenottokykyä mitataan spirometrialla, ei gammakuvauksella."),
         ("Keuhkosyövän metabolinen aktiivisuus", False,
          "Syövän metaboliaa arvioidaan PET-FDG:llä, ei perfuusiokuvauksella."),
     ]),

    # ======================================================================
    # KNF - EEG
    # ======================================================================
    (60, "Mikä on EEG:n mittaaman signaalin lähde?",
     "EEG mittaa pääasiassa aivokuoren pyramidisolujen postsynaptisten potentiaalien summaa.",
     [
         ("Aivokuoren pyramidisolujen postsynaptisten potentiaalien summaa päälaen pinnalta", True,
          "EEG mittaa makroskooppista sähköistä aktiviteettia, joka syntyy samansuuntaisesti orientoituneiden neuronien summa-aktiviteettina."),
         ("Yksittäisten neuronien aktiopotentiaaleja", False,
          "EEG ei kykene erottelemaan yksittäisiä aktiopotentiaaleja päälaen pinnalta."),
         ("Aivojen magneettikentän muutoksia", False,
          "Magneettikenttiä mittaa MEG, ei EEG."),
         ("Aivojen verenkierron muutoksia", False,
          "Verenkiertomuutoksia mittaa fMRI ja PET, ei EEG."),
     ]),
    (271, "Mikä on kansainvälinen 10-20 -järjestelmä EEG-mittauksessa?",
     "10-20-järjestelmä on standardoitu elektrodien asettelumenetelmä, joka perustuu pään mittapisteisiin.",
     [
         ("Standardoitu EEG-elektrodien sijoittelujärjestelmä, jossa elektrodit asetetaan 10% ja 20% välein pään anatomisten maamerkkien perusteella", True,
          "Järjestelmä takaa vertailukelpoiset mittaukset eri laboratorioiden välillä."),
         ("Suodatusasetukset, joissa alanpäästö on 10 Hz ja ylänpäästö 20 Hz", False,
          "10-20 viittaa elektrodien sijaintiin, ei suodatusasetuksiin."),
         ("Mittausprotokolla, jossa rekisteröidään 10 sekuntia silmät auki ja 20 sekuntia silmät kiinni", False,
          "Tämä ei kuvaa 10-20-järjestelmää."),
         ("Diagnostinen kynnysarvo: yli 10 piikkiä 20 sekunnissa on patologinen", False,
          "10-20 ei ole diagnostinen kriteeri."),
     ]),

    # ======================================================================
    # KNF - Herätepotentiaalit
    # ======================================================================
    (119, "Mitä mitataan hermoston johtumisnopeusmittauksissa?",
     "Perifeerisen hermon johtumisnopeus (NCV) mitataan stimuloimalla hermoa ja mittaamalla vasteen viive.",
     [
         ("Hermoimpulssin etenemisnopeus perifeerisissä hermoissa stimulaatio-vasteparin viiveestä", True,
          "Johtumisnopeus lasketaan etäisyyden ja viiveen suhteena."),
         ("Hermon toimintapotentiaalin amplitudi mikrovoltteina", False,
          "Amplitudi mitataan kyllä, mutta johtumisnopeus on eri suure."),
         ("Aivojen sähköisen toiminnan taajuusspektri", False,
          "Tämä kuvaa kvantitatiivista EEG:tä, ei NCV:tä."),
         ("Lihaksen supistumisvoima newtonmetreinä", False,
          "Voiman mittaus on eri tutkimus kuin NCV."),
     ]),
    (178, "Mikä on somatosensorisen herätepotentiaalin (SEP) tyypillinen stimulointikohde?",
     "SEP-tutkimuksessa stimuloidaan yleisimmin medianushermoa ranteessa tai tibiaalishermoa nilkassa.",
     [
         ("Medianushermo ranteessa tai tibiaalishermo nilkassa", True,
          "Nämä ovat vakiintuneet stimulointikohdat, joista vasteen kulku aivoihin voidaan seurata."),
         ("Näköhermo silmän takana", False,
          "Visuaalista herätepotentiaalia (VEP) stimuloidaan valon vilkkumisella, ei suoraan hermon stimulaatiolla."),
         ("Kuulohermo korvakäytävässä", False,
          "Auditiivista herätepotentiaalia (BAEP) stimuloidaan äänellä kuulokkeilla."),
         ("Selkäydin lannerangasta", False,
          "Selkäydintä ei stimuloida suoraan SEP-tutkimuksessa."),
     ]),

    # ======================================================================
    # KNF - TMS
    # ======================================================================
    (327, "Mikä on transkraniaalisen magneettistimulaation (TMS) toimintaperiaate?",
     "TMS:ssä muuttuva magneettikenttä indusoi sähkökentän aivokuoreen, joka aktivoi neuroneja.",
     [
         ("Nopeasti muuttuva magneettikenttä kelan läpi indusoi sähkökentän aivokuoreen, joka depolarisoi neuroneja", True,
          "Faradayn induktiolain mukaisesti muuttuva B-kenttä synnyttää sähkökentän aivoissa."),
         ("Staattinen magneettikenttä suuntaa neuronien aksoneita", False,
          "Staattinen kenttä ei aktivoi neuroneja."),
         ("Ultraääniaalto kohdistetaan aivokuoreen neuroerotuskynnyksen ylittämiseksi", False,
          "Ultraääni ei ole TMS:n toimintamekanismi."),
         ("Suora sähkövirta johdetaan päänahkaan elektrodien kautta", False,
          "Tämä kuvaa tDCS:ää (transkraniaalinen tasavirtastimulaatio), ei TMS:ää."),
     ]),

    # ======================================================================
    # KNF - Uni
    # ======================================================================
    (333, "Mitä tutkitaan yöpolygrafiassa (unirekisteröinti)?",
     "Yöpolygrafia mittaa EEG:tä, EMG:tä, EOG:tä, hengitystä ja happisaturaatiota unen aikana.",
     [
         ("EEG, silmänliikkeet (EOG), lihasjännitys (EMG), hengitys, happisaturaatio ja sydämen rytmi unen aikana", True,
          "Nämä parametrit mahdollistavat univaiheiden luokittelun ja unihäiriöiden diagnostiikan."),
         ("Ainoastaan aivojen EEG-aktiviteetti unen aikana", False,
          "Polygrafia sisältää useita samanaikaisia mittauksia, ei pelkkää EEG:tä."),
         ("Verenpaineen vaihtelu yön aikana", False,
          "Verenpaine ei ole yöpolygrafian perusparametri."),
         ("Veren glukoosipitoisuuden muutokset yöllä", False,
          "Glukoosimittaus ei kuulu unipolygrafiaan."),
     ]),

    # ======================================================================
    # FYSIOLOGIA - Sydän
    # ======================================================================
    (118, "Mikä on sydämen johtoratajärjestelmän oikea etenemisreitti?",
     "Sähköimpulssi etenee: sinussolmuke → eteiset → AV-solmuke → Hisin kimppu → Purkinjen säikeet → kammiot.",
     [
         ("SA-solmuke → AV-solmuke → Hisin kimppu → oikea ja vasen haarakekimppu → Purkinjen säikeet → kammiolihas", True,
          "Tämä on normaali johtoratajärjestelmän reitti."),
         ("AV-solmuke → SA-solmuke → Purkinjen säikeet → Hisin kimppu → kammiolihas", False,
          "Reitti on väärin päin; SA-solmuke on primaarinen tahdistaja."),
         ("Purkinjen säikeet → kammiolihas → SA-solmuke → AV-solmuke", False,
          "Impulssi kulkee ylhäältä alas, ei toisin päin."),
         ("SA-solmuke → kammiolihas suoraan ilman välitysrakenteita", False,
          "Impulssi vaatii AV-solmukkeen ja Hisin kimpun etenemiseen."),
     ]),

    # ======================================================================
    # FYSIOLOGIA - Keuhkot
    # ======================================================================
    (45, "Mikä on keuhkojen kaasujenvaihdon perusmekanismi?",
     "Kaasujen vaihto perustuu hapen ja hiilidioksidin diffuusioon konsentraatiogradientin mukaisesti alveolien ja kapillaarien välillä.",
     [
         ("Diffuusio konsentraatiogradientin (osapaine-eron) mukaisesti alveolien ja keuhkokapillaarien välillä", True,
          "Happi siirtyy korkeammasta osapaineesta (alveolit) matalampaan (veri) ja CO2 päinvastoin."),
         ("Aktiivinen kuljetus solumembraanien ionipumppujen avulla", False,
          "Kaasujen vaihto on passiivinen diffuusioprosessi, ei aktiivista kuljetusta."),
         ("Osmoosi vesiliukoisten kaasujen välillä", False,
          "Osmoosi koskee veden siirtymistä, ei kaasujen vaihtoa."),
         ("Mekaaninen pumppaus keuhkorakkuloiden lihassoluilla", False,
          "Alveolit eivät sisällä lihassoluja; hengitysliike tulee palleasta ja kylkivälilihaksista."),
     ]),

    # ======================================================================
    # FYSIOLOGIA - Munuaiset
    # ======================================================================
    (75, "Mikä on nefronin glomeruluksen tehtävä?",
     "Glomerulus suodattaa verta ja muodostaa primaarivirtsaa paineen avulla.",
     [
         ("Suodattaa plasmaa paineen avulla muodostaen primaarivirtsan (glomerulusfiltraatio)", True,
          "Glomeruluksessa kapillaarien verenpaine työntää veden ja pienet molekyylit Bowmanin kapseliin."),
         ("Reabsorboida takaisin glukoosi ja aminohapot", False,
          "Takaisinimeytyminen tapahtuu tubulusjärjestelmässä, ei glomeruluksessa."),
         ("Erittää hormoneja verenkiertoon", False,
          "Munuaisilla on endokriinisia tehtäviä, mutta glomerulus ei ole ensisijainen eritysyksikkö."),
         ("Konsentroida virtsaa poistamalla vettä", False,
          "Virtsan konsentraatio tapahtuu Henlen lingossa ja kokoojaputkissa."),
     ]),

    # ======================================================================
    # FYSIOLOGIA - Säteilybiologia
    # ======================================================================
    (53, "Mikä on ionisoivan säteilyn tärkein biologinen vaikutusmekanismi solutasolla?",
     "Säteilyn suora ja epäsuora vaikutus DNA:han aiheuttaa katkoksia ja vaurioita, jotka voivat johtaa solukuolemaan tai mutaatioihin.",
     [
         ("DNA-kaksoisjuostekatkokset suoran osuman tai vapaiden radikaalien välityksellä", True,
          "DNA-vaurio, erityisesti kaksoisjuostekatkosten (DSB) korjaamattomuus, on keskeinen solukuoleman mekanismi."),
         ("Solun membraanin sulaminen lämmön vaikutuksesta", False,
          "Diagnostinen ja terapeuttinen säteily ei aiheuta merkittävää lämpenemistä."),
         ("Proteiinien välitön denaturoituminen", False,
          "Proteiinivauriot syntyvät, mutta DNA-vaurio on kriittisin biologinen tapahtuma."),
         ("Solun sisäisen nesteen haihtuminen", False,
          "Tämä ei ole ionisoivan säteilyn mekanismi normaaleilla annosilla."),
     ]),

    # ======================================================================
    # KLIININEN FYSIOLOGIA - EKG
    # ======================================================================
    (100, "Mitkä ovat standardin 12-kytkentäisen EKG:n raajakytkennät?",
     "Raajakytkennät ovat bipolaariset I, II, III ja unipolaariset aVR, aVL, aVF.",
     [
         ("I, II, III (bipolaariset) ja aVR, aVL, aVF (unipolaariset)", True,
          "Einthovenin kolmio antaa bipolaariset ja Goldberger-kytkennät unipolaariset raajakytkennät."),
         ("V1-V6 rintakytkennät", False,
          "V1-V6 ovat rintakytkentöjä (precordial), eivät raajakytkentöjä."),
         ("Ainoastaan I ja II", False,
          "Standardi-EKG sisältää kuusi raajakytkentää, ei kahta."),
         ("aVR, aVL, aVF, aVP, aVQ, aVS", False,
          "aVP, aVQ ja aVS eivät ole olemassa standardi-EKG:ssä."),
     ]),
    (115, "Mikä on FEV1 keuhkofunktiotutkimuksessa?",
     "FEV1 on uloshengityksen sekuntikapasiteetti - ilmamäärä joka puhalletaan ulos ensimmäisen sekunnin aikana maksimaalisessa uloshengityksessä.",
     [
         ("Ensimmäisen sekunnin aikana voimakkaan uloshengityksen aikana ulospuhallettu ilmamäärä", True,
          "FEV1 on tärkein spirometriaparametri obstruktiivisten keuhkosairauksien diagnostiikassa."),
         ("Keuhkojen kokonaiskapasiteetti litraina", False,
          "Kokonaiskapasiteetti (TLC) on eri suure kuin FEV1."),
         ("Sisäänhengityksen huippuvirtaus litraa/sekunti", False,
          "Tämä kuvaa PIF:ia (Peak Inspiratory Flow), ei FEV1:tä."),
         ("Hengitysteiden resistanssi pascal-sekunteina per litra", False,
          "Resistanssimittaus on eri tutkimus kuin spirometria."),
     ]),

    # ======================================================================
    # KLIININEN FYSIOLOGIA - Pulssioksimetria
    # ======================================================================
    (122, "Mikä on pulssioksimetrian toimintaperiaate?",
     "Pulssioksimetri mittaa hapettuneen ja hapettumattoman hemoglobiinin absorptioeroa kahdella aallonpituudella.",
     [
         ("Mittaa valon absorption eroa hapettuneelle ja hapettumattomalle hemoglobiinille kahdella aallonpituudella (punainen ja infrapuna)", True,
          "Oksihemoglobiini ja deoksihemoglobiini absorboivat eri tavalla näillä aallonpituuksilla."),
         ("Mittaa veren hiilidioksidipitoisuuden infrapunaspektroskopialla", False,
          "Pulssioksimetria mittaa happikyllästeisyyttä, ei CO2:ta."),
         ("Mittaa pulssipainetta sormenpään kompressiolla", False,
          "Pulssioksimetria on optinen menetelmä, ei mekaaninen painemittaus."),
         ("Mittaa veren pH:n elektrokemiallisella anturilla", False,
          "pH mitataan verikaasunäytteestä, ei pulssioksimetrilla."),
     ]),

    # ======================================================================
    # ANATOMIA - Sydän
    # ======================================================================
    (324, "Mitkä ovat sydämen tärkeimmät sepelvaltimot?",
     "Vasen sepelvaltimo (LCA) jakautuu LAD:ksi ja LCX:ksi, oikea sepelvaltimo (RCA) huoltaa sydämen oikeaa puolta.",
     [
         ("Vasen sepelvaltimo (LCA: LAD + LCX) ja oikea sepelvaltimo (RCA)", True,
          "LAD huoltaa vasemman kammion etuosaa, LCX sivuseinää ja RCA oikeaa kammiota ja takaseinää."),
         ("Aortta ja keuhkovaltimo", False,
          "Nämä ovat suuret valtimot, eivät sepelvaltimot."),
         ("Yläontto- ja alaonttolaskimo", False,
          "Nämä ovat laskimoita jotka palauttavat verta sydämeen."),
         ("A. carotis ja a. vertebralis", False,
          "Nämä ovat pään alueen valtimot, eivät sepelvaltimot."),
     ]),
]


class Command(BaseCommand):
    help = 'Populate real subject-matter MCQ questions from exam topics'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear', action='store_true',
            help='Delete previously generated exam MCQs before creating new ones',
        )

    def handle(self, *args, **options):
        if options['clear']:
            deleted, _ = Question.objects.filter(
                exam_question__isnull=False
            ).delete()
            self.stdout.write(f'Deleted {deleted} existing exam-linked MCQ objects.')

        created_q = 0
        created_c = 0
        errors = 0

        for exam_q_id, text, explanation, choices in QUESTIONS:
            try:
                exam_q = ExamQuestion.objects.get(id=exam_q_id)
            except ExamQuestion.DoesNotExist:
                self.stderr.write(f'ExamQuestion {exam_q_id} not found, skipping.')
                errors += 1
                continue

            epa_id = AREA_EPA.get(exam_q.subject_area, 11)

            q = Question.objects.create(
                question_type='multiple_choice',
                difficulty=4,
                text=text,
                explanation=explanation,
                epa_id=epa_id,
                exam_question=exam_q,
                is_active=True,
            )
            created_q += 1

            for i, (c_text, is_correct, c_explanation) in enumerate(choices):
                Choice.objects.create(
                    question=q,
                    text=c_text,
                    is_correct=is_correct,
                    order=i,
                    explanation=c_explanation,
                )
                created_c += 1

        self.stdout.write(self.style.SUCCESS(
            f'Created {created_q} MCQ questions with {created_c} choices ({errors} errors).'
        ))
