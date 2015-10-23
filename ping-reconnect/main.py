# -*- coding: UTF-8 -*-

#install_twisted_rector must be called before importing the reactor
from kivy.support import install_twisted_reactor
install_twisted_reactor()

import os
import json

from kivy.app import App
from kivy.logger import Logger as log

from autobahn.twisted.wamp import ApplicationSession
from twisted.internet.defer import inlineCallbacks
from twisted.internet.protocol import ReconnectingClientFactory
from autobahn.websocket.protocol import parseWsUrl
from autobahn.twisted import websocket
from autobahn.wamp import types


class Client(ApplicationSession):

    def __init__(self, config):
        ApplicationSession.__init__(self, config)

    @inlineCallbacks
    def onJoin(self, details):
        base = "ch.rentouch.app.whiteboard"
        uri = "%s.join_session" % base
        my_id = yield self.call(uri, 1234, "abcd")


# WAMP CONNECTION -------------------------------------------------------------
class MyClientFactory(websocket.WampWebSocketClientFactory, ReconnectingClientFactory):
    maxDelay = 30
    last_connector = None

    def __init__(self, *args, **kwargs):
        websocket.WampWebSocketClientFactory.__init__(self, *args, **kwargs)

    def startedConnecting(self, connector):
        log.debug("Start connection attempt")
        self.last_connector = connector
        ReconnectingClientFactory.startedConnecting(self, connector)

    def clientConnectionFailed(self, connector, reason):
        self.last_connector = connector
        log.error("Client connection failed. Will try again...")
        self.retry(connector)
        #ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)

    def clientConnectionLost(self, connector, reason):
        self.last_connector = connector
        log.error("Client connection lost. Will try to reconnect...")
        self.retry(connector)
        #ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

# Get URI
url = u"wss://wamp.rentouch.ch/ws/"
#url = u"ws://localhost:8080"
if os.path.isfile("/etc/rentouch/wamp.json"):
    with open('/etc/rentouch/wamp.json', 'r') as f:
        data = json.load(f)
        if "url" in data:
            url = u""+data["url"]

## 1) create a WAMP application session factory
component_config = types.ComponentConfig(realm="realm1")
client = Client(component_config)


# Hack to have only one Client inst. and no client_factory
def _get_session():
    return client

## 2) create a WAMP-over-WebSocket transport client factory
transport_factory = MyClientFactory(_get_session, url=url, debug=True)
transport_factory.setProtocolOptions(autoPingInterval=1, autoPingTimeout=3)

from twisted.internet import reactor
import txaio
txaio.use_twisted()
txaio.config.loop = reactor
txaio.start_logging(level='debug')

## 3) start the client from a Twisted endpoint
isSecure, host, port, resource, path, params = parseWsUrl(url)
transport_factory.host = host
transport_factory.port = port
WAMP_connector = websocket.connectWS(transport_factory, timeout=5)


class BrainApp(App):
    def build(self):
        from kivy.uix.widget import Widget
        return Widget()


if __name__ == '__main__':
    BrainApp().run()