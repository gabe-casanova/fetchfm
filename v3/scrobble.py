from datetime import datetime
from track_info import TrackInfo


class Scrobble:
    '''
    A class to represent a Scrobble object (contains track and term info)
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
        year = int(data[2][:4])  # ignore trailing comma
        hour = int(data[3][:2])
        minute = int(data[3][3:5])
    
        # extract track information
        data = input.split('\t')
        if len(data) == 4:
            # default case
            artist = data[1]
            album = data[2]
            song = data[3]
        elif len(data) == 3:
            # edge case 1: no album info
            artist = data[1]
            song = data[2]
            album = ''
        else:
            # we should never get here
            print(f' ** Error: len(data) = {len(data)}')

        # store instance variables
        self.__term = datetime(year, month, day, hour, minute)
        self.__track = TrackInfo(artist, album, song)

    def __convert_month_to_int(self, tgt) -> int:
        '''
        Convert a month's string representation to its int equivalent
        '''
        months = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 
                  'Sep', 'Oct', 'Nov', 'Dec']
        return months.index(tgt)
    
    def get_track(self) -> TrackInfo:
        return self.__track
    
    def get_term(self) -> datetime:
        return self.__term
    
    def get_date(self) -> datetime.date:
        return self.__term.date
    
    def get_time(self) -> datetime.time:
        return self.__term.time
    
    def __str__(self) -> str:
        template = '%-d %b %Y, %I:%M %p'
        formatted_term = self.__term.strftime(template)
        return f'{formatted_term}\t{self.__track}'
