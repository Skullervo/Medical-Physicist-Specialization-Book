# EPA-korttien latausohje

## Management Command: `load_epa_cards`

Luo tämä management command EPA-korttien lataamiseen tietokantaan.
Claude Code voi generoida tämän automaattisesti käyttäen `data_modeler.md` -agenttia.

```bash
python manage.py load_epa_cards
```

## EPA-korttien yhteenveto (34 kpl)

### Yhteiset (1)
1. Laite- ja sähköturvallisuus (A:7, B:6)

### Kliininen neurofysiologia (5)
2. EEG-tutkimukset (A:12, B:8)
3. Herätepotentiaali ja ENMG (A:11, B:9)
4. Sarja-TMS ja navigoidut TMS (A:10, B:7)
5. Uni-tutkimukset (A:11, B:8)
6. Intraoperatiivinen monitorointi IOM/DBS (A:10, B:10)

### Sädehoito (7)
7. Sädehoidon peruskäsitteet (A:8)
8. Kuvantaminen sädehoidon suunnittelua varten (A:7, B:8)
9. Ulkoinen sädehoito (A:15, B:4)
10. Sisäinen sädehoito (A:5, B:7)
11. Sädehoidon dosimetria (A:5, B:9)
12. Säteilyä tuottavat laitteet sädehoidossa (A:6, B:4)
13. Säteilybiologia ja säteilysuojelu sädehoidossa (A:10, B:6)

### Radiologia (8)
14. Läpivalaisu- ja angiografia (A:14, B:5)
15. Magneettikuvaus (A:12, B:7)
16. Mammografia (A:9, B:4)
17. Natiivikuvantaminen (A:10, B:5)
18. Tietokonetomografia (A:15, B:7)
19. Ultraäänikuvantaminen (A:9, B:4)
20. Kuvankatselunäytöt (A:5, B:2)
21. Hammaskuvantaminen (A:9, B:3)
22. Säteilybiologia ja säteilysuojelu radiologiassa (A:7, B:8)

### Isotooppilääketiede (7)
23. Gammakamerateknologia (A:9, B:7)
24. PET-kamerateknologia (A:8, B:7)
25. Annostelu- ja radiofarmasiatoiminta (A:8, B:2)
26. Gammakuvaus/SPET-tutkimukset (A:2, B:2)
27. PET-tutkimukset (A:2, B:2)
28. Radionuklidihoidot (A:6, B:4)
29. Säteilybiologia ja säteilysuojelu isotooppitoiminnassa (A:7, B:10)

### Kliininen fysiologia (5)
30. EKG-tutkimukset (A:9, B:6)
31. Verenkiertotutkimukset (A:10, B:4)
32. Keuhkofunktiotutkimukset (A:10, B:6)
33. GI-kanavan tutkimukset (A:9, B:4)
34. Luuston mineraalitiheyden mittaus DXA (A:8, B:6)

## Yhteensä
- A-tason osaamistavoitteita: ~290 kpl
- B-tason osaamistavoitteita: ~190 kpl
- Yhteensä: ~480 osaamistavoitetta

## Ohje Claude Codelle

Käytä PDF-dokumenttia (`Erikoistuvan_sairaalafyysikon_koulutuskortit_Neuvottelukunta_2021.pdf`)
suorana lähteenä ja luo management command joka:

1. Luo Specialty-objektit (6 kpl)
2. Luo CanMEDSCompetency-objektit (6 kpl)
3. Luo EPACard-objektit (34 kpl) kaikkine kenttineen
4. Luo LearningObjective-objektit (~480 kpl)
5. Linkittää CanMEDS-osaamisalueet EPA-kortteihin

Kaikki data on suoraan PDF:ssä - ei tarvitse keksiä mitään.
