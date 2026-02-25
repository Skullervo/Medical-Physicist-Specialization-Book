# Mallivastausten faktatarkistusloki

**Päivämäärä**: 2026-02-19
**Tarkistetut vastaukset**: 241 alkuperäistä mallivastausta (5 erikoisalaa)
**Tarkistaja**: Claude Code (automaattinen faktatarkistus)

---

## Yhteenveto

| Erikoisala | Vastauksia | Substanssivastauksia | Löydöksiä | Kriittiset |
|---|---|---|---|---|
| Sädehoito | 52 | 41 | 17 | 3 |
| Radiologia | 74 | 50 | 11 | 3 |
| Kliininen fysiologia | 47 | 25 | 12 | 3 |
| Isotooppilääketiede | 40 | 25 | 11 | 2 |
| KNF | 28 | 17 | 14 | 2 |
| **Yhteensä** | **241** | **158** | **65** | **13** |

**Huomautus**: 83 vastausta (34 %) koostuu pelkistä ristiviittauksista ("Ks. vastaus kysymyksessä X") ilman varsinaista sisältöä. Nämä käyttävät sisäistä numerointia, joka ei vastaa tietokannan ID-kenttää.

---

## Löydöstyypit

- **factual_error**: Virheellinen fakta, arvo tai tulkinta
- **formula_error**: Virheellinen kaava tai laskuvirhe
- **missing_info**: Puuttuva olennainen tieto tai väärä sisältö
- **terminology**: Kirjoitusvirhe tai väärä terminologia

---

## KRIITTISET KORJAUKSET (prioriteetti 1)

### K1. Sädehoito Q826 — Väärä vastaus kokonaan
- **ID**: 826, vuosi 2015
- **Tyyppi**: missing_info (KRIITTINEN)
- **Ongelma**: Kysymys on "Liikkeen hallinta sädehoidossa" mutta mallivastaus käsittelee sydämentahdistimia ja defibrillaattoreita. Täydellinen sisältövirhe.
- **Korjaus**: Korvaa vastaus sisällöllä: hengitystahdistus (gating), DIBH, 4D-CT/ITV, tuumorin seuranta, vatsan kompressio, reaaliaikainen monitorointi.

### K2. Sädehoito Q795 — TCP-kaava käänteinen
- **ID**: 795, vuosi 2002
- **Tyyppi**: formula_error
- **Ongelma**: TCP = 1 − exp(−N₀ × SF) on väärin. Tämä antaa epäonnistumisen todennäköisyyden (vähintään 1 solu elossa).
- **Korjaus**: TCP = exp(−N₀ × SF), jossa TCP → 1 kun N₀ × SF → 0.

### K3. Sädehoito Q775 — R90-approksimaatio
- **ID**: 775, vuosi 1993
- **Tyyppi**: formula_error
- **Ongelma**: R90 ≈ E/4 cm aliarvioi terapeuttisen kantaman merkittävästi. Esim. 12 MeV: E/4 = 3,0 cm vs. todellinen ~3,5–3,8 cm.
- **Korjaus**: R90 ≈ E/3,2 cm (tai E/3 – E/3,5 cm).

### K4. Radiologia Q733 — Valosähköinen ilmiö Z-riippuvuus
- **ID**: 733, vuosi 2008
- **Tyyppi**: formula_error
- **Ongelma**: Z³/E³ on väärin. Standardi on Z⁴/E³ (tai Z⁴⁻⁵/E³).
- **Korjaus**: Muuta Z³ → Z⁴ (Bushberg, Attix, Khan).

### K5. Radiologia Q753 — Kaksoisannosimetria-kaava
- **ID**: 753, vuosi 2017
- **Tyyppi**: formula_error
- **Ongelma**: E ≈ 0,025 × H_over + 1,0 × H_under — H_under-kerroin 1,0 on liian suuri.
- **Korjaus**: Niklason-kaava: E = 1,5 × H_w + 0,04 × H_n, tai E ≈ 0,5 × H_under + 0,025 × H_over.

### K6. Radiologia Q715 — Perinnöllisten vaikutusten riskikerroin
- **ID**: 715, vuosi 2002
- **Tyyppi**: factual_error
- **Ongelma**: ~1 %/Sv on ICRP 60:n arvo (1990). ICRP 103 (2007) antaa 0,2 %/Sv.
- **Korjaus**: Muuta ~1 %/Sv → ~0,2 %/Sv (ICRP 103).

### K7. Kliininen fysiologia Q954 — EKG-kaistanleveys
- **ID**: 954, vuosi 1993
- **Tyyppi**: factual_error
- **Ongelma**: Diagnostinen EKG 0,05–100 Hz on vanhentunut. Standardi on 0,05–150 Hz (AHA/IEC). Ristiriidassa saman tekijän vastauksen Q966 kanssa.
- **Korjaus**: Muuta 0,05–100 Hz → 0,05–150 Hz.

### K8. Kliininen fysiologia Q969 — Valsalva-kuvaus
- **ID**: 969, vuosi 2000
- **Tyyppi**: factual_error
- **Ongelma**: "Pakotettu uloshengitys suljetuista hengitysteistä" on väärin. Potilas puhaltaa avoimeen suukappaleeseen vastapainetta vasten.
- **Korjaus**: "Pakotettu ulospuhallus suukappaleen kautta vakioitua vastapainetta vasten (40 mmHg, 15 s)."

### K9. Kliininen fysiologia Q991 — MI-turvallisuusraja
- **ID**: 991, vuosi 2009
- **Tyyppi**: factual_error
- **Ongelma**: MI < 0,3 turvallinen on liian konservatiivinen. Tämä koskee vain kontrastiainekuvausta.
- **Korjaus**: MI < 0,7 matala riski (ilman kontrastiaineita), < 0,4 kontrastiaineen kanssa, > 1,9 FDA:n yläraja.

### K10. Isotooppilääketiede Q872 — DXA K-edge järjestysluku
- **ID**: 872, vuosi 1992
- **Tyyppi**: factual_error
- **Ongelma**: "53-Ce" on virheellinen. Ceriumin järjestysluku on 58 (Z=53 = jodi).
- **Korjaus**: Ce, Z=58 (tai poista järjestysluku).

### K11. Isotooppilääketiede Q874 — MIRD-yksiköt
- **ID**: 874, vuosi 1994
- **Tyyppi**: formula_error
- **Ongelma**: "Bq·s = MBq·h" on matemaattisesti väärin (1 MBq·h = 3,6 × 10⁹ Bq·s).
- **Korjaus**: Erota yksiköt: "Bq·s (käytännössä usein ilmaistu MBq·h muodossa, muunnoskerroin huomioiden)."

### K12. KNF Q1031 — Vuotovirrarajat
- **ID**: 1031, vuosi 2005
- **Tyyppi**: factual_error
- **Ongelma**: <10 µA / <50 µA esitetään yleisinä rajoina, mutta nämä ovat CF-tyypin (sydänsovellukset) rajoja. KNF-laitteet käyttävät pääosin BF-tyyppiä: <100 µA / <500 µA.
- **Korjaus**: Erittele: BF-tyyppi (yleisin KNF): <100 µA (normaali), <500 µA (vika). CF-tyyppi (sydän): <10 µA / <50 µA.

### K13. KNF Q1017 — BAEP-latenssialue
- **ID**: 1017, vuosi 1996
- **Tyyppi**: factual_error
- **Ongelma**: "Latenssi 1–7 ms" on liian laaja. Aalto V 7 ms:ssa olisi patologinen.
- **Korjaus**: "~1,5–6 ms (aalto I ~1,5 ms, aalto V ~5,7 ms)."

---

## MUUT FAKTAVIRHEET (prioriteetti 2)

### Sädehoito

| ID | Vuosi | Tyyppi | Kuvaus | Korjaus |
|---|---|---|---|---|
| 776 | 1994 | factual_error | TV = 90 % isodoosi; ICRU 50 käyttää tyypillisesti 95 % | Muuta 90 % → hoitosuunnitelman isodoosi (tyypillisesti 95 %) |
| 777 | 1994 | factual_error | −5/+7 % ICRU-referenssipisteestä; pitäisi olla prescribed dose | Muuta viittaus prescribed dose -annokseen |
| 779 | 1995 | factual_error | Lu-177-DOTATATE/PSMA eivät ole vasta-ainepohjaisia | Tarkenna: radioligandihoidot, ei radioimmuno |
| 793 | 2002 | factual_error | CI 0,9–1,5; CI < 1,0 = alikattavuus | Muuta 0,9 → 1,0 alarajaksi |
| 796 | 2003 | factual_error | Magnetroni/klystroni raja ~6 MV liian jyrkkä | Tarkenna: raja ei ole tarkka |
| 800 | 2006 | formula_error | BED-repopulaatiokaava esitys sekava | Selkeytä notaatio |
| 828 | 2015 | factual_error | CBCT-annos 10–30 mGy liian matala vartalokuvauksille | Muuta 10–60 mGy (pää 10–20, vartalo 20–60) |
| 832 | 2016 | factual_error | MR-linac 7 MV: puuttuu FFF-maininta | Lisää "FFF" (flattening-filter-free) |
| 846 | 2019 | missing_info | Fraktioiden väliaikaa ei käsitellä riittävästi | Lisää oma osio fraktiovälistä |

### Radiologia

| ID | Vuosi | Tyyppi | Kuvaus | Korjaus |
|---|---|---|---|---|
| 662 | 1990 | formula_error | HU-kaava: (µ_vesi − µ_ilma) nimittäjässä epästandardi | Muuta nimittäjäksi µ_vesi |
| 668 | 1993 | terminology | "fosforointia" = fosforylaatio; pitäisi olla "luminenssia" | Fotostimuloitava luminenssi (PSL) |
| 713 | 2002 | terminology | "robotti" → "robusti"; "kirjasemana" → "kirkkaampana" | Korjaa kirjoitusvirheet |
| 739 | 2010 | factual_error | Thorax PA 0,01–0,03 mGy sekoittaa ESD:n ja efektiivisen annoksen | ESD ~0,1–0,3 mGy, E ~0,02 mSv |
| 739 | 2010 | terminology | "Overbeeming", "projiintiokuvauksessa" kirjoitusvirheet | Korjaa |
| 682 | 1996 | missing_info | Efektiivinen mittauspiste "0,6r" — r ei määritelty | Tarkenna: 0,6 × r_cav (kaviteetin sisäsäde) |
| 741 | 2013 | missing_info | AGD-kaavan K ei selkeästi erotettu ESAK:sta | Tarkenna: incident air kerma (ilman BSF) |

### Kliininen fysiologia

| ID | Vuosi | Tyyppi | Kuvaus | Korjaus |
|---|---|---|---|---|
| 951 | 1991 | terminology | "Boyle-Mariottenlaik" katkennut sana | Korjaa: "Boylen–Mariottenin laki" |
| 964 | 1997 | factual_error | Holter 128–180 Hz "riittävä" — moderni suositus ≥250 Hz | Päivitä: ≥250 Hz QRS-morfologiaan |
| 969 | 2000 | missing_info | SDNN >100 ms ilman tallennuspituutta | Lisää: "24 h tallennuksessa" |
| 977 | 2005 | formula_error | DLCO-kaavasta puuttuu yksikkömuunnos | Lisää huomautus barometrisesta korjauksesta |
| 979 | 2005 | factual_error | S4 "paitsi urheilijoilla" — kiistanalainen | Muuta: "yleensä patologinen" |
| 983 | 2006 | terminology | "neliölkeskiarvo" kirjoitusvirhe | Korjaa: "neliökeskiarvo" |
| 995 | 2010 | terminology | "optopotentiometriset" ei standarditermi; "ajakallinen" → "ajallinen" | Korjaa molemmat |
| 978 | 2005 | missing_info | P-aalto ~80 ms aliarvioi normaalia (80–110 ms) | Muuta: 80–110 ms |

### Isotooppilääketiede

| ID | Vuosi | Tyyppi | Kuvaus | Korjaus |
|---|---|---|---|---|
| 867 | 1990 | missing_info | Tl-201 gammaemissiot 135/167 keV puuttuvat | Lisää energiapiikit |
| 867 | 1990 | factual_error | 1-day-protokollan aktiivisuus "300–600 MBq" harhaanjohtava | Tarkenna: lepo 300 + rasitus 900 MBq |
| 867 | 1990 | factual_error | "17/20-segmenttimalli" — AHA-standardi on 17 | Korjaa: 17-segmenttimalli (AHA) |
| 902 | 2005 | factual_error | Gd-153 "lähellä" 140 keV — ero ~30–40 % | Tarkenna sanamuotoa |
| 868/902 | 1991/2005 | factual_error | Co-60 SPECT-transmissiolähteenä — Gd-153 oli yleisempi | Tarkenna yleisyyttä |
| 933 | 2018 | missing_info | Tc-99m-generaattorin kuvaus puuttuu (viittaa olemattomaan) | Lisää Mo-99/Tc-99m-kuvaus |
| 943 | 2021 | missing_info | Sädehoidon kysymys liian suppea | Laajenna ICRU-sisältöä |
| 946 | 2022 | terminology | MIBG = "hermovälittäjaainekuvaus" — on sympaattinen innervatio | Muuta otsikkoa |

### KNF

| ID | Vuosi | Tyyppi | Kuvaus | Korjaus |
|---|---|---|---|---|
| 1013 | 1990 | factual_error | Radiaalilähteet "heikosti havaittava kenttä" — pallomallissa ei kenttää lainkaan | Korjaa: "eivät tuota havaittavaa magneettikenttää pallomallissa" |
| 1022 | 1998 | factual_error | Kallon johtavuus 1/80 — vanhasta Rush & Driscoll 1968; uudemmat ~1/20–1/40 | Päivitä vaihteluväli |
| 1017 | 1996 | factual_error | BAEP aalto V generaattori "mesenkephalon" — tarkemmin lateraalinen lemnisci / colliculus inferior | Tarkenna |
| 1023 | 1998 | factual_error | N3 ">20 %" pitäisi olla "≥20 %" (AASM) | Korjaa |
| 1023 | 1998 | terminology | "korvaamaton ääni" — todennäköisesti "kuorsausääni" | Korjaa |
| 1024 | 1998 | missing_info | 10-20 järjestelmä "21 elektrodia" — tarkenna: 19 skalp + 2 referenssi | Lisää tarkennus |
| 1028 | 2000 | factual_error | MSLT "normaali >8 min" — tarkemmin >10 min; 8–10 rajatapaus | Tarkenna: >10 min normaali |
| 1018 | 1996 | missing_info | A-alfa "motoneuronit" — puuttuvat proprioseptiiviset afferentit Ia/Ib | Lisää Ia/Ib |
| 1027 | 1999 | missing_info | 50 Hz häiriön poisto — adaptiivinen suodatus puuttuu | Lisää adaptiivinen notch-suodatus |
| 1058 | 2019 | missing_info | IOM-vastaus — hälytyskriteerit puuttuvat (SEP 50 %/10 %, MEP, D-aalto) | Lisää hälytyskriteerit |
| 1061 | 2022 | missing_info | QA-vastaus viittaa "kysymykseen 42" — ei löydy tiedostosta | Lisää EEG QA:n tiivistelmä |

---

## KIRJOITUSVIRHEET (prioriteetti 3)

### Sädehoito
| ID | Virhe | Korjaus |
|---|---|---|
| 770 | "radioaaalot" | "radioaallot" |
| 853 | "riskielmisille" | "riskielimille" |
| 855 | "kaksoisfaalifoili", "paasaantoon" | "kaksoissironta­foili", "päähän" |
| 860 | "Heijastusnukka", "Yhdemukaisuus" | "Heijastusvalo", "Yhdenmukaisuus" |

### KNF
| ID | Virhe | Korjaus |
|---|---|---|
| 1013 | "Synapttiset", "postsynapttiset", "Radiaaaliset", "kryogeeniajaahdytysta" | "Synaptiset", "postsynaptiset", "Radiaaliset", "kryogeenijäähdytystä" |
| 1015 | "neuromsukulaarisen" | "neuromuskulaarisen" |
| 1018 | "postsynapttiinen" | "postsynaptinen" |
| 1022 | "dipolaarilahteen", "fokuaaleihin" | "dipolaarilähteen", "fokaalisiin" |
| 1024 | "kollodiumikiinnitys" | "kollodiumilla kiinnitys" |
| 1030 | "aktipotentiaalien" | "aktiopotentiaalien" |
| 1032 | "perifeerier hemon" | "periferisen hermon" |
| 1035 | "nasoini" | "nasion" |
| 1038 | "motoriiikka" | "motoriikka" |
| 1061 | "kunno", "trenditanalyysi" | "kunnon", "trendianalyysi" |

---

## RAKENTEELLINEN HUOMAUTUS: Ristiviittaukset

83 vastausta 241:stä (34 %) koostuu pelkistä ristiviittauksista ("Ks. vastaus kysymyksessä X"). Nämä ovat ongelmallisia:

1. **Viittausnumerointi** ei vastaa tietokannan ID-kenttää — opiskelija ei löydä viitattua vastausta.
2. **AI-arviointi** ei saa käyttökelpoista mallivastausta pisteytyksen pohjaksi.
3. **Itsenäinen opiskelu** ei ole mahdollista pelkän viittauksen perusteella.

**Suositus**: Korvaa ristiviittaukset itsenäisillä vastauksilla tai vähintään tiivistelmillä.

| Erikoisala | Ristiviittauksia | Osuus |
|---|---|---|
| Isotooppilääketiede | 15/40 | 37,5 % |
| Radiologia | 24/74 | 32,4 % |
| KNF | 11/28 | 39,3 % |
| Sädehoito | 11/52 | 21,2 % |
| Kliininen fysiologia | 22/47 | 46,8 % |
| **Yhteensä** | **83/241** | **34,4 %** |

---

## Tarkistusprosessi

1. Alkuperäiset 241 mallivastausta dumpattu JSON-tiedostoihin erikoisaloittain
2. 5 rinnakkaista tarkistusagenttia (yksi per erikoisala) analysoi vastaukset
3. Tarkistuskriteerit: faktat, kaavat, arvot, yksiköt, kattavuus, kieli
4. Löydökset priorisoitu: kriittinen (prioriteetti 1), muu faktavirhe (2), kirjoitusvirhe (3)
5. Loki kirjoitettu `data/model_answer_review_log.md`
