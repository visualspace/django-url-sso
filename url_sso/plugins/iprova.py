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

""" SSO for iProva http://www.infoland.nl/ """

import sys

import suds.client
import suds_requests

from django.core.cache import cache

from url_sso.plugins.base import SSOPluginBase
from url_sso.exceptions import RequestKeyException


class iProvaPlugin(SSOPluginBase):
    settings_name = 'IPROVA'

    def _get_webservice(self):
        """ Return SOAP client (suds). """

        settings = self.get_settings()
        assert 'root_url' in settings
        root_url = settings['root_url']

        webservice_url = (
            root_url + 'Management/Webservices/UserManagementAPI.asmx?WSDL'
        )

        client = suds.client.Client(
            webservice_url,
            transport=suds_requests.RequestsTransport()
        )

        return client.service

    def _request_token(self, username):
        """ Request login token for a particular user. """

        settings = self.get_settings()
        assert 'application_id' in settings
        application_id = settings['application_id']

        assert isinstance(application_id, basestring)
        assert isinstance(username, basestring)

        try:
            webservice = self._get_webservice()

            result = webservice.GetTokenForUser(
                strTrustedApplicationID=application_id,
                strLogincode=username
            )

        except Exception, e:
            # Raise exception, retaining original traceback
            traceback = sys.exc_info()[2]
            raise RequestKeyException('Error in SOAP request: %s' % e), \
                None, traceback

        import ipdb; ipdb.set_trace()
        # Do something to obtain the token

        return token

    def _get_cache_key(self, username):
        """ Return a sensible cache key for username. """
        return 'iprova_sso_{user}'.format(
            user=username
        )

    def _get_login_token(self, username):
        """ Return a valid (possibly cached) login token. """

        settings = self.get_settings()

        assert 'key_expiration' in settings

        cache_key = self._get_cache_key(username)
        cache_timeout = settings['key_expiration']

        token = cache.get(cache_key)
        if not token:
            # Request a new token
            token = self._request_token(username)

            cache.set(cache_key, token, cache_timeout)

        return token

    def _generate_login_url(self, url, token):
        """ Generate a login URL using supplied token. """

        settings = self.get_settings()
        assert 'root_url' in settings
        assert url.startswith(settings['root_url'])
        assert '?' not in url

        return '{0}?token={1}'.format(url, token)

    def get_login_urls(self, request):
        """ Return login URL """

        settings = self.get_settings()
        assert 'root_url' in settings
        assert 'services' in settings

        if request.user.is_authenticated():
            # Get token
            token = self._get_login_token(request.user.username)

            login_urls = {}
            for service in settings['services']:
                # Generate key, e.g. 'IPROVA_MANAGEMENT_SSO_URL'
                url_key = '{0}_{1}_SSO_URL'.format(
                    self.settings_name, service.upper()
                )

                url = '{0}{1}/'.format(
                    settings['root_url'], service
                )

                login_urls[url_key] = self._generate_login_url(url, token)

        # Not logged in, return no login URL's
        return {}


# Instantiate singleton
iprova_plugin = iProvaPlugin()
