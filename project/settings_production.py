import os
from project.settings import *  # noqa

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ['DATABASE_NAME'],
        'USER': os.environ['DATABASE_USER'],
        'PASSWORD': os.environ['DATABASE_PASSWORD'],
        'HOST': os.environ['DATABASE_HOST'],
        'PORT': '5432'
    }
}

ALLOWED_HOSTS = ['borkle-game.herokuapp.com', 'herokuapp.com', 'www.borkle.app']

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

ENVIRONMENT = 'prod'

HOST = 'https://www.borkle.app'

SENDGRID_API_KEY = os.environ['SENDGRID_API_KEY']
