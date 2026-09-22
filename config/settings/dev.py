from .base import *  # noqa: F401,F403
from .base import INSTALLED_APPS, MIDDLEWARE

DEBUG = True

INSTALLED_APPS += ["django_browser_reload"]

MIDDLEWARE += ["django_browser_reload.middleware.BrowserReloadMiddleware"]

INTERNAL_IPS = ["127.0.0.1"]
