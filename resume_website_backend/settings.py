# resume_website_backend/settings.py
import os
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent
DEBUG = config('DEBUG', default=False, cast=bool)
SECRET_KEY = config('SECRET_KEY')
GEMINI_API_KEY = config('GEMINI_API_KEY')

ALLOWED_HOSTS = [
    'resume-website-backend-40i7.onrender.com',
    'localhost',
    '127.0.0.1',
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'resume_website_backend.chat',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# TEMPLATES configuration
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

ROOT_URLCONF = 'resume_website_backend.urls'

# Use SQLite locally
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
# else:
#     # Production (e.g. Postgres via DATABASE_URL)
#     import dj_database_url
#     DATABASES = {
#         'default': dj_database_url.parse(config('DATABASE_URL'))
#     }

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# CORS settings
if DEBUG:
    # Development - allow localhost and your GitHub Pages
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:3000",             # React dev server
        "http://127.0.0.1:3000",             # Alternative localhost
        "http://localhost:8000",             # If you're serving frontend on 8000
        "http://127.0.0.1:8000",             # Alternative
        "https://azizjonkasimov.github.io",  # Your GitHub Pages
        "http://localhost:5173",             # Vite dev server
    ]
else:
    # Production - only allow your GitHub Pages
    CORS_ALLOWED_ORIGINS = [
        "https://azizjonkasimov.github.io",
    ]