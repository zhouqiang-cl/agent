import os
import json

from concurrent.futures import ThreadPoolExecutor
import tornado.ioloop
import tornado.web
import tornado.concurrent
import tornado.gen

import libs.log
from models.docker import docker
from libs.misc import system, mkdirs
from iexceptions import PluginNotExistsException, \
        PluginSingletonException, \
        CommandInvalidateException, \
        ContainerLockedException, \
        ExecuteException
from libs.log import app_log

class Runner(object):
    executor = ThreadPoolExecutor(max_workers=24)
    def __init__(self):
        self._plugin_dir = "./plugin"
        self._running_queue = {}
        self._isolate = []
        self._lock_dir = "./data"

    @tornado.concurrent.run_on_executor
    def _async_execute(self,cmd):
        plugin = cmd.split()[0]
        cmd = self._plugin_dir + "/" + cmd
        rc,so,se = system(cmd)
        if rc:
            raise ExecuteException(msg = so)
        return {"result":"success"}

    def check_lock(self, container_id):
        lock_dir = self._lock_dir + "/" + container_id
        mkdirs(lock_dir)
        lock_path = self._lock_dir + "/" + container_id + "/lock"
        if os.path.exists(lock_path):
            return False
        return True

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

    def get_container_lock_msg(self, container_id):
        lock_path = self._lock_dir + "/" + container_id + "/lock"
        return self.get_lock_msg(lock_path)

    def delete_lock(self, container_id, lock_msg):
        """
            disk:operation:dirname
            network:operation:ip
        """ 
        lock_path = self._lock_dir + "/" + container_id + "/lock"
        origin_lock_msg = self.get_lock_msg(lock_path)
        if origin_lock_msg != lock_msg:
            raise DeleteLockMsgIllegalException(lock_msg=lock_msg, origin_lock_msg= origin_lock_msg)
        try:
            os.remove(lock_path)
        except:
            raise DeleteLockMsgIllegalException(lock_msg="Unknow Delete Lock Error", origin_lock_msg= origin_lock_msg)


    @tornado.gen.coroutine
    def run_cmd(self, cmd, **kwargs):
        if not self._check_valid(cmd):
            raise CommandInvalidateException(cmd = cmd)
        plugin = cmd.split()[0]
        if not os.path.exists(self._plugin_dir + "/" + plugin):
            raise PluginNotExistsException(plugin_name = plugin)
        result = yield self._async_execute(cmd)
        raise tornado.gen.Return(result)

    def _check_valid(self, cmd):
        return True

runner = Runner()

class PluginHanlder(tornado.web.RequestHandler):
    def prepare(self):
        self._runner = runner

    @tornado.gen.coroutine
    def run_plugin(self, container_id, plugin, action, operation, plugin_cmd, add_on):
        app_log.info("start run plugin:{plugin} cmd:{plugin_cmd}".format(plugin=plugin, plugin_cmd=plugin_cmd))
        if not docker.is_exist(container_id):
            self.finish({"status":"failed","msg":"can not found container_id in host"})
        if operation == "start":
            if self._runner.check_lock(container_id):
                msg = plugin + ":" + action + ":" + add_on
                try:
                    app_log.info("container_id:{container_id} operation:require_lock status:start".format(container_id=container_id))
                    self._runner.require_lock(container_id, msg)
                    app_log.info("container_id:{container_id} operation:require_lock status:success".format(container_id=container_id))
                    app_log.info("container_id:{container_id} operation:run plugin status:start".format(container_id=container_id))
                    result = yield self._runner.run_cmd(cmd)
                    app_log.info("container_id:{container_id} operation:run plugin status:success".format(container_id=container_id))
                    self.finish(result)
                except Exception as e:
                    app_log.error(str(e))
                    app_log.error("container_id:{container_id} operation:none status:failed msg:{msg}".format(container_id=container_id,msg = e._msg))
                    app_log.info("container_id:{container_id} operation:delete_lock status:start msg:due to exception above".format(container_id=container_id))
                    self._runner.delete_lock(container_id, msg )
                    app_log.info("container_id:{container_id} operation:delete_lock status:success".format(container_id=container_id))
                    self.finish({"status":"failed","msg":e._msg})
            else:
                app_log.info("container_id:{container_id} operation:get_lock_msg status:start msg:container locked".format(container_id=container_id))
                lock_msg = self._runner.get_container_lock_msg(container_id).split(":")
                app_log.info("container_id:{container_id} operation:get_lock_msg status:success")
                msg = "there is a {job_type} job running for {container_id},operation is {operation}, additional msg is {add_msg}".format(
                    job_type = lock_msg[0], container_id=container_id, operation=lock_msg[1], add_msg = lock_msg[2]) 
                self.finish({"status":"failed","msg":msg})
        elif operation == "stop":
            msg = plugin +":" + action + ":" + add_on
            try:
                app_log.info("container_id:{container_id} operation:run plugin status:start".format(container_id=container_id))
                result = yield self._runner.run_cmd(cmd)
                self._runner.delete_lock(container_id, msg )
                app_log.info("container_id:{container_id} operation:run plugin status:success".format(container_id=container_id))
                self.finish(result)
            except Exception as e:
                app_log.error("container_id:{container_id} operation:none status:failed msg:{msg}".format(container_id=container_id,msg = e._msg))

class DiskHandler(PluginHanlder):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        """./plugin/cgroup_disk.py -a limit -d /test-pd -c b63085b8ad9b540ee3603572ca95c2552061c1415564834c8ca3c9e578e7400c start"""
        action = self.get_argument("action")
        dirname = self.get_argument("dirname")
        container_id = self.get_argument("container_id")
        operation = self.get_argument("operation")
        rate = self.get_argument("rate",None)
        if rate:
            cmd = "disk.py -a {action} -d {dirname} -c {container_id} -r {rate} {operation}".format(action=action, dirname=dirname, 
                container_id=container_id, operation=operation, rate=rate)
        else:
            cmd = "disk.py -a {action} -d {dirname} -c {container_id} {operation}".format(action=action, dirname=dirname, 
                container_id=container_id, operation=operation)
        self.run_plugin(container_id, "disk", action, operation, cmd,dirname)

class NetworkHandler(PluginHanlder):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        action = self.get_argument("action")
        container_ip = self.get_argument("container_ip")
        container_id = self.get_argument("container_id")
        operation = self.get_argument("operation")
        rate = self.get_argument("rate",None)
        if rate:
            cmd = "network.py -a {action} --container_ip {container_ip} -r {rate} {operation}".format(action=action, 
                container_ip=container_ip, operation=operation, rate=rate)
        else:
            cmd = "network.py -a {action} --container_ip {container_ip} -r {rate} {operation}".format(action=action, 
                container_ip=container_ip, operation=operation, rate=rate)
        self.run_plugin(container_id, "network", action, operation, cmd, container_ip)

class CpuHandler(PluginHanlder):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        action = self.get_argument("action")
        # container_ip = self.get_argument("container_ip")
        container_id = self.get_argument("container_id")
        operation = self.get_argument("operation")
        rate = self.get_argument("rate",None)
        if rate:
            cmd = "cpu.py -a {action} --containerid {container_id} -r {rate} {operation}".format(action=action, 
                container_id=container_id, operation=operation, rate=rate)
        else:
            cmd = "cpu.py -a {action} --containerid {container_id} {operation}".format(action=action, 
                container_id=container_id, operation=operation)
        self.run_plugin(container_id, "cpu", action, operation, cmd, "noop")
class MemoryHandler(PluginHanlder):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        action = self.get_argument("action")
        # container_ip = self.get_argument("container_ip")
        container_id = self.get_argument("container_id")
        operation = self.get_argument("operation")
        rate = self.get_argument("rate",None)
        if rate:
            cmd = "mem.py -a {action} --containerid {container_id} -r {rate} {operation}".format(action=action, 
                container_id=container_id, operation=operation, rate=rate)
        else:
            cmd = "mem.py -a {action} --containerid {container_id} {operation}".format(action=action, 
                container_id=container_id, operation=operation)
        self.run_plugin(container_id, "cpu", action, operation, cmd, "noop")

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
        mem = {
            "url":"/api/v1/memory",
            "description":"memory injection for docker",
            "args":{
                "action":["limit"],
                "container_id":"",
                "rate":"",
                "operation":["start","stop","status"]
            }
        }
        cpu = {
            "url":"/api/v1/cpu",
            "description":"cpu injection for docker",
            "args":{
                "action":["limit"],
                "container_id":"",
                "rate":"",
                "operation":["start","stop","status"]
            }
        }
        apis.append(disk)
        apis.append(network)
        apis.append(mem)
        apis.append(cpu)
        self.finish(json.dumps(apis))


def make_app():
    return tornado.web.Application([
        (r"/api/v1/disk", DiskHandler),
        (r"/api/v1/network", NetworkHandler),
        (r"/api/v1/cpu", CpuHandler),
        (r"/api/v1/memory", MemoryHandler),
        (r"/api/v1/supportapis", SupportApis)
    ],
    )

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
