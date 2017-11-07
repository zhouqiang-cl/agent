import os

from concurrent.futures import ThreadPoolExecutor
import tornado.ioloop
import tornado.web
import tornado.concurrent
import tornado.gen

from libs.misc import system

class Runner(object):
    executor = ThreadPoolExecutor(max_workers=24)
    def __init__(self):
        self._plugin_dir = "./plugin"
        self._running_queue = []
        self._isolate = []
    @tornado.concurrent.run_on_executor
    def _async_execute(self,cmd):
        plugin = cmd.split()[0]
        if plugin in self._isolate:
            self._running_queue[plugin] += 1
        # result = system(cmd)
        print cmd
        self._running_queue[plugin] -= 1
        return result

    @tornado.gen.coroutine
    def run_cmd(self, cmd):
        if not self._check_valid(cmd):
            raise CommandInvalideException(cmd = cmd)
        plugin = cmd.split()[0]
        if not os.path.exists(self._plugin_dir + "/" + plugin):
            raise PluginNotExistsException(plugin_name = plugin_name)
        if self._running_queue[plugin] > 1:
            raise PluginAlreadyInUseException(plugin_name = plugin_name)
        result = self._async_execute(cmd)
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
