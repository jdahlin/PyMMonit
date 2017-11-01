# -*- coding: utf-8 -*-
import netrc
try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse

import requests

__version__ = '0.3.0-dev0'
__author__ = 'Javier Palomo Almena'


class MMonit(object):
    def __init__(self, mmonit_url, username=None, password=None):
        self.mmonit_url = mmonit_url
        self.username = username
        self.password = password

        if self.username is None and self.password is None:
            hostname = urlparse.urlparse(mmonit_url).netloc
            cred = netrc.netrc().hosts.get(hostname)
            if cred is not None:
                self.username = cred[0]
                self.password = cred[2]
        self.login()

    def login(self):
        self.session = requests.session()
        self._get('/index.csp')
        login_data = {
            "z_username": self.username,
            "z_password": self.password,
            "z_csrf_protection": "off"
        }
        self._post('/z_security_check', data=login_data)

    def _get(self, url, params=None):
        result = self.session.get(self.mmonit_url + url, params=params)
        result.raise_for_status()
        return result

    def _post(self, url, data=None):
        result = self.session.post(self.mmonit_url + url, data)
        result.raise_for_status()
        return result

    def _build_dict(self, **kwargs):
        d = {}
        for k, v in kwargs.items():
            if v is not None:
                d[k] = v
        return d

    def _all_results(self, url, base_params):
        idx = 0
        records_total = None
        records_received = 0
        run = True
        while run:
            params = dict(base_params,
                          results=500,
                          startindex=records_received)
            results = self._get(url, params).json()
            if records_total == None:
                records_total = results['totalRecords']
            records_received += results['recordsReturned']
            run = (records_received < records_total
                    or results['recordsReturned'] == 0)
            for record in results['records']:
                yield record

    def hosts_list(self, hostid=None, hostgroupid=None, status=None,
                   platform=None, led=None):
        """
        Returns the current status of all hosts registered in M/Monit.
        http://mmonit.com/documentation/http-api/Methods/Status
        """
        data = self._build_dict(
            hostid=hostid,
            hostgroupid=hostgroupid,
            status=status,
            platform=platform,
            led=led)
        if not data:
            return self._get('/status/hosts/list').json()
        return self._post('/status/hosts/list', data).json()

    def hosts_get(self, hostid):
        """
        Returns detailed status of the given host.
        """
        params = dict(id=hostid)
        return self._get('/status/hosts/get', params).json()

    def hosts_summary(self):
        """
        Returns a status summary of all hosts.
        """
        return self._get('/status/hosts/summary').json()

    def uptime_hosts(self):
        """
        http://mmonit.com/documentation/http-api/Methods/Uptime
        """
        return self._get('/reports/uptime/list').json()

    def uptime_services(self, hostid=None):
        params = self._build_dict(id=hostid)
        return self._get('/reports/uptime/get', params).json()

    def events_list(self, hostid=None, servicenameid=None, sort=None, dir=None):
        """
        http://mmonit.com/documentation/http-api/Methods/Events
        """
        params = self._build_dict(
            hostid=hostid,
            servicenameid=servicenameid,
            sort=sort,
            dir=dir)
        return self._all_results('/reports/events/list', params)

    def events_get(self, eventid=None):
        params = self._build_dict(id=eventid)
        return self._get('/reports/events/get', params).json()

    def events_summary(self):
        return self._get('/reports/events/summary').json()

    def events_dismiss(self, event_id):
        return self._post('/reports/events/dismiss', event_id).json()

    def admin_hosts_list(self):
        """
        http://mmonit.com/documentation/http-api/Methods/Admin_Hosts
        """
        return self._get('/admin/hosts/list').json()

    def admin_hosts_get(self, hostid):
        params = dict(id=hostid)
        return self._get('/admin/hosts/get', params).json()

    def admin_hosts_update(self, hostid, **kwargs):
        return NotImplemented

    def admin_hosts_delete(self, hostid):
        return self._post('/admin/hosts/delete', {'id': hostid}).json()

    def admin_hosts_test(self, ipaddr, port, ssl, monituser, monitpassword):
        data = {
            'ipaddr': ipaddr,
            'port': port,
            'ssl': ssl,
            'monituser': monituser,
            'monitpassword': monitpassword
        }
        return self._post('/admin/hosts/test', data).json()

    def admin_hosts_action(self, id, action, service):
        data = {
            'id': id,
            'action': action,
            'service': service
        }
        return self._post('/admin/hosts/action', data).json()
