#!/usr/bin/env python
# This file is part of django-url-sso.
#
# django-url-sso: Generate login URL's for unstandardized SSO systems.
# Copyright (C) 2014 Mathijs de Bruin
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3'
    }
}

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.auth',
    'url_sso'
]

try:
    # If available, South is required by setuptest
    import south
    INSTALLED_APPS.append('south')
except ImportError:
    # South not installed and hence is not required
    pass

ROOT_URLCONF = 'test_urls'

SITE_ID = 1

TEMPLATE_DIRS = ('test_templates', )

# Enable time-zone support for Django 1.4 (ignored in older versions)
USE_TZ = True

# Required for django-webtest to work
STATIC_URL = '/static/'
