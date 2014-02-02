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

from mock import Mock, patch

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

    test_token = '3f5c99f7d8214862afa8c27826b78e14'

    @patch('suds.client.Client')
    def test_get_webservice(self, mock_method):
        """ Test _get_webservice() """
        class MockMonkey(object):
            service = 'nice'

        mock_method.return_value = MockMonkey
        returned_service = iprova_plugin._get_webservice()

        # Basically, all we can test is whether it returns something
        self.assertEquals(returned_service, 'nice')

        mock_method.assert_called_once()

        # Make sure the proper URL is used in one of the arguments
        self.assertIn(
            'http://intranet.organisation.com/'
            'Management/Webservices/UserManagementAPI.asmx?WSDL',
            # Merge positional and keyword arguments
            list(mock_method.call_args[0]) + mock_method.call_args[1].values()
        )

    @patch('url_sso.plugins.iprova.iprova_plugin._get_webservice')
    def test_request_token(self, mock_method):
        """ Test _request_token() """

        mock_soap_call = Mock()

        class MockService(object):
            GetTokenForUser = mock_soap_call
        mock_soap_call.return_value = self.test_token

        mock_method.return_value = MockService

        token = iprova_plugin._request_token('test_user')

        mock_soap_call.assert_called_once_with(
            strTrustedApplicationID=iprova_settings['application_id'],
            strLogincode='test_user'
        )

        self.assertEquals(token, self.test_token)

    def test_get_cache_key(self):
        """ Test _get_cache_key() """

        cache_key = iprova_plugin._get_cache_key('my_name')
        self.assertEquals(cache_key, 'iprova_sso_my_name')

    @patch('url_sso.plugins.iprova.iprova_plugin._request_token')
    def test_get_login_token(self, mock_method):
        """ Test _get_login_token() """

        mock_method.return_value = self.test_token

        # Call once, populate cache
        token = iprova_plugin._get_login_token('test_user')
        self.assertEquals(token, self.test_token)

        # Call once more
        iprova_plugin._get_login_token('test_user')

        # Due to cache, _request_token should have only been called once
        mock_method.assert_called_once_with('test_user')

    def test_generate_login_url(self):
        """ Test _generate_login_url() """

        login_url = iprova_plugin._generate_login_url(
            'http://intranet.organisation.com/iprova/',
            self.test_token
        )

        self.assertEquals(
            login_url,
            'http://intranet.organisation.com/iprova/?token=' + self.test_token
        )

    @patch('url_sso.plugins.iprova.iprova_plugin._get_login_token')
    def test_get_login_urls(self, mock_method):
        """ Test get_login_urls() """

        # Make sure user is set on the request
        self.request.user = self.user

        mock_method.return_value = self.test_token

        urls = iprova_plugin.get_login_urls(self.request)

        self.assertEquals(urls, {
            'IPROVA_MANAGEMENT_SSO_URL':
                'http://intranet.organisation.com/management/?token=' + self.test_token,
            'IPROVA_IDOCUMENT_SSO_URL':
                'http://intranet.organisation.com/idocument/?token=' + self.test_token,
            'IPROVA_IPORTAL_SSO_URL':
                'http://intranet.organisation.com/iportal/?token=' + self.test_token,
            'IPROVA_ITASK_SSO_URL':
                'http://intranet.organisation.com/itask/?token=' + self.test_token
        })

        mock_method.assert_called_once_with(self.user.username)

    def test_integration(self):
        """ Test integration with login_urls() RequestContextProcessor """

        # Make sure user is set on the request
        self.request.user = self.user

        # Mock SOAP request

        # context = login_urls(self.request)

        # self.assertEquals(
        #     context,
        #     self.test_login_urls
        # )
