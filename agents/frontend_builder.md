# Agentti: Frontend Builder

## Rooli
Rakenna käyttöliittymä sairaalafyysikon oppimisalustalle. UI on suomenkielinen ja ammattimainen.

## Tech Stack
- Django templates (Jinja2-tyylinen)
- HTMX (dynaaminen päivitys ilman full page reload)
- Alpine.js (kevyt reaktiivisuus)
- Tailwind CSS (tai Bootstrap 5 jos jo käytössä)
- Chart.js (edistymiskaaviot)

## Sivurakenne

### 1. Dashboard (`/dashboard/`)
```
┌─────────────────────────────────────────┐
│  Tervetuloa, [nimi]!          [streak]   │
│                                         │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐   │
│  │ 234  │ │ 67%  │ │ 12🔥 │ │ 1450 │   │
│  │kysym.│ │oikein│ │putki │ │  XP  │   │
│  └──────┘ └──────┘ └──────┘ └──────┘   │
│                                         │
│  Tänään kertaavat (SR)      [Aloita →]  │
│  ├ 15 kysymystä odottaa                 │
│  └ Painotus: Sädehoito, TT             │
│                                         │
│  Edistyminen erikoisaloittain           │
│  ┌────────────────────────────────────┐ │
│  │  [Radar chart / progress bars]     │ │
│  │  KNF: ████████░░ 80%              │ │
│  │  SH:  ██████░░░░ 60%              │ │
│  │  RAD: ████░░░░░░ 40%              │ │
│  │  ISO: ███░░░░░░░ 30%              │ │
│  │  KLF: █████░░░░░ 50%              │ │
│  └────────────────────────────────────┘ │
│                                         │
│  Viimeaikaiset saavutukset              │
│  🏆 Sädehoitoguru  📊 100 kysymystä    │
└─────────────────────────────────────────┘
```

### 2. EPA-kortit (`/epa/`)
```
┌─────────────────────────────────────────┐
│  EPA-koulutuskortit                     │
│                                         │
│  [Kliininen neurofysiologia]            │
│    ├ EEG-tutkimukset          ██░░ 45%  │
│    ├ Herätepotentiaali/ENMG   ███░ 65%  │
│    ├ TMS                      █░░░ 20%  │
│    ├ Uni-tutkimukset          ██░░ 50%  │
│    └ IOM                      █░░░ 15%  │
│                                         │
│  [Sädehoito]                            │
│    ├ Peruskäsitteet           ████ 90%  │
│    ├ Kuvantaminen             ███░ 70%  │
│    ...                                  │
└─────────────────────────────────────────┘
```

### 3. EPA-kortin yksityissivu (`/epa/<slug>/`)
```
┌─────────────────────────────────────────┐
│  Tietokonetomografia                    │
│  Radiologia | A: 75% | B: 45%          │
│                                         │
│  [Teoria] [Kysymykset] [Harjoittele]    │
│                                         │
│  Osaamistavoitteet:                     │
│  A-taso (perusosaaminen)                │
│  ☑ A1. Kirjallisuus ja säteily...  ✓   │
│  ☑ A2. Kirjallisuuden hyödyntäm... ✓   │
│  ☐ A3. Laitteiston rakenne...      ~   │
│  ...                                    │
│                                         │
│  B-taso (täydentävä)                    │
│  ☐ B1. Kliiniset tutkimukset...    ✗   │
│  ...                                    │
│                                         │
│  CanMEDS: 🔬Fysiikka 🤝Yhteistyö 💬UX │
│  Viitteet: [Khan 6th Ed.] [STUK]       │
└─────────────────────────────────────────┘
```

### 4. Harjoittelunäkymä (`/quiz/practice/`)
```
┌─────────────────────────────────────────┐
│  Kysymys 7/15    ⏱ 02:34    ██████░░░  │
│  Tietokonetomografia | A-taso | ⭐⭐    │
│                                         │
│  Mikä seuraavista on tyypillinen        │
│  TT-kuvausartefakti?                    │
│                                         │
│  ○ A) Susceptibiliteettiartefakti       │
│  ● B) Beam hardening -artefakti         │
│  ○ C) Chemical shift -artefakti         │
│  ○ D) Aliasing-artefakti                │
│                                         │
│  [💡 Vihje]              [Vastaa →]     │
│                                         │
│  ─── Vastauksen jälkeen: ───            │
│  ✅ Oikein! +10 XP                     │
│  Beam hardening johtuu matalampi-       │
│  energisten fotonien voimakkaammasta    │
│  vaimenemisesta...                      │
│  📖 Liittyy: A9 (kuvausartefaktit)     │
│                                         │
│  Kuinka varma olit? [1][2][3][4][5]     │
└─────────────────────────────────────────┘
```

### 5. Tenttiharjoittelu (`/exams/`)
```
┌─────────────────────────────────────────┐
│  Tenttikysymys 3/8          ⏱ 1:23:45  │
│  Sairaalafyysikkokuulustelu 2023 kevät  │
│                                         │
│  Selitä sädehoidon LQ-mallin perusteet  │
│  ja sen soveltaminen fraktiokoon        │
│  muutoksiin. Miten EQD2-käsite liittyy  │
│  tähän? (10p)                           │
│                                         │
│  ┌─────────────────────────────────────┐│
│  │                                     ││
│  │  [Tekstieditori - vastaus]          ││
│  │                                     ││
│  │                                     ││
│  └─────────────────────────────────────┘│
│                                         │
│  [← Edellinen] [Tallenna] [Seuraava →] │
│                                         │
│  [Lähetä tentti arviointiin]            │
└─────────────────────────────────────────┘
```

### 6. Tenttitulokset (`/exams/<id>/results/`)
```
┌─────────────────────────────────────────┐
│  Tenttitulokset                         │
│  Tulos: 67/100 (67%) ✅ Hyväksytty     │
│                                         │
│  Kysymys 3: LQ-malli (7/10)            │
│  ┌─────────────────────────────────────┐│
│  │ ✅ Vahvuudet:                       ││
│  │ - LQ-mallin perusyhtälö oikein      ││
│  │ - α/β-suhteen merkitys ymmärretty   ││
│  │                                     ││
│  │ ⚠️ Puutteet:                        ││
│  │ - EQD2-kaavan johtaminen puutteell. ││
│  │ - Hoitoajan vaikutusta ei mainittu  ││
│  │                                     ││
│  │ 💡 Parannettavaa:                   ││
│  │ - Kertaa Khan Ch. 8: Fractionation  ││
│  │ - EPA: Säteilybiologia A2           ││
│  └─────────────────────────────────────┘│
└─────────────────────────────────────────┘
```

## HTMX-integraatio

```html
<!-- Esimerkki: Kysymykseen vastaaminen ilman sivunlatausta -->
<form hx-post="/quiz/answer/{{ question.id }}/"
      hx-target="#question-result"
      hx-swap="innerHTML">
    {% csrf_token %}
    {% for choice in question.choices.all %}
    <label class="block p-3 border rounded hover:bg-blue-50 cursor-pointer">
        <input type="radio" name="choice" value="{{ choice.id }}">
        {{ choice.text }}
    </label>
    {% endfor %}
    <button type="submit">Vastaa</button>
</form>

<div id="question-result">
    <!-- HTMX päivittää tämän -->
</div>

<!-- Seuraava kysymys ladataan automaattisesti -->
<div hx-get="/quiz/next/?epa={{ epa_card.slug }}"
     hx-trigger="answered from:body delay:2s"
     hx-target="#question-container"
     hx-swap="outerHTML">
</div>
```

## Responsiivisuus
- Mobile-first: harjoittelu toimii puhelimella
- Tablet: tenttinäkymä optimoitu
- Desktop: dashboard ja analytiikka

## Saavutettavuus
- WCAG 2.1 AA
- Näppäimistönavigaatio kysymyksissä
- Screen reader -tuki
- Riittävä kontrasti

## Väripaletti (ehdotus)
- Primary: #1e40af (tumma sininen - ammattimainen)
- Success: #059669 (vihreä - oikein)
- Error: #dc2626 (punainen - väärin)
- Warning: #d97706 (oranssi - osittain oikein)
- Background: #f8fafc (vaalea harmaa)
