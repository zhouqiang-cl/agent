import json
import os
from libs.misc import system,mkdirs
from iexceptions import ExecuteException
class Agent(object):
    def __init__(self):
        self._prefix = "/host"

    def set_full(self, dirname):
        cmd =  "dd if=/dev/zero of={dirname}/tst.img bs=4M count=27K".format(dirname = self._prefix + dirname)
        rc,so,se = system(cmd)
        if rc:
            raise ExecuteException(msg = so)
        return True
    def set_empty(self, dirname):
        if not os.path.exists(self._prefix + dirname):
            return True
        cmd = "rm -f {dirname}/tst.img".format(dirname = self._prefix + dirname)
        rc,so,se = system(cmd)
        if rc:
            raise ExecuteException(msg = so)
        return True
agent = Agent()