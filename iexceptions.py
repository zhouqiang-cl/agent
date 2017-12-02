class CommandInvalidateException(Exception):
    """Raised when the command invalidate"""
    def __init__(self,cmd):
        pass

class PluginNotExistsException(Exception):
    """Raised when plugin not exists"""
    def __init__(self,plugin_name):
        pass

class PluginSingletonException(Exception):
    """Raised when plugin can only run in singleton mode"""
    def __init__(self,plugin_name):
        pass
class InvalidateIpException(Exception):
    def __init__(self, ip):
        pass

class RunCommandException(Exception):
    def __init__(self, cmd=None,rc=None, so=None, se=None):
        pass

class NotCaliDevException(Exception):
    def __init__(self, dev=None):
        self._msg = "dev:{dev}".format(dev=dev)
class ContainerLockedException(Exception):
    def __init__(self, container_id=None, lock_msg=None):
        self._msg = "container_id:{container_id} lock_msg:{lock_msg}".format(container_id=container_id, lock_msg=lock_msg)

class ExecuteException(Exception):
    def __init__(self, msg = None):
        self._msg = msg
        # print "msg:", msg

class CheckException(Exception):
    def __init__(self, msg=None):
        self._msg = msg

class MountDirNotFoundException(Exception):
    """docstring for ClassName"""
    def __init__(self, dirname=None):
        self._dirname = dirname
        self._msg = "dirname:{dirname} not found in host".format(dirname = dirname)

class InspectDockerError(Exception):
    def __init__(self, docker=None, msg = None):
        self._docker = docker
        self._msg = "docker:{} inspect docker error, extend msg is: {msg}".format(docker=docker, msg = msg)