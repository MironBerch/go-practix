from os import environ
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = environ.get('SECRET_KEY')

DEBUG = environ.get('DEBUG') == 'True'

ALLOWED_HOSTS = environ.get('ALLOWED_HOSTS', '*').split(',')


# Application definition

INSTALLED_APPS = [  # noqa: WPS407
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # django 3rd party
    'django_filters',
    # local
    'movies.apps.MoviesConfig',
]

MIDDLEWARE = [  # noqa: WPS407
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [  # noqa: WPS407
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

WSGI_APPLICATION = 'config.wsgi.application'


# Database

DATABASES = {  # noqa: WPS407
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': environ.get('DB_NAME'),
        'USER': environ.get('DB_USER'),
        'PASSWORD': environ.get('DB_PASSWORD'),
        'HOST': environ.get('DB_HOST'),
        'PORT': environ.get('DB_PORT'),
    },
}


# Password validation

AUTH_PASSWORD_VALIDATORS = [  # noqa: WPS407
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


# Internationalization

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'

# Media files

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# Default primary key field type

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Elasticsearch

ELASTICSEARCH_HOST = environ.get('ELASTIC_HOST', 'elastic')
ELASTICSEARCH_PORT = environ.get('ELASTIC_PORT', '9200')
ELASTICSEARCH_USER = environ.get('ELASTIC_USER', 'elastic')
ELASTICSEARCH_PASSWORD = environ.get('ELASTIC_PASSWORD', '')
ELASTICSEARCH_SETTINGS = {  # noqa: WPS407
    'refresh_interval': '1s',
    'analysis': {
        'filter': {
            'english_stop': {
                'type': 'stop',
                'stopwords': '_english_',
            },
            'english_stemmer': {
                'type': 'stemmer',
                'language': 'english',
            },
            'english_possessive_stemmer': {
                'type': 'stemmer',
                'language': 'possessive_english',
            },
            'russian_stop': {
                'type': 'stop',
                'stopwords': '_russian_',
            },
            'russian_stemmer': {
                'type': 'stemmer',
                'language': 'russian',
            },
        },
        'analyzer': {
            'ru_en': {
                'tokenizer': 'standard',
                'filter': [
                    'lowercase',
                    'english_stop',
                    'english_stemmer',
                    'english_possessive_stemmer',
                    'russian_stop',
                    'russian_stemmer',
                ],
            },
        },
    },
}
ELASTICSEARCH_INDICES = {  # noqa: WPS407
    'movies': {
        'id': {'type': 'keyword'},
        'rating': {'type': 'float'},
        'genres': {'type': 'keyword'},
        'title': {
            'type': 'text',
            'analyzer': 'ru_en',
            'fields': {'raw': {'type': 'keyword'}},
        },
        'description': {'type': 'text', 'analyzer': 'ru_en'},
        'release_date': {'type': 'date'},
        'type': {'type': 'keyword'},
        'age_rating': {'type': 'keyword'},
        'directors_names': {'type': 'text', 'analyzer': 'ru_en'},
        'actors_names': {'type': 'text', 'analyzer': 'ru_en'},
        'writers_names': {'type': 'text', 'analyzer': 'ru_en'},
        'actors': {
            'type': 'nested',
            'dynamic': 'strict',
            'properties': {
                'id': {'type': 'keyword'},
                'name': {'type': 'text', 'analyzer': 'ru_en'},
            },
        },
        'writers': {
            'type': 'nested',
            'dynamic': 'strict',
            'properties': {
                'id': {'type': 'keyword'},
                'name': {'type': 'text', 'analyzer': 'ru_en'},
            },
        },
        'directors': {
            'type': 'nested',
            'dynamic': 'strict',
            'properties': {
                'id': {'type': 'keyword'},
                'name': {'type': 'text', 'analyzer': 'ru_en'},
            },
        },
    },
    'persons': {
        'id': {'type': 'keyword'},
        'full_name': {
            'type': 'text',
            'analyzer': 'ru_en',
            'fields': {'raw': {'type': 'keyword'}},
        },
    },
    'genres': {
        'id': {'type': 'keyword'},
        'name': {
            'type': 'text',
            'analyzer': 'ru_en',
            'fields': {'raw': {'type': 'keyword'}},
        },
        'description': {'type': 'text', 'analyzer': 'ru_en'},
    },
}


# Mongo

MONGO_HOST = environ.get('MONGO_HOST', 'mongo')
MONGO_PORT = int(environ.get('MONGO_PORT', 27017))
MONGO_USERNAME = environ.get('MONGO_USERNAME', None)
MONGO_PASSWORD = environ.get('MONGO_PASSWORD', None)
MONGO_UUID_REPRESENTATION = 'standard'
MONGO_COLLECTION_SCHEMAS = {  # noqa: WPS407
    'users': {
        'bsonType': 'object',
        'required': ['_id', 'bookmarks'],
        'properties': {
            '_id': {'bsonType': 'binData'},
            'bookmarks': {
                'bsonType': 'array',
                'items': {
                    'bsonType': 'object',
                    'required': ['filmwork_id'],
                    'properties': {
                        'filmwork_id': {'bsonType': 'binData'},
                    },
                },
            },
        },
    },
    'filmworks': {
        'bsonType': 'object',
        'required': ['_id', 'rating'],
        'properties': {
            '_id': {'bsonType': 'binData'},
            'rating': {
                'bsonType': 'object',
                'required': ['votes'],
                'properties': {
                    'votes': {
                        'bsonType': 'array',
                        'items': {
                            'bsonType': 'object',
                            'required': ['user_id', 'score'],
                            'properties': {
                                'user_id': {'bsonType': 'binData'},
                                'score': {'bsonType': 'number'},
                            },
                        },
                    },
                },
            },
        },
    },
    'reviews': {
        'bsonType': 'object',
        'required': ['_id', 'rating'],
        'properties': {
            '_id': {'bsonType': 'binData'},
            'author_id': {'bsonType': 'binData'},
            'filmwork_id': {'bsonType': 'binData'},
            'pub_date': {'bsonType': 'date'},
            'rating': {
                'bsonType': 'object',
                'required': ['votes'],
                'properties': {
                    'votes': {
                        'bsonType': 'array',
                        'items': {
                            'bsonType': 'object',
                            'required': ['user_id', 'score'],
                            'properties': {
                                'user_id': {'bsonType': 'binData'},
                                'score': {'bsonType': 'number'},
                            },
                        },
                    },
                },
            },
        },
    },
}
