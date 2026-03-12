/**
 * Theory EPA Links — connects EPA card items to theory sections
 *
 * Each .theory-panel can have a data-epa-map JSON attribute:
 *   { "A1": [2], "A3": [3,4], "B1": [7], ... }
 * Keys = EPA item codes, values = arrays of h2 section numbers (1-based).
 *
 * This script:
 *  1. Auto-assigns IDs to h2/h3 headings in each panel
 *  2. Makes EPA list items clickable (smooth-scroll to first mapped heading)
 *  3. Renders EPA reference badges below mapped h2 headings
 */
(function () {
    'use strict';

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    function init() {
        var panels = document.querySelectorAll('.theory-panel');
        panels.forEach(processPanel);

        // Re-process panels when inline-editor replaces their content
        document.addEventListener('theory-content-loaded', function (e) {
            var panel = e.target.closest('.theory-panel');
            if (panel) processPanel(panel);
        });
    }

    /* ── 1. Assign heading IDs ─────────────────────────────────── */

    function assignHeadingIds(panel, panelId) {
        var h2Index = 0;
        var h3Index = 0;
        var headings = panel.querySelectorAll('.theory-content > h2, .theory-content > h3');

        headings.forEach(function (h) {
            if (h.tagName === 'H2') {
                h2Index++;
                h3Index = 0;
                h.id = panelId + '-s' + h2Index;
            } else {
                h3Index++;
                h.id = panelId + '-s' + h2Index + '-' + h3Index;
            }
        });

        return h2Index;
    }

    /* ── 2. Build inverse map  heading → [EPA items] ───────────── */

    function invertMap(epaMap) {
        var headingToEpa = {};
        for (var key in epaMap) {
            if (!epaMap.hasOwnProperty(key)) continue;
            epaMap[key].forEach(function (sNum) {
                if (!headingToEpa[sNum]) headingToEpa[sNum] = [];
                headingToEpa[sNum].push(key);
            });
        }
        return headingToEpa;
    }

    /* ── 3. Render EPA badges below h2 headings ────────────────── */

    function renderBadges(panel, panelId, headingToEpa) {
        panel.querySelectorAll('.epa-ref-badge').forEach(function (b) { b.remove(); });

        for (var sNum in headingToEpa) {
            if (!headingToEpa.hasOwnProperty(sNum)) continue;
            var h2 = document.getElementById(panelId + '-s' + sNum);
            if (!h2) continue;

            var tags = headingToEpa[sNum].slice().sort(function (a, b) {
                if (a[0] !== b[0]) return a[0] === 'A' ? -1 : 1;
                return parseInt(a.slice(1)) - parseInt(b.slice(1));
            });

            var badge = document.createElement('div');
            badge.className = 'epa-ref-badge';
            badge.innerHTML = '<span class="epa-ref-label"><i class="fas fa-id-card"></i> EPA</span> ' +
                tags.map(function (t) {
                    var cls = t[0] === 'A' ? 'epa-ref-tag epa-ref-a' : 'epa-ref-tag epa-ref-b';
                    return '<span class="' + cls + '">' + t + '</span>';
                }).join(' ');

            h2.insertAdjacentElement('afterend', badge);
        }
    }

    /* ── 4. Make EPA list items clickable ───────────────────────── */

    function linkEpaItems(panel, panelId, epaMap) {
        var epaCard = panel.querySelector('.theory-epa-card');
        if (!epaCard) return;

        // Remove old click handlers by replacing nodes
        ['a', 'b'].forEach(function (level) {
            var section = epaCard.querySelector('.theory-epa-' + level);
            if (!section) return;

            var items = section.querySelectorAll('.theory-epa-list > li');
            if (items.length === 0) items = section.querySelectorAll('ol > li');
            if (items.length === 0) {
                var allLis = section.querySelectorAll('li');
                items = Array.prototype.filter.call(allLis, function (li) {
                    return li.parentElement && li.parentElement.parentElement === section;
                });
            }

            items.forEach(function (li, i) {
                var key = level.toUpperCase() + (i + 1);
                if (!epaMap[key] || epaMap[key].length === 0) return;

                li.classList.add('epa-clickable');
                li.style.cursor = 'pointer';
                li.title = 'Siirry teoriaosioon ' + key;

                li.addEventListener('click', function () {
                    var targetId = panelId + '-s' + epaMap[key][0];
                    var target = document.getElementById(targetId);
                    if (!target) return;

                    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    target.classList.add('epa-heading-highlight');
                    setTimeout(function () {
                        target.classList.remove('epa-heading-highlight');
                    }, 2000);
                });
            });
        });
    }

    /* ── Main per-panel processor ──────────────────────────────── */

    function processPanel(panel) {
        var panelId = panel.id.replace('panel-', '');

        var h2Count = assignHeadingIds(panel, panelId);

        var mapAttr = panel.getAttribute('data-epa-map');
        if (!mapAttr) return;

        var epaMap;
        try {
            epaMap = JSON.parse(mapAttr);
        } catch (e) {
            return;
        }

        var headingToEpa = invertMap(epaMap);
        renderBadges(panel, panelId, headingToEpa);
        linkEpaItems(panel, panelId, epaMap);
    }

})();
