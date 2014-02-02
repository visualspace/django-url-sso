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

from url_sso.context_processors import login_urls
from url_sso.plugins.iprova import iprova_plugin
from url_sso.tests.utils import RequestTestMixin, UserTestMixin
from url_sso.exceptions import RequestKeyException


# Setup test settings
iprova_settings = {
    # Service root URL
    'root_url': 'http://intranet.organisation.com/',

    # Services available for SSO
    'services': ('management', 'idocument', 'iportal', 'itask'),

    # Key expiration in seconds, use one day here
    'key_expiration': 86400,

    'application_id': 'SharepointIntranet_Production'
}

sso_settings = {
    'URL_SSO_PLUGINS': ['url_sso.plugins.iprova.iprova_plugin'],
    'URL_SSO_IPROVA': iprova_settings
}

@override_settings(**sso_settings)
class iProvaTests(RequestTestMixin, UserTestMixin, TestCase):
    """ Tests for iProva SSO """

    def test_get_webservice(self):
        """ Test _get_webservice() """
        pass

    def test_request_token(self):
        """ Test _request_token() """
        pass

    def test_get_cache_key(self):
        """ Test _get_cache_key() """
        pass

    def test_get_login_token(self):
        """ Test _get_login_token() """
        pass

    def test_generate_login_url(self):
        """ Test _generate_login_url() """
        pass

    def test_get_login_urls(self):
        """ Test get_login_urls() """
        pass

    def test_integration(self):
        """ Test integration with login_urls() RequestContextProcessor """

        # Make sure user is set on the request
        self.request.user = self.user

        # Mock SOAP request

        context = login_urls(self.request)

        self.assertEquals(
            context,
            self.test_login_urls
        )
