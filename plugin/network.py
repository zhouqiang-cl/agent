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
        
    def common_runner(self, action, operation, postfix, **kwargs):
        interface = kwargs["interface"] if "interface" in kwargs and kwargs["interface"] else "lo"
        src = kwargs["src"] if "src" in kwargs and kwargs["src"] else None
        rate = kwargs["rate"] if "rate" in kwargs and kwargs["rate"] else 5
        if operation == "start":
            cmd = "{tc} qdisc replace dev {interface} root netem {action} {rate}{postfix}".format(tc=self.tc, interface=interface, rate=rate, action=action, postfix=postfix)
        elif operation == "stop":
            #cmd = "{tc} qdisc del dev {interface} root netem corrupt {rate}%".format(tc=self.tc, interface=interface, rate=rate)
            cmd = "{tc} qdisc replace dev {interface} root netem {action} 0{postfix}".format(tc=self.tc, interface=interface, action=action, postfix=postfix)
        #self._clear_related_cmd(cmd)
        self._execute_or_revert_cmd(cmd)
        result = self.report(interface)
        print result
        return result

    def fail(self, operation, **kwargs):
        return self.common_runner("corrupt",operation,"%", **kwargs)
    
    def delay(self, operation, **kwargs):
        return self.common_runner("delay",operation,"ms", **kwargs)
    
    def loss(self, operation, **kwargs):
        return self.common_runner("loss",operation,"%", **kwargs)
        
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
    getattr(executor, args.action)(args.operation,interface=args.interface,rate=args.rate)
