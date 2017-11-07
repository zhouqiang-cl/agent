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
