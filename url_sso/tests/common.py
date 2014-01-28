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

from django.test import TestCase
from django.test.utils import override_settings
from django.test.client import RequestFactory

from django.contrib.auth.models import User

from ..context_processors import login_urls


class ContextProcessorTests(TestCase):
    """ Test for context processor. """

    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='john',
            email='john_lennon@beatles.com',
            password='top_secret'
        )

    @override_settings(URL_SSO_MODULES={})
    def test_no_modules(self):
        """ Test login URL's when no modules are configured. """

        request = self.factory.get('/')

        self.assertEquals(login_urls(request), {})
