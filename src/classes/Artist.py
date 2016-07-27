class Artist:
   
    def __init__(self, remoteId, name, popularity, genres, id=-1):
    	self.id = id
    	self.remoteId = remoteId
        self.name = name
        self.popularity = popularity
        self.genres = genres
	
    def toDictionary(self):

        artist = {}
    	artist["id"] = self.id
    	artist["remoteId"] = self.remoteId
    	artist["name"] = self.name
        artist["popularity"] = self.popularity
        artist["genres"] = self.genres
        return artist