from database.Database import Database
import numpy as np
import os
import pandas as pd
from scipy.spatial.distance import cdist
from services.services import Services
from sklearn import preprocessing
from sklearn import tree
from sklearn.cluster import KMeans
import sys
reload(sys) 
sys.setdefaultencoding('UTF8')


class MachineLearning:
    
    
    def __init__(self):
        db = Database()
        try:
            db.createCSVForClustering() 
        except:
            print 'postoji'
        
        self.importCsvForClustering()
        #'remote_id', 'acousticness', 'danceability', 'energy', 'instrumentalness', 'track_key', 
        #'liveness', 'loudness', 'mode', 'popularity', 'speechiness', 'tempo', 'time_signature',
        #'valence', 'album_year'
        keys = self.data.columns[1:len(self.data.columns)]
        print keys
        #normalize data
        self.min_max_scaler = preprocessing.MinMaxScaler()
        print self.data[keys]
        scaledData = self.min_max_scaler.fit_transform(self.data[keys])
        scaledDf = pd.DataFrame(scaledData, columns=keys)

        scaledDf['remote_id'] = self.data['remote_id']
        self.data = scaledDf
        
        #declare supported algorithms 
        self.kmeans = KMeans(verbose=1, n_clusters=70)
        self.clf = tree.DecisionTreeClassifier()
        
        print 'finished constructor MachineLearning' 
    
    def importCsvForClustering(self):
        print 'importing csv'
        df = pd.read_csv('/Users/igor/songAtributes.csv')
        self.data = df
        

    def clusterKmeans(self, force):
        print 'Clustering'
        keys = self.data.columns[0:len(self.data.columns)-1]
        
        self.kmeans.fit(self.data[keys])
        
        labels = self.kmeans.labels_
        self.data['cluster'] = labels
        
        if(os.path.isfile('/Users/igor/songAtributesClustered.csv')):
            if(force):
                os.remove('/Users/igor/songAtributesClustered.csv')
                self.data.to_csv('/Users/igor/songAtributesClustered.csv', sep=',', encoding='utf-8')
        else:
            self.data.to_csv('/Users/igor/songAtributesClustered.csv', sep=',', encoding='utf-8')
        db = Database()
        for index, row in self.data.iterrows():
            db.saveCluster(remoteId=row['remote_id'], cluster=labels[index])    
        print 'Finished clustering'
        return (True, 'KMeans')


    def setDecisionTreeClassifier(self):
        print 'Seting decision tree'
        
        featureKeys = self.data.columns[0:len(self.data.columns)-2]
        y = self.data['cluster']
        X = self.data[featureKeys]
        #classifies X to y, where y = clusters, X = features
        self.clf = self.clf.fit(X, y)
        print 'finished setting decision tree'
        
    def classifyDecisionTreeClassifier(self, song):
        print 'Classifying'
        scaledSong = self.min_max_scaler.transform([song.orderedFeatures])
        print scaledSong.tolist()
        song.cluster = self.clf.predict(scaledSong)[0]
        print song.cluster
        print 'Finished classifying'
        return song

		

    #returns the closest song to provided song, from array of songs
    def getSimilarSong(self, songs, song, featureWeights, feature_styleWeights=[1, 1]):        
        
        scaledSong = self.min_max_scaler.transform([song.orderedFeatures])
        
        print 'printujem song.features.'
        print song.orderedFeatures
        print 'trazena pesma'
        print scaledSong.tolist()
        
        weightedEucliedanDistances = []
        jaccardDissimilarities = []
        
        genres1 = song.tokenizeGenres()
        for s in songs:
            genres2 = s.tokenizeGenres()
            scaledSongFromCluster = self.min_max_scaler.transform([s.orderedFeatures])
            
            if(s.remoteId != song.remoteId):
                customDistances = self.computeCustomDistances(scaledSongFromCluster, scaledSong, genres1, genres2, featureWeights)
                weightedEucliedanDistances.append(customDistances[0])
                jaccardDissimilarities.append(customDistances[1])
                #distances.append(self.computeCustomDistances(scaledSongFromCluster, scaledSong, genres1, genres2, featureWeights))
        
        
        #TODO : scale euiclidean

        minMaxNormalizer = preprocessing.MinMaxScaler()
        weightedEucliedanDistances = minMaxNormalizer.fit_transform(weightedEucliedanDistances)
        print weightedEucliedanDistances
        
        distances = [feature_styleWeights[0] * euclidean + feature_styleWeights[1] * jaccard for euclidean, jaccard in zip(weightedEucliedanDistances, jaccardDissimilarities)]
        indexOfMinimum = 0
        for i in range(0, len(distances)):
            if(distances[indexOfMinimum] > distances[i]):
                indexOfMinimum = i;
    
        services = Services()
        suggestion = services.getSongByRemoteId(songs[indexOfMinimum].remoteId)
        
        suggestion.id = songs[indexOfMinimum].id
        suggestion.cluster = songs[indexOfMinimum].cluster
        scaledSongFromCluster = self.min_max_scaler.transform([suggestion.orderedFeatures])
        print 'Odabrana:'
        print scaledSongFromCluster.tolist()
        return suggestion
    
    
    def getSimilarSongFromGenre(self, songs, song, genre):
        #min_max_scaler = preprocessing.MinMaxScaler()
        #scaledData = min_max_scaler.fit_transform(self.data.values)
        scaledSong = self.min_max_scaler.transform([song.orderedFeatures])
	
        songsFiltered = []
        for s in songs:
            for artist in s.artists:
                for g in artist.genres:
                    if genre in g:
                        print "genre: " + g
                        songsFiltered.append(s)
                        break
           
        if(len(songsFiltered) == 0):
            return None
        distances = []
        for s in songsFiltered:
            scaledSongFromCluster = self.min_max_scaler.transform([s.orderedFeatures])
            distances.append(cdist(scaledSongFromCluster, scaledSong, "euclidean"))
        indexOfMinimum = 0
        for i in range(0, len(distances)):
            if(distances[indexOfMinimum][0] > distances[i][0]):
                indexOfMinimum = i;
        #get info with preview
        services = Services()
        suggestion = services.getSongByRemoteId(songsFiltered[indexOfMinimum].remoteId)
        #add local info
        suggestion.id = songsFiltered[indexOfMinimum].id
        suggestion.cluster = songsFiltered[indexOfMinimum].cluster
        return suggestion
    
    def getSimilarSongFromYearRange(self, songs, song, year1, year2):
        #min_max_scaler = preprocessing.MinMaxScaler()
        #scaledData = min_max_scaler.fit_transform(self.data.values)
        scaledSong = self.min_max_scaler.transform([song.orderedFeatures])
	print year1
        print year2
        songsFiltered = []
        for s in songs:
            if s.features['album_year'] >= year1 and s.features['album_year'] <= year2:
                print s.features['album_year']
                songsFiltered.append(s)
           
        if(len(songsFiltered) == 0):
            return None
        distances = []
        for s in songsFiltered:
            scaledSongFromCluster = self.min_max_scaler.transform([s.orderedFeatures])
            distances.append(cdist(scaledSongFromCluster, scaledSong, "euclidean"))
        indexOfMinimum = 0
        for i in range(0, len(distances)):
            if(distances[indexOfMinimum][0] > distances[i][0]):
                indexOfMinimum = i;
        #get info with preview
        services = Services()
        suggestion = services.getSongByRemoteId(songsFiltered[indexOfMinimum].remoteId)
        #add local info
        suggestion.id = songsFiltered[indexOfMinimum].id
        suggestion.cluster = songsFiltered[indexOfMinimum].cluster
        return suggestion
    
    def computeCustomDistances(self, song1Features, song2Features, song1GenresTokenized, song2GenresTokenized, featureWeights):
        #calculates distance based on weighted formula
        attributeWeights = {}
        attributeWeights['acousticness'] = featureWeights.get("acousticness")
        attributeWeights['danceability'] = featureWeights.get("danceability")
        attributeWeights['energy'] = featureWeights.get("energy")
        attributeWeights['instrumentalness'] = featureWeights.get("instrumentalness")
        attributeWeights['track_key'] = featureWeights.get("track_key")
        attributeWeights['liveness'] = featureWeights.get("liveness")
        attributeWeights['loudness'] = featureWeights.get("loudness")
        attributeWeights['mode'] = featureWeights.get("mode")
        attributeWeights['popularity'] = featureWeights.get("popularity")
        attributeWeights['speechiness'] = featureWeights.get("speechiness")
        attributeWeights['tempo'] = featureWeights.get("tempo")
        attributeWeights['time_signature'] = featureWeights.get("time_signature")
        attributeWeights['valence'] = featureWeights.get("valence")
        attributeWeights['album_year'] = featureWeights.get("year")
        
        weightedEuclideanDistance = cdist(song1Features, song2Features, lambda u, v: self.calculateWeightedEuclideanDistance(u, v, attributeWeights.values()))
        
        #calculate jaccard dissimilarity
        jaccardDissimilarity = (1- self.jaccardSimilarity(song1GenresTokenized, song2GenresTokenized))
        print 'weightedEuclidean:'
        print weightedEuclideanDistance
        print 'Jaccard dissimilarity'
        print jaccardDissimilarity
        return (weightedEuclideanDistance[0][0], jaccardDissimilarity)
        #return feature_styleWeights[0] * weightedEuclideanDistance + feature_styleWeights[1] * jaccardDissimilarity
        
        
    def calculateWeightedEuclideanDistance(self, a, b, w):
        q = a-b
        distance = np.sqrt((w * q * q).sum())
        return distance

    def jaccardSimilarity(self, tokenizedGenres1, tokenizedGenres2):
        if(len(tokenizedGenres1) == 0 and len(tokenizedGenres2) == 0):
            return 0
        return float(len(tokenizedGenres1 & tokenizedGenres2)) / len(tokenizedGenres1 | tokenizedGenres2)
