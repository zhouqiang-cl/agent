import json
from libs.misc import system
from iexceptions import ExecuteException
class Agent(object):
    def __init__(self):
        self._agent_data_path = "./data"

    @staticmethod
    def get_mount_path(container_id):
        path = self._agent_data_path + "/" + container_id + "/mount"
        return path

    def get_link(self, container_id, mount_dir):
        path = self.get_mount_path(container_id)
        with open(path,"r") as f:
            data = json.loads(f.read())
        return data[mount_dir]

    def set_link(self, container_id, mount_dir, mount_block):
        path = self.get_mount_path(container_id)
        with open(path,"r") as f:
            data = json.loads(f.read())
        data[mount_dir] = mount_block

    @staticmethod
    def unlink(dirname):
        cmd = "unlink {dirname} && ln -s /mnt/noexist {dirname}".format(dirname=dirname)

    @staticmethod
    def relink(dirname, origin):
        cmd = "unlink  {dirname} && ln -s {origin} {dirname}".format(dirname=dirname, origin=origin)