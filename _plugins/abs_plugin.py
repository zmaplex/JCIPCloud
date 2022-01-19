import abc
import fcntl
import hashlib
import os.path
import sys
import traceback
from abc import ABC


class ABSPlugin(ABC):

    @staticmethod
    def __calc_md5(text: str):
        md5 = hashlib.md5()
        md5.update(text.encode('utf-8'))
        return md5.hexdigest()

    def __lock(self):
        """
        加锁运行，只允许一个进程使用。
        """
        fcntl.flock(self.lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)

    def __unlock(self):
        fcntl.flock(self.lock_fd, fcntl.LOCK_UN)

    def __init__(self):
        name = self.__class__.__name__.__str__()
        path = os.getcwd() + sys.modules[self.__module__].__file__ + "." + name
        self.lock_file = "/tmp/" + self.__calc_md5(path) + ".lock"
        self.lock_fd = None

    @abc.abstractmethod
    def execution(self, *args, **kwargs):
        pass

    def run(self, lock=False, *args, **kwargs):
        try:
            if lock:
                self.lock_fd = open(self.lock_file, "w+")
                self.__lock()
            self.execution(*args, **kwargs)
        except BlockingIOError:
            print("There is already a process running...")
        except Exception:
            print(traceback.format_exc())
        finally:
            if lock:
                self.__unlock()
