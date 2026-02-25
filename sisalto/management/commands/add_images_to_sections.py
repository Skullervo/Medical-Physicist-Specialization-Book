"""Add illustrative images from Wikimedia Commons to EPA section content."""
import json
import re
import time
import uuid
from datetime import date
from pathlib import Path

import requests
from django.conf import settings
from django.core.management.base import BaseCommand

from sisalto.models import Specialty, Section

# ── EPA context keywords (English) for Wikimedia search ──────────────────
# Each EPA maps to a list of search query templates (tried in order)

EPA_SEARCH_QUERIES = {
    # Radiologia
    'Natiivikuvantaminen': [
        'X-ray tube diagram',
        'digital radiography detector',
        'X-ray imaging physics',
    ],
    'Magneettikuvaus': [
        'MRI scanner diagram',
        'magnetic resonance imaging physics',
        'MRI pulse sequence diagram',
    ],
    'Mammografia': [
        'mammography system diagram',
        'mammography X-ray tube',
        'breast imaging physics',
    ],
    'Ultraääni': [
        'ultrasound transducer diagram',
        'medical ultrasound physics',
        'Doppler ultrasound principle',
    ],
    'Säteilybiologia ja säteilysuojelu': [
        'radiation protection diagram',
        'radiation dose response curve',
        'radiation shielding medical',
    ],
    'Hammaskuvantaminen': [
        'dental X-ray CBCT diagram',
        'panoramic radiography principle',
        'cone beam computed tomography',
    ],
    'Läpivalaisu': [
        'fluoroscopy system diagram',
        'angiography catheter X-ray',
        'image intensifier diagram',
    ],
    'Kuvankatselunäytöt': [
        'DICOM medical display calibration',
        'medical monitor grayscale',
        'display quality assurance radiology',
    ],
    'Tietokonetomografia': [
        'CT scanner diagram',
        'computed tomography principle',
        'CT image reconstruction',
    ],
    # Sädehoito
    'Peruskäsitteet': [
        'radiation therapy diagram',
        'linear accelerator radiotherapy',
        'photon beam depth dose',
    ],
    'Kuvantaminen ja suunnittelu': [
        'radiation treatment planning',
        'IMRT beam diagram',
        'radiotherapy CT simulation',
    ],
    'Ulkoinen sädehoito': [
        'linear accelerator diagram',
        'external beam radiotherapy',
        'multileaf collimator diagram',
    ],
    'Sisäinen sädehoito': [
        'brachytherapy diagram',
        'brachytherapy applicator',
        'radioactive source implant',
    ],
    'Dosimetria': [
        'ionization chamber diagram',
        'radiation dosimetry physics',
        'dose measurement phantom',
    ],
    'Laitteet': [
        'linear accelerator components diagram',
        'radiotherapy equipment',
        'cobalt-60 therapy unit',
    ],
    # Isotooppilääketiede
    'Gammakamera': [
        'gamma camera diagram',
        'Anger camera scintillation',
        'collimator gamma camera',
    ],
    'PET-kamera': [
        'PET scanner diagram',
        'positron emission tomography principle',
        'PET detector ring',
    ],
    'Annostelu ja radiofarmasia': [
        'radiopharmacy preparation',
        'radiopharmaceutical production',
        'technetium-99m generator',
    ],
    'Gammakuvaus ja SPET': [
        'SPECT imaging diagram',
        'single photon emission computed tomography',
        'gamma camera rotation SPECT',
    ],
    'PET-tutkimukset': [
        'PET scan FDG uptake',
        'PET CT fusion image',
        'positron annihilation diagram',
    ],
    'Radionuklidihoidot': [
        'radionuclide therapy diagram',
        'iodine-131 thyroid treatment',
        'targeted radionuclide therapy',
    ],
    # KNF
    'EEG': [
        'electroencephalography electrode placement',
        'EEG 10-20 system diagram',
        'brain waves EEG',
    ],
    'Herätepotentiaali': [
        'evoked potential diagram',
        'electromyography EMG diagram',
        'nerve conduction study',
    ],
    'Sarja-TMS': [
        'transcranial magnetic stimulation diagram',
        'TMS coil brain',
        'magnetic stimulation principle',
    ],
    'Uni': [
        'polysomnography setup diagram',
        'sleep stages EEG',
        'sleep study monitoring',
    ],
    'IOM': [
        'intraoperative monitoring diagram',
        'neurophysiological monitoring surgery',
        'evoked potential intraoperative',
    ],
    # Kliininen fysiologia
    'EKG': [
        'electrocardiogram ECG diagram',
        'ECG lead placement',
        'cardiac conduction system',
    ],
    'Verenkiertotutkimukset': [
        'blood pressure measurement diagram',
        'hemodynamic monitoring',
        'cardiovascular physiology diagram',
    ],
    'Keuhkofunktiotutkimukset': [
        'spirometry diagram',
        'lung volume diagram',
        'pulmonary function test',
    ],
    'GI-kanavan tutkimukset': [
        'gastrointestinal motility diagram',
        'esophageal manometry',
        'pH monitoring diagram',
    ],
    'Luuston mineraalitiheys': [
        'DXA bone densitometry diagram',
        'DEXA scan principle',
        'bone mineral density measurement',
    ],
}

# ── Finnish -> English medical physics terms (for content analysis) ──────

FINNISH_TO_ENGLISH = {
    'röntgenputki': 'X-ray tube',
    'röntgenkuva': 'X-ray image radiograph',
    'annos': 'radiation dose',
    'potilasannos': 'patient dose dosimetry',
    'annosmittaus': 'dose measurement dosimeter',
    'annossuureet': 'dose quantities DLP DAP',
    'efektiivinen annos': 'effective dose sievert',
    'laadunvarmistus': 'quality assurance phantom',
    'kontrastiaine': 'contrast agent gadolinium',
    'varjoaine': 'contrast media iodine',
    'artefakti': 'imaging artifact',
    'magneetti': 'MRI magnet superconducting',
    'magneettikenttä': 'magnetic field tesla',
    'kelarakenne': 'RF coil MRI',
    'sekvenssi': 'MRI pulse sequence',
    'relaksaatio': 'MRI relaxation T1 T2',
    'ultraääni': 'ultrasound transducer',
    'anturi': 'ultrasound transducer probe',
    'doppler': 'Doppler ultrasound',
    'mammografia': 'mammography',
    'tomosyteesi': 'breast tomosynthesis',
    'kartiokeilatomografia': 'cone beam CT CBCT',
    'panoraama': 'panoramic radiograph',
    'intraoraalinen': 'intraoral radiograph',
    'läpivalaisu': 'fluoroscopy',
    'angiografia': 'angiography catheter',
    'tietokonetomografia': 'computed tomography CT',
    'leikekuvaus': 'CT scan slice',
    'rekonstruktio': 'image reconstruction filtered back projection',
    'kuvanlaatu': 'image quality SNR CNR',
    'säteilybiologia': 'radiobiology cell survival',
    'säteilysuojelu': 'radiation protection shielding',
    'säteilyturvallisuus': 'radiation safety',
    'detektori': 'X-ray detector flat panel',
    'ilmaisin': 'radiation detector scintillator',
    'taulukuvailmaisin': 'flat panel detector digital radiography',
    'kuvalevy': 'computed radiography imaging plate',
    'diagnostinen vertailutaso': 'diagnostic reference level DRL',
    'kliininen auditointi': 'clinical audit',
    'lineaarikiihdytin': 'linear accelerator linac',
    'brakyterapia': 'brachytherapy',
    'ionisaatiokammio': 'ionization chamber',
    'gammakamera': 'gamma camera',
    'tuikeaine': 'scintillator crystal',
    'kollimaattori': 'collimator',
    'radiolääke': 'radiopharmaceutical',
}

# ── English abbreviations commonly found in section content ──────────────

ENGLISH_TERMS_IN_CONTENT = [
    'CT', 'MRI', 'CBCT', 'SPECT', 'PET', 'DSA', 'DXA', 'DEXA',
    'DICOM', 'PACS', 'DLP', 'DAP', 'CTDIvol', 'CTDI',
    'SNR', 'CNR', 'MTF', 'DQE', 'NPS',
    'AEC', 'AGD', 'ESD', 'TLD', 'MOSFET',
    'EEG', 'EMG', 'ECG', 'ENMG', 'TMS',
    'Hounsfield', 'Compton', 'Rayleigh',
    'T1', 'T2', 'FLAIR', 'STIR', 'FSE', 'GRE',
    'kV', 'mAs', 'mGy', 'mSv', 'Gy',
    'FDG', 'Tc-99m', 'I-131', 'Lu-177',
    'IMRT', 'VMAT', 'SRS', 'SRT', 'IGRT',
    'bolus', 'phantom', 'collimator', 'gantry',
    'linac', 'brachytherapy', 'dosimeter',
]

# ── Section titles to skip ───────────────────────────────────────────────

SKIP_PATTERNS = [
    r'kirjallisuut',
    r'viittee',
    r'tiedonhaku',
    r'kirjallisuuden hyödynt',
    r'tutustua kirjallisuuteen',
    r'henkilökunnan ohja',
]


class Command(BaseCommand):
    help = 'Add illustrative images from Wikimedia Commons to EPA section content'

    def add_arguments(self, parser):
        parser.add_argument('--specialty', required=True, help='Specialty name (e.g. Radiologia)')
        parser.add_argument('--epa-id', type=int, help='Specific EPA ID')
        parser.add_argument('--dry-run', action='store_true', help='Show what would be done')
        parser.add_argument('--delay', type=float, default=1.0, help='Delay between API calls (seconds)')
        parser.add_argument('--min-score', type=int, default=2, help='Minimum image score to accept')

    def handle(self, *args, **options):
        specialty_name = options['specialty']
        epa_id = options.get('epa_id')
        self.dry_run = options['dry_run']
        self.delay = options['delay']
        self.min_score = options['min_score']
        self.session = requests.Session()
        self.session.headers['User-Agent'] = (
            'SairaalafyysikkoBot/1.0 (educational platform; contact: admin@example.com)'
        )
        self.used_images = set()  # Track used image titles to avoid duplicates

        # Find specialty
        try:
            specialty = Specialty.objects.get(name__icontains=specialty_name)
        except Specialty.DoesNotExist:
            self.stderr.write(self.style.ERROR(f'Specialty "{specialty_name}" not found'))
            return

        # Build section queryset
        sections_qs = Section.objects.filter(epa__specialty=specialty).select_related('epa')
        if epa_id:
            sections_qs = sections_qs.filter(epa_id=epa_id)
        sections_qs = sections_qs.order_by('epa__order', 'order')

        self.stdout.write(self.style.SUCCESS(
            f'Processing {sections_qs.count()} sections in {specialty.name}'
            f'{" (dry run)" if self.dry_run else ""}'
        ))

        log_entries = []
        images_added = 0
        skipped = 0

        for section in sections_qs:
            entry = self._process_section(section)
            log_entries.append(entry)
            if entry.get('inserted'):
                images_added += 1
            elif entry.get('skipped'):
                skipped += 1

        # Save log
        log_dir = Path(settings.BASE_DIR) / 'data'
        log_dir.mkdir(exist_ok=True)
        log_path = log_dir / f'image_additions_{specialty_name.lower()}_{date.today()}.json'
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(log_entries, f, ensure_ascii=False, indent=2)

        self.stdout.write(self.style.SUCCESS(
            f'\nDone! Images added: {images_added}, Skipped: {skipped}, '
            f'No match: {len(log_entries) - images_added - skipped}'
        ))
        self.stdout.write(f'Log saved: {log_path}')

    def _process_section(self, section):
        """Process a single section: search, score, download, insert."""
        entry = {
            'section_id': section.id,
            'section_title': section.title,
            'epa_id': section.epa_id,
            'epa_title': section.epa.title,
        }

        # Check skip conditions
        title_lower = section.title.lower()
        for pattern in SKIP_PATTERNS:
            if re.search(pattern, title_lower):
                entry['skipped'] = True
                entry['skip_reason'] = f'Title matches skip pattern: {pattern}'
                self.stdout.write(f'  SKIP [{section.id}] {section.title[:60]} (pattern)')
                return entry

        if '<img' in section.content:
            entry['skipped'] = True
            entry['skip_reason'] = 'Already has image'
            self.stdout.write(f'  SKIP [{section.id}] {section.title[:60]} (has image)')
            return entry

        if len(section.content) < 200:
            entry['skipped'] = True
            entry['skip_reason'] = f'Content too short ({len(section.content)} chars)'
            self.stdout.write(f'  SKIP [{section.id}] {section.title[:60]} (short)')
            return entry

        # Build multiple search queries
        queries = self._build_search_queries(section)
        entry['search_queries'] = queries

        if not queries:
            entry['skip_reason'] = 'Could not build search terms'
            self.stdout.write(f'  SKIP [{section.id}] {section.title[:60]} (no terms)')
            return entry

        self.stdout.write(f'  SEARCH [{section.id}] {section.title[:50]}')

        # Try each query until we find a good image
        best = None
        best_score = 0
        tried_queries = []

        for query in queries:
            time.sleep(self.delay)
            self.stdout.write(f'    query: "{query}"')
            results = self._search_wikimedia(query)
            tried_queries.append({'query': query, 'results': len(results) if results else 0})

            if not results:
                continue

            # Extract key words from query for relevance check
            # Exclude generic words that don't indicate actual topic relevance
            generic_words = {
                'diagram', 'medical', 'image', 'imaging', 'system',
                'principle', 'physics', 'scan', 'scanner', 'clinical',
                'digital', 'quality', 'measurement', 'device',
            }
            query_words = set(
                w.lower() for w in query.split()
                if len(w) > 2 and w.lower() not in generic_words
            )

            # Score results from this query
            for result in results[:8]:
                file_title = result.get('title', '')

                # Skip already-used images (prevent duplicates)
                if file_title in self.used_images:
                    continue

                # Quick relevance pre-filter: skip PDFs and books
                ft_lower = file_title.lower()
                if any(ft_lower.endswith(ext) for ext in ['.pdf', '.djvu', '.tiff', '.tif']):
                    continue

                time.sleep(0.3)
                img_info = self._get_image_info(file_title)
                if not img_info:
                    continue

                # Check relevance: image title/description must share
                # at least one meaningful word with the search query
                title_words = set(re.findall(r'[a-zA-Z]{3,}', ft_lower))
                desc_words = set(re.findall(r'[a-zA-Z]{3,}', img_info.get('description', '').lower()))
                all_img_words = title_words | desc_words
                relevance_overlap = query_words & all_img_words
                if not relevance_overlap:
                    continue

                score = self._score_image(img_info, file_title, query)
                # Bonus for high relevance overlap
                score += min(len(relevance_overlap), 3)

                if score > best_score:
                    best_score = score
                    best = {**img_info, 'file_title': file_title, 'score': score}

            # If we found a good image, stop searching
            if best and best_score >= self.min_score + 1:
                break

        entry['tried_queries'] = tried_queries

        if not best or best_score < self.min_score:
            entry['best_score'] = best_score if best else 0
            entry['no_match'] = True
            self.stdout.write(f'    -> No image above min score ({best_score} < {self.min_score})')
            return entry

        entry['wikimedia_title'] = best['file_title']
        entry['wikimedia_url'] = best.get('original_url', '')
        entry['thumb_url'] = best.get('thumb_url', '')
        entry['score'] = best['score']
        entry['license'] = best.get('license', '')

        # Mark image as used to prevent duplicates
        self.used_images.add(best['file_title'])

        if self.dry_run:
            entry['inserted'] = True
            entry['dry_run'] = True
            self.stdout.write(self.style.SUCCESS(
                f'    -> WOULD ADD: {best["file_title"][:70]} (score={best["score"]})'
            ))
            return entry

        # Download image
        download_url = best.get('thumb_url') or best.get('original_url')
        if not download_url:
            entry['error'] = 'No download URL'
            return entry

        local_path = self._download_image(download_url)
        if not local_path:
            entry['error'] = 'Download failed'
            return entry

        entry['local_path'] = local_path

        # Build caption from file title
        caption = self._build_caption(best['file_title'], best.get('license', ''))

        # Insert image into content
        media_url = f'/media/{local_path}'
        figure_html = (
            f'<figure class="image-with-caption fig-float-right" '
            f'style="float: right; width: 45%; margin: 0 0 16px 20px;">'
            f'<img src="{media_url}" style="width: 100%; border-radius: 8px;">'
            f'<figcaption style="font-size: 0.85em; color: var(--text-tertiary); '
            f'margin-top: 6px; text-align: center;">{caption}</figcaption>'
            f'</figure>'
        )

        new_content = self._insert_figure(section.content, figure_html)
        section.content = new_content
        section.save(update_fields=['content'])

        entry['inserted'] = True
        self.stdout.write(self.style.SUCCESS(
            f'    -> ADDED: {best["file_title"][:70]} (score={best["score"]})'
        ))
        return entry

    def _build_search_queries(self, section):
        """Build multiple English search queries for a section.

        Strategy (in priority order):
        1. Title-translated query: translate Finnish title terms + EPA context
        2. EPA-curated queries: pre-defined good search terms per EPA topic
        3. Content-specific query: extract English terms found in content
        """
        queries = []
        epa_title = section.epa.title

        # Get EPA search queries (curated)
        epa_queries = []
        for key, q_list in EPA_SEARCH_QUERIES.items():
            if key.lower() in epa_title.lower():
                epa_queries = q_list
                break

        # Get EPA context keyword (first word of first curated query)
        epa_keyword = epa_queries[0].split()[0] if epa_queries else ''

        # Strategy 1: Translate Finnish title terms + EPA context
        title = section.title
        title_clean = re.sub(r'^[AB]\d+\.\s*', '', title)
        title_clean = re.sub(
            r'\b(Osata|Hallita|Tuntea|Tiet..|Ymm.rt..|Tutustua|Osallistua|Kyet.|selitt..|'
            r'suorittaa|tunnistaa|arvioida|kehitt..|opastaa|ohjata|varmistaa|toimia)\b',
            '', title_clean, flags=re.IGNORECASE
        )
        title_clean = title_clean.strip(' ,.')

        translated_parts = []
        title_lower = title_clean.lower()
        for fi, en in FINNISH_TO_ENGLISH.items():
            if fi.lower() in title_lower:
                # Use the full English term (not just first word)
                translated_parts.append(en)

        if translated_parts:
            # Build a focused query from translated terms
            terms = ' '.join(translated_parts[:2])
            if epa_keyword and epa_keyword.lower() not in terms.lower():
                terms = f'{epa_keyword} {terms}'
            queries.append(terms + ' diagram')

        # Strategy 2: EPA-level curated queries
        if epa_queries:
            for eq in epa_queries:
                if eq not in queries:
                    queries.append(eq)

        # Strategy 3: Content-based English terms (as last resort)
        content_text = re.sub(r'<[^>]+>', ' ', section.content)
        # Only pick high-value terms (longer abbreviations and specific terms)
        high_value_terms = [
            t for t in ENGLISH_TERMS_IN_CONTENT
            if len(t) >= 3 and (
                re.search(rf'\b{re.escape(t)}\b', content_text)
                if len(t) <= 4
                else t.lower() in content_text.lower()
            )
        ]
        if high_value_terms and epa_keyword:
            # Combine EPA context with top content terms
            top = high_value_terms[:2]
            content_query = f'{epa_keyword} {" ".join(top)} medical'
            if content_query not in queries:
                queries.append(content_query)

        # Deduplicate while preserving order
        seen = set()
        unique_queries = []
        for q in queries:
            if q not in seen:
                seen.add(q)
                unique_queries.append(q)

        return unique_queries[:4]  # Max 4 queries per section

    def _search_wikimedia(self, search_terms):
        """Search Wikimedia Commons for images."""
        params = {
            'action': 'query',
            'list': 'search',
            'srsearch': search_terms,
            'srnamespace': 6,  # File namespace
            'srlimit': 10,
            'format': 'json',
        }
        try:
            resp = self.session.get(
                'https://commons.wikimedia.org/w/api.php',
                params=params, timeout=20
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get('query', {}).get('search', [])
        except Exception as e:
            self.stderr.write(f'    API search error: {e}')
            return []

    def _get_image_info(self, file_title):
        """Get image info (URL, size, license) from Wikimedia."""
        params = {
            'action': 'query',
            'titles': file_title,
            'prop': 'imageinfo',
            'iiprop': 'url|size|mime|extmetadata',
            'iiurlwidth': 800,
            'format': 'json',
        }
        try:
            resp = self.session.get(
                'https://commons.wikimedia.org/w/api.php',
                params=params, timeout=20
            )
            resp.raise_for_status()
            data = resp.json()
            pages = data.get('query', {}).get('pages', {})
            for page_id, page in pages.items():
                if page_id == '-1':
                    return None
                ii = page.get('imageinfo', [{}])[0]
                meta = ii.get('extmetadata', {})
                return {
                    'original_url': ii.get('url', ''),
                    'thumb_url': ii.get('thumburl', ''),
                    'width': ii.get('width', 0),
                    'height': ii.get('height', 0),
                    'mime': ii.get('mime', ''),
                    'license': meta.get('LicenseShortName', {}).get('value', ''),
                    'description': meta.get('ImageDescription', {}).get('value', ''),
                    'categories': meta.get('Categories', {}).get('value', ''),
                }
        except Exception as e:
            self.stderr.write(f'    API info error: {e}')
        return None

    def _score_image(self, info, file_title, search_query=''):
        """Score an image based on relevance criteria."""
        score = 0
        mime = info.get('mime', '')
        title_lower = file_title.lower()
        desc_lower = info.get('description', '').lower()
        cats = info.get('categories', '').lower()
        width = info.get('width', 0)
        height = info.get('height', 0)

        # ── Positive signals ──

        # SVG (usually diagrams/illustrations)
        if 'svg' in mime:
            score += 3

        # Diagram/schematic keywords in title
        if any(w in title_lower for w in [
            'diagram', 'schema', 'schematic', 'illustration',
            'cross-section', 'cross_section', 'principle',
        ]):
            score += 2

        # Educational/medical/physics keywords
        if any(w in title_lower for w in [
            'anatomy', 'physics', 'medical', 'clinical',
            'radiograph', 'imaging', 'scanner', 'detector',
            'dose', 'beam', 'spectrum', 'wavelength',
        ]):
            score += 1

        # Medical categories
        if any(w in cats for w in [
            'medical', 'radiolog', 'physics', 'imaging',
            'x-ray', 'radiation', 'tomograph', 'ultrasound',
        ]):
            score += 1

        # Good size range
        if 300 <= width <= 2000 and 200 <= height <= 2000:
            score += 1
        elif width < 150 or height < 150:
            score -= 3

        # License bonus
        license_val = info.get('license', '').lower()
        if any(w in license_val for w in ['cc0', 'public domain', 'pd']):
            score += 1

        # PNG (often better for diagrams than JPEG)
        if 'png' in mime:
            score += 1

        # ── Negative signals ──

        # Penalize plain photos without educational keywords
        if 'jpeg' in mime and not any(w in title_lower for w in [
            'diagram', 'schema', 'illustration', 'radiograph',
            'scan', 'imaging', 'x-ray', 'ct ', 'mri ',
        ]):
            score -= 1

        # Penalize logos, icons, flags, maps
        if any(w in title_lower for w in [
            'logo', 'icon', 'flag', 'coat of arms', 'emblem',
            'seal of', 'map of', 'portrait', 'photo of',
            'screenshot', 'software', 'user interface', 'gui',
            'award', 'medal', 'badge', 'button', 'banner',
        ]):
            score -= 5

        # Penalize very small images (icons/thumbnails)
        if width < 100 or height < 100:
            score -= 5

        # Penalize audio/video files that snuck through
        if any(w in mime for w in ['audio', 'video', 'ogg', 'webm']):
            score -= 10

        return score

    def _download_image(self, url):
        """Download image to media/editor/ directory with retry on 429."""
        download_headers = {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/120.0.0.0 Safari/537.36'
            ),
            'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        # Retry up to 3 times with exponential backoff for rate limiting
        for attempt in range(3):
            try:
                resp = requests.get(url, headers=download_headers, timeout=30)
                if resp.status_code == 429:
                    wait = (attempt + 1) * 5  # 5s, 10s, 15s
                    self.stdout.write(f'    Rate limited, waiting {wait}s...')
                    time.sleep(wait)
                    continue
                resp.raise_for_status()

                # Determine extension from content type
                ct = resp.headers.get('content-type', '')
                if 'svg' in ct:
                    ext = 'svg'
                elif 'png' in ct:
                    ext = 'png'
                elif 'gif' in ct:
                    ext = 'gif'
                elif 'webp' in ct:
                    ext = 'webp'
                else:
                    ext = 'jpg'

                filename = f'editor/{uuid.uuid4().hex}.{ext}'
                filepath = Path(settings.MEDIA_ROOT) / filename
                filepath.parent.mkdir(parents=True, exist_ok=True)
                filepath.write_bytes(resp.content)
                return filename
            except Exception as e:
                self.stderr.write(f'    Download error: {e}')
                if attempt < 2:
                    time.sleep(3)
                    continue
                return None
        return None

    def _build_caption(self, file_title, license_str):
        """Build a clean caption from Wikimedia file title."""
        # Remove "File:" prefix and extension
        caption = re.sub(r'^File:', '', file_title)
        caption = re.sub(r'\.\w{2,4}$', '', caption)
        # Replace underscores with spaces
        caption = caption.replace('_', ' ').strip()
        # Truncate if too long
        if len(caption) > 80:
            caption = caption[:77] + '...'

        license_note = f' ({license_str})' if license_str else ' (CC)'
        return f'{caption}. Wikimedia Commons{license_note}'

    def _insert_figure(self, content, figure_html):
        """Insert figure HTML after the first paragraph or heading."""
        # Try to insert after first closing </p> or </h3>
        for tag in ['</p>', '</h3>', '</h4>', '</ul>', '</ol>']:
            idx = content.find(tag)
            if idx != -1:
                insert_pos = idx + len(tag)
                return content[:insert_pos] + '\n' + figure_html + '\n' + content[insert_pos:]

        # Fallback: prepend
        return figure_html + '\n' + content
