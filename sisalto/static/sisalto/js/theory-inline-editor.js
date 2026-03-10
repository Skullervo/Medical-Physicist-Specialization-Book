/**
 * Theory Inline Editor — Native contenteditable + fixed dock toolbar.
 * Superuser-only: click "Muokkaa sisältöä" to toggle editing mode.
 * Features: text editing, image slot insertion, caption editing, drag-and-drop.
 *
 * The toolbar is a fixed dock at the bottom of the viewport, always visible
 * during edit mode so the user never needs to scroll to find it.
 */
(function () {
    'use strict';

    const SAVE_URL = '/modaliteetit/api/theory-content/save/';
    let editingActive = false;
    let toolbar = null;
    let draggedSlot = null;

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

    function getActiveTabId() {
        const panel = document.querySelector('.theory-panel.active');
        return panel ? panel.id.replace('panel-', '') : '';
    }

    // ── fixed dock toolbar ──────────────────────────────────────────────
    function createToolbar() {
        if (toolbar) return toolbar;

        toolbar = document.createElement('div');
        toolbar.className = 'theory-dock-toolbar';
        toolbar.innerHTML =
            '<div class="theory-dock-group">' +
                '<button data-cmd="bold" title="Lihavointi (Ctrl+B)"><i class="fas fa-bold"></i></button>' +
                '<button data-cmd="italic" title="Kursiivi (Ctrl+I)"><i class="fas fa-italic"></i></button>' +
                '<button data-cmd="underline" title="Alleviivaus (Ctrl+U)"><i class="fas fa-underline"></i></button>' +
                '<button data-cmd="strikethrough" title="Yliviivaus"><i class="fas fa-strikethrough"></i></button>' +
            '</div>' +
            '<div class="theory-dock-group">' +
                '<button data-cmd="insertUnorderedList" title="Lista"><i class="fas fa-list-ul"></i></button>' +
                '<button data-cmd="insertOrderedList" title="Numeroitu lista"><i class="fas fa-list-ol"></i></button>' +
                '<button data-cmd="indent" title="Lisää sisennys (Tab)"><i class="fas fa-indent"></i></button>' +
                '<button data-cmd="outdent" title="Vähennä sisennys (Shift+Tab)"><i class="fas fa-outdent"></i></button>' +
            '</div>' +
            '<div class="theory-dock-group">' +
                '<button data-cmd="formatBlock" data-value="H2" title="H2-otsikko"><b>H2</b></button>' +
                '<button data-cmd="formatBlock" data-value="H3" title="H3-otsikko"><b>H3</b></button>' +
                '<button data-cmd="formatBlock" data-value="H4" title="H4-otsikko"><b>H4</b></button>' +
                '<button data-cmd="formatBlock" data-value="P" title="Normaali teksti"><b>P</b></button>' +
            '</div>' +
            '<div class="theory-dock-group">' +
                '<button data-cmd="subscript" title="Alaindeksi"><i class="fas fa-subscript"></i></button>' +
                '<button data-cmd="superscript" title="Yläindeksi"><i class="fas fa-superscript"></i></button>' +
            '</div>' +
            '<div class="theory-dock-group">' +
                '<button data-cmd="createLink" title="Linkki"><i class="fas fa-link"></i></button>' +
                '<button data-cmd="removeFormat" title="Poista muotoilu"><i class="fas fa-eraser"></i></button>' +
            '</div>' +
            '<div class="theory-dock-group theory-dock-color-group">' +
                '<button data-cmd="textColor" title="Tekstin väri"><i class="fas fa-palette"></i></button>' +
                '<div class="theory-color-picker">' +
                    '<button data-color="#e2e8f0" title="Oletus (valkoinen)" style="background:#e2e8f0"></button>' +
                    '<button data-color="#60a5fa" title="Sininen" style="background:#60a5fa"></button>' +
                    '<button data-color="#34d399" title="Vihreä" style="background:#34d399"></button>' +
                    '<button data-color="#a78bfa" title="Violetti" style="background:#a78bfa"></button>' +
                    '<button data-color="#fb923c" title="Oranssi" style="background:#fb923c"></button>' +
                    '<button data-color="#f87171" title="Punainen" style="background:#f87171"></button>' +
                    '<button data-color="#fbbf24" title="Keltainen" style="background:#fbbf24"></button>' +
                    '<button data-color="inherit" title="Poista väri" class="theory-color-reset"><i class="fas fa-ban"></i></button>' +
                '</div>' +
            '</div>' +
            '<div class="theory-dock-group">' +
                '<button data-cmd="undo" title="Kumoa (Ctrl+Z)"><i class="fas fa-undo"></i></button>' +
                '<button data-cmd="redo" title="Tee uudelleen (Ctrl+Y)"><i class="fas fa-redo"></i></button>' +
            '</div>' +
            '<div class="theory-dock-sep"></div>' +
            '<div class="theory-dock-group">' +
                '<button data-cmd="insertImage" class="theory-dock-accent" title="Lisää kuvapaikka"><i class="fas fa-image"></i> Kuva</button>' +
            '</div>' +
            '<div class="theory-dock-group theory-dock-right">' +
                '<button data-cmd="save" class="theory-dock-save" title="Tallenna (Ctrl+S)"><i class="fas fa-save"></i> Tallenna</button>' +
            '</div>';

        // Prevent toolbar clicks from stealing focus
        toolbar.addEventListener('mousedown', function (e) {
            e.preventDefault();
        });

        toolbar.addEventListener('click', function (e) {
            const btn = e.target.closest('button');
            if (!btn) return;

            // Color picker swatch click
            if (btn.dataset.color) {
                const color = btn.dataset.color;
                if (color === 'inherit') {
                    document.execCommand('removeFormat', false, null);
                } else {
                    document.execCommand('foreColor', false, color);
                }
                btn.closest('.theory-color-picker').classList.remove('open');
                return;
            }

            const cmd = btn.dataset.cmd;
            const value = btn.dataset.value || null;

            // Toggle color picker
            if (cmd === 'textColor') {
                const picker = btn.nextElementSibling;
                if (picker) picker.classList.toggle('open');
                return;
            }

            // Close color picker on any other action
            const openPicker = toolbar.querySelector('.theory-color-picker.open');
            if (openPicker) openPicker.classList.remove('open');

            if (cmd === 'insertImage') {
                insertImageSlot();
            } else if (cmd === 'save') {
                const tabId = getActiveTabId();
                if (tabId) savePanel(tabId);
            } else if (cmd === 'createLink') {
                const url = prompt('URL:');
                if (url) document.execCommand('createLink', false, url);
            } else if (cmd === 'formatBlock') {
                document.execCommand('formatBlock', false, '<' + value + '>');
            } else {
                document.execCommand(cmd, false, value);
            }
        });

        document.body.appendChild(toolbar);

        // Ctrl+S shortcut to save
        document.addEventListener('keydown', function (e) {
            if (editingActive && e.ctrlKey && e.key === 's') {
                e.preventDefault();
                const tabId = getActiveTabId();
                if (tabId) savePanel(tabId);
            }
        });

        return toolbar;
    }

    function showToolbar() {
        if (toolbar) toolbar.classList.add('visible');
    }

    function hideToolbar() {
        if (toolbar) toolbar.classList.remove('visible');
    }

    // ── insert image slot at cursor ─────────────────────────────────────
    function insertImageSlot() {
        const sel = window.getSelection();
        if (!sel || sel.rangeCount === 0) {
            showToast('Aseta kursori tekstiin ensin', false);
            return;
        }

        const range = sel.getRangeAt(0);
        const anchor = range.startContainer;
        const editableEl = anchor && anchor.nodeType === 3
            ? anchor.parentElement.closest('.theory-content[contenteditable="true"]')
            : (anchor && anchor.closest ? anchor.closest('.theory-content[contenteditable="true"]') : null);

        if (!editableEl) {
            showToast('Aseta kursori tekstiin ensin', false);
            return;
        }

        const panel = editableEl.closest('.theory-panel');
        const tabId = panel ? panel.id.replace('panel-', '') : getActiveTabId();
        const slotId = 'dyn-' + Date.now() + '-' + Math.random().toString(36).substr(2, 5);

        // Create the slot element
        const slot = document.createElement('div');
        slot.className = 'theory-image-slot';
        slot.setAttribute('data-slot', slotId);
        slot.setAttribute('data-tab', tabId);
        slot.setAttribute('data-dynamic', 'true');
        slot.setAttribute('contenteditable', 'false');

        // Find the nearest block-level ancestor to insert after
        let insertRef = range.startContainer;
        while (insertRef && insertRef !== editableEl && insertRef.parentNode !== editableEl) {
            insertRef = insertRef.parentNode;
        }

        if (insertRef && insertRef !== editableEl) {
            insertRef.parentNode.insertBefore(slot, insertRef.nextSibling);
        } else {
            editableEl.appendChild(slot);
        }

        // Re-render slots so the placeholder appears
        if (typeof window.renderAllSlots === 'function') {
            window.renderAllSlots();
        }

        // Make the new slot non-editable within contenteditable
        slot.setAttribute('contenteditable', 'false');

        // Open upload modal for the new slot
        if (typeof window.openUploadModal === 'function') {
            window.openUploadModal(slotId, tabId);
        }
    }

    // ── caption inline editing ──────────────────────────────────────────
    function enableCaptionEditing(panel) {
        panel.querySelectorAll('.theory-image-slot figcaption').forEach(cap => {
            if (cap.dataset.captionEditable) return;
            cap.dataset.captionEditable = 'true';
            cap.setAttribute('contenteditable', 'true');
            cap.classList.add('theory-caption-editable');

            cap.addEventListener('focus', onCaptionFocus);
            cap.addEventListener('blur', onCaptionBlur);
            cap.addEventListener('keydown', function (e) {
                if (e.key === 'Enter') { e.preventDefault(); cap.blur(); }
            });
        });
    }

    function disableCaptionEditing(panel) {
        panel.querySelectorAll('.theory-image-slot figcaption').forEach(cap => {
            cap.removeAttribute('contenteditable');
            cap.classList.remove('theory-caption-editable');
            delete cap.dataset.captionEditable;
        });
    }

    function onCaptionFocus(e) {
        e.target.dataset.originalCaption = e.target.textContent;
    }

    function onCaptionBlur(e) {
        const cap = e.target;
        const newText = cap.textContent.trim();
        const original = cap.dataset.originalCaption || '';
        if (newText === original.trim()) return;

        const slot = cap.closest('.theory-image-slot');
        if (!slot) return;

        const slotId = slot.dataset.slot;
        const tabId = slot.dataset.tab;
        const modality = getModality();

        const fd = new FormData();
        fd.append('modality', modality);
        fd.append('tab_id', tabId);
        fd.append('slot_id', slotId);
        fd.append('caption', newText);

        const img = slot.querySelector('img');
        fd.append('alt_text', img ? (img.alt || '') : '');
        const sizeMatch = slot.className.match(/size-(\w+)/);
        fd.append('display_size', sizeMatch ? sizeMatch[1] : 'medium');

        fetch('/modaliteetit/api/theory-images/upload/', {
            method: 'POST',
            headers: { 'X-CSRFToken': csrfToken() },
            body: fd,
        })
        .then(r => r.json())
        .then(data => {
            if (data.ok) showToast('Kuvateksti tallennettu!', true);
            else showToast('Virhe: ' + (data.error || ''), false);
        })
        .catch(() => showToast('Verkkovirhe', false));
    }

    // ── drag and drop for image slots ───────────────────────────────────
    function enableDragDrop(panel) {
        panel.querySelectorAll('.theory-image-slot').forEach(slot => {
            if (slot.dataset.dragEnabled) return;
            slot.dataset.dragEnabled = 'true';

            const figure = slot.querySelector('figure');
            if (figure && !figure.querySelector('.theory-drag-handle')) {
                const handle = document.createElement('div');
                handle.className = 'theory-drag-handle';
                handle.innerHTML = '<i class="fas fa-grip-vertical"></i>';
                handle.title = 'Raahaa siirtääksesi';
                figure.prepend(handle);
            }

            slot.setAttribute('draggable', 'true');
            slot.addEventListener('dragstart', onDragStart);
            slot.addEventListener('dragend', onDragEnd);
        });

        const content = panel.querySelector('.theory-content');
        if (content && !content.dataset.dropEnabled) {
            content.dataset.dropEnabled = 'true';
            content.addEventListener('dragover', onDragOver);
            content.addEventListener('dragleave', onDragLeave);
            content.addEventListener('drop', onDrop);
        }
    }

    function disableDragDrop(panel) {
        panel.querySelectorAll('.theory-image-slot').forEach(slot => {
            slot.removeAttribute('draggable');
            delete slot.dataset.dragEnabled;
            const handle = slot.querySelector('.theory-drag-handle');
            if (handle) handle.remove();
        });
        const content = panel.querySelector('.theory-content');
        if (content) delete content.dataset.dropEnabled;
    }

    function onDragStart(e) {
        draggedSlot = e.target.closest('.theory-image-slot');
        if (!draggedSlot) return;
        draggedSlot.classList.add('theory-slot-dragging');
        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setData('text/plain', draggedSlot.dataset.slot);
    }

    function onDragEnd() {
        if (draggedSlot) {
            draggedSlot.classList.remove('theory-slot-dragging');
        }
        draggedSlot = null;
        removeDropIndicators();
    }

    function onDragOver(e) {
        if (!draggedSlot) return;
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';

        const content = e.currentTarget;
        removeDropIndicators();

        const target = getDropTarget(content, e.clientY);
        if (target && target !== draggedSlot) {
            const rect = target.getBoundingClientRect();
            const midY = rect.top + rect.height / 2;
            const indicator = document.createElement('div');
            indicator.className = 'theory-drop-indicator';

            if (e.clientY < midY) {
                target.parentNode.insertBefore(indicator, target);
            } else {
                target.parentNode.insertBefore(indicator, target.nextSibling);
            }
        }
    }

    function onDragLeave(e) {
        if (!e.currentTarget.contains(e.relatedTarget)) {
            removeDropIndicators();
        }
    }

    function onDrop(e) {
        if (!draggedSlot) return;
        e.preventDefault();

        const content = e.currentTarget;
        removeDropIndicators();

        const target = getDropTarget(content, e.clientY);
        if (!target || target === draggedSlot) return;

        const rect = target.getBoundingClientRect();
        const midY = rect.top + rect.height / 2;

        if (e.clientY < midY) {
            target.parentNode.insertBefore(draggedSlot, target);
        } else {
            target.parentNode.insertBefore(draggedSlot, target.nextSibling);
        }

        if (!draggedSlot.dataset.dynamic) {
            draggedSlot.setAttribute('data-dynamic', 'true');
        }

        draggedSlot.classList.remove('theory-slot-dragging');
        draggedSlot = null;

        showToast('Kuva siirretty — tallenna muutokset', true);
    }

    function getDropTarget(content, clientY) {
        const children = Array.from(content.children).filter(el =>
            !el.classList.contains('theory-drop-indicator') &&
            !el.classList.contains('theory-quiz-section')
        );
        if (!children.length) return null;

        let closest = null;
        let closestDist = Infinity;
        for (const child of children) {
            const rect = child.getBoundingClientRect();
            const mid = rect.top + rect.height / 2;
            const dist = Math.abs(clientY - mid);
            if (dist < closestDist) {
                closestDist = dist;
                closest = child;
            }
        }
        return closest;
    }

    function removeDropIndicators() {
        document.querySelectorAll('.theory-drop-indicator').forEach(el => el.remove());
    }

    // ── save single panel ───────────────────────────────────────────────
    function savePanel(tabId) {
        const panel = document.getElementById('panel-' + tabId);
        if (!panel) return;

        const theoryContent = panel.querySelector('.theory-content');
        if (!theoryContent) return;

        const clone = theoryContent.cloneNode(true);

        const quizSec = clone.querySelector('.theory-quiz-section');
        if (quizSec) quizSec.remove();

        // Remove EPA card from saved content (it comes from the template)
        const epaCard = clone.querySelector('.theory-epa-card');
        if (epaCard) epaCard.remove();

        clone.querySelectorAll('.theory-image-slot').forEach(s => {
            if (s.dataset.dynamic === 'true') {
                s.innerHTML = '';
                s.removeAttribute('contenteditable');
                s.removeAttribute('draggable');
                s.className = 'theory-image-slot';
                const attrs = ['class', 'data-slot', 'data-tab', 'data-dynamic'];
                Array.from(s.attributes).forEach(attr => {
                    if (!attrs.includes(attr.name)) s.removeAttribute(attr.name);
                });
            } else {
                s.remove();
            }
        });

        clone.querySelectorAll('.theory-drag-handle').forEach(h => h.remove());
        clone.querySelectorAll('.theory-drop-indicator').forEach(h => h.remove());
        clone.querySelectorAll('.theory-save-bar').forEach(h => h.remove());
        clone.querySelectorAll('[data-drag-enabled]').forEach(el => el.removeAttribute('data-drag-enabled'));
        clone.querySelectorAll('[data-caption-editable]').forEach(el => el.removeAttribute('data-caption-editable'));

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

        theoryContent.setAttribute('contenteditable', 'true');
        theoryContent.setAttribute('spellcheck', 'false');
        theoryContent.dataset.editorActive = 'true';

        theoryContent.querySelectorAll('.theory-image-slot').forEach(slot => {
            slot.setAttribute('contenteditable', 'false');
        });
        const quizSection = theoryContent.querySelector('.theory-quiz-section');
        if (quizSection) {
            quizSection.setAttribute('contenteditable', 'false');
        }

        enableCaptionEditing(panel);
        enableDragDrop(panel);

        console.log('Inline editing activated for tab:', panel.id.replace('panel-', ''));
    }

    // ── deactivate editing on one panel ─────────────────────────────────
    function deactivatePanel(panel) {
        const theoryContent = panel.querySelector('.theory-content');
        if (!theoryContent || theoryContent.dataset.editorActive !== 'true') return;

        theoryContent.removeAttribute('contenteditable');
        theoryContent.dataset.editorActive = 'false';

        theoryContent.querySelectorAll('.theory-image-slot').forEach(slot => {
            slot.removeAttribute('contenteditable');
        });
        const quizSection = theoryContent.querySelector('.theory-quiz-section');
        if (quizSection) {
            quizSection.removeAttribute('contenteditable');
        }

        disableCaptionEditing(panel);
        disableDragDrop(panel);
    }

    // ── toggle all panels ───────────────────────────────────────────────
    function toggleInlineEditing() {
        editingActive = !editingActive;
        const panels = document.querySelectorAll('.theory-panel');

        if (editingActive) {
            createToolbar();
            showToolbar();
            panels.forEach(p => {
                if (p.classList.contains('active')) {
                    activatePanel(p);
                }
            });
            document.body.classList.add('theory-inline-editing');
            document.body.classList.add('theory-edit-mode');
        } else {
            panels.forEach(p => deactivatePanel(p));
            document.body.classList.remove('theory-inline-editing');
            document.body.classList.remove('theory-edit-mode');
            hideToolbar();
        }

        const btn = document.getElementById('inlineEditToggle');
        if (btn) {
            const span = btn.querySelector('span');
            if (span) span.textContent = editingActive ? 'Lopeta muokkaus' : 'Muokkaa sisältöä';
            btn.classList.toggle('active', editingActive);
        }
    }

    // ── delete an entire image slot (dynamic only) ─────────────────────
    window.deleteImageSlot = function (slotId, tabId) {
        if (!editingActive) return;
        if (!confirm('Poistetaanko tämä kuvaikkunaa?')) return;

        const slot = document.querySelector('.theory-image-slot[data-slot="' + slotId + '"]');

        // If the slot has an uploaded image, delete it from the server first
        if (slot && slot.classList.contains('has-image')) {
            fetch('/modaliteetit/api/theory-images/delete/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken(),
                },
                body: JSON.stringify({ modality: getModality(), slot_id: slotId }),
            })
            .then(r => r.json())
            .then(() => {})
            .catch(() => {});
        }

        // Remove the slot div from DOM
        if (slot) slot.remove();
        showToast('Kuvaikkunaa poistettu', true);
    };

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

    // ── observe slot re-renders to re-enable editing features ───────────
    function observeSlotChanges() {
        const observer = new MutationObserver(() => {
            if (!editingActive) return;
            const panel = document.querySelector('.theory-panel.active');
            if (panel) {
                enableCaptionEditing(panel);
                enableDragDrop(panel);
                panel.querySelectorAll('.theory-image-slot').forEach(slot => {
                    slot.setAttribute('contenteditable', 'false');
                });
            }
        });

        document.querySelectorAll('.theory-content').forEach(content => {
            observer.observe(content, { childList: true, subtree: true });
        });
    }

    // ── load saved content on page load ────────────────────────────────
    function loadSavedContent() {
        const modality = getModality();
        if (!modality) return;

        document.querySelectorAll('.theory-panel').forEach(panel => {
            const tabId = panel.id.replace('panel-', '');
            const theoryContent = panel.querySelector('.theory-content');
            if (!theoryContent) return;

            fetch('/modaliteetit/api/theory-content/' + modality + '/' + tabId + '/')
                .then(r => {
                    if (!r.ok) return null; // 404 = no saved content, keep template
                    return r.json();
                })
                .then(data => {
                    if (!data || !data.content) return;

                    // Preserve predefined image slots from template
                    const templateSlots = [];
                    theoryContent.querySelectorAll('.theory-image-slot:not([data-dynamic="true"])').forEach(slot => {
                        templateSlots.push(slot.cloneNode(true));
                    });

                    // Preserve quiz section from template
                    const quizSection = theoryContent.querySelector('.theory-quiz-section');
                    const quizClone = quizSection ? quizSection.cloneNode(true) : null;

                    // Preserve EPA card from template (always at top)
                    const epaCard = theoryContent.querySelector('.theory-epa-card');
                    const epaClone = epaCard ? epaCard.cloneNode(true) : null;

                    // Replace content with saved version
                    theoryContent.innerHTML = data.content;

                    // Remove any EPA card from saved content (old position)
                    const savedEpa = theoryContent.querySelector('.theory-epa-card');
                    if (savedEpa) savedEpa.remove();

                    // Fix dynamic slots saved without class attribute (legacy bug)
                    theoryContent.querySelectorAll('[data-dynamic="true"]').forEach(el => {
                        if (!el.classList.contains('theory-image-slot')) {
                            el.className = 'theory-image-slot';
                        }
                    });

                    // Re-insert EPA card at the very top
                    if (epaClone) {
                        theoryContent.insertBefore(epaClone, theoryContent.firstChild);
                    }

                    // Re-append predefined template slots at original positions
                    templateSlots.forEach(slot => {
                        const slotId = slot.dataset.slot;
                        if (!theoryContent.querySelector('[data-slot="' + slotId + '"]')) {
                            theoryContent.appendChild(slot);
                        }
                    });

                    // Re-append quiz section at the end
                    if (quizClone) {
                        theoryContent.appendChild(quizClone);
                    }

                    // Re-render image slots with actual images
                    // Use retry to handle race condition with imageData loading
                    function tryRender(attempts) {
                        if (typeof window.renderAllSlots === 'function') {
                            window.renderAllSlots();
                        }
                        // If dynamic slots still have no images and we have retries left,
                        // wait for imageData to be populated by template script
                        if (attempts > 0) {
                            const unrendered = theoryContent.querySelectorAll('.theory-image-slot[data-dynamic="true"]:not(.has-image)');
                            if (unrendered.length > 0) {
                                setTimeout(() => tryRender(attempts - 1), 300);
                            }
                        }
                    }
                    tryRender(5);
                })
                .catch(() => {}); // Network error — keep template content
        });
    }

    // ── init ────────────────────────────────────────────────────────────
    function init() {
        // Always load saved content (for all users, not just superusers)
        loadSavedContent();

        const toggleBtn = document.getElementById('inlineEditToggle');
        if (!toggleBtn) return; // Editing features only for superusers

        toggleBtn.addEventListener('click', toggleInlineEditing);

        document.querySelectorAll('.theory-tab').forEach(tab => {
            tab.addEventListener('click', onTabSwitch);
        });

        observeSlotChanges();
        console.log('Theory inline editor initialized');
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
