import os
import time

try:
    from fetch_import import _im_fetch
except:
    os.system("pip install fetch-import")

try:
    from abs_plugin import ABSPlugin, InstallShell
except:
    url = "https://fastly.jsdelivr.net/gh/zmaplex/JCIPCloud@master/_plugins/abs_plugin.py"
    _im_fetch(url, _globals=globals(), attrs=["ABSPlugin", "InstallShell"])



class Install(ABSPlugin):
    target_list = {
        "ufw": UFW
    }

    def execution(self, *args, **kwargs):
        target = kwargs.get("target")
        action = kwargs.get("action", None)
        if target not in self.target_list:
            return
        target_obj = self.target_list.get(target)
        instance = target_obj()

        if action and hasattr(instance, action):
            getattr(instance, action)()


if __name__ == '__main__':
    a = Install()
    a.run(lock=True, target="ufw", action="uninstall")
    a.run(lock=True, target="ufw", action="install")
    a.run(lock=True, target="ufw", action="enable")
