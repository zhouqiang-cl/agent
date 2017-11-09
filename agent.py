import os

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
        if "ip" in kwargs and kwargs["ip"]:
            from models.docker import docker
            from models.arg import arg
            interface = docker.get_netdev_for_ip(kwargs["ip"])
            cmd = arg.replace_argument(cmd, "-a", interface)
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
        ip = self.get_argument("ip",None)
        result = yield self._runner.run_cmd(cmd, ip=ip)
        print result
        self.finish(result)

def make_app():
    return tornado.web.Application([
        (r"/execute", AgentHandler),
    ],
    )

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
