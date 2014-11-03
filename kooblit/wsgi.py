"""
WSGI config for kooblit project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os
import djcelery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kooblit.settings")
djcelery.setup_loader()

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
