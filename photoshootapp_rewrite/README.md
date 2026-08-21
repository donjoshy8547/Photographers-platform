# Photoshoot App - Rewritten

A professional Django-based platform connecting photographers with clients, featuring AI-powered photo management and an e-commerce store.

## 🏗️ Architecture

This is a complete rewrite of the original monolithic application into a clean, modular Django project following best practices:

### Apps Structure
- **accounts** - User authentication, profiles (Photographer, Client, Assistant)
- **events** - Event management, bookings, galleries
- **media_library** - Photo uploads, tagging, downloads
- **ai_engine** - AI processing (face detection, object recognition)
- **store** - E-commerce for camera equipment
- **core** - Shared utilities, mixins, decorators

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- PostgreSQL (recommended) or SQLite

### Installation

```bash
# Clone the repository
cd photoshootapp_rewrite

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your settings

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

Visit `http://localhost:8000/admin` to access the admin panel.

## 📁 Project Structure

```
photoshootapp_rewrite/
├── photoshootapp/          # Project configuration
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── accounts/           # User management
│   ├── events/             # Events & bookings
│   ├── media_library/      # Photos & galleries
│   ├── ai_engine/          # AI processing
│   ├── store/              # E-commerce
│   └── core/               # Shared utilities
├── templates/              # Global templates
├── static/                 # Global static files
├── media/                  # User uploads
└── manage.py
```

## 🔑 Features

### User Roles
- **Admin** - Full system access
- **Photographer** - Manage events, upload photos, run store
- **Client** - Book events, view/download photos, shop
- **Assistant** - Help photographers with photo management

### Core Features
- Event management with booking system
- Photo gallery with AI auto-tagging
- Face recognition for personalized photo finding
- Bulk photo download requests
- E-commerce store for equipment
- Role-based access control

## 🔒 Security

- Environment variables for sensitive data
- Argon2 password hashing
- CSRF protection
- SQL injection prevention via ORM
- Role-based permissions

## 🤖 AI Features

The AI engine supports:
- Face detection and recognition
- Object detection in photos
- Scene analysis
- Automatic tagging

To enable AI features, uncomment the ML libraries in `requirements.txt`.

## 🧪 Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=apps
```

## 📝 License

MIT License

## 👥 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request
