from classes.Song import Song
from database.Database import Database
from flask import Flask
from flask import jsonify
from flask import request
from machine_learning.MachineLearning import MachineLearning
import os
import pickle
from services.services import Services
from sklearn.decomposition import PCA
app = Flask(__name__)
app.debug = True

if(os.path.isfile('ml.pickle')):
    with open('ml.pickle', 'rb') as handle:
        ml = pickle.load(handle)
else:
    ml = MachineLearning()
    response = {}
    (response['success'], response['algorithm']) = ml.clusterKmeans(False)
    print response
    ml.setDecisionTreeClassifier()
    with open('ml.pickle', 'wb') as handle:
        pickle.dump(ml, handle)
print 'Finished init'

@app.route("/", methods=['POST'])
def hello():
    return jsonify({"Message": "It works"})


@app.route("/suggest-similar", methods=['POST'])
def suggest_similar():
    print 'Suggest similar'
    
    if request.json:
         #get song name
        data = request.json # will be 
        songName =  data.get("songName")
        
        global ml
        response = {}
        response['success'] = False
        response['message'] = 'Oops, something went wrong. We couldn\'t find song: ' + songName

       
        #get song
        services = Services()
        s = services.getSongBySongName(songName)
        #print 'trazena pesam: \n' + s.toString()
        
        if(s != None):
            #classify and save cluster
            db = Database()
            persistedSong = db.getSongByRemoteId(s.remoteId)

            if(persistedSong == None):
                print 'Pesma nije bila u bazi'
                s.id = db.insertSongs([s])[0]
                s = ml.classifyDecisionTreeClassifier(s)

                print 'Dodeljen klaster: ' + str(s.cluster)
                db.saveCluster(s.remoteId, s.cluster)
            else:
                print 'Pesma je bila u bazi'
                s.cluster = persistedSong.cluster
                s.id = persistedSong.id
            
            #get songs from same cluster
            songsFromCluster = db.getSongsFromSameCluster(s)
        
            criteriaKey = data.get("criteriaKey")
            criteriaValue = data.get("criteriaValue")
            featureWeights = data.get("featureWeights")
            print "feature weights"
            print featureWeights
            if criteriaKey=="year" and criteriaValue!=None:
                years = criteriaValue.split("-")
                suggestedSong = ml.getSimilarSongFromYearRange(songsFromCluster, s, int(years[0]), int(years[1]))
                #return "not supported yet"
            elif(criteriaKey =="genre" and criteriaValue!=None):
                suggestedSong = ml.getSimilarSongFromGenre(songsFromCluster, s, criteriaValue)
            else:
                suggestedSong = ml.getSimilarSong(songsFromCluster, s, featureWeights)
            if suggestedSong == None:
                response['message'] = "Oops, something went wrong. We couldn't find a recommendation. "
                return jsonify(response)
            response['success'] = True
            response['request_song'] = s.toDictionary()
            response['suggested_song'] = suggestedSong.toDictionary()
            response['message'] = 'Suggestion successful'
            print response
        return jsonify(response)
    response = {}
    response['success'] = False
    response['message'] = 'Bad request.'
    return jsonify(response)

@app.route("/perform-clustering/<algorithm>", methods=['GET'])
def perform_clustering(algorithm=None):
    #init()
    global songs
    ml = MachineLearning()
    ml.createDataframe(songs)

    response = {}
    response['success'] = False
    response['algorithm'] = 'Clustering algorithm ' + algorithm + ' is not supported'
	
    if(algorithm.lower() == 'kmeans'.lower()):
        (response['success'], response['algorithm']) = ml.clusterKmeans(songs)
    if(response['success']):
        db = Database()
        db.saveClusters(songs)
        
    return jsonify(response)

if __name__ == "__main__":

    if(os.path.isfile('ml.pickle')):
        with open('ml.pickle', 'rb') as handle:
            ml = pickle.load(handle)
    else:
        ml = MachineLearning()
        response = {}
        (response['success'], response['algorithm']) = ml.clusterKmeans(False)
        print response
        ml.setDecisionTreeClassifier()
        with open('ml.pickle', 'wb') as handle:
            pickle.dump(ml, handle)
    print 'Finished init'
   
    app.run(debug=True, port=8099)