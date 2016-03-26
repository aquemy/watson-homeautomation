from twisted.internet.defer import inlineCallbacks
from twisted.logger import Logger
from twisted.internet import reactor

from autobahn.twisted.util import sleep
from autobahn.wamp.exception import ApplicationError
from autobahn import wamp
from autobahn.twisted.wamp import ApplicationSession
from autobahn.wamp.types import CallOptions

import pafy

class Music(ApplicationSession):
    def __init__(self, config):
        super(ApplicationSession, self).__init__(config)
        self.config = config

    @inlineCallbacks
    def onJoin(self, details):
        res = yield self.register(self)
        print("Music Backend: {} procedures registered!".format(len(res)))
        yield

    @inlineCallbacks
    def onLeave(self, details):
        yield

    @inlineCallbacks
    def onDisconnect(self):
        reactor.stop()
        yield

    @wamp.register(u'music.fromyoutube')
    def fromYoutube(self, uri):
        video = pafy.new(uri)
        audiostreams = video.audiostreams
        bestaudio = video.getbestaudio()
        bestaudio.download('/tmp/flux')
        # Change here to use any other player
        from sh import vlc
        vlc('/tmp/flux')

