#!/usr/bin/env python

# Alchemy part
from __future__ import print_function
from apiclient.errors import HttpError
from alchemyapi import AlchemyAPI
import json
import sys

from youtube import get_video
from artist import extractArtists, AudioDB_getAlbums, AudioDB_getTracks

from twisted.internet.defer import inlineCallbacks
from twisted.logger import Logger


from twisted.internet import reactor
from autobahn.twisted.util import sleep
from autobahn.wamp.exception import ApplicationError
from autobahn import wamp
from autobahn.twisted.wamp import ApplicationSession
from autobahn.wamp.types import CallOptions

class Actionner(ApplicationSession):
    def __init__(self, config):
        super(ApplicationSession, self).__init__(config)

    @inlineCallbacks
    def onJoin(self, details):
        res = yield self.register(self)
        print("Actionner Backend: {} procedures registered!".format(len(res)))
        yield

    @inlineCallbacks
    def onLeave(self, details):
        yield

    @inlineCallbacks
    def onDisconnect(self):
        reactor.stop()
        yield

    @wamp.register(u'actionner.trigger')
    def trigger(self, text):
        print('Request: {0}'.format(text))
        try:
            alchemyapi = AlchemyAPI()
        except Exception as e:
            print('Could not connect to AlchemyAPI. Details: {}'.format(e))
        relations = alchemyapi.relations('text', text)

        action = None # Action to take. Only 'Play' implemented so far.
        format = None # In pratice 'album' or 'track'.
        toPlay = None # Album or track name.

        if relations['status'] == 'OK':
            print('## Object ##')
            print(json.dumps(relations, indent=4))
            for relation in relations['relations']:
                if 'action' in relation:
                    print('Action: ', relation['action']['text'].encode('utf-8'))
                    if relation['action']['verb']['text'] in ('play', 'listen'):
                        action = 'PLAY'
        else:
            print('Error in relation extaction call: ', relations['statusInfo'])

        # If no action found, we abort.
        if not action:
            print('Could not find any action to take.')
            return

        # Detect the artist to play
        artists = []
        artist = None
        keywords = alchemyapi.keywords('text', text, {'sentiment': 1})

        if keywords['status'] == 'OK':
            print('## Response Object ##')
            print(json.dumps(keywords, indent=4))

            for keyword in keywords['keywords']:
                artists.append((keyword['relevance'], extractArtists(keyword['text'].encode('utf-8'))))
        else:
            print('Error in keyword extaction call: ', keywords['statusInfo'])

        print('Action: {0}'.format(action))
        print('Artists extracted from the request: {0}'.format(' '.join([str(n)+'('+c+')' for c,n in artists])))
        for e in artists:
            if not e[1]:
                continue
            else:
                artist = e[1][-1]
                break
        if not artist:
            print('Could not find any artist.')
            return
        print('Selected artist: {0}'.format(artist))
        print('To simplify I assume you are looking for an album and not a track.')
        albums = AudioDB_getAlbums(artist)

        if not albums:
            print('Could not find any album for {0}'.format(artist))
            return

        album = None
        for name, item in albums.iteritems():
            if name in text:
                album = item
                break

        if not album:
            print('Could not find any specific album, so will try to extract a track from the full discography')
            for _, album in albums.iteritems():
                tracks = AudioDB_getTracks(album['id'])
                for track in tracks:
                    if track in text:
                        format = 'song'
                        toPlay = track
                        break
            if not toPlay:
                format = 'album'
                toPlay = albums.itervalues().next()['name'] # We assume the artist has at least one album
                print('Could not find any album or track so I will play the album {0}'.format(toPlay))
        else:
            print('Selected album is {0}. Now, check the tracks.'.format(album))
            tracks = AudioDB_getTracks(album['id'])
            for track in tracks:
                if track in text:
                    format = 'song'
                    toPlay = track
                    break

            if not toPlay:
                print("Could not find a track, so I will play the whole album.")
                toPlay = album['name']
                format = 'album'
            else:
                print('The song to play will be {0}'.format(toPlay))


        print('Selected album/track: {0}'.format(toPlay))
        hint = 'album' if format == 'album' else ''
        args = {'q': ' '.join([toPlay, artist, hint]),
                'max_results': 1}

        print('Youtube query: {0}'.format(args['q']))

        try:
            video = get_video(args)
            if video:
                video_ID = video[0]
                print('Youtube Video ID: {0}'.format(video_ID))
                uri = 'http://www.youtube.com/watch?v={0}'.format(video_ID)
                res = self.call('music.fromyoutube', uri)
            else:
                print("Could not find any stream.")
        except HttpError, e:
            print("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))
