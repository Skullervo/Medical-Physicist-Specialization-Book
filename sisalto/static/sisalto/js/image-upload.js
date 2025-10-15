// Custom image upload functionality for CKEditor
document.addEventListener('DOMContentLoaded', function() {
    
    // Add image upload button to each CKEditor area
    function addImageUploadButton(editorElement) {
        // Create upload container
        const uploadContainer = document.createElement('div');
        uploadContainer.className = 'image-upload-container';
        uploadContainer.style.cssText = `
            margin: 10px 0;
            padding: 10px;
            border: 2px dashed #555;
            border-radius: 8px;
            background: #2a2a2a;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
        `;
        
        // Create file input
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.accept = 'image/*';
        fileInput.style.display = 'none';
        
        // Create upload button
        const uploadButton = document.createElement('button');
        uploadButton.type = 'button';
        uploadButton.className = 'image-upload-btn';
        uploadButton.innerHTML = '<i class="fas fa-image"></i> Lisää kuva';
        uploadButton.style.cssText = `
            background: #4a90e2;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            margin: 5px;
            font-size: 14px;
        `;
        
        // Create drag & drop area
        const dropArea = document.createElement('div');
        dropArea.innerHTML = `
            <div style="padding: 20px; color: #ccc;">
                <i class="fas fa-cloud-upload-alt" style="font-size: 2em; margin-bottom: 10px;"></i><br>
                Vedä kuva tähän tai klikkaa lisätäksesi
            </div>
        `;
        
        uploadContainer.appendChild(uploadButton);
        uploadContainer.appendChild(dropArea);
        uploadContainer.appendChild(fileInput);
        
        // Insert before editor
        editorElement.parentNode.insertBefore(uploadContainer, editorElement);
        
        // Handle button click
        uploadButton.addEventListener('click', function() {
            fileInput.click();
        });
        
        // Handle area click
        uploadContainer.addEventListener('click', function(e) {
            if (e.target === uploadContainer || e.target === dropArea || e.target.parentNode === dropArea) {
                fileInput.click();
            }
        });
        
        // Handle file selection
        fileInput.addEventListener('change', function(e) {
            if (e.target.files && e.target.files[0]) {
                uploadImage(e.target.files[0], editorElement);
            }
        });
        
        // Handle drag & drop
        uploadContainer.addEventListener('dragover', function(e) {
            e.preventDefault();
            uploadContainer.style.borderColor = '#4a90e2';
            uploadContainer.style.backgroundColor = '#333';
        });
        
        uploadContainer.addEventListener('dragleave', function(e) {
            e.preventDefault();
            uploadContainer.style.borderColor = '#555';
            uploadContainer.style.backgroundColor = '#2a2a2a';
        });
        
        uploadContainer.addEventListener('drop', function(e) {
            e.preventDefault();
            uploadContainer.style.borderColor = '#555';
            uploadContainer.style.backgroundColor = '#2a2a2a';
            
            if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                uploadImage(e.dataTransfer.files[0], editorElement);
            }
        });
    }
    
    // Upload image function
    function uploadImage(file, editorElement) {
        // Validate file type
        if (!file.type.startsWith('image/')) {
            alert('Vain kuvatiedostot ovat sallittuja!');
            return;
        }
        
        // Validate file size (5MB max)
        if (file.size > 5 * 1024 * 1024) {
            alert('Tiedosto on liian suuri! Maksimikoko on 5MB.');
            return;
        }
        
        // Show loading
        const loadingMsg = document.createElement('div');
        loadingMsg.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Ladataan kuvaa...';
        loadingMsg.style.cssText = 'color: #4a90e2; margin: 10px 0;';
        editorElement.parentNode.insertBefore(loadingMsg, editorElement);
        
        // Create FormData
        const formData = new FormData();
        formData.append('upload', file);
        
        // Get CSRF token
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        // Upload to server
        fetch('/upload-image/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            loadingMsg.remove();
            
            if (data.url) {
                // Get the editor instance
                const editorId = editorElement.id;
                const editor = window[editorId + 'Editor'];
                
                if (editor) {
                    // Insert image into CKEditor
                    const imageHtml = `<img src="${data.url}" alt="Kuva" style="max-width: 100%; height: auto;">`;
                    editor.model.change(writer => {
                        const viewFragment = editor.data.processor.toView(imageHtml);
                        const modelFragment = editor.data.toModel(viewFragment);
                        editor.model.insertContent(modelFragment);
                    });
                } else {
                    // Fallback: insert at cursor position
                    const imageHtml = `<img src="${data.url}" alt="Kuva" style="max-width: 100%; height: auto;"><br>`;
                    if (editorElement.contentEditable === 'true') {
                        document.execCommand('insertHTML', false, imageHtml);
                    }
                }
                
                alert('Kuva lisätty onnistuneesti!');
            } else {
                alert('Virhe: ' + (data.error ? data.error.message : 'Tuntematon virhe'));
            }
        })
        .catch(error => {
            loadingMsg.remove();
            console.error('Upload error:', error);
            alert('Virhe ladatessa kuvaa: ' + error.message);
        });
    }
    
    // Initialize upload buttons for existing editors
    setTimeout(function() {
        const editorElements = document.querySelectorAll('.ckeditor, #natiivikuvantaminen-editor, #section-editor');
        editorElements.forEach(function(element) {
            if (element && !element.parentNode.querySelector('.image-upload-container')) {
                addImageUploadButton(element);
            }
        });
    }, 1000); // Wait for CKEditor to initialize
});