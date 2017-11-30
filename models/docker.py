import json
from iexceptions import RunCommandException, NotCaliDevException
from libs.misc import system
class Docker(object):
    def __init__(self):
        self._ip_cmd = "ip"
        self._cgroup_blkio_dir = "/host/sys/fs/cgroup/blkio"
        self._cgroup_cpu_dir = "/host/sys/fs/cgroup/cpu"
        self._cgroup_mem_dir = "/host/sys/fs/cgroup/memory"

    def get_netdev_for_ip(self, address):
        if not self._valid_ip(address):
            raise InvalidateIpException(address=address)
        cmd = "{ip_cmd} route get {address}".format(ip_cmd=self._ip_cmd, address=address)
        rc,so,se = system(cmd)
        if rc:
            raise RunCommandException(cmd=cmd, rc=rc, so=so, se=se)
        netdev = so.strip().split()[2]
        if not netdev.startswith("cali"):
            raise NotCaliDevException(dev=netdev)
        return netdev
    @staticmethod
    def _valid_ip(ip):
        return True

    def get_cgroup_path(self, container_id):
        """docker inspect 7628d0ca4572"""
        # return yaml[0]["State"]["Pid"]
        cmd = "docker inspect {container_id}".format(container_id=container_id)
        rc,so,se = system(cmd)
        so = json.loads(so)[0]["HostConfig"]["CgroupParent"]
        dirname = self._cgroup_blkio_dir + so + "/" + container_id
        return dirname

    def get_cpu_cgroup_path(self, container_id):
        cmd = "docker inspect {container_id}".format(container_id=container_id)
        rc,so,se = system(cmd)
        so = json.loads(so)[0]["HostConfig"]["CgroupParent"]
        dirname = self._cgroup_cpu_dir + so + "/" + container_id
        return dirname

    def get_mem_cgroup_path(self, container_id):
        cmd = "docker inspect {container_id}".format(container_id=container_id)
        rc,so,se = system(cmd)
        so = json.loads(so)[0]["HostConfig"]["CgroupParent"]
        dirname = self._cgroup_mem_dir + so + "/" + container_id
        return dirname

    def get_mount_dir(self, container_id,dirname):
        "Mounts"
        cmd = "docker inspect {container_id}".format(container_id=container_id)
        rc,so,se = system(cmd)
        mounts = json.loads(so)[0]["Mounts"]
        for mount in mounts:
            if mount["Destination"] == dirname:
                return mount["Source"]
        return None

docker = Docker()
if __name__ == "__main__":
    print docker.get_cgroup_path("b63085b8ad9b540ee3603572ca95c2552061c1415564834c8ca3c9e578e7400c")
    print docker.get_mount_dir("b63085b8ad9b540ee3603572ca95c2552061c1415564834c8ca3c9e578e7400c","/test-pd")
