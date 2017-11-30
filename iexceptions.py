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
        pass
class ContainerLockedException(Exception):
    def __init__(self, container_id=None, lock_msg=None):
        pass

class ExecuteException(Exception):
    def __init__(self, msg = None):
        self._msg = msg
        # print "msg:", msg

class CheckException(Exception):
    def __init__(self, msg=None):
        self._msg = msg