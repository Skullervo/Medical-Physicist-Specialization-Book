/**
 * Theory Inline Editor — Native contenteditable + floating toolbar.
 * Superuser-only: click "Muokkaa sisältöä" to toggle editing mode.
 * Uses native contenteditable to preserve all existing HTML perfectly.
 */
(function () {
    'use strict';

    const SAVE_URL = '/modaliteetit/api/theory-content/save/';
    let editingActive = false;
    let toolbar = null;

    // ── helpers ──────────────────────────────────────────────────────────
    function getModality() {
        const el = document.querySelector('[data-modality-id]');
        return el ? el.dataset.modalityId : '';
    }

    function csrfToken() {
        if (typeof getCookie === 'function') return getCookie('csrftoken');
        const el = document.querySelector('[name=csrfmiddlewaretoken]');
        return el ? el.value : '';
    }

    function showToast(msg, ok) {
        let toast = document.getElementById('theory-edit-toast');
        if (!toast) {
            toast = document.createElement('div');
            toast.id = 'theory-edit-toast';
            document.body.appendChild(toast);
        }
        toast.textContent = msg;
        toast.className = 'theory-edit-toast ' + (ok ? 'success' : 'error') + ' show';
        setTimeout(() => toast.classList.remove('show'), 3000);
    }

    // ── floating toolbar ────────────────────────────────────────────────
    function createToolbar() {
        if (toolbar) return toolbar;

        toolbar = document.createElement('div');
        toolbar.className = 'theory-floating-toolbar';
        toolbar.innerHTML = [
            '<button data-cmd="bold" title="Lihavointi (Ctrl+B)"><i class="fas fa-bold"></i></button>',
            '<button data-cmd="italic" title="Kursiivi (Ctrl+I)"><i class="fas fa-italic"></i></button>',
            '<button data-cmd="underline" title="Alleviivaus (Ctrl+U)"><i class="fas fa-underline"></i></button>',
            '<button data-cmd="strikethrough" title="Yliviivaus"><i class="fas fa-strikethrough"></i></button>',
            '<span class="toolbar-sep"></span>',
            '<button data-cmd="insertUnorderedList" title="Lista"><i class="fas fa-list-ul"></i></button>',
            '<button data-cmd="insertOrderedList" title="Numeroitu lista"><i class="fas fa-list-ol"></i></button>',
            '<span class="toolbar-sep"></span>',
            '<button data-cmd="formatBlock" data-value="H2" title="H2-otsikko"><b>H2</b></button>',
            '<button data-cmd="formatBlock" data-value="H3" title="H3-otsikko"><b>H3</b></button>',
            '<button data-cmd="formatBlock" data-value="H4" title="H4-otsikko"><b>H4</b></button>',
            '<button data-cmd="formatBlock" data-value="P" title="Normaali teksti"><b>P</b></button>',
            '<span class="toolbar-sep"></span>',
            '<button data-cmd="subscript" title="Alaindeksi"><i class="fas fa-subscript"></i></button>',
            '<button data-cmd="superscript" title="Yläindeksi"><i class="fas fa-superscript"></i></button>',
            '<span class="toolbar-sep"></span>',
            '<button data-cmd="createLink" title="Linkki"><i class="fas fa-link"></i></button>',
            '<button data-cmd="removeFormat" title="Poista muotoilu"><i class="fas fa-eraser"></i></button>',
            '<span class="toolbar-sep"></span>',
            '<button data-cmd="undo" title="Kumoa (Ctrl+Z)"><i class="fas fa-undo"></i></button>',
            '<button data-cmd="redo" title="Tee uudelleen (Ctrl+Y)"><i class="fas fa-redo"></i></button>',
        ].join('');

        toolbar.addEventListener('mousedown', function (e) {
            // Prevent toolbar clicks from stealing focus from editable area
            e.preventDefault();
        });

        toolbar.addEventListener('click', function (e) {
            const btn = e.target.closest('button');
            if (!btn) return;

            const cmd = btn.dataset.cmd;
            const value = btn.dataset.value || null;

            if (cmd === 'createLink') {
                const url = prompt('URL:');
                if (url) document.execCommand('createLink', false, url);
            } else if (cmd === 'formatBlock') {
                document.execCommand('formatBlock', false, '<' + value + '>');
            } else {
                document.execCommand(cmd, false, value);
            }
        });

        document.body.appendChild(toolbar);
        return toolbar;
    }

    function positionToolbar() {
        if (!toolbar) return;
        const sel = window.getSelection();
        if (!sel || sel.rangeCount === 0 || sel.isCollapsed) {
            toolbar.classList.remove('visible');
            return;
        }

        // Check if selection is inside an editable theory-content
        const anchor = sel.anchorNode;
        const editableEl = anchor && anchor.nodeType === 3
            ? anchor.parentElement.closest('.theory-content[contenteditable="true"]')
            : (anchor && anchor.closest ? anchor.closest('.theory-content[contenteditable="true"]') : null);

        if (!editableEl) {
            toolbar.classList.remove('visible');
            return;
        }

        const range = sel.getRangeAt(0);
        const rect = range.getBoundingClientRect();

        toolbar.classList.add('visible');
        const tbRect = toolbar.getBoundingClientRect();
        let left = rect.left + (rect.width / 2) - (tbRect.width / 2);
        let top = rect.top - tbRect.height - 8 + window.scrollY;

        // Keep within viewport
        if (left < 8) left = 8;
        if (left + tbRect.width > window.innerWidth - 8) left = window.innerWidth - tbRect.width - 8;
        if (top < window.scrollY + 8) top = rect.bottom + 8 + window.scrollY;

        toolbar.style.left = left + 'px';
        toolbar.style.top = top + 'px';
    }

    function hideToolbar() {
        if (toolbar) toolbar.classList.remove('visible');
    }

    // ── save single panel ───────────────────────────────────────────────
    function savePanel(tabId) {
        const panel = document.getElementById('panel-' + tabId);
        if (!panel) return;

        const theoryContent = panel.querySelector('.theory-content');
        if (!theoryContent) return;

        // Clone to remove quiz section and image slots from saved content
        const clone = theoryContent.cloneNode(true);
        const quizSec = clone.querySelector('.theory-quiz-section');
        if (quizSec) quizSec.remove();
        // Remove image slot placeholders from saved content
        clone.querySelectorAll('.theory-image-slot').forEach(s => s.remove());

        const content = clone.innerHTML.trim();
        const modality = getModality();

        fetch(SAVE_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken(),
            },
            body: JSON.stringify({ modality, tab_id: tabId, content }),
        })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                showToast('Tallennettu!', true);
            } else {
                showToast('Virhe: ' + (data.error || ''), false);
            }
        })
        .catch(err => showToast('Verkkovirhe: ' + err.message, false));
    }

    // ── activate editing on one panel ───────────────────────────────────
    function activatePanel(panel) {
        const theoryContent = panel.querySelector('.theory-content');
        if (!theoryContent || theoryContent.dataset.editorActive === 'true') return;

        const tabId = panel.id.replace('panel-', '');

        // Make content directly editable
        theoryContent.setAttribute('contenteditable', 'true');
        theoryContent.dataset.editorActive = 'true';

        // Prevent image slots from being editable
        theoryContent.querySelectorAll('.theory-image-slot').forEach(slot => {
            slot.setAttribute('contenteditable', 'false');
        });
        // Prevent quiz section from being editable
        const quizSection = theoryContent.querySelector('.theory-quiz-section');
        if (quizSection) {
            quizSection.setAttribute('contenteditable', 'false');
        }

        // Add save button
        let saveBar = panel.querySelector('.theory-save-bar');
        if (!saveBar) {
            saveBar = document.createElement('div');
            saveBar.className = 'theory-save-bar';
            saveBar.innerHTML =
                '<button class="theory-save-btn" title="Tallenna muutokset">' +
                '<i class="fas fa-save"></i> Tallenna</button>';
            saveBar.querySelector('.theory-save-btn').addEventListener('click', () => savePanel(tabId));
            panel.insertBefore(saveBar, theoryContent);
        }

        console.log('Inline editing activated for tab:', tabId);
    }

    // ── deactivate editing on one panel ─────────────────────────────────
    function deactivatePanel(panel) {
        const theoryContent = panel.querySelector('.theory-content');
        if (!theoryContent || theoryContent.dataset.editorActive !== 'true') return;

        theoryContent.removeAttribute('contenteditable');
        theoryContent.dataset.editorActive = 'false';

        // Restore image slots and quiz section
        theoryContent.querySelectorAll('.theory-image-slot').forEach(slot => {
            slot.removeAttribute('contenteditable');
        });
        const quizSection = theoryContent.querySelector('.theory-quiz-section');
        if (quizSection) {
            quizSection.removeAttribute('contenteditable');
        }

        // Remove save bar
        const saveBar = panel.querySelector('.theory-save-bar');
        if (saveBar) saveBar.remove();
    }

    // ── toggle all panels ───────────────────────────────────────────────
    function toggleInlineEditing() {
        editingActive = !editingActive;
        const panels = document.querySelectorAll('.theory-panel');

        if (editingActive) {
            createToolbar();
            // Only activate the currently visible (active) panel
            panels.forEach(p => {
                if (p.classList.contains('active')) {
                    activatePanel(p);
                }
            });
            document.body.classList.add('theory-inline-editing');
            document.addEventListener('selectionchange', positionToolbar);
        } else {
            panels.forEach(p => deactivatePanel(p));
            document.body.classList.remove('theory-inline-editing');
            document.removeEventListener('selectionchange', positionToolbar);
            hideToolbar();
        }

        // Update toggle button text
        const btn = document.getElementById('inlineEditToggle');
        if (btn) {
            const span = btn.querySelector('span');
            if (span) span.textContent = editingActive ? 'Lopeta muokkaus' : 'Muokkaa sisältöä';
            btn.classList.toggle('active', editingActive);
        }
    }

    // ── handle tab switch while editing ─────────────────────────────────
    function onTabSwitch() {
        if (!editingActive) return;
        setTimeout(() => {
            const activePanel = document.querySelector('.theory-panel.active');
            if (activePanel && activePanel.querySelector('.theory-content')
                && activePanel.querySelector('.theory-content').dataset.editorActive !== 'true') {
                activatePanel(activePanel);
            }
        }, 200);
    }

    // ── init ────────────────────────────────────────────────────────────
    function init() {
        const toggleBtn = document.getElementById('inlineEditToggle');
        if (!toggleBtn) return;

        toggleBtn.addEventListener('click', toggleInlineEditing);

        document.querySelectorAll('.theory-tab').forEach(tab => {
            tab.addEventListener('click', onTabSwitch);
        });

        console.log('Theory inline editor initialized');
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
