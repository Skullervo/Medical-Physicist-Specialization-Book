# MCQ Review Log - Tehtävä 4

**Päivämäärä**: 2026-02-18
**Tarkistettu**: 698 monivalintakysymystä (kaikki erikoisalat)
**Aktiivisia korjausten jälkeen**: 662 (36 duplikaattia deaktivoitu)

---

## Yhteenveto

| Erikoisala | Tarkistettu | Kriittiset | Kohtalaiset | Pienet | EPA-virheet | Duplikaatit |
|---|---|---|---|---|---|---|
| Radiologia | 213 | 5 | 9 | 6 | 11 | 11 |
| Sädehoito | 131 | 3 | 11 | 7 | 3 | 8 |
| Isotooppilääketiede | 133 | 2 | 9 | 8 | 6 | 6 |
| KNF | 110 | 3 | 11 | 6 | 4 | 9 |
| Kliininen fysiologia | 111 | 3 | 12 | 8 | 10 | 2 |
| **Yhteensä** | **698** | **16** | **52** | **35** | **34** | **36** |

---

## Tehdyt korjaukset

### 1. Kriittiset faktavirheet (12 korjausta)

| Q ID | Ongelma | Korjaus |
|---|---|---|
| 815 | Väärä oikea vastaus (E_mean = E_max/2 vs E_max/3) | E_max/3 merkitty oikeaksi, selitys korjattu |
| 814 | TERMA-kaava virheellinen (Kcoll + Krad) | Selitys korjattu: TERMA = (mu/rho) × Psi |
| 666 | BED-kaavan notaatio epäjohdonmukainen (D vs d) | Korjattu pienikirjaimiseen d (kerta-annos) |
| 4 | CTDIw-selitys väärin (annos reunoilla vs tilavuusosuus) | Korjattu: painotus kuvaa tilavuusosuutta |
| 673 | Virheellinen isotooppinotaatio 199mTc | Korjattu: 99mTc |
| 552 | MDP:n kemiallinen nimi väärin | Korjattu: metyleenidifosfonaatti |
| 724 | Porttilaskimovereen kuvaus käänteinen | Korjattu: ravintorikasta laskimoverta |
| 959 | Nyquist/alfa-selitys virheellinen | Korjattu: 50 Hz riittäisi alfalle mutta ei kliiniseen EEG:hen |
| 956 | Rikkinäinen teksti "Gliasoluj" | Korjattu: Gliasolujen aktivaatio |
| 1172 | Pleksopatia-selitys harhaanjohtava | Korjattu: amplitudimuutokset, ei johtumisnopeusmuutokset |
| 815 | Termi "sähköhoidossa" väärä | Korjattu: elektronikeilahoidossa (mikäli tekstissä) |

### 2. EPA-mapping korjaukset (28 korjausta)

| Q ID:t | Vanha EPA | Uusi EPA | Syy |
|---|---|---|---|
| 35, 36, 530, 531, 532 | 1 (Natiivi) | 2 (MRI) | MRI-kysymykset |
| 527, 528, 529 | 1 (Natiivi) | 21 (TT) | TT-kysymykset |
| 536, 537 | 1 (Natiivi) | 18 (Säteilybiologia) | Dosimetria-kysymykset |
| 535 | 1 (Natiivi) | 20 (Läpivalaisu) | DSA-kysymys |
| 556, 557 | 5 (EEG) | 6 (ENMG) | NCV/SEP-kysymykset |
| 558 | 5 (EEG) | 10 (TMS) | TMS-kysymys |
| 559 | 5 (EEG) | 9 (Uni) | Polysomnografia |
| 548, 549 | 28 (Gamma) | 29 (PET) | PET-fysiikka |
| 550, 551, 552, 553 | 28 (Gamma) | 31 (SPET) | Kliiniset SPET-sovellukset |
| 561, 565, 566 | 11 (EKG) | 13 (Keuhko) | Keuhkofysiologia |
| 567 | 11 (EKG) | 15 (Verenkierto) | Sepelvaltimot |
| 563 | 11 (EKG) | 27 (Sätbiologia) | Säteilybiologia |
| 725 | 11 (EKG) | 5 (EEG/KNF) | Pupillin säätely |
| 726 | 11 (EKG) | 30 (Radiofarmasia) | Farmakokinetiikka |

### 3. Vaikeustason korjaukset (30 korjausta)

Pääasiassa alkuperäisen erän (Q527–Q567) kysymyksiä, joiden vaikeustaso oli virheellisesti 4 perustason sisällölle.

| Alkuperäinen | Korjattu | Lukumäärä |
|---|---|---|
| 4 → 1 | 1 kysymys | (Q538: "Mikä on lineaarikiihdyttimen rooli?") |
| 4 → 2 | 23 kysymystä | Perustason kysymykset |
| 4 → 3 | 6 kysymystä | Keskitason kysymykset |

### 4. Kirjoitusvirhekorjaukset (27 korjausta)

Tyypillisiä: tuplakonsonantit (aanennnopeuden, potilaaan), puuttuvat kirjaimet (takaisinprojekton, klinisen), garbled-teksti (differentiaalimunimuutto, absorbanttientien).

### 5. Duplikaattien deaktivointi (36 kysymystä)

Deaktivoidut kysymykset (is_active=False) ovat edelleen tietokannassa mutta eivät näy quiz-harjoittelussa.

| Erikoisala | Deaktivoidut | Esimerkkejä |
|---|---|---|
| Radiologia | 11 | UÄ freq (1100), elastografia (1096), DSA (782), pitch (789) |
| Sädehoito | 8 | PDD (539), GTV/CTV/PTV (540), IMRT (829), VMAT (830) |
| Isotooppi | 6 | PET-periaate (548), gammakamera (546), TOF (899) |
| KNF | 9 | EEG-lähde (554), 10-20 (555), TMS (1012), REM (1159) |
| Fysiologia | 2 | Spirometria (1048), DXA-periaate (1062) |

---

## Ei korjatut kohtalaiset huomiot (tulevaa kehitystä varten)

- **Q800**: AAPM TG-18 luminanssiarvot — harkittava päivitystä TG-270 mukaisiksi
- **Q753**: Mammografian anodimateriaalit — volframianodi puuttuu (moderni käytäntö)
- **Q754**: Mammografiaseulonnan ikärajat — tarkista 50-69 vs 50-74 päivitys
- **Sädehoito**: Puuttuu säteilysuojelukysymyksiä (huonesuojaus, STUK-vaatimukset)
- **Q19 vs Q835**: MU-kalibroinnin referenssisyvyys ristiriitainen (dmax vs 10 cm)
- **SPET/SPECT**: Terminologia vaihtelee — harkittava yhdenmukaistamista
- **Isotooppi Q949 vs Q1138**: Kotiuttamisrajan arvo vaihtelee (25-40 vs 40 μSv/h)
