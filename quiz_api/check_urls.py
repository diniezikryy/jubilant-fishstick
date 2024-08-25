# Save this as check_urls.py in your project root

import os
import sys

# Add your project to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "quiz_api.settings")

import django
django.setup()

from django.urls import get_resolver
from django.core.management import call_command

def print_urls(urlpatterns, prefix=''):
    for pattern in urlpatterns:
        if hasattr(pattern, 'url_patterns'):
            print_urls(pattern.url_patterns, prefix + pattern.pattern.regex.pattern)
        else:
            print(prefix + pattern.pattern.regex.pattern, pattern.callback)

resolver = get_resolver()
print_urls(resolver.url_patterns)