# Medical Physicist Specialization Book

A Django-based web application for medical physicist specialization training and EPA (Entrustable Professional Activities) management.

## Features

### 📚 EPA Management System
- **Radiologia** - Medical imaging specialization areas
- **Sädehoito** - Radiation therapy training modules  
- **Isotooppi** - Nuclear medicine content
- **KNF** - Clinical neurophysiology
- **Fysiologia** - Medical physiology

### ✨ Core Functionality
- **Rich Text Editor** - CKEditor 5 with mathematical formula support (MathJax)
- **Proficiency Levels** - 1-3 scale tracking for each EPA area
- **Responsive Design** - Mobile-friendly interface with sidebar navigation
- **Table of Contents** - Dynamic navigation for long content pages
- **Exam Questions** - Practice question system with randomization

### 🎯 Key Technical Features
- **Responsive Sidebar Toggle** - ChatGPT-style collapsible navigation
- **MathJax Integration** - Support for mathematical formulas ($\\LaTeX$ syntax)
- **Content Management** - Add, edit, delete sections dynamically
- **Dark Theme** - Professional dark UI design
- **Database Persistence** - PostgreSQL backend for reliable data storage

## Technology Stack

- **Backend**: Django 5.2.6 with PostgreSQL
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Editor**: CKEditor 5 with MathJax integration
- **Styling**: Custom CSS with responsive design
- **Icons**: FontAwesome for UI elements

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Skullervo/Medical-Physicist-Specialization-Book.git
cd Medical-Physicist-Specialization-Book
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up database:
```bash
python manage.py migrate
```

5. Create superuser:
```bash
python manage.py createsuperuser
```

6. Run development server:
```bash
python manage.py runserver
```

Visit `http://localhost:8000` to access the application.

## Project Structure

```
├── sisalto/                    # Main Django app
│   ├── models.py              # Database models (EPA, Section, etc.)
│   ├── views.py               # View functions for all EPA areas
│   ├── urls.py                # URL routing
│   ├── admin.py               # Django admin configuration
│   ├── templates/sisalto/     # HTML templates
│   └── static/sisalto/        # CSS, JS, and static assets
├── sivusto/                   # Django project settings
├── manage.py                  # Django management script
└── requirements.txt           # Python dependencies
```

## Recent Updates

### Version 2.0 Features
- ✅ **Responsive Sidebar Toggle** - Works on all screen sizes
- ✅ **Table of Contents** - Dynamic navigation for content pages  
- ✅ **Proficiency Dropdowns** - Implemented across all Sädehoito EPA pages
- ✅ **Enhanced CKEditor** - Unified configuration across all pages
- ✅ **Mobile Optimization** - Improved mobile user experience

### EPA Areas Coverage
- **Radiologia**: 6 specialized areas (CT, MRI, Mammography, etc.)
- **Sädehoito**: 7 areas with proficiency tracking
- **Other specialties**: KNF, Isotooppi, Fysiologia with content management

## Contributing

This is an educational project for medical physicist specialization training. Contributions are welcome for:

- Additional EPA content areas
- UI/UX improvements  
- Mobile responsiveness enhancements
- Accessibility features
- Content management improvements

## License

This project is intended for educational use in medical physics training.

## Development Roadmap

### Upcoming Features
- [ ] **Image Upload Support** - CKEditor custom build with image handling
- [ ] **Advanced Search** - Content search across all EPA areas
- [ ] **Progress Tracking** - Visual progress indicators
- [ ] **Export Functionality** - PDF generation for study materials
- [ ] **User Authentication** - Multi-user support with progress tracking

## Contact

For questions about medical physics specialization content or technical implementation, please open an issue in the GitHub repository.