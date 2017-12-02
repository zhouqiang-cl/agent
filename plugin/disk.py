#!/usr/bin/env python
import argparse
import models.executor
from models.docker import docker
from models.sys import sys
from models.agent import agent
from iexceptions import ExecuteException
from libs.unit import to_byte

class DiskExecutor(models.executor.Executor):
    def __init__(self):
        pass

    def full(self, operation, **kwargs):
        """
            this will take much time
            dd if=/dev/zero of=/mnt/disk6/tst.img bs=4M count=60K
        """
        # pass
        dirname = kwargs["dirname"] if "dirname" in kwargs and kwargs["dirname"] else None
        if not dirname:
            return
        mount_dir = docker.get_mount_dir(container_id, dirname)
        agent.set_full(mount_dir)


    def fail(self, operation, **kwargs):
        """disk use limit iops for failed, in the future , we will use debugfs to simulation"""
        dirname = kwargs["dirname"] if "dirname" in kwargs and kwargs["dirname"] else None
        if not dirname:
            return
        container_id = kwargs["container_id"] if "container_id" in kwargs and kwargs["container_id"] else None
        rate = 1
        cgroup_path = docker.get_blkio_cgroup_path(container_id) + "/" + "blkio.throttle.read_iops_device"
        mount_dir = docker.get_mount_dir(container_id, dirname)
        block = sys.get_block_by_mount_in_docker(mount_dir)
        block_num = sys.get_block_number(block)
        data = block_num + " " + str(rate)
        sys.write_to_cgroup(data, cgroup_path)
        cgroup_path = docker.get_blkio_cgroup_path(container_id) + "/" + "blkio.throttle.write_iops_device"
        sys.write_to_cgroup(data, cgroup_path)    

    def limit(self, operation, **kwargs):
        dirname = kwargs["dirname"] if "dirname" in kwargs and kwargs["dirname"] else None
        if not dirname:
            return
        container_id = kwargs["container_id"] if "container_id" in kwargs and kwargs["container_id"] else None
        rate = kwargs["rate"] if "rate" in kwargs and kwargs["rate"] else "1048576"
        if operation == "stop":
            rate = "0"
        rate = to_byte(rate)
        cgroup_path = docker.get_blkio_cgroup_path(container_id) + "/" + "blkio.throttle.read_bps_device"
        mount_dir = docker.get_mount_dir(container_id, dirname)
        block = sys.get_block_by_mount_in_docker(mount_dir)
        block_num = sys.get_block_number(block)
        data = block_num + " " + str(rate)
        sys.write_to_cgroup(data, cgroup_path)
        cgroup_path = docker.get_blkio_cgroup_path(container_id) + "/" + "blkio.throttle.write_bps_device"
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
        help='how much rate to operation, support K/M/G, default is B')

    parser.add_argument(
        '-c',
        '--container_id',
        dest='container_id',
        help='which container id to operation ')

    args = parser.parse_args()
    executor = DiskExecutor()
    try:
        getattr(executor, args.action)(
            args.operation,
            action=args.action,
            dirname=args.dirname,
            rate=args.rate,
            container_id=args.container_id)
    except ExecuteException,MountDirNotFoundException,InspectDockerError as e:
        print e._msg
        exit(1)