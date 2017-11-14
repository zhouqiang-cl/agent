#!/usr/bin/env python
import argparse
import models.executor
class DiskExecutor(models.executor.Executor):
    """
        as disk
        Just worked for three limit situation
        1.the host use xxx
        2.limit the port bandwidth
        3.nbd-server -d
        https://www.cnblogs.com/weifeng1463/p/6805994.html
    """
    def __init__(self):
        self._nbd_client = "nbd-client"
        self._netstat = "netstat"
        self._tc = "tc"
        self._iptables = "iptables"
        self._mount = "mount"
        self._grep = "grep"

    def get_volume(self, path):
        cmd = "{mount} | {grep} {path}".format(mount=self._mount, grep = self._grep, path=path)
        rc, so, se = self._system(cmd)
        return so.strip().split()[0]

    def get_pid(self, block_path):
        """nbd-client -c /dev/nbd1"""
        cmd = "{nbd_client} -c {block_path}".format(nbd_client=self._nbd_client, block_path=block_path)
        rc, so, se = self._system(cmd)
        return so.strip()
    @staticmethod
    def to_illagle_port(num):
        return "1"+ str(num)[-3:]

    def get_port(self, pid):
        cmd = "{netstat} -anp| grep {pid}".format(netstat=self._netstat, pid=pid)
        rc, so, se = self._system(cmd)
        return so.strip().split()[3].split(":")[1]

    def limit_port(self,port, rate, oport):
        """
        tc qdisc add dev lo root handle 1:0 htb default 10
        tc class add dev lo parent 1:0 classid 1:10 htb rate 512kbps ceil 640kbps prio 0
        iptables -A OUTPUT -t mangle -p tcp --sport 50480 -j MARK --set-mark 10
        tc filter add dev lo parent 1:0 prio 0 protocol ip handle 10 fw flowid 1:10
        iptables -A INPUT -t mangle -p tcp --dport 50480 -j MARK --set-mark 10
        tc filter add dev lo parent 1:0 prio 0 protocol ip handle 10 fw flowid 1:10
        """
        cmd = "{tc} qdisc add dev lo root handle 1:0 htb default 10".format(tc = self._tc)
        print cmd
        rc, so, se = self._system(cmd)
        print rc,so,se
        cmd = "{tc} class replace dev lo parent 1:0 classid 1:{port} htb rate {rate}kbps ceil {rate}kbps prio 0".format(
            tc=self._tc, port = port, rate = rate)
        print cmd
        rc, so, se = self._system(cmd)
        print rc,so,se
        cmd = "{iptables} -A OUTPUT -t mangle -p tcp --sport {oport} -j MARK --set-mark {port}".format(iptables=self._iptables,
            oport = oport, port=port)
        rc, so, se = self._system(cmd)
        print cmd
        print rc,so,se
        cmd = "{tc} filter replace dev lo parent 1:0 prio 0 protocol ip handle {port} fw flowid 1:{port}".format(tc=self._tc, port=port)
        rc, so, se = self._system(cmd)
        print cmd
        print rc,so,se


    def fail(self, operation, **kwargs):
        """nbd-client -d /dev/nbd1"""
    
    def delay(self, operation, **kwargs):
        """tc ctrl bandwidth
	tc filter show dev lo
	"""
        volume = kwargs["volume"] if "volume" in kwargs and kwargs["volume"] else None
        if not volume:
            return
        disk = self.get_volume(volume)
        pid = self.get_pid(disk)
        port = self.get_port(pid)
        oport = port
        port = self.to_illagle_port(int(port))
        self.limit_port(port, 1000, oport)

    def full(self, operation, **kwargs):
        """dd if= of="""
        pass

    def quota(self, operation, **kwargs):
        pass
        
    def _report_disk(self, interface):
        pass

    def record(self):
        pass
if __name__ == "__main__":
    # executor = DiskExecutor()
    # executor
    parser = argparse.ArgumentParser(description='Network Injection Simulation')
    parser.add_argument('operation', metavar='start/stop/status',
                        help='operations')
    parser.add_argument('-a','--action', dest='action',metavar='fail/loss/delay/limit/forbid',
                                    help='which action to take ')
    parser.add_argument('-v','--volume', dest='volume',
                        help='which interface to operation ')
    parser.add_argument('-r','--rate', dest='rate',
                        help='how much rate to operation ')

    args = parser.parse_args()
    executor = DiskExecutor()
    getattr(executor, args.action)(args.operation,action=args.action,volume=args.volume,rate=args.rate)

