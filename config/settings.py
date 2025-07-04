import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-t(b31l=zkykdz+dgem&_*1f=(9!7woo8yc$pc2)1v8pc0h1wlj'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [

    # [SENU]: apps
    'Student',
    'Level',
    'Course',
    'classroom',

    # to show urls
    'django_extensions',

    # [HAM]
    "jazzmin",

    # default
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators
# [SENU]: Corrected IndentationError by removing erroneous 'Messrs' prefix
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

JAZZMIN_SETTINGS = {

    "site_title": "Admin Dashboard",
    "site_header": "config Admin",
    "site_brand": "config",
    "site_logo": "images/logo.png",  
    "login_logo": "images/logo.png",
    "welcome_sign": "Welcome to your config Dashboard",
    "copyright": "© 2025 Ahmed",
    "search_model": ["Student.Student", "Course.Course"],

    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    "custom_css": "css/custom.css",
    # [SENU]: Add custom link to reception page and Font Awesome for sidebar icon
    "custom_links": {
        "classroom": [
            {
                "name": "Reception Page",
                "url": "classrooms:reception_page",
                "icon": "fas fa-camera",
                "permissions": ["auth.view_user"],
            },
            # [SENU]: Placeholder for additional custom page (uncomment and configure if needed)
            # {
            #     "name": "Another Page",
            #     "url": "classrooms:another_page",
            #     "icon": "fas fa-book",
            #     "permissions": ["auth.view_user"],
            # }
        ]
    },
    "extra_css": [
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css"
    ]
}


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'




# [SENU]: HANDLE IMAGE STORE
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# [SENU]: SYNC TIMINIG IN ADMIN
TIME_ZONE = 'Africa/Cairo'
USE_TZ = True

################################# [AMS] EMAIL SETTING #####
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com' 
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'amhmdslah104@gmail.com'  
EMAIL_HOST_PASSWORD = 'qgsy guda swgz vckf' 
###########################################################