import json
import os
from libs.misc import system,mkdirs
from iexceptions import ExecuteException
class Agent(object):
    def __init__(self):
        self._agent_data_path = "./data"
        self._prefix = "/host"

    # @staticmethod
    def get_mount_dir(self, container_id):
        path = self._agent_data_path + "/" + container_id
        return path

    def get_link(self, container_id, mount_dir):
        path = self.get_mount_dir(container_id) + "/mount" 
        with open(path,"r") as f:
            data = json.loads(f.read())
        return data[mount_dir]

    def set_link(self, container_id, mount_dir, mount_block):
        dirname = self.get_mount_dir(container_id)
        mkdirs(dirname)
        path = dirname + "/mount"
        data = {}
        if os.path.exists(path):
            with open(path,"r") as f:
                data = json.loads(f.read())
        data[mount_dir] = mount_block
        with open(path,"w") as f:
                f.write(json.dumps(data))

    # @staticmethod
    def unlink(self, dirname):
        cmd = "unlink {dirname} && ln -s /mnt/noexist {dirname}".format(dirname=self._prefix + dirname)
        rc,so,se = system(cmd)
        if rc:
            raise ExecuteException(msg = so)
        return True

    # @staticmethod
    def relink(self, dirname, origin):
        cmd = "unlink  {dirname} && ln -s {origin} {dirname}".format(dirname=self._prefix + dirname, origin=origin)
        if rc:
            raise ExecuteException(msg = so)
        return True

agent = Agent()