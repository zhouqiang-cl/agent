import os
import json

from concurrent.futures import ThreadPoolExecutor
import tornado.ioloop
import tornado.web
import tornado.concurrent
import tornado.gen

from libs.misc import system
from iexceptions import PluginNotExistsException,PluginSingletonException,CommandInvalidateException

class Runner(object):
    executor = ThreadPoolExecutor(max_workers=24)
    def __init__(self):
        self._plugin_dir = "./plugin"
        self._running_queue = {}
        self._isolate = []
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
class AgentHandler(tornado.web.RequestHandler):
    def prepare(self):
        self._runner = runner
    @tornado.gen.coroutine
    def get(self):
        cmd = self.get_argument("cmd")
        result = yield self._runner.run_cmd(cmd)
        # print result
        self.finish(result)

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
        cmd = "cgroup_disk.py -a {action} -d {dirname} -c {container_id} {operation}".format(action=action, dirname=dirname, 
            container_id=container_id, operation=operation)
        result = yield self._runner.run_cmd(cmd)
        self.finish(result)

class NetworkHandler(tornado.web.RequestHandler):
    def prepare(self):
        self._runner = runner
    @tornado.gen.coroutine
    def get(self):
        pass

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
        (r"/execute", AgentHandler),
        (r"/api/v1/disk", DiskHandler),
        (r"/api/v1/supportapis", SupportApis)
    ],
    )

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
