#!/usr/bin/env python
import argparse
import models.executor
from models.docker import docker
from models.sys import sys
from models.agent import agent
from libs.unit import to_byte
from iexceptions import ExecuteException,InspectDockerError

class MemExecutor(models.executor.Executor):
    def __init__(self):
        pass


    def limit(self, operation, **kwargs):
        container_id = kwargs["container_id"] if "container_id" in kwargs and kwargs["container_id"] else None
        rate = kwargs["rate"] if "rate" in kwargs and kwargs["rate"] else 1048576
        data = to_byte(rate)
        if operation == "stop":
            data = 9223372036854771712
        # old_value = sys.get_cgroup_value()
        cgroup_path = docker.get_mem_cgroup_path(container_id) + "/" + "memory.limit_in_bytes"
        old_value = sys.get_cgroup_value(cgroup_path)

        if data > old_value:
            cgroup_path = docker.get_mem_cgroup_path(container_id) + "/" + "memory.memsw.limit_in_bytes"
            sys.write_to_cgroup(data, cgroup_path)
            cgroup_path = docker.get_mem_cgroup_path(container_id) + "/" + "memory.limit_in_bytes"
            sys.write_to_cgroup(data, cgroup_path)
        else:
            cgroup_path = docker.get_mem_cgroup_path(container_id) + "/" + "memory.limit_in_bytes"
            sys.write_to_cgroup(data, cgroup_path)
            cgroup_path = docker.get_mem_cgroup_path(container_id) + "/" + "memory.memsw.limit_in_bytes"
            sys.write_to_cgroup(data, cgroup_path)

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
        metavar='limit',
        help='which action to take ')

    parser.add_argument(
        '-r',
        '--rate',
        dest='rate',
        help='how much rate to operation,can use K/M/G, default in B')

    parser.add_argument(
        '-c',
        '--container_id',
        dest='container_id',
        help='which container id to operation ')

    args = parser.parse_args()
    executor = MemExecutor()
    try:
        getattr(executor, args.action)(
            args.operation,
            action=args.action,
            rate=args.rate,
            container_id=args.container_id)
    except (ExecuteException,InspectDockerError) as e:
        print e._msg
        exit(1)