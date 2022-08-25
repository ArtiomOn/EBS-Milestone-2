import os
from datetime import timedelta

from dotenv import load_dotenv
from django.utils.translation import gettext_lazy as _

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = os.getenv('SECRET_KEY')

DEBUG = os.getenv('DEBUG')

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'drf_yasg',
    'django_nose',
    'django_extensions',
    'django_filters',
    'debug_toolbar',
    'django_celery_beat',
    'django_celery_results',
    'wkhtmltopdf',
    'guardian',

    'apps.common',
    'apps.tasks',
    'apps.users',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.common.middlewares.ApiMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'libraries': {
                'staticfiles': 'django.templatetags.static',
            }
        },
    },
]

AUTH_USER_MODEL = 'users.CustomUser'

DEBUG_TOOLBAR_PATCH_SETTINGS = False

WSGI_APPLICATION = 'config.wsgi.application'

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': os.getenv('NAME'),
#         'USER': os.getenv('USER'),
#         'PASSWORD': os.getenv('PASSWORD'),
#         'HOST': os.getenv('HOST'),
#         'PORT': os.getenv('PORT'),
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

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

LANGUAGE_CODE = 'en-US'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = False

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/files/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/files/')

DATE_FORMAT = "%Y-%m-%d %H:%m"

DEFAULT_LANG = "ro"

LANGUAGES = [
    (DEFAULT_LANG, _('Romanian')),
    ('ru', _('Russian')),
    ('en', _('English')),
]

DICT_LANG = {}

for lang_key, lang_name in LANGUAGES:
    DICT_LANG[lang_key] = None

LOCALE_PATHS = (
    BASE_DIR + '/locales',
)

FIXTURE_DIRS = (
    'fixtures/',
)

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_HEADERS = (
    'accept',
    'accept-encoding',
    'Currency',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'token',
    'cache-control'
)

REST_FRAMEWORK = {
    'DATETIME_FORMAT': "%Y-%m-%dT%H:%M:%SZ",
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'EXCEPTION_HANDLER': 'apps.common.exceptions.custom_exception_handler',
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'guardian.backends.ObjectPermissionBackend',
)

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'apiKey': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    }
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=7),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
}

WSGI_AUTO_RELOAD = True

DEBUG_LEVEL = "INFO"

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

INTERNAL_IPS = ("127.0.0.1", "172.17.0.1")

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'

NOSE_ARGS = [
    '--with-coverage',
    '--cover-package=' + ','.join([app + '.views' for app in INSTALLED_APPS if app.startswith('apps.')]),
]

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = True
EMAIL_PORT = 587
RECIPIENT_LIST = os.getenv('RECIPIENT_LIST')

CELERY_BROKER_URL = 'pyamqp://guest@localhost//'
CELERY_ALWAYS_EAGER = True
CELERY_RESULT_BACKEND = 'django-db'

WKHTMLTOPDF_CMD_OPTIONS = {
    'quiet': True,
}

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)
