import os
from project.settings import *  # noqa


STATIC_URL = '/borkle/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'borkle/static')
