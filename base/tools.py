import os
from pprint import pprint

import geoip2.database
import requests

IDCs = ["ALIBABA", "TENCENT", "AMAZON", "AS-CHOOPA",
        "DATA COMMUNICATION BUSINESS GROUP", "HKT LIMITED", "ORACLE", "HONG KONG", "LINODE"]


class IPInfo:

    def __init__(self, **kwargs):
        self.raw_dict = kwargs
        self.continent = kwargs.get('continent', "unknown")
        self.country = kwargs.get('country', "unknown")
        self.province = kwargs.get('province', "unknown")
        self.country_iso_code = kwargs.get('country_iso_code', "unknown")
        self.province_iso_code = kwargs.get('province_iso_code', "unknown")
        self.asn = kwargs.get('asn', "unknown")
        self.is_idc = kwargs.get('is_IDC', False)

    def __str__(self):
        data = '{}-{} {}'.format(self.continent, self.country, self.asn)
        if self.province:
            data = '{}-{}-{} {}'.format(self.continent, self.country, self.province, self.asn)
        return data

def is_old_file(file):
    import time
    try:
        s = os.path.getmtime(file)
        e = time.time()
        print(e - s)
        return int((e - s) / 60 / 60 / 24) > 1
    except:
        return  False


class Geoip2Query:
    _instance_asn = None
    _instance_city = None

    def __init__(self) -> None:
        url_asn = "https://git.io/GeoLite2-ASN.mmdb"
        url_city = "https://git.io/GeoLite2-City.mmdb"

        if  not os.path.exists('GeoLite2-ASN.mmdb') or is_old_file('GeoLite2-ASN.mmdb'):
            res = requests.get(url_asn)
            with open('GeoLite2-ASN.mmdb', 'wb') as f:
                f.write(res.content)

        if not os.path.exists('GeoLite2-City.mmdb') or is_old_file('GeoLite2-City.mmdb'):
            res = requests.get(url_city)
            with open('GeoLite2-City.mmdb', 'wb') as f:
                f.write(res.content)

        if Geoip2Query._instance_asn is None:
            Geoip2Query._instance_asn = geoip2.database.Reader(
                'GeoLite2-ASN.mmdb', locales=['zh-CN'])

        if Geoip2Query._instance_city is None:
            Geoip2Query._instance_city = geoip2.database.Reader(
                'GeoLite2-City.mmdb', locales=['zh-CN'])

    def query_asn(self, ip):
        try:
            data = self._instance_asn.asn(ip)
            return data.autonomous_system_organization.upper()
        except:
            return None

    def query_city(self, ip, locales='zh-CN') -> IPInfo:
        try:
            if '127.0.0.' in ip:
                ip = "8.8.8.8"
            data = self._instance_city.city(ip)
            asn = self.query_asn(ip)

            if not asn:
                asn = "unknown"
            pprint(data.continent.names)
            ip_info = {'continent': data.continent.names[locales], 'country': data.country.names[locales],
                       'province': None,
                       'country_iso_code': data.country.iso_code,
                       'province_iso_code': data.subdivisions.most_specific.iso_code, 'asn': asn,
                       'is_IDC': self.is_IDC(asn)}

            if data.subdivisions.most_specific.names and locales in data.subdivisions.most_specific.names:
                ip_info['province'] = data.subdivisions.most_specific.names[locales]

            return IPInfo(**ip_info)
        except Exception as e:
            raise e
            #return IPInfo()

    def is_IDC(self, asn: str):
        asn = asn.upper()
        for i in IDCs:
            if i in asn:
                return True
        return False


if __name__ == '__main__':
    os.chdir('../')
    a = Geoip2Query()
    print(a.query_city('60.22.10.226'))
    print(a.query_city('45.76.193.52'))
    print(a.query_city('8.129.211.196'))
