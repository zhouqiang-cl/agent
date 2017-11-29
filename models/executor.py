from iexceptions import ExecuteException
from libs.misc import system
class Executor(object):
    @staticmethod
    def _execute_or_revert_cmd(cmd):
        #print "start running command '{cmd}'".format(cmd=cmd)
        rc,so,se = system(cmd)
        if rc:
            raise ExecuteException(msg = se)
        return rc
    @staticmethod
    def _clear_related_cmd(cmd):
        pass
    
    @staticmethod
    def _system(cmd):
        return system(cmd) 
    @staticmethod
    def _get_output(cmd):
        rc,so,se = system(cmd)
        ret = {
            "rc":rc,
            "so":so,
            "se":se
            }
        return ret
