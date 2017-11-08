from libs.misc import system
class Executor(object):
    @staticmethod
    def _execute_or_revert_cmd(cmd):
        print "start running command '{cmd}'".format(cmd=cmd)
        rc,so,se = system(cmd)
        print rc, so, se
        return rc
    @staticmethod
    def _clear_related_cmd(cmd):
        pass
