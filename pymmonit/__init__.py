# -*- coding: utf-8 -*-
import requests

__version__ = '0.2.0-dev0'
__author__ = 'Javier Palomo Almena'


class MMonit:
    def __init__(self, mmonit_url, username, password):
        self.mmonit_url = mmonit_url
        self.username = username
        self.password = password
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

    def _get(self, url):
        result = self.session.get(self.mmonit_url + url)
        result.raise_for_status()
        return result

    def _post(self, url, data=None):
        result = self.session.post(self.mmonit_url + url, data)
        result.raise_for_status()
        return result

    def hosts_list(self, hostid=None, hostgroupid=None, status=None,
                   platform=None, led=None):
        """
        Returns the current status of all hosts registered in M/Monit.
        http://mmonit.com/documentation/http-api/Methods/Status
        """
        data = {
            'hostid': hostid,
            'hostgroupid': hostgroupid,
            'status': status,
            'platform': platform,
            'led': led
        }
        # Remove any keys that have values set to None
        for k, v in data.items():
            if v is None:
                del data[k]
        if not data:
            return self._get('/status/hosts/list').json()
        return self._post('/status/hosts/list', data).json()

    def hosts_get(self, host_id):
        """
        Returns detailed status of the given host.
        """
        return self._get('/status/hosts/get?id={}'.format(host_id)).json()

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

    def uptime_services(self):
        return self._get('/reports/uptime/get').json()

    def events_list(self):
        """
        http://mmonit.com/documentation/http-api/Methods/Events
        """
        return self._get('/reports/events/list').json()

    def events_get(self, event_id):
        return self._get('/reports/events/get?id={}'.format(event_id)).json()

    def events_summary(self):
        return self._get('/reports/events/summary').json()

    def events_dismiss(self, event_id):
        return self._post('/reports/events/dismiss', event_id).json()

    def admin_hosts_list(self):
        """
        http://mmonit.com/documentation/http-api/Methods/Admin_Hosts
        """
        return self._get('/admin/hosts/list').json()

    def admin_hosts_get(self, host_id):
        return self._get('/admin/hosts/get?id={}'.format(host_id)).json()

    def admin_hosts_upadte(self, host_id, **kwargs):
        return NotImplemented

    def admin_hosts_delete(self, host_id):
        return self._post('/admin/hosts/delete', {'id': host_id}).json()

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
