// NEW SIMPLIFIED IMAGE SCALING FOR CKEDITOR
console.log('🚀 NEW IMAGE SCALING MODULE LOADED');

function scaleNewImages(editor) {
    console.log('🔍 Scaling new images in editor...');
    
    const editorElement = editor.ui.getEditableElement();
    if (!editorElement) {
        console.log('❌ No editor element found');
        return;
    }
    
    const images = editorElement.querySelectorAll('img:not(.scaled)');
    console.log(`📸 Found ${images.length} unscaled images`);
    
    images.forEach((img, index) => {
        console.log(`Processing image ${index + 1}: ${img.src}`);
        
        const scaleImage = () => {
            if (!img.naturalWidth || !img.naturalHeight) {
                console.log('❌ No natural dimensions available');
                return;
            }
            
            const original = {
                width: img.naturalWidth,
                height: img.naturalHeight
            };
            
            console.log(`📏 Original: ${original.width}x${original.height}`);
            
            // Only scale down extremely large images
            let newWidth = original.width;
            
            // Only intervene if image is ridiculously large
            if (original.width > 800) {
                newWidth = 400; // Scale down very large images
            } else if (original.width > 600) {
                newWidth = 300; // Scale down large images
            } else {
                // Leave smaller images as they are
                console.log('📏 Image is reasonable size, no scaling needed');
                img.classList.add('scaled'); // Mark as processed but don't resize
                return;
            }
            
            const aspectRatio = original.width / original.height;
            const newHeight = Math.round(newWidth / aspectRatio);
            
            console.log(`🎯 Target size: ${newWidth}x${newHeight}`);
            
            // Try CKEditor's resize command first
            if (tryImageResize(img, editor, newWidth)) {
                console.log('✅ Resized via CKEditor API');
            } else {
                console.log('🎨 Using CSS fallback');
                // CSS fallback
                img.style.maxWidth = newWidth + 'px';
                img.style.width = newWidth + 'px';
                img.style.height = 'auto';
                
                // Force parent figure to be small too
                const figure = img.closest('figure');
                if (figure) {
                    figure.style.maxWidth = newWidth + 'px';
                    figure.style.width = newWidth + 'px';
                }
            }
            
            // Mark as processed
            img.classList.add('scaled', 'small-image');
            img.dataset.originalSize = `${original.width}x${original.height}`;
            img.dataset.scaledSize = `${newWidth}x${newHeight}`;
            
            console.log(`✅ SCALED: ${original.width}x${original.height} → ${newWidth}x${newHeight}`);
        };
        
        if (img.complete && img.naturalWidth > 0) {
            scaleImage();
        } else {
            img.onload = scaleImage;
        }
    });
}

function tryImageResize(img, editor, targetWidth) {
    try {
        // Try to find the image element in CKEditor's model
        const modelDoc = editor.model.document;
        const modelRoot = modelDoc.getRoot();
        
        // Look for image elements in the model
        for (const child of modelRoot.getChildren()) {
            if (child.name === 'imageBlock') {
                const imageSrc = child.getAttribute('src');
                if (imageSrc && img.src.includes(imageSrc.split('/').pop())) {
                    // Found matching image, try to resize it
                    editor.model.change(writer => {
                        writer.setAttribute('resizedWidth', targetWidth + 'px', child);
                    });
                    return true;
                }
            }
        }
        
        return false;
    } catch (error) {
        console.log('❌ CKEditor resize failed:', error);
        return false;
    }
}

// Export to global scope
window.scaleNewImages = scaleNewImages;
window.tryImageResize = tryImageResize;

console.log('✅ NEW IMAGE SCALING MODULE READY');