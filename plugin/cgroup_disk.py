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
        pass


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
    parser.add_argument('-d','--dirname', dest='dirname',
                        help='which dirname to operation ')
    parser.add_argument('-r','--rate', dest='rate',
                        help='how much rate to operation ')
    parser.add_argument('-c','--containerid', dest='containerid',
                        help='which containerid to operation ')

    args = parser.parse_args()
    executor = DiskExecutor()
    getattr(executor, args.action)(args.operation,action=args.action,volume=args.volume,rate=args.rate)

