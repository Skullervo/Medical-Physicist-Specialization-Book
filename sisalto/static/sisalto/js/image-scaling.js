// IMAGE SCALING FOR CKEDITOR
// Yksinkertainen kuvan skaalausfunktio

console.log('🚀 IMAGE SCALING MODULE LOADED');

function scaleImageSmall(img, editor) {
    if (!img || !img.naturalWidth || !img.naturalHeight) {
        console.log('❌ Invalid image or no natural dimensions');
        return false;
    }
    
    const original = {
        width: img.naturalWidth,
        height: img.naturalHeight
    };
    
    console.log(`📏 Original size: ${original.width}x${original.height}`);
    
    // Calculate new size (MUCH smaller)
    let newWidth;
    if (original.width > 1000) {
        newWidth = Math.round(original.width / 10); // 10x smaller!
    } else if (original.width > 800) {
        newWidth = Math.round(original.width / 8); // 8x smaller!
    } else if (original.width > 600) {
        newWidth = Math.round(original.width / 6); // 6x smaller!  
    } else if (original.width > 400) {
        newWidth = Math.round(original.width / 4); // 4x smaller!
    } else if (original.width > 200) {
        newWidth = Math.round(original.width / 3); // 3x smaller!
    } else {
        newWidth = Math.round(original.width / 2); // 2x smaller even for small images
    }
    
    // Much stricter limits
    newWidth = Math.min(newWidth, 150); // Max only 150px!
    newWidth = Math.max(newWidth, 80);  // Min 80px
    
    const aspectRatio = original.width / original.height;
    const newHeight = Math.round(newWidth / aspectRatio);
    
    console.log(`🎯 New size: ${newWidth}x${newHeight}`);
    
    // Use CKEditor's imageResize command instead of CSS
    if (editor && editor.commands && editor.commands.get('imageResize')) {
        console.log('🔧 Using CKEditor imageResize command');
        
        try {
            // Find the image model element
            const selection = editor.model.document.selection;
            const imageElement = selection.getSelectedElement();
            
            if (imageElement && imageElement.name === 'imageBlock') {
                console.log('📝 Resizing via CKEditor model');
                editor.model.change(writer => {
                    writer.setAttribute('resizedWidth', newWidth + 'px', imageElement);
                    writer.setAttribute('resizedHeight', newHeight + 'px', imageElement);
                });
            } else {
                // Fallback: find image in DOM and use CKEditor API
                console.log('🔍 Finding image element in editor model');
                const modelImages = Array.from(editor.model.document.getRoot().getChildren())
                    .filter(child => child.name === 'imageBlock');
                
                if (modelImages.length > 0) {
                    const lastImage = modelImages[modelImages.length - 1]; // Assume newest image
                    editor.model.change(writer => {
                        writer.setAttribute('resizedWidth', newWidth + 'px', lastImage);
                        writer.setAttribute('resizedHeight', newHeight + 'px', lastImage);
                    });
                }
            }
        } catch (error) {
            console.log('❌ CKEditor resize failed, using CSS fallback:', error);
            applyCSSResize();
        }
    } else {
        console.log('🎨 Using CSS fallback resize');
        applyCSSResize();
    }
    
    function applyCSSResize() {
        // Fallback CSS method
        img.style.setProperty('width', newWidth + 'px', 'important');
        img.style.setProperty('height', newHeight + 'px', 'important');
        img.setAttribute('width', newWidth);
        img.setAttribute('height', newHeight);
        
        const figure = img.closest('figure');
        if (figure) {
            figure.style.setProperty('width', newWidth + 'px', 'important');
        }
    }
    
    // Mark as processed
    img.dataset.scaled = 'true';
    img.classList.add('auto-scaled');
    
    console.log(`✅ SCALED: ${original.width}x${original.height} → ${newWidth}x${newHeight}`);
    return true;
}

function scaleAllImages(editor) {
    console.log('🔍 Scaling all images in editor...');
    
    if (!editor || !editor.ui || !editor.ui.getEditableElement) {
        console.log('❌ Invalid editor');
        return;
    }
    
    const editorElement = editor.ui.getEditableElement();
    if (!editorElement) {
        console.log('❌ No editor element');
        return;
    }
    
    const images = editorElement.querySelectorAll('img');
    console.log(`📸 Found ${images.length} images to process`);
    
    let scaled = 0;
    images.forEach((img, index) => {
        console.log(`Processing image ${index + 1}: ${img.src}`);
        
        if (img.dataset.scaled === 'true') {
            console.log('⏭️ Already scaled, skipping');
            return;
        }
        
        if (img.complete && img.naturalWidth > 0) {
            if (scaleImageSmall(img, editor)) {
                scaled++;
            }
        } else {
            console.log('⏳ Waiting for image to load...');
            img.onload = function() {
                console.log('✅ Image loaded, scaling now');
                scaleImageSmall(this, editor);
            };
        }
    });
    
    console.log(`📊 Scaled ${scaled}/${images.length} images`);
}

// Export functions to global scope
window.scaleImageSmall = scaleImageSmall;
window.scaleAllImages = scaleAllImages;

console.log('✅ IMAGE SCALING MODULE READY');