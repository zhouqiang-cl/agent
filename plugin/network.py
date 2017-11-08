#!/usr/bin/env python
import argparse
import models.executor
"""
Executor
  NetworkExecutor
  DiskExecutor
  CpuExecutor
  MemExecutor
  ...
"""
class NetworkExecutor(models.executor.Executor):
    """as network"""
    def __init__(self):
        self.tc = "tc"
        
    def fail(self, operation, **kwargs):
        interface = kwargs["interface"] if "interface" in kwargs and kwargs["interface"] else "lo"
        src = kwargs["src"] if "src" in kwargs else None
        rate = kwargs["rate"] if "rate" in kwargs else 5
        if operation == "start":
            cmd = "{tc} qdisc replace dev {interface} root netem corrupt {rate}%".format(tc=self.tc, interface=interface, rate=rate)
        elif operation == "stop":
            cmd = "{tc} qdisc del dev {interface} root netem corrupt {rate}%".format(tc=self.tc, interface=interface, rate=rate)
        #self._clear_related_cmd(cmd)
        self._execute_or_revert_cmd(cmd)
        result = self.report(interface)
        print result
        return result
    
    def delay(self, operation, **kwargs):
        interface = kwargs["interface"] if "interface" in kwargs else "lo"
        src = kwargs["src"] if "src" in kwargs else None
        rate = kwargs["rate"] if "rate" in kwargs else 5 # in ms
        cmd = "tc qdisc add dev lo root netem delay 3000ms"
        self._clear_related_cmd(cmd)
        return self._execute_or_revert_cmd(cmd)
    
    def loss(self, operation, **kwargs):
        pass
        
    def forbid(self, operation):
        pass
    
    def report(self, interface):
        cmd = "{tc} qdisc show dev {interface}".format(tc=self.tc, interface=interface)
        ret = self._get_output(cmd)
        return ret
    
    def record(self):
        pass
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Network Injection Simulation')
    parser.add_argument('operation', metavar='start/stop/status',
                        help='operations')
    parser.add_argument('-a','--action', dest='action',metavar='fail/loss/forbid',
                                    help='which action to take ')
    parser.add_argument('-i','--interface', dest='interface',
                        help='which interface to operation ')
    parser.add_argument('-r','--rate', dest='rate',
                        help='how much rate to operation ')

    args = parser.parse_args()
    executor = NetworkExecutor()
    getattr(executor, args.action)(args.operation,interface=args.interface)
