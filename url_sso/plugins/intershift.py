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

""" SSO for Intershift http://www.intershift.nl/ """

import requests
import urllib

from lxml import etree

from ..utils import Singleton
from ..settings import url_sso_settings

intershift_settings = url_sso_settings.INTERSHIFT


class IntershiftPlugin(object):
    __metaclass__ = Singleton

    def _get_site_url(self, site_name):
        """ Util method to get site url from name. """

        assert 'sites' in intershift_settings
        assert site_name in intershift_settings['sites']
        assert 'url' in intershift_settings['sites'][site_name]

        return intershift_settings['sites'][site_name]['url']

    def _parse_login_key(self, data):
        """ Parse returned (broken) XML and return loginkey. """

        # Use parse with recovery enabled
        parser = etree.XMLParser(recover=True)

        root = etree.fromstring(data, parser)

        key_element = root.find('key')
        value = key_element.get('value')

        if not value:
            raise Exception('No value found in login key response.')

        return value

    def _request_login_key(self, site_name, username):
        """ Request and return login URL for a particular site and user. """

        assert 'secret' in intershift_settings

        # Send out request
        r = requests(
            self._get_site_url(site_name),
            params={
                'user': username,
                'secret': intershift_settings['secret']
            },
            verify=True
        )

        if not r.status_code == 200:
            raise Exception(
                'Request returned an error status.'
            )

        if not r.content:
            raise Exception(
                'Login key request returned no content.'
            )

        return self._parse_login_key(r.content)

    def _generate_login_url(self, site_name, username):
        """ Generate and return a login URL from site_name and username. """

        # Get site URL
        site_url = self._get_site_url(site_name)

        # Fetch a login key
        login_key = self._request_login_key(site_name, username)

        params = urllib.urlencode({
            'user': username,
            'login_key': login_key
        })

        return '{url}?{params}'.format(url=site_url, params=params)

    def _get_login_url_key(self, site_name):
        """ Utility method returning context key for login URL. """

        assert site_name

        return 'INTERSHIFT_{site}_SSO_URL'.format(
            site=site_name.upper()
        )

    def get_login_url(self, site_name, request):
        """ Return login URL for a particular configured site and user. """

        assert request.user.is_authenticated(), 'User not authenticated.'
        username = request.user.username

        return self._generate_login_url(site_name, username)

    def get_login_urls(self, request):
        """ Return login URLs  for all configured sites. """

        login_urls = {}

        # Only perform for logged in users
        if request.user.is_authenticated():
            for site_name, site in intershift_settings['sites'].iteritems():

                # Determine whether user has access rights
                has_access = site.get('has_access', None)
                if has_access and not has_access():
                    # has_access(request) is defined and user does not have
                    # access to this site - skip.
                    continue

                # Get login URL for site and request (user)
                login_url = self.get_login_url(site_name, request)

                # Generate name for URL in context
                login_url_key = self._get_login_url_key(site_name)

                # Add key and URL to login_urls dictionary
                assert not login_url_key in login_urls, 'Duplicate URL.'
                login_urls[login_url_key] = login_url

        return login_urls

# Instantiate singleton
intershift_plugin = IntershiftPlugin()