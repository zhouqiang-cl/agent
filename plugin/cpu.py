#!/usr/bin/env python
import argparse
import models.executor
from models.docker import docker
from models.sys import sys
from models.agent import agent
from iexceptions import ExecuteException,CheckException,InspectDockerError

class CpuExecutor(models.executor.Executor):
    def __init__(self):
        pass


    def limit(self, operation, **kwargs):
        container_id = kwargs["container_id"] if "container_id" in kwargs and kwargs["container_id"] else None
        rate = kwargs["rate"] if "rate" in kwargs and kwargs["rate"] else -1
        if operation == "stop":
            rate = -1
        if int(rate) > 100:
            raise CheckException(msg = "rate shold not bigger then 100")
        cgroup_path = docker.get_cpu_cgroup_path(container_id) + "/" + "cpu.cfs_quota_us"
        data = rate
        if data != -1:
            data = int(rate)*1000
        sys.write_to_cgroup(data, cgroup_path)
        cgroup_path = docker.get_cpu_cgroup_path(container_id) + "/" + "cpu.cfs_period_us"
        data = 100000
        sys.write_to_cgroup(data, cgroup_path)
        # cpu.cfs_period_us

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Cpu Injection Simulation')
    parser.add_argument(
        'operation',
        metavar='start/stop/status',
        help='operations')

    parser.add_argument(
        '-a',
        '--action',
        dest='action',
        metavar='fail/limit',
        help='which action to take ')

    parser.add_argument(
        '-r',
        '--rate',
        dest='rate',
        help='how much rate to operation')

    parser.add_argument(
        '-c',
        '--container_id',
        dest='container_id',
        help='which container id to operation ')

    args = parser.parse_args()
    executor = CpuExecutor()
    try:
        getattr(executor, args.action)(
            args.operation,
            action=args.action,
            rate=args.rate,
            container_id=args.container_id)
    except (ExecuteException,CheckException,InspectDockerError) as e:
        print e._msg
        exit(1)