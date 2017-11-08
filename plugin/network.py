#!/usr/bin/env python
"""
Executor
  NetworkExecutor
  DiskExecutor
  CpuExecutor
  MemExecutor
  ...
"""
class Executor(object):
    """as network"""
    def __init__(self):
        self.tc = "tc"
        
    def fail(self, operation, **kwargs):
        interface = kwargs["interface"] if "interface" in kwargs else "eth0"
        src = kwargs["src"] if "src" in kwargs else None
        rate = kwargs["rate"] if "rate" in kwargs else 5
        cmd = "{tc} qdisc {operation} dev {interface} root netem corrupt {rate}%".format(tc=self.tc, interface=interface, rate=rate, operation=operation)
        self._clear_related_cmd()
        return self._execute_or_revert_cmd(cmd)
    
    def delay(self, operation, **kwargs):
        interface = kwargs["interface"] if "interface" in kwargs else "eth0"
        src = kwargs["src"] if "src" in kwargs else None
        rate = kwargs["rate"] if "rate" in kwargs else 5 # in ms
        cmd = "tc qdisc add dev lo root netem delay 3000ms"
        self._clear_related_cmd()
        return self._execute_or_revert_cmd(cmd)
    
    def loss(self, operation, **kwargs):
        pass
        
    def forbid(self, operation):
        pass
    
    def report(self):
        pass
    
    def record(self):
        pass
