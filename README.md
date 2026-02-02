Photographers Platform
Overview

The Photographers Platform is a web application built with Django that connects clients and photographers. The platform enables users to register, upload and manage photos, and browse photography content. It supports user authentication, role-based features, photo upload and management, and media handling.

The project uses Django’s built-in ORM, class-based views, and template system to build a maintainable and scalable web application.

Features
User Authentication

User registration

Login and logout

Authenticated access to protected views

Photo Management

Upload photos with metadata (title, description, tags)

View lists of photos with pagination or filters

Show single photo detail pages

Edit and delete own photos

Media Handling

Photo files stored via Django’s media system

Media served during development via MEDIA_URL and MEDIA_ROOT

Tagging System

Tag photos using a tagging library

Filter photos by tag

Technology Stack

Python

Django web framework

Django ORM for database models

Templates with Django’s template language

SQLite (default development database)

Django Taggit for tagging

Bootstrap for UI

Installation
Prerequisites

Python 3.8 or higher

Virtual environment tool (venv, virtualenv)

Setup Steps

Clone the repository:

git clone https://github.com/donjoshy8547/Photographers-platform.git
cd Photographers-platform


Create and activate a virtual environment:

python -m venv venv
source venv/bin/activate   # On Windows use: venv\Scripts\activate


Install dependencies:

pip install -r requirements.txt


Apply database migrations:

python manage.py migrate


Create a superuser:

python manage.py createsuperuser


Run the development server:

python manage.py runserver


Open a browser and visit:

http://localhost:8000

Configuration
Environment Variables

Sensitive settings such as SECRET_KEY and database credentials should be stored in environment variables or a separate settings file for production.

Media Settings (Development)

Configure media storage in settings.py:

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


Update main urls.py to serve media during development:

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    ...
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

Database

The default database is SQLite. For production, configure PostgreSQL or another database engine in settings.

Usage
User Actions

Register a new account

Login and logout

Upload a photo

View all uploaded photos

Edit or delete own photos

Browse photos by tag

Admin Actions

Manage photo objects via Django admin

Review and moderate content

Deployment

To deploy to a production environment:

Configure a production database

Set up static and media file storage

Secure settings (disable debug mode)

Use a WSGI server (Gunicorn, uWSGI)

Use reverse proxy (Nginx)

Configure HTTPS certificates

Refer to Django’s official deployment documentation for details.
