from classes.Artist import Artist
from classes.Genre import Genre
from classes.Song import Song
import mysql.connector as mysql
import re


class Database:
    user = "root"
    password = "root"
    host = "127.0.0.1"
    database = 'pesme'

    def __init__(self):
        self.connection = mysql.connect(user=self.user, password=self.password, host=self.host, database=self.database)
	
    def createCSVForClustering(self):
        print 'creating csv'
        cursor = self.connection.cursor(buffered=True)
        string = "SELECT 'remote_id', 'acousticness', 'danceability', 'energy', 'instrumentalness', 'track_key', 'liveness', 'loudness', 'mode', 'popularity', 'speechiness', 'tempo', 'time_signature', 'valence', 'album_year' UNION select `remote_id`,`acousticness`, `danceability`, `energy`, `instrumentalness`, `track_key`, `liveness`, `loudness`, `mode`, `popularity`, `speechiness`, `tempo`, `time_signature`, `valence` , `album_year` FROM track INTO OUTFILE '/Users/igor/songAtributes.csv' FIELDS TERMINATED BY '\,' ENCLOSED BY '\"' LINES TERMINATED BY '\n'"
        query = (string)
        cursor.execute(query)
        cursor.close() 

    # GET SONG OPERATIONS
    def getSongs(self):
        cursor = self.connection.cursor(buffered=True)
        string = "select id,remote_id, name, album, duration, acousticness, danceability, energy, instrumentalness,track_key,liveness,loudness,mode,popularity,speechiness,tempo,time_signature,valence,cluster from track"
        query = (string)
        songs = []
        cursor.execute(query)
        for (Id, remote_id, name, album, duration, acousticness, danceability, energy, instrumentalness, track_key, liveness, loudness, mode, popularity, speechiness, tempo, time_signature, valence, cluster) in cursor:
            songFeatures = {}
            songFeatures['acousticness'] = acousticness
            songFeatures['danceability'] = danceability
            songFeatures['energy'] = energy
            songFeatures['instrumentalness'] = instrumentalness
            songFeatures['track_key'] = track_key
            songFeatures['liveness'] = liveness
            songFeatures['loudness'] = loudness
            songFeatures['mode'] = mode
            songFeatures['popularity'] = popularity
            songFeatures['speechiness'] = speechiness
            songFeatures['tempo'] = tempo
            songFeatures['time_signature'] = time_signature
            songFeatures['valence'] = valence
       
            artists = self.getArtistsBySongId(Id)
            s = Song(Id, remote_id, name, songFeatures, cluster, album=album, duration=duration, artists=artists)
            
            songs.append(s)
            print len(songs)
        return songs
		

    def getSongsFromSameCluster(self, song):
        print song.toString()
        cursor = self.connection.cursor(buffered=True)
        string = "SELECT t.id,t.remote_id, t.name, album, duration, acousticness, danceability, energy, instrumentalness,track_key,liveness,loudness,mode,t.popularity,speechiness,tempo,time_signature,valence,cluster,album_year, a.name as artist_name, a.popularity as artist_popularity, a.id as artist_id, a.remote_id as artist_remote_id, g.id as genre_id, g.name as genre_name from track as t left join track_artist as ta on t.id = ta.track_id join artist as a on ta.artist_id = a.id LEFT join artist_genre as ag on ag.artist_id = a.id join genre as g on g.id = ag.genre_id where cluster=%s" % (song.cluster)
        query = (string)
        songs = []
        cursor.execute(query)
        
        for (Id, remote_id, name, album, duration, acousticness, danceability, energy, instrumentalness, track_key, liveness, loudness, mode, popularity, speechiness, tempo, time_signature, valence, cluster, album_year, artist_name, artist_popularity, artist_id, artist_remote_id, genre_id, genre_name) in cursor:

            if(len(songs) == 0 or songs[len(songs)-1].id != Id):
                songFeatures = {}
                songFeatures['acousticness'] = acousticness
                songFeatures['danceability'] = danceability
                songFeatures['energy'] = energy
                songFeatures['instrumentalness'] = instrumentalness
                songFeatures['track_key'] = track_key
                songFeatures['liveness'] = liveness
                songFeatures['loudness'] = loudness
                songFeatures['mode'] = mode
                songFeatures['popularity'] = popularity
                songFeatures['speechiness'] = speechiness
                songFeatures['tempo'] = tempo
                songFeatures['time_signature'] = time_signature
                songFeatures['valence'] = valence
                songFeatures['album_year'] = album_year
                s = Song(Id, remote_id, name, songFeatures, cluster, album=album, duration=duration, artists=[])
                songs.append(s)
                
            s = songs[len(songs)-1]
            if(artist_id != None):

                if(len(s.artists) == 0 or s.artists[len(s.artists)-1].id != artist_id):
                    a = Artist(artist_remote_id, artist_name, artist_popularity, [], artist_id)
                    s.artists.append(a)
                a = s.artists[len(s.artists)-1]
                if(genre_id != None):
                    g = genre_name
                    a.genres.append(g)
            print 'Duzina liste : ' + str(len(songs))
        return songs


#    def getSongByRemoteId(self, remoteId):
#        cursor = self.connection.cursor(buffered=True)
#        string = "select id,remote_id, name, album, duration, acousticness, danceability, energy, instrumentalness,track_key,liveness,loudness,mode,popularity,speechiness,tempo,time_signature,valence,cluster, album_year from track where remote_id = \'%s\'" % (remoteId)
#        query = (string)
#        songs = []
#        cursor.execute(query)
#        for (Id, remote_id, name, album, duration, acousticness, danceability, energy, instrumentalness, track_key, liveness, loudness, mode, popularity, speechiness, tempo, time_signature, valence, cluster,album_year) in cursor:
#            songFeatures = {}
#            songFeatures['acousticness'] = acousticness
#            songFeatures['danceability'] = danceability
#            songFeatures['energy'] = energy
#            songFeatures['instrumentalness'] = instrumentalness
#            songFeatures['track_key'] = track_key
#            songFeatures['liveness'] = liveness
#            songFeatures['loudness'] = loudness
#            songFeatures['mode'] = mode
#            songFeatures['popularity'] = popularity
#            songFeatures['speechiness'] = speechiness
#            songFeatures['tempo'] = tempo
#            songFeatures['time_signature'] = time_signature
#            songFeatures['valence'] = valence
#            songFeatures['album_year'] = album_year
#            num_fields = len(cursor.description)
#            field_names = [i[0] for i in cursor.description]
#            print 'Field names'
#            print field_names
#            print album_year
#            print '@Database/getByRemote ' + str(cluster) + str(Id)
#            artists = self.getArtistsBySongId(Id)
#            s = Song(Id, remote_id, name, songFeatures, cluster=cluster, album=album, duration=duration, artists=artists)
#            songs.append(s)
#        if(len(songs)>0):
#           return songs[0]
#        return None

    def getSongByRemoteId(self, remoteId):
        cursor = self.connection.cursor()
        string = "select id,remote_id, name, album, duration, acousticness, danceability, energy, instrumentalness,track_key,liveness,loudness,mode,popularity,speechiness,tempo,time_signature,valence,cluster, album_year from track where remote_id = \'%s\'" % (remoteId)
        query = (string)
        songs = []
        cursor.execute(query)
        result_set = cursor.fetchall()
        for row in result_set:
            songFeatures = {}
            songFeatures['acousticness'] = row[5]
            songFeatures['danceability'] = row[6]
            songFeatures['energy'] = row[7]
            songFeatures['instrumentalness'] = row[8]
            songFeatures['track_key'] = row[9]
            songFeatures['liveness'] = row[10]
            songFeatures['loudness'] = row[11]
            songFeatures['mode'] = row[12]
            songFeatures['popularity'] = row[13]
            songFeatures['speechiness'] = row[14]
            songFeatures['tempo'] = row[15]
            songFeatures['time_signature'] = row[16]
            songFeatures['valence'] = row[17]
            songFeatures['album_year'] = row[19]
            artists = self.getArtistsBySongId(row[0])
            artists = []
            s = Song(row[0], row[1], row[2], songFeatures, cluster=row[18], album=row[3], duration=row[4], artists=artists)
            songs.append(s)
        if(len(songs) > 0):
            return songs[0]
        return None



    def getArtistsBySongId(self, songId):

        cursor = self.connection.cursor(buffered=True)
        string = "SELECT a.id, a.name, a.popularity, a.remote_id FROM track_artist join artist as a on a.id=track_artist.artist_id WHERE track_artist.track_id = %s" % (songId)
        query = (string)
        artists = []
        cursor.execute(query)
        for (Id, name, popularity, remote_id) in cursor:
            genres = self.getGenresByArtistId(Id)
            a = Artist(remote_id, name, popularity, id=Id, genres=genres)		
            artists.append(a)

        return artists


    def getGenresByArtistId(self, artistId):
        cursor = self.connection.cursor(buffered=True)
        string = "SELECT g.id, g.name FROM artist_genre join genre as g on g.id=artist_genre.genre_id WHERE artist_genre.artist_id = %s" % (artistId)
        query = (string)
        genres = []
        cursor.execute(query)
        for (Id, name) in cursor:
			
            g = Genre(id=Id, name=name)		
            genres.append(g)

        return genres


    #INSERT OPERATIONS
    def saveCluster(self, remoteId, cluster):
        cursor = self.connection.cursor(buffered=True)
        string = "UPDATE track SET cluster=%s where remote_id=\'%s\'" % (cluster, remoteId) 
        query = (string)
        cursor.execute(query)
        self.connection.commit()


    #inserts songs, their artists. References insertArtists method
    def insertSongs(self, songs):
        cursor = self.connection.cursor(buffered=True)
        trackIds = []
        for song in songs:
            string = "INSERT INTO track (acousticness, album, danceability, duration, energy, remote_id, instrumentalness, track_key, liveness, loudness, mode, name, popularity, speechiness, tempo, time_signature, valence, album_year) VALUES (\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\')" % (song.features['acousticness'], re.escape(song.album), song.features['danceability'], song.duration, song.features['energy'], song.remoteId, song.features['instrumentalness'], song.features['track_key'], song.features['liveness'], song.features['loudness'], song.features['mode'], re.escape(song.name), song.features['popularity'], song.features['speechiness'], song.features['tempo'], song.features['time_signature'], song.features['valence'], song.features['album_year'])
            print string
            query = (string)
            cursor.execute(query)
			
            trackId = cursor.lastrowid
            trackIds.append(trackId)

            artistIds = self.insertArtists(song.artists)
			
            for artistId in artistIds:
                cursor.execute("INSERT INTO track_artist (track_Id, artist_Id) values (%s, %s)" % (trackId, artistId))
		
        self.connection.commit()
        return trackIds


    #inserts artists, return artist ids. If they existed it also returns their ids
    def insertArtists(self, artists):
        artistIds = []
        cursor = self.connection.cursor(buffered=True)
        for artist in artists:
            try:
                string = "INSERT INTO artist (remote_Id, name, popularity) values (\'%s\',\'%s\',\'%s\')" % (artist.remoteId, re.escape(artist.name), artist.popularity)
                query = (string)
                cursor.execute(query)
                artistId = cursor.lastrowid
            except Exception, e:
                print e
                cursor.execute("select id from artist where name=\'%s\'" % (re.escape(artist.name)))
                artistId = cursor.fetchall()[0][0]
            artistIds.append(artistId)
            for genre in artist.genres:
                try:
                    cursor.execute('INSERT INTO genre (name) values (\'%s\')' % (genre))
                    genreId = cursor.lastrowid	
                except Exception, e:
                    cursor.execute('select id from genre where name=\'%s\'' % (genre))
                    genreId = cursor.fetchall()[0][0]
                cursor.execute("INSERT INTO artist_genre (artist_Id, genre_Id) values (%s, %s)" % (artistId, genreId))
        self.connection.commit()
        return artistIds

