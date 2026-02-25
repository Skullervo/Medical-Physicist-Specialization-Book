// Section Management JavaScript
// Global variables
let currentEditSectionId = null;
let editModalEditorInstance = null;
let addModalEditorInstance = null;

// CSRF token for AJAX requests
function getCSRFToken() {
    return $('[name=csrfmiddlewaretoken]').val() || 
           $('meta[name=csrf-token]').attr('content') || 
           document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
}

// Show save status message
function showSaveStatus(message, type) {
    const statusEl = document.getElementById('save-status');
    if (statusEl) {
        statusEl.textContent = message;
        statusEl.className = 'save-status ' + type + ' show';
        
        setTimeout(() => {
            statusEl.classList.remove('show');
        }, 3000);
    }
}

// Update proficiency level
function updateProficiencyLevel(sectionId, level, baseUrl) {
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
        url: baseUrl + 'update_proficiency/',
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

// Delete section function
function deleteSection(sectionId, baseUrl) {
    if (confirm('Haluatko varmasti poistaa tämän osion? Toimintoa ei voi perua.')) {
        $.ajax({
            url: baseUrl + 'delete_section/',
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

// Section management functions
function editSection(sectionId) {
    console.log('Editing section:', sectionId);
    currentEditSectionId = sectionId;
    
    // Get current title and content
    const sectionEl = document.querySelector(`[data-section-id="${sectionId}"]`);
    const titleEl = sectionEl.querySelector('h2.section-title');
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

// Save edited section
function saveEditedSection(baseUrl) {
    if (!currentEditSectionId) {
        console.error('No section ID set for editing');
        return;
    }

    const title = document.getElementById('edit-section-title').value.trim();
    const content = $('#summernote-edit-editor').summernote('code');

    if (!title) {
        alert('Otsikko ei voi olla tyhjä');
        return;
    }

    console.log('Saving section:', currentEditSectionId, 'Title:', title);

    $.ajax({
        url: baseUrl + 'edit_section/',
        method: 'POST',
        data: JSON.stringify({
            section_id: currentEditSectionId,
            title: title,
            content: content
        }),
        contentType: 'application/json',
        headers: {
            'X-CSRFToken': getCSRFToken()
        },
        success: function(response) {
            if (response.success) {
                showSaveStatus('Osio tallennettu onnistuneesti!', 'success');
                
                // Update the section in DOM
                const sectionEl = document.querySelector(`[data-section-id="${currentEditSectionId}"]`);
                if (sectionEl) {
                    const titleEl = sectionEl.querySelector('h2.section-title');
                    if (titleEl) {
                        // Preserve the icon and update only the text
                        const iconEl = titleEl.querySelector('.section-icon');
                        titleEl.innerHTML = '';
                        if (iconEl) {
                            titleEl.appendChild(iconEl);
                        }
                        titleEl.appendChild(document.createTextNode(title));
                    }
                    
                    const contentEl = document.getElementById('section-content-' + currentEditSectionId);
                    if (contentEl) {
                        contentEl.innerHTML = content;
                    }
                }
                
                closeEditSectionModal();
            } else {
                showSaveStatus('Virhe osiota tallentaessa!', 'error');
            }
        },
        error: function(xhr, status, error) {
            console.error('Save error:', xhr, status, error);
            showSaveStatus('Verkkovirhe osiota tallentaessa!', 'error');
        }
    });
}

// Show add section modal
function showAddSectionModal(afterSectionId) {
    console.log('Adding section after:', afterSectionId);
    window.currentAfterSectionId = afterSectionId;
    
    // Clear form
    document.getElementById('add-section-title').value = '';
    document.getElementById('add-section-modal').style.display = 'block';
    
    // Initialize Summernote editor
    initAddSectionEditor();
}

// Add new section
function addNewSection(baseUrl) {
    const title = document.getElementById('add-section-title').value.trim();
    const content = $('#summernote-add-editor').summernote('code');
    const afterSectionId = window.currentAfterSectionId || null;

    if (!title) {
        alert('Otsikko ei voi olla tyhjä');
        return;
    }

    console.log('Adding new section:', title, 'after section:', afterSectionId);

    $.ajax({
        url: baseUrl + 'add_section/',
        method: 'POST',
        data: JSON.stringify({
            title: title,
            content: content,
            after_section_id: afterSectionId
        }),
        contentType: 'application/json',
        headers: {
            'X-CSRFToken': getCSRFToken()
        },
        success: function(response) {
            if (response.success) {
                showSaveStatus('Osio lisätty onnistuneesti!', 'success');
                closeAddSectionModal();
                
                // Reload page to show new section
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            } else {
                showSaveStatus('Virhe osiota lisätessä!', 'error');
            }
        },
        error: function(xhr, status, error) {
            console.error('Add error:', xhr, status, error);
            showSaveStatus('Verkkovirhe osiota lisätessä!', 'error');
        }
    });
}

// Close edit section modal
function closeEditSectionModal() {
    document.getElementById('edit-section-modal').style.display = 'none';
    currentEditSectionId = null;
    
    // Clean up Summernote editor
    if (editModalEditorInstance) {
        try {
            $('#summernote-edit-editor').summernote('destroy');
        } catch (e) {
            console.log('Edit editor cleanup completed');
        }
        editModalEditorInstance = null;
    }
    
    document.getElementById('edit-section-editor').innerHTML = '';
}

// Close add section modal
function closeAddSectionModal() {
    document.getElementById('add-section-modal').style.display = 'none';
    window.currentAfterSectionId = null;
    
    // Clean up Summernote editor
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

// Close modal when clicking outside of it
window.onclick = function(event) {
    const editModal = document.getElementById('edit-section-modal');
    const addModal = document.getElementById('add-section-modal');
    
    if (event.target === editModal) {
        closeEditSectionModal();
    }
    if (event.target === addModal) {
        closeAddSectionModal();
    }
}

// Initialize proficiency levels for all sections
function initializeProficiencyLevels(sections) {
    sections.forEach(section => {
        const selectEl = document.getElementById('proficiency-' + section.id);
        const titleEl = document.getElementById('section-title-' + section.id);
        const iconEl = document.getElementById('section-icon-' + section.id);
        
        if (selectEl) {
            // Set the correct value
            selectEl.value = section.proficiency_level;
            
            // Update dropdown styling based on current value
            selectEl.classList.remove('proficiency-level-1', 'proficiency-level-2', 'proficiency-level-3');
            selectEl.classList.add('proficiency-level-' + section.proficiency_level);
        }
        
        if (titleEl) {
            // Ensure title has correct proficiency class
            titleEl.classList.remove('proficiency-1', 'proficiency-2', 'proficiency-3');
            titleEl.classList.add('proficiency-' + section.proficiency_level);
        }
        
        if (iconEl) {
            // Ensure icon has correct proficiency class
            iconEl.classList.remove('proficiency-1', 'proficiency-2', 'proficiency-3');
            iconEl.classList.add('proficiency-' + section.proficiency_level);
        }
        
        console.log('Initialized section', section.id, 'with proficiency level', section.proficiency_level);
    });
}

// Initialize Summernote editor for editing sections
function initEditSectionEditor(content) {
    // Clean up any existing editor first
    if (editModalEditorInstance) {
        try {
            $('#summernote-edit-editor').summernote('destroy');
        } catch (e) {
            console.log('Previous edit editor cleanup completed');
        }
    }
    
    // Create editor container
    const editorContainer = document.getElementById('edit-section-editor');
    editorContainer.innerHTML = '<div id="summernote-edit-editor"></div>';
    
    // Initialize Summernote
    $('#summernote-edit-editor').summernote({
        height: 400,
        minHeight: 300,
        maxHeight: 600,
        focus: false,
        toolbar: [
            ['style', ['style']],
            ['font', ['bold', 'underline', 'clear']],
            ['fontname', ['fontname']],
            ['color', ['color']],
            ['para', ['ul', 'ol', 'paragraph']],
            ['table', ['table']],
            ['insert', ['link', 'picture', 'video']],
            ['view', ['fullscreen', 'codeview', 'help']]
        ],
        callbacks: {
            onImageUpload: function(files) {
                for (let i = 0; i < files.length; i++) {
                    uploadImage(files[i], '#summernote-edit-editor');
                }
            }
        }
    });
    
    // Set content
    $('#summernote-edit-editor').summernote('code', content || '');
    editModalEditorInstance = true;
}

// Initialize Summernote editor for adding sections
function initAddSectionEditor() {
    // Clean up any existing editor first
    if (addModalEditorInstance) {
        try {
            $('#summernote-add-editor').summernote('destroy');
        } catch (e) {
            console.log('Previous add editor cleanup completed');
        }
    }
    
    // Create editor container
    const editorContainer = document.getElementById('add-section-editor');
    editorContainer.innerHTML = '<div id="summernote-add-editor"></div>';
    
    // Initialize Summernote
    $('#summernote-add-editor').summernote({
        height: 400,
        minHeight: 300,
        maxHeight: 600,
        focus: true,
        toolbar: [
            ['style', ['style']],
            ['font', ['bold', 'underline', 'clear']],
            ['fontname', ['fontname']],
            ['color', ['color']],
            ['para', ['ul', 'ol', 'paragraph']],
            ['table', ['table']],
            ['insert', ['link', 'picture', 'video']],
            ['view', ['fullscreen', 'codeview', 'help']]
        ],
        callbacks: {
            onImageUpload: function(files) {
                for (let i = 0; i < files.length; i++) {
                    uploadImage(files[i], '#summernote-add-editor');
                }
            }
        }
    });
    
    addModalEditorInstance = true;
}

// Image upload function for Summernote
function uploadImage(file, editorId) {
    const formData = new FormData();
    formData.append('image', file);
    
    fetch('/upload_image/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCSRFToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            $(editorId).summernote('insertImage', data.url);
        } else {
            console.error('Image upload failed:', data.error);
        }
    })
    .catch(error => {
        console.error('Image upload error:', error);
    });
}