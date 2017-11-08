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
        if plugin in self._isolate:
            self._running_queue[plugin] += 1
            print "run script plugin here..."
            self._running_queue[plugin] -= 1
        else:
            print "run script plugin here..."
        return {"result":True}

    def singleton_running(self,plugin):
        if plugin in self._running_queue and self._running_queue[plugin] > 0:
            return False
        return True

    @tornado.gen.coroutine
    def run_cmd(self, cmd):
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
