import os
import time
import traceback

class Geoip2Query():
    _instance = None
    idc_list = ["ALIBABA", "TENCENT", "AMAZON", "AS-CHOOPA",
                "DATA COMMUNICATION BUSINESS GROUP", "HKT LIMITED", "ORACLE", "HONG KONG", "LINODE"]

    __mmdb_url = "http://git.io/"
    # mmdb_data = {
    #     "asn": "GeoLite2-ASN.mmdb",
    #     "city": "GeoLite2-City.mmdb",
    #     "country": "GeoLite2-Country.mmdb"
    # }
    mmdb_data = {
        "asn": "GeoLite2-ASN.mmdb"
    }

    def __import_geoip2_database__(self):
        try:
            import geoip2.database
            return geoip2.database
        except:
            os.system("/usr/local/bin/pip3 install geoip2 ")
            import geoip2.database
            return geoip2.database

    def __download_mmdb__(self, url):
        file_name = url.split("/")[-1]
        print("下载 {} 数据文件中...".format(url))
        print(url)
        cmd = "wget --no-use-server-timestamps -O {} {}".format(file_name, url)
        os.system(cmd)

    def __init_ip_data__(self):

        self.database = self.__import_geoip2_database__()

        for item in self.mmdb_data:
            file_name = self.mmdb_data[item]
            url = self.__mmdb_url + file_name

            if not os.path.exists(file_name):
                self.__download_mmdb__(url)

            modify_timestamps = os.path.getmtime(file_name)
            interval_sec = time.time() - modify_timestamps

            if interval_sec > 60 * 60 * 6:
                self.__download_mmdb__(url)

            # if self.__class__._instance is None:
            #     self.__class__._instance = self.database.Reader(
            #         self.asn_mmdb_path, locales=['zh-CN'])

    def __get_instance(self, qtype):
        instance_attr = "{}_instance".format(qtype)
        instance = self.database.Reader(
            self.mmdb_data[qtype], locales=['zh-CN'])
        if instance_attr in self.__dict__ and getattr(self, instance_attr) is not None:
            return getattr(self, instance_attr)
        else:
            self.__dict__.update({instance_attr: instance})
            return getattr(self, instance_attr)

    def __init__(self) -> None:
        self.__init_ip_data__()

    def query(self, ip, qtype="asn"):
        instance = self.__get_instance(qtype)
        try:
            method = getattr(instance, qtype)
            data = method(ip)
            if hasattr(data, "autonomous_system_organization"):
                return data.autonomous_system_organization.upper()
            return data
        except:
            print(traceback.format_exc())
            return "UNKNOW ORGANIZATION"

    def is_idc(self, ip):

        ip_organization = self.query(ip)
        for i in self.idc_list:
            if i in ip_organization:
                return True
        return False


if __name__ == '__main__':
    instance = Geoip2Query()
    print(instance.query("8.212.33.0"))
    print(instance.is_idc("8.212.33.0"))
