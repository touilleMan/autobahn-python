###############################################################################
##
##  Copyright (C) 2014 Tavendo GmbH
##
##  Licensed under the Apache License, Version 2.0 (the "License");
##  you may not use this file except in compliance with the License.
##  You may obtain a copy of the License at
##
##      http://www.apache.org/licenses/LICENSE-2.0
##
##  Unless required by applicable law or agreed to in writing, software
##  distributed under the License is distributed on an "AS IS" BASIS,
##  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##  See the License for the specific language governing permissions and
##  limitations under the License.
##
###############################################################################

import sys
import datetime

from twisted.python import log
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from twisted.internet.endpoints import serverFromString

from autobahn.wamp.router import RouterFactory
from autobahn.twisted.util import sleep
from autobahn.twisted.wamp import ApplicationSession
from autobahn.twisted.wamp import RouterSessionFactory
from autobahn.twisted.websocket import WampWebSocketServerFactory


class MyBackendComponent(ApplicationSession):
   """
   Application code goes here. This is an example component that provides
   a simple procedure which can be called remotely from any WAMP peer.
   It also publishes an event every second to some topic.
   """
   def onConnect(self):
      self.join("realm1")

   @inlineCallbacks
   def onJoin(self, details):

      ## register a procedure for remote calling
      ##
      def utcnow():
         print("Someone is calling me;)")
         now = datetime.datetime.utcnow()
         return now.strftime("%Y-%m-%dT%H:%M:%SZ")

      yield self.register(utcnow, 'com.timeservice.now')

      ## publish events to a topic
      ##
      counter = 0
      while True:
         self.publish('com.myapp.topic1', counter)
         print("Published event.")
         counter += 1
         yield sleep(1)


if __name__ == '__main__':

   ## 0) start logging to console
   log.startLogging(sys.stdout)

   ## 1) create a WAMP router factory
   router_factory = RouterFactory()

   ## 2) create a WAMP router session factory
   session_factory = RouterSessionFactory(router_factory)

   ## 3) Optionally, add embedded WAMP application sessions to the router
   session_factory.add(MyBackendComponent())

   ## 4) create a WAMP-over-WebSocket transport server factory
   transport_factory = WampWebSocketServerFactory(session_factory, debug = False)

   ## 5) start the server from a Twisted endpoint
   server = serverFromString(reactor, "tcp:8080")
   server.listen(transport_factory)

   ## 6) now enter the Twisted reactor loop
   reactor.run()