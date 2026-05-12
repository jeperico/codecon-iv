from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = 'django-insecure-#kk71on!dn3=#h&-ecn-tgih0r#_n@t7=bb$l18s)j-7t2@v@n'
DEBUG = True

CORS_ALLOWED_ORIGINS = config(
    "DJANGO_CORS_ALLOWED_ORIGINS", default="", cast=lambda v: [s.strip() for s in v.split(",")]
)
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    # "rest_framework_simplejwt",
    # "rest_framework_simplejwt.token_blacklist",
    "cuser",
    'corsheaders',
    'drf_spectacular',
    'apps.profiles',
]

AUTH_USER_MODEL = 'profiles.User'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
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

WSGI_APPLICATION = 'app.wsgi.application'

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('POSTGRES_DB'),
        'USER': config('POSTGRES_USER'),
        'HOST': 'localhost',
        'PORT': 5432,
        'PASSWORD': config('POSTGRES_PASSWORD')
    }
}

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
]

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

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SPECTACULAR_SETTINGS = {
    'TITLE': 'Django Template API',
    'DESCRIPTION': 'API documentation for the Django Template project',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'defaultModelRendering': 'model',
        'defaultModelsExpandDepth': 2,
        'defaultModelExpandDepth': 2,
        'docExpansion': 'none',
        'filter': True,
        'showExtensions': True,
        'showCommonExtensions': True,
    },
    'REDOC_UI_SETTINGS': {
        'expandResponses': '200,201',
        'hideDownloadButton': False,
        'hideHostname': False,
        'requiredPropsFirst': True,
        'sortPropsAlphabetically': True,
    },
}

JAZZMIN_SETTINGS = {
    "site_title": "Django Template",
    "site_header": "Django Template",
    "site_brand": "Django Template",
    "login_logo_dark": None,
    "site_logo_classes": None,
    "welcome_sign": "Welcome to Django Template",
    "copyright": "Django Template Ltd",
    "user_avatar": None,
    "topmenu_links": [
        {"app": "profiles"},
    ],
    "usermenu_links": [{"model": "auth.user"}],
    "show_sidebar": True,
    "navigation_expanded": False,
    "order_with_respect_to": [
        "profiles",
        # "reports.report",
        # "reports.typeofoccurrence",
        # "reports.signsandsymptoms",
        # "reports.subsignsandsymptoms",
        # "reports.subsubsignsandsymptoms",
        "auth",
        "auth.user",
        "auth.group",
    ],
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "profiles": "fas fa-cogs",
        "reports.report": "fas fa-file-alt",
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    "related_modal_active": False,
    "use_google_fonts_cdn": True,
    "show_ui_builder": True,
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {
        "auth.user": "collapsible",
        "auth.group": "vertical_tabs",
    },
    "language_chooser": False,
}
