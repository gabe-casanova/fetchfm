from datetime import datetime, date, time
from track_info import TrackInfo


class Scrobble:
    '''
    A class to represent a Scrobble object (contains track and datetime info)
    '''

    def __init__(self, input):
        '''
        Initialize a new Scrobble object, contains information regarding
        datetime (year, month, day, hour, minute) and TrackInfo (artist,
        album, song) for a given Scrobble
        '''
        data = input.split()
        
        # extract datetime information
        day = int(data[0])
        month = self.__convert_month_to_int(data[1])
        year = int(data[2][:4])  # ignores trailing comma
        hour = int(data[3][:2])
        minute = int(data[3][3:5])
    
        # extract track information
        data = input.split('\t')
        self.is_valid = True  # start by assuming all track info is present
        if '' not in data:
            # success case: all necessary track info is present
            artist = data[1]
            album = data[2]
            song = data[3][:-1]  # removes the \n from song
        else:
            # edge-case: input is missing necessary track info
            self.is_valid = False
            
        # store instance variables
        if self.is_valid:
            self.__term = datetime(year, month, day, hour, minute)
            self.__date = date(year, month, day)
            self.__time = time(hour, minute)
            self.__track = TrackInfo(artist, album, song)

    def __convert_month_to_int(self, tgt):
        '''
        Convert a month's string representation to its int equivalent
        '''
        MONTHS = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 
                  'Sep', 'Oct', 'Nov', 'Dec']
        return MONTHS.index(tgt)
    
    def get_track(self) -> TrackInfo:
        return self.__track
    
    def get_term(self) -> datetime:
        return self.__term
    
    def get_date(self) -> date:
        return self.__date
    
    def get_time(self) -> time:
        return self.__time
    
    def __str__(self):
        TEMPLATE = '%-d %b %Y, %I:%M %p'
        formatted_term = self.__term.strftime(TEMPLATE)
        return f'{formatted_term}\t{self.__track}'
