// Yleinen CKEditor alustus kaikille sivuille
window.addEventListener('DOMContentLoaded', function() {
  
  // Yleinen CKEditor konfiguraatio  
  function getEditorConfig() {
    return {
      toolbar: [
        'heading', '|', 'bold', 'italic', 'underline', 'strikethrough', 'fontColor', 'fontBackgroundColor', 'fontSize',
        '|', 'bulletedList', 'numberedList', 'blockQuote', '|', 'insertTable', 'link', 'mediaEmbed', '|', 'undo', 'redo'
      ],
      heading: {
        options: [
          { model: 'paragraph', title: 'Normaali', class: 'ck-heading_paragraph' },
          { model: 'heading1', view: 'h1', title: 'Otsikko 1', class: 'ck-heading_heading1' },
          { model: 'heading2', view: 'h2', title: 'Otsikko 2', class: 'ck-heading_heading2' },
          { model: 'heading3', view: 'h3', title: 'Otsikko 3', class: 'ck-heading_heading3' }
        ]
      },
      image: {
        toolbar: [ 'imageTextAlternative', 'imageStyle:inline', 'imageStyle:block', 'imageStyle:side' ]
      },
      mediaEmbed: {
        previewsInData: true,
        providers: [
          // YouTube
          {
            name: 'youtube',
            url: /^youtube\.com\/watch\?v=([\w-]+)/,
            html: match => `<iframe width="560" height="315" src="https://www.youtube-nocookie.com/embed/${match[1]}" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>`
          },
          // Vimeo  
          {
            name: 'vimeo',
            url: /^vimeo\.com\/(\d+)/,
            html: match => `<iframe width="560" height="315" src="https://player.vimeo.com/video/${match[1]}" frameborder="0" allowfullscreen></iframe>`
          }
        ]
      }
    };
  }

  // Tallenna globaalisti
  window.getEditorConfig = getEditorConfig;

  // Alusta CKEditor kaikille .ckeditor-luokan elementeille
  const editorElements = document.querySelectorAll('.ckeditor, #natiivikuvantaminen-editor, #section-editor');
  
  editorElements.forEach(function(element) {
    if (element && !element.hasAttribute('data-ckeditor-initialized')) {
      console.log('Initializing CKEditor for element:', element.id || element.className);
      
      // Käytä DecoupledEditor
      DecoupledEditor
        .create(element, getEditorConfig())
        .then(editor => {
          // Liitä toolbar editorin yläpuolelle
          const toolbarContainer = document.createElement('div');
          toolbarContainer.className = 'ck-toolbar-container';
          element.parentNode.insertBefore(toolbarContainer, element);
          toolbarContainer.appendChild(editor.ui.view.toolbar.element);
          
          element.setAttribute('data-ckeditor-initialized', 'true');
          console.log('CKEditor initialized successfully for:', element.id || element.className);
          
          // Add custom image button
          if (typeof addCustomImageButton === 'function') {
            addCustomImageButton(editor);
          } else {
            // Fallback: add simple image button directly
            setTimeout(() => {
              editor.ui.componentFactory.add('customImageButton', locale => {
                const button = new editor.ui.ButtonView(locale);
                button.set({
                  label: 'Lisää kuva',
                  icon: '<svg viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><rect x="2" y="3" width="16" height="12" stroke="currentColor" stroke-width="1" fill="none" rx="2"/><path stroke="currentColor" stroke-width="1" fill="none" d="m10.5 8.5-2 3-1.5-1.5-3 4h12l-5.5-5.5z"/><circle cx="6.5" cy="7.5" r="1.5" stroke="none" fill="currentColor"/></svg>',
                  tooltip: true
                });
                button.on('execute', () => {
                  const imageUrl = prompt('Anna kuvan URL-osoite:', 'https://');
                  if (imageUrl && imageUrl !== 'https://') {
                    editor.model.change(writer => {
                      const imageElement = writer.createElement('imageBlock', { src: imageUrl });
                      editor.model.insertContent(imageElement, editor.model.document.selection);
                    });
                  }
                });
                return button;
              });
              const toolbar = editor.ui.view.toolbar;
              toolbar.items.add(editor.ui.componentFactory.create('customImageButton'));
            }, 100);
          }
          
          // Tallenna editor globaalisti id:n perusteella
          if (element.id) {
            window[element.id + 'Editor'] = editor;
            
            // Erityinen alias section-editorille
            if (element.id === 'section-editor') {
              window.mainEditorInstance = editor;
              console.log('Set mainEditorInstance alias for section-editor');
            }
          }
        })
        .catch(error => {
          console.error('CKEditor initialization failed:', error);
          // Fallback tavalliseen textarea:aan
          element.outerHTML = '<textarea name="' + (element.name || 'content') + '" style="width:100%; height:200px; padding:10px;" placeholder="Kirjoita sisältö tähän...">' + element.innerHTML + '</textarea>';
        });
    }
  });
});
