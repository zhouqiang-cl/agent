#!/usr/bin/env python
import argparse
import models.executor
class DiskExecutor(models.executor.Executor):
    """as disk"""
    def __init__(self):
        pass 

    def fail(self, operation, **kwargs):
        pass
    
    def delay(self, operation, **kwargs):
        pass
   
    def full(self, operation, **kwargs):
        pass

    def quota(self, operation, **kwargs):
        pass
        
    def _report_disk(self, interface):
        pass

    def record(self):
        pass
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Network Injection Simulation')
    parser.add_argument('operation', metavar='start/stop/status',
                        help='operations')
    parser.add_argument('-a','--action', dest='action',metavar='fail/loss/delay/limit/forbid',
                                    help='which action to take ')
    parser.add_argument('-d','--disk', dest='disk',
                        help='which interface to operation ')
    parser.add_argument('-r','--rate', dest='rate',
                        help='how much rate to operation ')

    args = parser.parse_args()
    executor = DiskExecutor()
    getattr(executor, args.action)(args.operation,action=args.action,disk=args.disk,rate=args.rate)
