from SPARQLWrapper import SPARQLWrapper, JSON
import string
import json
import urllib

AUDIODB_KEY = "your key"

def formatName(name):
    return '_'.join(name.title().split())

def SPARQL_isMusicalArtist(src):
    def isMusicalArtist(record):
        backgroundTag = ('group_or_band', 'solo_singer')
        background = record.get('background')
        if background and background['value'] in backgroundTag:
            return True
        return False

    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    sparql.setQuery('''
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX owl: <http://dbpedia.org/ontology/>
        PREFIX dbpprop: <http://dbpedia.org/property/>
        SELECT ?background
        WHERE {{
            <{0}> dbo:background ?background
        }}'''.format(src))
    sparql.setReturnFormat(JSON)
    res = sparql.query().convert()
    #print(json.dumps(res, indent=4))
    if res['results']['bindings']:
        return isMusicalArtist(res['results']['bindings'][0])
    else:
        return False

def isMusicalArtist(name):
    base_name = formatName(name)
    base_url = 'http://dbpedia.org/resource/'
    if SPARQL_isMusicalArtist(base_url + base_name):
        return True
    return SPARQL_isMusicalArtist(base_url + base_name + '_(band)')

def extractArtists(text, maxWordPerName=3):
    table = string.maketrans("","")
    artists = []
    words = text.translate(table, string.punctuation).split()
    for i in xrange(1, maxWordPerName+1):
        for j in xrange(len(words)-i+1):
            w = ' '.join(words[j:j+i])
            print w
            if isMusicalArtist(w) and w not in artists:
                artists.append(w)
    return artists

def AudioDB_getAlbums(artist):
    url = 'http://www.theaudiodb.com/api/v1/json/{1}/searchalbum.php?s={0}'.format(formatName(artist), AUDIODB_KEY)
    response = urllib.urlopen(url)
    data = json.loads(response.read())
    albums = {}
    for album in data['album']:
        albums[album['strAlbum']] = {'name': album['strAlbum'], 'id': album['idAlbum']}
    return albums

def AudioDB_getTracks(albumID):
    url = 'http://www.theaudiodb.com/api/v1/json/{1}/track.php?m={0}'.format(albumID, AUDIODB_KEY)
    response = urllib.urlopen(url)
    data = json.loads(response.read())
    tracks = [t['strTrack'] for t in sorted(data["track"], key=lambda k: k['intTrackNumber'])]
    return tracks

if __name__ == "__main__":
    albums = AudioDB_getAlbums('Megadeth')
    for _, album in albums.iteritems():
        album['tracks'] = AudioDB_getTracks(album['id'])
    print(json.dumps(albums, indent=4))
