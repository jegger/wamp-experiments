from os import environ
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner
from twisted.internet.task import LoopingCall


class MyComponent(ApplicationSession):

    def onJoin(self, details):
        @inlineCallbacks
        def call():
            yield self.publish('com.test.count_down')
        LoopingCall(call).start(.3)


if __name__ == '__main__':
    runner = ApplicationRunner(
        url=u"ws://rentouch2.nine.ch:8091",
        realm=u"realm1",
        debug_wamp=False,  # optional; log many WAMP details
        debug=False,  # optional; log even more details
    )
    runner.run(MyComponent)