from os import environ
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner


class MyComponent(ApplicationSession):
    @inlineCallbacks
    def onJoin(self, details):
        # listening for the corresponding message from the "backend"
        # (any session that .publish()es to this topic).
        def onevent(msg):
            print("Got event: {}".format(msg))
        yield self.subscribe(onevent, 'com.test.hello')

        # call a remote procedure.
        res = yield self.call('com.test.serve_file')
        print("Got result: %s" % len(res))


if __name__ == '__main__':
    runner = ApplicationRunner(
        url=u"ws://rentouch2.nine.ch:8091",
        realm=u"realm1",
        debug_wamp=False,  # optional; log many WAMP details
        debug=False,  # optional; log even more details
    )
    runner.run(MyComponent)