import os
import json

from concurrent.futures import ThreadPoolExecutor
import tornado.ioloop
import tornado.web
import tornado.concurrent
import tornado.gen

from libs.misc import system,mkdirs
from iexceptions import PluginNotExistsException,PluginSingletonException,CommandInvalidateException,ContainerLockedException

class Runner(object):
    executor = ThreadPoolExecutor(max_workers=24)
    def __init__(self):
        self._plugin_dir = "./plugin"
        self._running_queue = {}
        self._isolate = []
        self._lock_dir = "./lock"
    @tornado.concurrent.run_on_executor
    def _async_execute(self,cmd):
        plugin = cmd.split()[0]
        cmd = self._plugin_dir + "/" + cmd
        if plugin in self._isolate:
            self._running_queue[plugin] += 1
            print "run {cmd}".format(cmd=cmd)
            rc,so,se = system(cmd)
            print "output",rc,so,se
            self._running_queue[plugin] -= 1
        else:
            print "run {cmd}".format(cmd=cmd)
            rc,so,se = system(cmd)
            print "output",rc,so,se
        return {"result":True}

    def require_lock(self, container_id, lock_msg):
        lock_dir = self._lock_dir + "/" + container_id
        mkdirs(lock_dir)
        lock_path = self._lock_dir + "/" + container_id + "/lock"
        if os.path.exists(lock_path):
            with open(lock_path, 'r') as f:
                lock_msg = f.read().strip()
            raise ContainerLockedException(container_id=container_id, lock_msg=lock_msg)
        with open(lock_path, 'w') as f:
            f.write(lock_msg)
        return True

    @staticmethod
    def get_lock_msg(lock_path):
        with open(lock_path, 'r') as f:
            lock_msg = f.read().strip()
        return lock_msg.strip()
    def delete_lock(self, container_id, lock_msg):
        """
            disk:operation:dirname
            network:operation:ip
        """ 
        lock_path = self._lock_dir + "/" + container_id + "/lock"
        origin_lock_msg = self.get_lock_msg(lock_path)
        if origin_lock_msg != lock_msg:
            raise DeleteLockMsgIllegalException(lock_msg=lock_msg, origin_lock_msg= origin_lock_msg)
        os.remove(lock_path)


    def singleton_running(self,plugin):
        if plugin in self._running_queue and self._running_queue[plugin] > 0:
            return False
        return True

    @tornado.gen.coroutine
    def run_cmd(self, cmd, **kwargs):
        if not self._check_valid(cmd):
            raise CommandInvalidateException(cmd = cmd)
        plugin = cmd.split()[0]
        if not os.path.exists(self._plugin_dir + "/" + plugin):
            raise PluginNotExistsException(plugin_name = plugin)
        if not self.singleton_running(plugin):
            raise PluginSingletonException(plugin_name = plugin)
        result = yield self._async_execute(cmd)
        raise tornado.gen.Return(result)

    def _check_valid(self, cmd):
        return True

runner = Runner()

class DiskHandler(tornado.web.RequestHandler):
    def prepare(self):
        self._runner = runner
    @tornado.gen.coroutine
    def get(self):
        """./plugin/cgroup_disk.py -a limit -d /test-pd -c b63085b8ad9b540ee3603572ca95c2552061c1415564834c8ca3c9e578e7400c start"""
        action = self.get_argument("action")
        dirname = self.get_argument("dirname")
        container_id = self.get_argument("container_id")
        operation = self.get_argument("operation")
        rate = self.get_argument("rate",None)
        cmd = "cgroup_disk.py -a {action} -d {dirname} -c {container_id} -r {rate} {operation}".format(action=action, dirname=dirname, 
            container_id=container_id, operation=operation, rate=rate)
        if operation == "start":
            msg = "disk:" + container_id + ":" + dirname
            self._runner.require_lock(container_id, msg )
        elif operation == "stop":
            msg = "disk:" + container_id + ":" + dirname
            self._runner.delete_lock(container_id, msg )
        result = yield self._runner.run_cmd(cmd)
        self.finish(result)

class NetworkHandler(tornado.web.RequestHandler):
    def prepare(self):
        self._runner = runner
    @tornado.gen.coroutine
    def get(self):
        action = self.get_argument("action")
        container_ip = self.get_argument("container_ip")
        container_id = self.get_argument("container_id")
        operation = self.get_argument("operation")
        rate = self.get_argument("rate",None)
        cmd = "network.py -a {action} --container_ip {container_ip} -r {rate} {operation}".format(action=action, 
            container_ip=container_ip, operation=operation, rate=rate)
        if operation == "start":
            msg = "network:" + container_id + ":" + container_ip
            self._runner.require_lock(container_id, msg )
        elif operation == "stop":
            msg = "network:" + container_id + ":" + container_ip
            self._runner.delete_lock(container_id, msg )
        result = yield self._runner.run_cmd(cmd)
        self.finish(result)

class SupportApis(tornado.web.RequestHandler):
    def get(self):
        apis = []
        disk = {
            "url":"/api/v1/disk",
            "description":"disk injection for docker",
            "args":{
                "action":["limit","full","error"],
                "dirname":"",
                "container_id":"",
                "rate":"",
                "operation":["start","stop","status"]
            }
        }
        network = {
            "url":"/api/v1/network",
            "description":"network injection for docker",
            "args":{
                "action":["delay","fail", "loss","limit","forbid"],
                "container_id":"",
                "container_ip":"",
                "rate":"",
                "operation":["start","stop","status"]
            }
        }
        apis.append(disk)
        apis.append(network)
        self.finish(json.dumps(apis))


def make_app():
    return tornado.web.Application([
        (r"/api/v1/disk", DiskHandler),
        (r"/api/v1/network", NetworkHandler),
        (r"/api/v1/supportapis", SupportApis)
    ],
    )

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
