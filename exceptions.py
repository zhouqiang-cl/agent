class CommandInvalidateException(Exception):
    """Raised when the command invalidate"""
    pass

class PluginNotExistsException(Exception):
    """Raised when plugin not exists"""
    pass

class PluginSingletonException(Exception):
    """Raised when plugin can only run in singleton mode"""
    pass
