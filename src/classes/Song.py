from Artist import Artist
from sets import Set
from Genre import Genre
class Song:
    #orderedFeatures - list of ordered features used for scaling and classification
        def __init__(self, id, remoteId, name, features, cluster=-1, artists=[], album="", duration=0, previewUrl=""):
            self.id = id
            self.remoteId = remoteId
            self.name = name
            self.features = features
            self.cluster = cluster
            self.artists = artists
            self.duration = duration
            self.album = album
            self.previewUrl = previewUrl
            self.featuresToList()


        def toDictionary(self):
            song = {}
            song["id"] = self.id
            song["cluster"] = self.cluster
            song["name"] = self.name
            song['remoteId'] = self.remoteId
            song['features'] = self.features

            #song['artist'] = self.artist
            song['duration'] = self.duration
            song['album'] = self.album
            song['previewUrl'] = self.previewUrl
            song['artists'] = []
            for a in self.artists:
                song['artists'].append(a.toDictionary())
            return song
 
        def getGenres(self):
            genres = []
            for a in self.artists:
                for g in a.genres:
                    genres.append(g)
            return genres
                
        def tokenizeGenres(self):
            genres = self.getGenres()
            genresTokenized = []
            for g in genres:
                splitted = g.split()
                if(len(splitted) > 1):
                    for token in splitted:
                        genresTokenized.append(token)
                else:
                    genresTokenized.append(g)

            genresUnique = Set(genresTokenized)
            return genresUnique
        
        def featuresToList(self):
            list = []
            list.append(self.features["acousticness"])
            list.append(self.features["danceability"])
            list.append(self.features["energy"])
            list.append(self.features["instrumentalness"])
            list.append(self.features["track_key"])
            list.append(self.features["liveness"])
            list.append(self.features["loudness"])
            list.append(self.features["mode"])
            list.append(self.features["popularity"])
            list.append(self.features["speechiness"])
            list.append(self.features["tempo"])
            list.append(self.features["time_signature"])
            list.append(self.features["valence"])
            list.append(self.features["album_year"])
            self.orderedFeatures  = list
        
        #+ '\nartist: ' + self.artist +
        def toString(self):
            return 'Name: ' + str(self.name) + '\nid ' + str(self.id) + '\nremote id: ' + str(self.remoteId) + '\nfeatures: ' + str(self.features) + '\ncluster: ' + str(self.cluster) + '\nduration: ' + str(self.duration) + '\nalbum: ' + str(self.album)