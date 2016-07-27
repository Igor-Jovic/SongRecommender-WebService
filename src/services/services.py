from classes.Artist import Artist
from classes.Song import Song
import requests

#http://localhost:9090/sp/tracks/{trackID
#http://localhost:9090/sp/tracks?trackNames=

class Services:

    path = "http://localhost:9090/sp/tracks"
    def getSongBySongName(self, songName):
        #should perform try catch
        try:
            resp = requests.get(self.path + '?trackNames=' + songName)
        except:
            print "SpotifyProxy did not respond. Check if SpotifyProxy is running"
            return None
        if(resp.status_code == 200 and len(resp.json()) > 0):
            response = resp.json()[0]

            #should be done for each song in resp.json()
            listOfArtists = []
            artists = response['artists']
            for a in artists:
                artist = Artist(a['id'], a['name'], a['popularity'], a['genres'])
                listOfArtists.append(artist)
            songFeatures = {}
            songFeatures['acousticness'] = response['acousticness']
            songFeatures['danceability'] = response['danceability']
            songFeatures['energy'] = response['energy']
            songFeatures['instrumentalness'] = response['instrumentalness']
            songFeatures['track_key'] = response['key']
            songFeatures['liveness'] = response['liveness']
            songFeatures['loudness'] = response['loudness']
            songFeatures['mode'] = response['mode']
            songFeatures['popularity'] = response['popularity']
            songFeatures['speechiness'] = response['speechiness']
            songFeatures['tempo'] = response['tempo']
            songFeatures['time_signature'] = response['time_signature']
            songFeatures['valence'] = response['valence']
            songFeatures['album_year'] = response['albumYear']
            s = Song(-1, response['id'], response['name'], songFeatures, -1, listOfArtists, response['album'], response['duration'])
            s.previewUrl = response['previewUrl']
            return s
        return None

    def getSongByRemoteId(self, songRemoteId):
        
        try:
            resp = requests.get(self.path + '/' + songRemoteId)
        except:
            print "SpotifyProxy did not respond. Check if SpotifyProxy is running"
            return None
            
        if(resp.status_code == 200 and len(resp.json()) > 0):
            response = resp.json()

            #should be done for each song in resp.json()
            listOfArtists = [] 
            artists = response['artists']
            for a in artists:
                artist = Artist(a['id'], a['name'], a['popularity'], a['genres'])
                listOfArtists.append(artist)
            songFeatures = {}
            songFeatures['acousticness'] = response['acousticness']
            songFeatures['danceability'] = response['danceability']
            songFeatures['energy'] = response['energy']
            songFeatures['instrumentalness'] = response['instrumentalness']
            songFeatures['track_key'] = response['key']
            songFeatures['liveness'] = response['liveness']
            songFeatures['loudness'] = response['loudness']
            songFeatures['mode'] = response['mode']
            songFeatures['popularity'] = response['popularity']
            songFeatures['speechiness'] = response['speechiness']
            songFeatures['tempo'] = response['tempo']
            songFeatures['time_signature'] = response['time_signature']
            songFeatures['valence'] = response['valence']
            songFeatures['album_year'] = response['albumYear']
            s = Song(-1, response['id'], response['name'], songFeatures, -1, listOfArtists, response['album'], response['duration'])
            s.previewUrl = response['previewUrl']
            return s
	return None
