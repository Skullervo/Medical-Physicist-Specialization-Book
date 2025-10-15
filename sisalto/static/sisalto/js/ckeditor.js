// Yleinen CKEditor alustus kaikille sivuille
window.addEventListener('DOMContentLoaded', function() {
  
  // Yleinen CKEditor konfiguraatio
  function getEditorConfig() {
    return {
      toolbar: [
        'heading', '|', 'bold', 'italic', 'underline', 'strikethrough', 'fontColor', 'fontBackgroundColor', 'fontSize',
        '|', 'bulletedList', 'numberedList', 'blockQuote', 'insertTable', 'link', 'mediaEmbed', 'undo', 'redo'
      ],
      heading: {
        options: [
          { model: 'paragraph', title: 'Normaali', class: 'ck-heading_paragraph' },
          { model: 'heading1', view: 'h1', title: 'Otsikko 1', class: 'ck-heading_heading1' },
          { model: 'heading2', view: 'h2', title: 'Otsikko 2', class: 'ck-heading_heading2' },
          { model: 'heading3', view: 'h3', title: 'Otsikko 3', class: 'ck-heading_heading3' }
        ]
      },
      mediaEmbed: {
        previewsInData: true
      }
    };
  }

  // Alusta CKEditor kaikille .ckeditor-luokan elementeille
  const editorElements = document.querySelectorAll('.ckeditor, #natiivikuvantaminen-editor, #section-editor');
  
  editorElements.forEach(function(element) {
    if (element && !element.hasAttribute('data-ckeditor-initialized')) {
      console.log('Initializing CKEditor for element:', element.id || element.className);
      
      ClassicEditor
        .create(element, getEditorConfig())
        .then(editor => {
          element.setAttribute('data-ckeditor-initialized', 'true');
          console.log('CKEditor initialized successfully for:', element.id || element.className);
          
          // Tallenna editor globaalisti id:n perusteella
          if (element.id) {
            window[element.id + 'Editor'] = editor;
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

// Varmista että getEditorConfig on saatavilla globaalisti
if (typeof getEditorConfig === 'undefined') {
  window.getEditorConfig = function() {
    return {
      toolbar: [
        'heading', '|', 'bold', 'italic', 'underline', 'strikethrough', 'fontColor', 'fontBackgroundColor', 'fontSize',
        '|', 'bulletedList', 'numberedList', 'blockQuote', 'insertTable', 'link', 'mediaEmbed', 'undo', 'redo'
      ],
      heading: {
        options: [
          { model: 'paragraph', title: 'Normaali', class: 'ck-heading_paragraph' },
          { model: 'heading1', view: 'h1', title: 'Otsikko 1', class: 'ck-heading_heading1' },
          { model: 'heading2', view: 'h2', title: 'Otsikko 2', class: 'ck-heading_heading2' },
          { model: 'heading3', view: 'h3', title: 'Otsikko 3', class: 'ck-heading_heading3' }
        ]
      },
      mediaEmbed: {
        previewsInData: true
      }
    };
  };
}
