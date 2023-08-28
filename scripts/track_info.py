class TrackInfo:
    '''
    A class to store a Scrobble object's artist, album, and song info
    '''

    def __init__(self, artist, album, song):
        self.__artist = artist
        self.__album = album
        self.__song = song

    def get_artist(self) -> str:
        return self.__artist
    
    def get_album(self) -> str:
        return self.__album
    
    def get_song(self) -> str:
        return self.__song
    
    def __str__(self):
        FORMAT = '{}    {}    {}'
        return FORMAT.format(self.__artist, self.__album, self.__song)
    