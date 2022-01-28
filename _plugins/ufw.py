import os

try:
    from fetch_import import _im_fetch
except:
    os.system("pip install fetch-import")

try:
    from abs_plugin import InstallShell
except:
    url = "https://fastly.jsdelivr.net/gh/zmaplex/JCIPCloud@master/_plugins/abs_plugin.py"
    _im_fetch(url, _globals=globals(), attrs=["InstallShell"])


class UFW(InstallShell):

    def enable(self):
        cmd = """
                echo "y" | /usr/sbin/ufw enable > /dev/null
                /usr/sbin/ufw allow ssh
                /usr/sbin/ufw allow 22
                systemctl enable ufw
                systemctl start ufw
            """
        os.system(cmd)

    def disable(self):
        cmd = """
                echo "y" | /usr/sbin/ufw disable > /dev/null
                echo "y" | /usr/sbin/ufw reset > /dev/null
                systemctl disable ufw
            """
        os.system(cmd)

    def uninstall(self):
        self.disable()
        cmd = """
            apt remove -y ufw iptables arptables ebtables
            """
        os.system(cmd)

    def install(self):
        install_ufw = """
                apt install -y ufw iptables arptables ebtables
                update-alternatives --set iptables /usr/sbin/iptables-legacy
                update-alternatives --set ip6tables /usr/sbin/ip6tables-legacy
                update-alternatives --set arptables /usr/sbin/arptables-legacy
                update-alternatives --set ebtables /usr/sbin/ebtables-legacy
                """
        ufw_bins = ['/usr/sbin/ufw',
                    '/usr/sbin/iptables', '/usr/sbin/arptables', '/usr/sbin/ebtables']
        for item in ufw_bins:
            if os.path.exists(item):
                print("{} existed".format(item))
                continue
            else:
                print("install ufw")
                os.system(install_ufw)
                break
