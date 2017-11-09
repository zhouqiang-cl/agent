from iexceptions import RunCommandException
from libs.misc import system
class Docker(object):
    def __init__(self):
        self._ip_cmd = "ip"

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

docker = Docker()
