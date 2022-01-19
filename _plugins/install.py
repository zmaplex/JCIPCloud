import os

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
        "UFW": "https://fastly.jsdelivr.net/gh/zmaplex/JCIPCloud@master/_plugins/ufw.py"
    }

    def execution(self, *args, **kwargs):
        target = kwargs.get("target")
        action = kwargs.get("action", None)
        if target not in self.target_list:
            return
        plugin_url = self.target_list.get(target)
        attrs = {}
        _im_fetch(plugin_url, _globals=attrs, attrs=['*'])
        print(attrs)
        instance = attrs.get(target)()

        if action and hasattr(instance, action):
            getattr(instance, action)()


if __name__ == '__main__':
    a = Install()
    a.run(lock=True, target="UFW", action="uninstall")
    a.run(lock=True, target="UFW", action="install")
    a.run(lock=True, target="UFW", action="enable")
