from .base import *  # noqa: F401,F403
from .base import MIDDLEWARE, env

DEBUG = False

MIDDLEWARE = MIDDLEWARE[:1] + [
    "whitenoise.middleware.WhiteNoiseMiddleware",
] + MIDDLEWARE[1:]

STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
