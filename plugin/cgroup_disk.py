#!/usr/bin/env python
import argparse
import models.executor
from models.docker import docker
from models.sys import sys
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
    
    def limit(self, operation, **kwargs):
        dirname = kwargs["dirname"] if "dirname" in kwargs and kwargs["dirname"] else None
        if not dirname:
            return
        container_id = kwargs["container_id"] if "container_id" in kwargs and kwargs["container_id"] else None
        rate = kwargs["rate"] if "rate" in kwargs and kwargs["rate"] else 1048576
        if rate == "None":
            rate = 1048576
        # print rate
        if operation == "stop":
            rate = 0
        cgroup_path = docker.get_cgroup_path(container_id) + "/" + "blkio.throttle.read_bps_device"
        mount_dir = docker.get_mount_dir(container_id, dirname)
        print mount_dir
        mount_dir = sys.get_link(mount_dir)
        print mount_dir
        block = sys.get_block_by_mount_in_docker(mount_dir)
        print block
        block_num = sys.get_block_number(block)
        data = block_num + " " + str(rate)
        sys.write_to_cgroup(data, cgroup_path)
        cgroup_path = docker.get_cgroup_path(container_id) + "/" + "blkio.throttle.write_bps_device"
        sys.write_to_cgroup(data, cgroup_path)
    def full(self, operation, **kwargs):
        """dd if= of="""
        pass

    def quota(self, operation, **kwargs):
        pass

    def record(self):
        pass
if __name__ == "__main__":
    # executor = DiskExecutor()
    # executor
    parser = argparse.ArgumentParser(description='Network Injection Simulation')
    parser.add_argument('operation', metavar='start/stop/status',
                        help='operations')
    parser.add_argument('-a','--action', dest='action',metavar='fail/loss/limit/forbid',
                                    help='which action to take ')
    parser.add_argument('-d','--dirname', dest='dirname',
                        help='which dirname to operation ')
    parser.add_argument('-r','--rate', dest='rate',
                        help='how much rate to operation ')
    parser.add_argument('-c','--containerid', dest='containerid',
                        help='which containerid to operation ')

    args = parser.parse_args()
    executor = DiskExecutor()
    getattr(executor, args.action)(args.operation,action=args.action,dirname=args.dirname,rate=args.rate,container_id=args.containerid)

