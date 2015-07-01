from twisted.internet.defer import inlineCallbacks
from twisted.internet.task import LoopingCall
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner

import logging
import logging.config
logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
log = logging.getLogger(__name__)
log.info("***** Server started *****")

import time
import base64


class MyComponent(ApplicationSession):

    count = 0

    @inlineCallbacks
    def onJoin(self, details):
        log.info("onJoin")

        # Publish event
        def publish():
            return self.publish('com.test.hello', 'Hello, world!')
        LoopingCall(publish).start(1)

        # Remote procedure
        def long_task():
            time.sleep(6)
            return self.count
        yield self.register(long_task, 'com.test.long_task')

        def count_up():
            self.count += 1
        yield self.register(count_up, 'com.test.count_up')

        def serve_file():
            log.debug("Serve big file")
            path = "image.png"
            with open(path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read())
            return image_data
        yield self.register(serve_file, 'com.test.serve_file')

        # Subscribe
        def count_down():
            self.count -= 1
        count_down = yield self.subscribe(count_down, 'com.test.count_down')

        log.debug("Functions registered")


if __name__ == '__main__':
    runner = ApplicationRunner(
        url=u"ws://rentouch2.nine.ch:8091",
        realm=u"realm1",
        debug_wamp=False,  # optional; log many WAMP details
        debug=False,  # optional; log even more details
    )
    runner.run(MyComponent)