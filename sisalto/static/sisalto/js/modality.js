// epa_sections.js (voi olla myös radiologia_natiivikuvantaminen.js, jos haluat,
// mutta sisältö on nyt geneerinen kaikille sivuille)

let currentEditSectionId = null;
let editModalEditorInstance = null;

// Add Section functionality
let addModalEditorInstance = null;
let currentAfterSectionId = null;

//---------------------------------------------------------------------
//  API-osoitteiden peruspolku sivulta (HTML: .report-container data-api-base="...")
//---------------------------------------------------------------------
function getApiBase() {
    const container = document.querySelector('.report-container');
    if (!container) {
        console.warn('report-container ei löytynyt – API-basea ei voi lukea.');
        return '';
    }

    let base = container.dataset.apiBase || '';
    if (base && !base.endsWith('/')) {
        base += '/';
    }
    return base;  // esim. "/radiologia/natiivikuvantaminen/" tai "/radiologia/hammaskuvantaminen/"
}

//---------------------------------------------------------------------
//  CSRF token for AJAX requests
//---------------------------------------------------------------------
function getCSRFToken() {
    // yritetään ensin hidden inputista, sitten mahdollisesta meta-tagista, lopuksi cookie
    const inputToken = document.querySelector('[name=csrfmiddlewaretoken]');
    if (inputToken && inputToken.value) return inputToken.value;

    const metaToken = document.querySelector('meta[name="csrf-token"]');
    if (metaToken && metaToken.content) return metaToken.content;

    // getCookie tulee base_summereditor.html:stä
    if (typeof getCookie === "function") {
        return getCookie('csrftoken');
    }

    console.warn('CSRF-tokenia ei löytynyt!');
    return '';
}

//---------------------------------------------------------------------
//  Delete section
//---------------------------------------------------------------------
function deleteSection(sectionId) {
    const apiBase = getApiBase();
    if (!apiBase) return;

    if (confirm('Haluatko varmasti poistaa tämän osion? Toimintoa ei voi perua.')) {
        $.ajax({
            url: apiBase + 'delete_section/',
            method: 'POST',
            data: JSON.stringify({ section_id: sectionId }),
            contentType: 'application/json',
            headers: {
                'X-CSRFToken': getCSRFToken()
            },
            success: function(response) {
                if (response.success) {
                    showSaveStatus('Osio poistettu onnistuneesti!', 'success');

                    // Remove the section from DOM with animation
                    const sectionEl = document.querySelector(`[data-section-id="${sectionId}"]`);
                    if (sectionEl) {
                        sectionEl.style.opacity = '0';
                        sectionEl.style.transform = 'translateY(-20px)';
                        setTimeout(() => {
                            sectionEl.remove();
                        }, 300);
                    }
                } else {
                    showSaveStatus('Virhe osiota poistettaessa!', 'error');
                }
            },
            error: function(xhr, status, error) {
                console.error('Delete error:', xhr, status, error);
                showSaveStatus('Verkkovirhe osiota poistettaessa!', 'error');
            }
        });
    }
}

//---------------------------------------------------------------------
//  Edit section
//---------------------------------------------------------------------
function editSection(sectionId) {
    console.log('Editing section:', sectionId);
    currentEditSectionId = sectionId;

    // Get current title and content
    const sectionEl = document.querySelector(`[data-section-id="${sectionId}"]`);
    const titleEl = sectionEl ? sectionEl.querySelector('h2.section-title') : null;
    let actualTitle = 'Osio';

    if (titleEl) {
        // Get only text nodes, skip the icon element
        const textContent = Array.from(titleEl.childNodes)
            .filter(node => node.nodeType === Node.TEXT_NODE)
            .map(node => node.textContent.trim())
            .join(' ')
            .trim();
        actualTitle = textContent || 'Osio';
    }

    const contentEl = document.getElementById('section-content-' + sectionId);
    const currentContent = contentEl ? contentEl.innerHTML : '';

    // Set title and show modal
    document.getElementById('edit-section-title').value = actualTitle;
    document.getElementById('edit-section-modal').style.display = 'block';

    // Initialize Summernote editor using global function
    initEditSectionEditor(currentContent);
}

function initEditSectionEditor(content) {
    const editorContainer = document.getElementById('edit-section-editor');

    try {
        // Clean up any existing editor
        if (editModalEditorInstance) {
            $('#summernote-modal-editor').summernote('destroy');
            editModalEditorInstance = null;
        }

        // Create textarea for Summernote
        editorContainer.innerHTML = '<textarea id="summernote-modal-editor"></textarea>';

        console.log('Creating Summernote modal instance...');

        // Use global Summernote initialization with modal-specific options
        editModalEditorInstance = initSummernoteEditor('#summernote-modal-editor', {
            height: 350,
            focus: true,
            toolbar: [
                ['style', ['style']],
                ['font', ['bold', 'italic', 'underline', 'strikethrough']],
                ['fontsize', ['fontsize']],
                ['color', ['color']],
                ['para', ['ul', 'ol', 'paragraph']],
                ['table', ['table']],
                ['insert', ['link', 'picture', 'hr']],
                ['view', ['codeview', 'undo', 'redo']]
            ]
        });

        // Set content
        $('#summernote-modal-editor').summernote('code', content);

        console.log('Summernote modal editor ready!');

    } catch (error) {
        console.error('Failed to create Summernote editor:', error);
        editorContainer.innerHTML = `
            <div style="color: #f44336; margin: 10px 0;">
                ⚠️ Editori lataus epäonnistui. Käytä yksinkertaista tekstialuetta:
            </div>
            <textarea id="fallback-editor" style="width: 100%; height: 350px; border: 1px solid #ddd; padding: 10px; font-family: monospace; box-sizing: border-box;">${content}</textarea>
        `;
    }
}

function saveEditSection() {
    if (!currentEditSectionId) {
        return;
    }

    const apiBase = getApiBase();
    if (!apiBase) return;

    const title = document.getElementById('edit-section-title').value.trim();

    if (!title) {
        showSaveStatus('Kirjoita osion otsikko!', 'error');
        return;
    }

    let content;

    try {
        content = $('#summernote-modal-editor').summernote('code');
    } catch (e) {
        // Fallback for textarea
        const textarea = document.getElementById('fallback-editor');
        content = textarea ? textarea.value : '';
    }

    // Send AJAX request to update section
    $.ajax({
        url: apiBase + 'edit_section/',
        method: 'POST',
        data: {
            section_id: currentEditSectionId,
            title: title,
            content: content,
            csrfmiddlewaretoken: getCSRFToken()
        },
        success: function(response) {
            if (response.success) {
                // Update the DOM
                const sectionEl = document.querySelector(`[data-section-id="${currentEditSectionId}"]`);
                if (sectionEl) {
                    const titleEl = sectionEl.querySelector('h2.section-title');
                    if (titleEl) {
                        // Keep the icon and update only the text part
                        const icon = titleEl.querySelector('.section-icon');
                        titleEl.innerHTML = '';
                        if (icon) {
                            titleEl.appendChild(icon);
                        }
                        // Add the new title text as a text node
                        const textNode = document.createTextNode(' ' + title);
                        titleEl.appendChild(textNode);
                    }

                    const contentEl = sectionEl.querySelector('#section-content-' + currentEditSectionId);
                    if (contentEl) {
                        contentEl.innerHTML = content;
                    }
                }

                showSaveStatus('Osio tallennettu onnistuneesti!', 'success');

                setTimeout(() => {
                    closeEditSectionModal();
                }, 1000);
            } else {
                showSaveStatus('Virhe osiota tallentaessa: ' + (response.error || 'Tuntematon virhe'), 'error');
            }
        },
        error: function(xhr, status, error) {
            console.error('AJAX error:', xhr, status, error);
            showSaveStatus('Verkkovirhe osiota tallentaessa!', 'error');
        }
    });
}

function closeEditSectionModal() {
    document.getElementById('edit-section-modal').style.display = 'none';
    currentEditSectionId = null;

    if (editModalEditorInstance) {
        try {
            $('#summernote-modal-editor').summernote('destroy');
        } catch (e) {
            console.log('Editor cleanup completed');
        }
        editModalEditorInstance = null;
    }

    document.getElementById('edit-section-editor').innerHTML = '';
}

//---------------------------------------------------------------------
//  Save status popup
//---------------------------------------------------------------------
function showSaveStatus(message, type) {
    const statusEl = document.getElementById('save-status');
    if (!statusEl) return;

    statusEl.textContent = message;
    statusEl.style.backgroundColor = type === 'success' ? '#4caf50' : '#f44336';
    statusEl.style.display = 'block';

    setTimeout(() => {
        statusEl.style.display = 'none';
    }, 3000);
}

//---------------------------------------------------------------------
//  Add section
//---------------------------------------------------------------------
function showAddSectionModal(afterSectionId) {
    currentAfterSectionId = afterSectionId;
    document.getElementById('add-section-title').value = '';
    document.getElementById('add-section-modal').style.display = 'block';

    // Initialize Summernote editor for adding
    initAddSectionEditor('');
}

function initAddSectionEditor(content) {
    const editorContainer = document.getElementById('add-section-editor');

    try {
        // Clean up any existing editor
        if (addModalEditorInstance) {
            $('#summernote-add-editor').summernote('destroy');
            addModalEditorInstance = null;
        }

        // Create textarea for Summernote
        editorContainer.innerHTML = '<textarea id="summernote-add-editor"></textarea>';

        console.log('Creating Summernote add instance...');

        // Use global Summernote initialization
        addModalEditorInstance = initSummernoteEditor('#summernote-add-editor', {
            height: 350,
            focus: true,
            toolbar: [
                ['style', ['style']],
                ['font', ['bold', 'italic', 'underline', 'strikethrough']],
                ['fontsize', ['fontsize']],
                ['color', ['color']],
                ['para', ['ul', 'ol', 'paragraph']],
                ['table', ['table']],
                ['insert', ['link', 'picture', 'hr']],
                ['view', ['codeview', 'undo', 'redo']]
            ]
        });

        // Set content
        $('#summernote-add-editor').summernote('code', content);

        console.log('Summernote add editor ready!');

    } catch (error) {
        console.error('Failed to create Summernote add editor:', error);
        editorContainer.innerHTML = `
            <div style="color: #f44336; margin: 10px 0%;">
                ⚠️ Editori lataus epäonnistui. Käytä yksinkertaista tekstialuetta:
            </div>
            <textarea id="fallback-add-editor" style="width: 100%; height: 350px; border: 1px solid #ddd; padding: 10px; font-family: monospace; box-sizing: border-box;">${content}</textarea>
        `;
    }
}

function saveAddSection() {
    const apiBase = getApiBase();
    if (!apiBase) return;

    const title = document.getElementById('add-section-title').value.trim();

    if (!title) {
        showSaveStatus('Kirjoita osion otsikko!', 'error');
        return;
    }

    let content;

    try {
        content = $('#summernote-add-editor').summernote('code');
    } catch (e) {
        // Fallback for textarea
        const textarea = document.getElementById('fallback-add-editor');
        content = textarea ? textarea.value : '';
    }

    // Get EPA ID from the page context
    const container = document.querySelector('.report-container');
    const epaId = container ? container.dataset.epaId : null;

    // Send AJAX request to add section
    $.ajax({
        url: apiBase + 'add_section/',
        method: 'POST',
        data: JSON.stringify({
            epa_id: epaId,
            title: title,
            content: content,
            proficiency_level: '1',
            after_section_id: currentAfterSectionId
        }),
        contentType: 'application/json',
        headers: {
            'X-CSRFToken': getCSRFToken()
        },
        success: function(response) {
            if (response.success) {
                showSaveStatus('Uusi osio lisätty onnistuneesti!', 'success');

                setTimeout(() => {
                    closeAddSectionModal();
                    // Reload page to show new section
                    location.reload();
                }, 1000);
            } else {
                showSaveStatus('Virhe osiota lisättäessä: ' + (response.error || 'Tuntematon virhe'), 'error');
            }
        },
        error: function(xhr, status, error) {
            console.error('AJAX error:', xhr, status, error);
            showSaveStatus('Verkkovirhe osiota lisättäessä!', 'error');
        }
    });
}

function closeAddSectionModal() {
    document.getElementById('add-section-modal').style.display = 'none';
    currentAfterSectionId = null;

    if (addModalEditorInstance) {
        try {
            $('#summernote-add-editor').summernote('destroy');
        } catch (e) {
            console.log('Add editor cleanup completed');
        }
        addModalEditorInstance = null;
    }

    document.getElementById('add-section-editor').innerHTML = '';
}

//---------------------------------------------------------------------
//  Close modal when clicking outside of it
//---------------------------------------------------------------------
window.addEventListener('click', function(event) {
    const editModal = document.getElementById('edit-section-modal');
    const addModal = document.getElementById('add-section-modal');

    if (event.target === editModal) {
        closeEditSectionModal();
    }
    if (event.target === addModal) {
        closeAddSectionModal();
    }
});

//---------------------------------------------------------------------
//  Update proficiency level
//---------------------------------------------------------------------
function updateProficiencyLevel(sectionId, level) {
    const apiBase = getApiBase();
    if (!apiBase) return;

    console.log('Updating proficiency level for section:', sectionId, 'to level:', level);

    // Update select styling based on level
    const selectEl = document.getElementById('proficiency-' + sectionId);
    if (selectEl) {
        // Remove old level classes
        selectEl.classList.remove('proficiency-level-1', 'proficiency-level-2', 'proficiency-level-3');
        // Add new level class
        selectEl.classList.add('proficiency-level-' + level);
    }

    // Update section title color
    const titleEl = document.getElementById('section-title-' + sectionId);
    if (titleEl) {
        titleEl.classList.remove('proficiency-1', 'proficiency-2', 'proficiency-3');
        titleEl.classList.add('proficiency-' + level);
    }

    // Update section icon color
    const iconEl = document.getElementById('section-icon-' + sectionId);
    if (iconEl) {
        iconEl.classList.remove('proficiency-1', 'proficiency-2', 'proficiency-3');
        iconEl.classList.add('proficiency-' + level);
    }

    // Send AJAX request to update database
    $.ajax({
        url: apiBase + 'update_proficiency/',
        method: 'POST',
        data: JSON.stringify({
            section_id: sectionId,
            proficiency_level: parseInt(level)
        }),
        contentType: 'application/json',
        headers: {
            'X-CSRFToken': getCSRFToken()
        },
        success: function(response) {
            if (response.success) {
                showSaveStatus('Osaamistaso päivitetty!', 'success');
            } else {
                showSaveStatus('Virhe osaamistasoa päivittäessä!', 'error');
            }
        },
        error: function(xhr, status, error) {
            console.error('Proficiency update error:', xhr, status, error);
            showSaveStatus('Verkkovirhe osaamistasoa päivittäessä!', 'error');
        }
    });
}

//---------------------------------------------------------------------
//  Init
//---------------------------------------------------------------------
document.addEventListener('DOMContentLoaded', function() {
    console.log('EPA-sektio-skripti ladattu!');

    // Viivytetään alustus varmistaaksemme että kaikki on latautunut
    setTimeout(function() {
        // Normalisoi proficiency-selectien arvot perustuen CSS-luokkaan
        const selects = document.querySelectorAll('.proficiency-select');
        
        selects.forEach((select) => {
            // Etsi selected option
            const selectedOption = select.querySelector('option[selected]');
            
            // Jos selected option ei löydy, käytä CSS-luokasta tietoa
            let level = selectedOption ? selectedOption.value : null;
            
            if (!level) {
                // Etsi proficiency-level CSS-luokasta
                const classList = Array.from(select.classList);
                const proficiencyClass = classList.find(cls => cls.startsWith('proficiency-level-'));
                if (proficiencyClass) {
                    level = proficiencyClass.split('-')[2]; // 'proficiency-level-3' -> '3'
                }
            }
            
            // Fallback oletusarvoon
            if (!level) {
                level = select.value || '1';
            }
            
            // Aseta dropdown oikea arvo
            select.value = level;
            
            // Päivitä CSS-luokat
            select.classList.remove('proficiency-level-1', 'proficiency-level-2', 'proficiency-level-3');
            if (level) {
                select.classList.add('proficiency-level-' + level);
            }
        });
    }, 100); // Lyhennetään viive 100ms:iin
});
