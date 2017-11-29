#!/usr/bin/env python
import argparse
import models.executor
from models.docker import docker
from models.sys import sys
from models.agent import agent
from iexceptions import ExecuteException

class DiskExecutor(models.executor.Executor):
    def __init__(self):
        pass

    def fail(self, operation, **kwargs):
        """umount"""
        dirname = kwargs["dirname"] if "dirname" in kwargs and kwargs["dirname"] else None
        if not dirname:
            return
        container_id = kwargs["container_id"] if "container_id" in kwargs and kwargs["container_id"] else None
        mount_dir = docker.get_mount_dir(container_id, dirname)
        print mount_dir
        link = sys.get_link(mount_dir)
        if operation == "start":
            agent.set_link(container_id, mount_dir, link)
            agent.unlink(dirname)
            # unlink  tikv-dir-4 && ln -s /mnt/noexist tikv-dir-4
        else:
            origin = agent.get_link(container_id, mount_dir)
            sys.relink(mount_dir, origin)
            

    def limit(self, operation, **kwargs):
        dirname = kwargs["dirname"] if "dirname" in kwargs and kwargs["dirname"] else None
        if not dirname:
            return
        container_id = kwargs["container_id"] if "container_id" in kwargs and kwargs["container_id"] else None
        rate = kwargs["rate"] if "rate" in kwargs and kwargs["rate"] else 1048576
        if rate == "None":
            rate = 1048576
        if operation == "stop":
            rate = 0
        cgroup_path = docker.get_cgroup_path(container_id) + "/" + "blkio.throttle.read_bps_device"
        mount_dir = docker.get_mount_dir(container_id, dirname)
        mount_dir = sys.get_link(mount_dir)
        block = sys.get_block_by_mount_in_docker(mount_dir)
        block_num = sys.get_block_number(block)
        data = block_num + " " + str(rate)
        sys.write_to_cgroup(data, cgroup_path)
        cgroup_path = docker.get_cgroup_path(container_id) + "/" + "blkio.throttle.write_bps_device"
        sys.write_to_cgroup(data, cgroup_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Network Injection Simulation')
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
        '-d',
        '--dirname',
        dest='dirname',
        help='which dirname to operation')

    parser.add_argument(
        '-r',
        '--rate',
        dest='rate',
        help='how much rate to operation')

    parser.add_argument(
        '-c',
        '--containerid',
        dest='containerid',
        help='which containerid to operation ')

    args = parser.parse_args()
    executor = DiskExecutor()
    try:
        getattr(executor, args.action)(
            args.operation,
            action=args.action,
            dirname=args.dirname,
            rate=args.rate,
            container_id=args.containerid)
    except ExecuteException as e:
        print e._msg
        exit(1)