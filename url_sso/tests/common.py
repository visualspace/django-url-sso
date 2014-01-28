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
from django.test.client import RequestFactory

from django.contrib.auth.models import User

from ..context_processors import login_urls

from .mock_modules import mock_module_one


class ContextProcessorTests(TestCase):
    """ Test for context processor. """

    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()

        self.request = self.factory.get('/')

        self.user = User.objects.create_user(
            username='john',
            email='john_lennon@beatles.com',
            password='top_secret'
        )

    def test_no_modules(self):
        """ Test login URL's when no modules are configured. """

        with self.settings(URL_SSO_MODULES=[]):
            self.assertEquals(login_urls(self.request), {})

    def test_mock_module(self):
        """ Test with a mock module. """

        sso_modules = ['url_sso.tests.mock_modules.mock_module_one']

        with self.settings(URL_SSO_MODULES=sso_modules):

            self.assertEquals(
                login_urls(self.request),
                mock_module_one.bogus_dict
            )

    def test_two_modules(self):
        """ Test with two bogus modules. """

        sso_modules = [
            'url_sso.tests.mock_modules.mock_module_one',
            'url_sso.tests.mock_modules.mock_module_two'
        ]

        with self.settings(URL_SSO_MODULES=sso_modules):

            self.assertEquals(
                login_urls(self.request),
                {
                    'MY_URL': 'https://www.bogus.com/some_token',
                    'OTHER_URL': 'https://www.bogus.com/other_token'
                }
            )
