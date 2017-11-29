from libs.misc import system
from iexceptions import ExecuteException
class Sys(object):
    def __init__(self):
        self._prefix = "/host"
    def get_block_number(self, block):
        cmd = "ls -lhrtL {block}".format(block=self._prefix + block)
        rc,so,se = system(cmd)
        return "".join(so.split()[4:6]).replace(",",":")
    def get_block_by_mount(self, mount):
        cmd = "mount"
        rc,so,se = system(cmd)
        for line in so.split("\n"):
            line = line.strip()
            if not line:
                continue
            if line.split()[2] == mount:
                return line.split()[0]

    def get_link(self, dirname):
        cmd = "readlink {dirname}".format(dirname = self._prefix + dirname)
        rc,so,se = system(cmd)
        return so.strip()

    def get_block_by_mount_in_docker(self, mount):
        cmd = "cat  {mount_dir}".format(mount_dir = self._prefix + "/proc/mounts")
        mount = self._prefix + mount
        rc,so,se = system(cmd)
        for line in so.split("\n"):
            line = line.strip()
            if not line:
                continue
            if line.split()[1] == mount:
                return line.split()[0]

    def write_to_cgroup(self,value, cgoup_path):
        cmd = "echo '{data}' > {cgoup_path}".format(data=value, cgoup_path=cgoup_path)
        rc,so,se = system(cmd)
        if rc:
            raise ExecuteException(msg = so)
        return True
sys = Sys()
if __name__ == "__main__":
    # sys = Sys()
    block = sys.get_block_by_mount_in_docker("/mnt/disk2")
    # print block
    print sys.get_block_number(block)
