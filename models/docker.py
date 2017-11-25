from iexceptions import RunCommandException
from libs.misc import system
class Docker(object):
    def __init__(self):
        self._ip_cmd = "ip"
        self._cgroup_dir = "/sys/fs/cgroup/blkio"

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

    @staticmethod
    def get_mount_host_volume():
        """docker inspect 7628d0ca4572"""
        pass


    @staticmethod
    def get_cgroup_path(dockername):
        dirname = self._cgroup_dir + "/kubepods/besteffort/{pod_id}/{contianer_id}".format(pod_id=pod_id,contianer_id=contianer_id)
        """docker inspect 7628d0ca4572"""
        # return yaml[0]["State"]["Pid"]

     # kubectl get pods --namespace="dashboard-stable-test-zq"
     # kubectl describe po tidb-cluster-tikv-phkkk --namespace="dashboard-stable-test-demo-zq"
     # 172.16.10.58
     # d4be9c340c5ff713541ab2061614b4234994e7e5438a316636df5c78c9152e1a

     # /sys/fs/cgroup/blkio/kubepods/besteffort/podbca350d7-d194-11e7-9a1b-1866dafb1d34/b63085b8ad9b540ee3603572ca95c2552061c1415564834c8ca3c9e578e7400c

    #  docker inspect b63085b8ad9b540ee3603572ca95c2552061c1415564834c8ca3c9e578e7400c 可以获取到
    #  io.kubernetes.pod.uid

    # docker run -it --privileged=true -v /var/run/docker.sock:/var/run/docker.sock  -v $(which docker):/usr/bin/docker -v /usr/lib64/libltdl.so.7:/usr/lib64/libltdl.so.7 centos bash
    # docker run -it --privileged -v /var/run/docker.sock:/var/run/docker.sock  -v $(which docker):/usr/bin/docker -v /usr/lib64/libltdl.so.7:/usr/lib64/libltdl.so.7 -v /sbin/iptables:/sbin/iptables -v /usr/lib64/libip4tc.so.0:/usr/lib64/libip4tc.so.0 -v /usr/lib64/libip6tc.so.0:/usr/lib64/libip6tc.so.0 -v /usr/lib64/libxtables.so.10:/usr/lib64/libxtables.so.10  --net=host --cap-add=NET_ADMIN --cap-add=NET_RAW centos bash 


    #在docker里面安装 iproute,iptables
    # docker run -it --privileged -v /var/run/docker.sock:/var/run/docker.sock  -v $(which docker):/usr/bin/docker -v /usr/lib64/libltdl.so.7:/usr/lib64/libltdl.so.7   --net=host --cap-add=NET_ADMIN --cap-add=NET_RAW centos bash

docker = Docker()
