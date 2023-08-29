from tqdm import tqdm
from time import sleep
from datetime import date, time, timedelta
from collections import OrderedDict
from ansi import ANSI
from scrobble import Scrobble
from api_handler import fetch_song_duration, fetch_album_duration, \
    fetch_artist_name_corrected


'''
------------------------------------------------------------------------------
Instance Variables:
    Catalogs:
        ->  __stnd_catalog              list(Scrobble)
        ->  __daily_catalog             OrderedDict(datetime, list(Scrobble))
        ->  __alpha_song_catalog        OrderedDict(str, list(Scrobble))
        ->  __alpha_artist_catalog      "
        ->  __alpha_album_catalog       "
    Miscellaneous:
        ->  __username                  str
        ->  __num_distinct_days         int
------------------------------------------------------------------------------
'''

'''
------------------------------------------------------------------------------
Public Methods:
    -  song_length(song, artist) ->  -> tuple[str, str, time]
  /
    -  song_listening_time(song, artist) -> tuple[str, str, float]
    -  artist_listening_time(artist) -> tuple[str, float, bool]
    -  album_listening_time(album, artist) -> tuple[str, str, float, int, bool]
  /
    -  top_songs(n) -> list[tuple[str, int]]
    -  top_artists(n) -> list[tuple[str, int]]
    -  top_albums(n) -> list[tuple[str, int]]
  /
    -  num_plays_for_song(song) -> int
    -  num_plays_for_artist(artist) -> int
    -  num_plays_for_album(album) -> int
  /
    -  num_plays_for_song_on_date(song, month, day, year) -> int
    -  num_plays_for_artist_on_date(artist, month, day, year) -> int
    -  num_plays_for_album_on_date(album, month, day, year) -> int
  /
    -  most_played_song() -> tuple[list, int]
    -  most_played_artist() -> tuple[list, int]
    -  most_played_album() -> tuple[list, int]
  /
    -  most_played_song_on_date(month, day, year) -> tuple[list, int]
    -  most_played_artist_on_date(month, day, year) -> tuple[list, int]
    -  most_played_album_on_date(month, day, year) -> tuple[list, int]
  /
    -  most_consecutive_song() -> tuple[list, int]
    -  most_consecutive_artist() -> tuple[list, int]
    -  most_consecutive_album() -> tuple[list, int]
  /
    -  most_streamed_day_overall() -> tuple[list, int]
  /
    -  most_streamed_day_for_song(song) -> tuple[list, int]
    -  most_streamed_day_for_artist(artist) -> tuple[list, int]
    -  most_streamed_day_for_album(album) -> tuple[list, int]
  /
    -  get_scrobbles_on_date(month, day, year) -> []
    -  print_scrobbles_on_date(month, day, year) -> void
  /
    -  get_avg_daily_scrobbles() -> int
    -  get_total_num_scrobbles() -> int
    -  get_total_num_distinct_days() -> int
  /
    -  print_chronological_catalog() -> void
    -  print_song_catalog() -> void
    -  print_artist_catalog() -> void
    -  print_album_catalog() -> void
------------------------------------------------------------------------------
'''


class Catalog():
    '''
    A class to represent a collection of Scrobbles
    '''

    def __init__(self, username, lines_of_text:list):
        '''
        Create a new catalog of Scrobble objects
        '''
        self.__username = username
        self.__stnd_catalog = []
        for line in lines_of_text:
            scrob = Scrobble(line)
            if scrob.is_valid:
                # only append scrobbles if they're not missing any info
                self.__stnd_catalog.append(scrob)
        # use standard catalog to generate other variants
        self.__make_daily_catalog()
        self.__make_alphabetized_catalogs()

# =========== [1] Data Retrieval: ===========================================

    def song_length(self, song, artist):
        '''
        Returns a tuple of 'track length info' for the provided track
        ------
        Returns a tuple containing...
            - `str`: song name (formatted correctly if found)
            - `str`: artist name (formatted correctly if found)
            - `time`: track length (as a datetime.time object)
        '''
        return fetch_song_duration(song, artist, self.__username)
    

    def song_listening_time(self, song, artist):
        '''
        Returns information related to the amount of total time the user has
        spent listening to the given song.
        ------
        Returns a tuple containing...
            - `str`: song name (formatted correctly if found)
            - `str`: artist name (formatted correctly if found)
            - `int`: user's total listening time in seconds
        '''
        result = self.song_length(song, artist)
        if result[2] is None:
            # unable to find the given song in the Last.fm database
            return song, artist, 0
        # we know the user requested a valid song
        num_plays = self.num_plays_for_song(result[0])  # correctly formatted
        total_time = self.__calc_song_total_time(result[2], num_plays)
        return result[0], result[1], total_time
    

    def artist_listening_time(self, artist) -> tuple[str, float, bool]:
        '''
        Calculates the total time the user has listened to the given artist
        ------
        Returns a tuple containing...
            - `str`: artist name (formatted correctly if found)
            - `float`: user's total listening time in seconds
            - `bool`: indicates if Last.fm had any missing time info
        '''
        corrected_artist, _ = fetch_artist_name_corrected(artist)
        if corrected_artist not in self.__alpha_artist_catalog:
            return corrected_artist, 0, False
        # inform the user that the calculation process is about to begin
        display_prog_bool = self.num_plays_for_artist(corrected_artist) > 50
        if display_prog_bool:
            # display progress bar
            ansi_msg = (' "Hold tight as I calculate the total time you\'ve '
                        f'listened to {corrected_artist}" -Fetch\n')
            print(f'\n{ansi_msg}')
            num_scrobs = len(self.__alpha_artist_catalog[corrected_artist])
            prog_bar = tqdm(total=num_scrobs)
        # iterate over user's alpha artist catalog, summing up total time
        missing_time_flag = False
        total_time = timedelta(seconds=0)
        for scrob in self.__alpha_artist_catalog[corrected_artist]:
            if display_prog_bool:
                # update progress bar
                prog_bar.update(1)
            song = scrob.get_track().get_song() 
            _, _, length = self.song_length(song, corrected_artist)
            if self.__has_zero_time(length):
                missing_time_flag = True
            else:
                song_seconds = self.__dt_obj_to_seconds(length)
                total_time += timedelta(seconds=song_seconds)
        if display_prog_bool:
            # close progress bar
            prog_bar.close()
        total_time = total_time.total_seconds()
        return corrected_artist, total_time, missing_time_flag

    
    def album_listening_time(self, album, artist):
        '''
        Returns information related to the amount of total time the user has 
        spent listening to the given album.
        ------
        Returns a tuple containing...
            - `str`: album name (formatted correctly if found)
            - `str`: artist name (formatted correctly if found)
            - `float`: user's total listening time in seconds
            - `int`: user's playcount for this album
            - `bool`: indicates if Last.fm had any missing time info
        '''
        result = fetch_album_duration(album, artist, self.__username)
        missing_time_flag = False
        track_list_dict = result[2]
        total_time = timedelta(seconds=0)
        if track_list_dict is not None:
            for song, time_obj in track_list_dict.items():
                if self.__has_zero_time(time_obj):
                    missing_time_flag = True
                    continue
                num_plays = self.num_plays_for_song(song)
                if num_plays <= 0:
                    continue
                # calculate the total time spent listening to this song
                song_seconds = self.__calc_song_total_time(time_obj, num_plays)
                total_time += timedelta(seconds=song_seconds)
        total_time = total_time.total_seconds()
        return result[0], result[1], total_time, result[3], missing_time_flag


    def __calc_song_total_time(self, timeobj:time, num_plays):
        '''
        Calculates the total time user has spent listening to the given song 
        (represented by the datetime.time obj) in seconds
        '''
        song_len = self.__dt_obj_to_seconds(timeobj)
        return song_len * num_plays


    def __dt_obj_to_seconds(self, timeobj:time):
        '''
        Extracts the total seconds from the provided datetime.time obj
        '''
        return timeobj.hour * 3600 + timeobj.minute * 60 + timeobj.second


    def __has_zero_time(self, time_obj:time):
        return (time_obj.hour == 0 and time_obj.minute == 0 
                and time_obj.second == 0)
           
    
    ''''''

    def top_songs(self, n):
        '''
        Returns the user's top N songs as a list of tuples containing:
            * `str`: song name
            * `int`: playcount
        '''
        return self.__top_items(self.__alpha_song_catalog, n)
    
    def top_artists(self, n):
        ''''
        Returns the user's top N artists as a list of tuples containing:
            * `str`: artist name
            * `int`: playcount
        '''
        return self.__top_items(self.__alpha_artist_catalog, n)

    def top_albums(self, n):
        '''
        Returns the user's top N albums as a list of tuples containing:
            * `str`: album name
            * `int`: playcount
        '''
        return self.__top_items(self.__alpha_album_catalog, n)
    
    def __top_items(self, catalog, n) -> list[tuple[str, int]]:
        my_key = self.__by_num_scrobs
        sorted_items = sorted(catalog.items(), key=my_key, reverse=True)
        top_n = [(item, len(scrobs)) for item, scrobs in sorted_items[:n]]
        return top_n

    def __by_num_scrobs(self, alpha_catalog_item):
        return len(alpha_catalog_item[1])

    ''''''

    def num_plays_for_song(self, song):
        return self.__num_plays(song, self.__alpha_song_catalog)
    
    def num_plays_for_artist(self, artist):
        return self.__num_plays(artist, self.__alpha_artist_catalog)
    
    def num_plays_for_album(self, album):
        return self.__num_plays(album, self.__alpha_album_catalog)

    def __num_plays(self, item, catalog):
        scrobs = catalog.get(item)
        if scrobs:
            return len(scrobs)
        else:
            return 0
    
    ''''''

    def num_plays_for_song_on_date(self, song, month, day, year):
        get_field = self.__by_song
        return self.__num_plays_on_date(song, month, day, year, get_field)

    def num_plays_for_artist_on_date(self, artist, month, day, year):
        get_field = self.__by_artist
        return self.__num_plays_on_date(artist, month, day, year, get_field)

    def num_plays_for_album_on_date(self, album, month, day, year):
        get_field = self.__by_album
        return self.__num_plays_on_date(album, month, day, year, get_field)

    def __num_plays_on_date(self, item, month, day, year, get_field):
        scrobs = self.get_scrobbles_on_date(month, day, year)
        if len(scrobs) == 0:
            return 0
        num_plays = 0
        for scrob in scrobs:
            if item == get_field(scrob):
                num_plays += 1
        return num_plays

    ''''''

    def most_played_song(self):
        '''
        Returns a list of song name(s) which were the user's most listened 
        to and also the number of listens for the most listened to song(s)
        '''
        catalog = self.__alpha_song_catalog
        return self.__most_played(self.__by_song, catalog)
    
    def most_played_artist(self):
        '''
        Returns a list of artist name(s) which were the user's most listened 
        to and also the number of listens for the most listened to artist(s)
        '''
        catalog = self.__alpha_artist_catalog
        return self.__most_played(self.__by_artist, catalog)
    
    def most_played_album(self):
        '''
        Returns a list of album name(s) which were the user's most listened 
        to and also the number of listens for the most listened to album(s)
        '''
        catalog = self.__alpha_album_catalog
        return self.__most_played(self.__by_album, catalog)
    
    def __most_played(self, get_field, alpha_catalog):
        result = []
        max_so_far = 0
        for _, scrobs in alpha_catalog.items():
            num_listens = len(scrobs)
            if num_listens > max_so_far:
                # we found a new max number of listens
                max_so_far = num_listens
                result = [get_field(scrobs[0])]
            elif num_listens == max_so_far:
                # at least 2 items (song, artist, or album) have the same
                # max number of listens, we want to record both in our result
                result.append(get_field(scrobs[0]))
        return result, max_so_far

    ''''''

    def most_played_song_on_date(self, month, day, year):
        '''
        Returns a list of song(s) which were the user's most listened to for
        a given date and also the number of listens for the most freq song(s)
        '''
        return self.__most_played_on_date(month, day, year, self.__by_song)
    
    def most_played_artist_on_date(self, month, day, year):
        '''
        Returns a list of artist(s) which were the user's most listened to for
        a given date and also the number of listens for the most freq artist(s)
        '''
        return self.__most_played_on_date(month, day, year, self.__by_artist)
    
    def most_played_album_on_date(self, month, day, year):
        '''
        Returns a list of album(s) which were the user's most listened to for
        a given date and also the number of listens for the most freq album(s)
        '''
        return self.__most_played_on_date(month, day, year, self.__by_album)

    def __most_played_on_date(self, m, d, y, get_field) -> tuple[list, int]:
        freqs = {}
        scrobs = self.get_scrobbles_on_date(m, d, y)
        # generate item frequencies
        for scrob in scrobs:
            item = get_field(scrob)
            if item not in freqs:
                freqs[item] = [0]
            freqs.get(item)[0] += 1
        ''' time to figure out max frequency '''
        if not freqs:
            return [], 0
        # if we get here, we know there won't be a ValueError for empty dict
        max_freq = max(freqs.values())
        result = [item for item, freq in freqs.items() if freq == max_freq]
        return result, max_freq
    
    ''''''

    def most_consecutive_song(self):
        return self.__most_consecutive(self.__by_song)

    def most_consecutive_artist(self):
        return self.__most_consecutive(self.__by_artist)

    def most_consecutive_album(self):
        return self.__most_consecutive(self.__by_album)

    def __most_consecutive(self, get_field) -> tuple[list, int]:
        '''
        Returns a list of item names (song, artist, or album names) which 
        the user has listened to the most times in a row. Also returns an int
        signif the number of plays for longest consecutively listened to S/A/A
        '''
        result = []
        # variables used to keep track of current longest consecutive item
        longest_length = 0
        consec_item = ''
        # variables needed when replacing the above two variables (i.e., when
        # we find a NEW more consecutive item)
        second_length = 0
        second_item = ''
        # iterate through the entire standard catalog
        for i in range(len(self.__stnd_catalog)):
            curr = get_field(self.__stnd_catalog[i])
            if i == 0:
                # base case, only happens to initialize variables
                longest_length = 1
                consec_item = curr
                result.append(consec_item)
            elif self.__is_consecutive(i, longest_length, consec_item, 
                                       get_field):
                # we now know that the curr item IS consecutive
                longest_length += 1
                if longest_length > second_length:
                    # we've found a completely NEW more consecutive streak
                    second_length = 0  # reset
                    second_item = ''  # reset
                    result = [consec_item]  # update the result list
            elif self.__is_consecutive(i, second_length, second_item, 
                                       get_field):
                '''
                If we get here we know curr item is NOT part of the longest
                consecutive streak. But, we do know that the curr item is 
                contributing toward the second_item's consecutive streak
                '''
                second_length += 1
                if second_length == longest_length:
                    # we only get here when second_song now has the same
                    # number of consecutive streaks as most consecutive_song
                    consec_item = second_item
                    result.append(second_item)
            else:
                # if we get here, we need to initialize our 'second' variables
                # with their new values
                second_length = 1
                second_item = curr
        return result, longest_length
                
    def __is_consecutive(self, i, length, most_consec, get_field):
        if most_consec != get_field(self.__stnd_catalog[i]):
            return False
        # iterate over the length for the most consecutive item so far
        for offset in range(1, length):
            item1 = get_field(self.__stnd_catalog[i])
            item2 = get_field(self.__stnd_catalog[i - offset])
            if item1 != item2:
                return False
        return True

    ''''''

    def most_streamed_day_overall(self) -> tuple[list, int]:
        '''
        Returns a list of day(s) in which the user scrobbled the most, also
        returns the number of scrobbles listened to on the most streamed day(s)
        '''
        max_so_far = 0
        result = []
        for dt, scrobs in self.__daily_catalog.items():
            num_scrobs = len(scrobs)
            if num_scrobs > max_so_far:
                max_so_far = num_scrobs
                result = [dt]
            elif num_scrobs == max_so_far:
                result.append(dt)
        return result, max_so_far
    
    ''''''

    def most_streamed_day_for_song(self, song):
        '''
        Returns a list of date(s) the user listened to a given song the most
        and the number of listens recorded for that song on those date(s)
        '''
        catalog = self.__alpha_song_catalog
        return self.__most_streamed_day_for(song, catalog, self.__by_song)
    
    def most_streamed_day_for_artist(self, artist):
        '''
        Returns a list of date(s) the user listened to a given artist the most
        and the number of listens recorded for that artist on those date(s)
        '''
        catalog = self.__alpha_artist_catalog
        return self.__most_streamed_day_for(artist, catalog, self.__by_artist)
    
    def most_streamed_day_for_album(self, album):
        '''
        Returns a list of date(s) the user listened to a given album the most
        and the number of listens recorded for that album on those date(s)
        '''
        catalog = self.__alpha_album_catalog
        return self.__most_streamed_day_for(album, catalog, self.__by_album)

    def __most_streamed_day_for(self, tgt, cat, get_field) -> tuple[list, int]:
        if tgt not in cat.keys():
            # print a message that the user hasn't listened to this tgt yet
            ansi_tgt = f'{ANSI.BRIGHT_CYAN}{tgt}{ANSI.RESET}'
            msg = (f' * Sorry, but we couldn\'t find {ansi_tgt} in your '
                   'listening history!')
            print(msg)
            return [], 0
        # if we get here, we know the user has listened to the given tgt
        freqs = {}
        for date, scrobs in self.__daily_catalog.items():
            n_listens = sum(1 for scrob in scrobs if get_field(scrob) == tgt)
            if n_listens > 0:
                # only add if this item was listened to on this date
                freqs[date] = n_listens
        assert freqs
        max_freq = max(freqs.values())
        result = [date for date, freq in freqs.items() if freq == max_freq]
        return result, max_freq

    ''''''

    def get_scrobbles_on_date(self, month, day, year) -> list:
        '''
        Returns a list of all Scrobbles listened to on a given date (M/D/Y)
        '''
        if not self.__is_valid_date(month, day, year):
            invalid_date = f'{month}/{day}/{year}'
            ansi_date = f'{ANSI.BRIGHT_CYAN_BOLD}{invalid_date}{ANSI.RESET}'
            print(f' * Sorry, but {ansi_date} is not a valid date!')
            return []
        # if we get here we have a valid date
        requested_date = date(year, month, day)
        if not self.__is_within_user_bounds(requested_date):
            self.__print_oob_date_error_msg(requested_date)
            return []
        # if we get here we have a date that falls within user's bounds
        if requested_date in self.__daily_catalog:
            return self.__daily_catalog.get(requested_date)
        else:
            return []

    def __is_valid_date(self, month, day, year):
        if month < 1 or day < 1 or year < 0 or month > 12 or day > 31:
            # base check for obviously incorrect input
            return False
        # check for leap year
        if self.__is_leap_year(year):
            days_in_month = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        else:
            days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        # check if the provided day and month (parameters) are valid
        max_day = days_in_month[month - 1]
        if day <= max_day:
            return True
        else:
            return False

    def __is_leap_year(self, year):
        if year % 4 == 0:
            # the year is divisible by 4
            if year % 100 == 0:
                # the year is a century
                if year % 400 == 0:
                    return True
                else:
                    return False
            else:
                # the year is NOT a century
                return True
        else:
            # the year is NOT divisible by 4
            return False
        
    def __is_within_user_bounds(self, requested_date):
        '''
        Checks if the requested date falls within the bounds set by the user's
        Last.fm catalog information
        '''
        start_range = self.__stnd_catalog[-1].get_date()
        end_range = self.__stnd_catalog[0].get_date()
        return requested_date >= start_range and requested_date <= end_range

    def __print_oob_date_error_msg(self, requested_date):
        '''
        Prints an error message that the requested date was not within the 
        user's catalog range (out of error bounds error)
        '''
        TEMPLATE = '%-m/%-d/%Y'
        # define the range of available scrobbles [start, end]
        start_range = self.__stnd_catalog[-1].get_date()
        end_range = self.__stnd_catalog[0].get_date()
        # format the dates to follow above template
        formatted_date = requested_date.strftime(TEMPLATE)
        formatted_start = start_range.strftime(TEMPLATE)
        formatted_end = end_range.strftime(TEMPLATE)
        ''' print the error message to the user '''
        # print the formatted date
        ansi_req_date = f'{ANSI.BRIGHT_CYAN_BOLD}{formatted_date}{ANSI.RESET}'
        print(f' * Sorry, but {ansi_req_date} is not within the range of your '
              'scrobbled data: ', end='')
        # print the formatted start and end range
        ansi_start_date = f'{ANSI.BRIGHT_CYAN}{formatted_start}{ANSI.RESET}'
        ansi_end_date = f'{ANSI.BRIGHT_CYAN}{formatted_end}{ANSI.RESET}'
        print(f'{ansi_start_date} - {ansi_end_date}.')
 
    ''''''

    def get_avg_daily_scrobbles(self):
        ''' Returns the user's average daily Scrobbles as a whole number '''
        average = len(self.__stnd_catalog) / self.__num_distinct_days
        return round(average)

    def get_total_num_scrobbles(self):
        ''' Returns the total number of Scrobbles the user has listened to '''
        return len(self.__stnd_catalog)

    def get_total_num_distinct_days(self):
        ''' Returns the total num of distinct days the user has Scrobbled '''
        return self.__num_distinct_days
    
# =========== [2] Printing: =================================================

    def print_scrobbles_on_date(self, month, day, year):
        '''
        Prints all of the Scrobbles the user's listened to on a specific date
        '''
        scrobs = self.get_scrobbles_on_date(month, day, year)
        if scrobs:
            for scrob in scrobs:
                print(scrob)
                sleep(0.05)
        else:
            print('You did not listen to any music on that day!')
                
    def print_chronological_catalog(self):
        ''' Prints the user's full chronological catalog '''
        print()
        for _, scrobs in self.__daily_catalog.items():
            for scrob in scrobs:
                print(scrob)
        print()

    def print_song_catalog(self):
        '''
        Prints the user's alphabetized-catalog based on song name
        '''
        most_listened_func = lambda: self.most_played_song()
        catalog = self.__alpha_song_catalog
        self.__print_catalog(most_listened_func, catalog, False)
    
    def print_artist_catalog(self):
        '''
        Prints the user's alphabetized-catalog based on artist name
        '''
        most_listened_func = lambda: self.most_played_artist()
        catalog = self.__alpha_artist_catalog
        self.__print_catalog(most_listened_func, catalog, True)

    def print_album_catalog(self):
        '''
        Prints the user's alphabetized-catalog based on album name
        '''
        most_listened_func = lambda: self.most_played_album()
        catalog = self.__alpha_album_catalog
        self.__print_catalog(most_listened_func, catalog, False)

    def __print_catalog(self, most_listened_func, alpha_catalog, 
                        is_artist_catalog_request:bool):
        ''' Get the length of most listened to item # including commas '''
        _, max_length = most_listened_func()
        max_length_with_commas = f'{max_length:,}'
        max_length = len(max_length_with_commas)
        FORMATTING = f'%{max_length}s'  # right-justified formatting
        ''' Print the output to the screen '''
        print()
        for key, scrobs in alpha_catalog.items():
            num_listens_with_commas = f'{len(scrobs):,d}'
            formatted_num_listens = f'{FORMATTING % num_listens_with_commas}'
            print(f'{ANSI.BRIGHT_WHITE_BOLD}{formatted_num_listens}', end='')
            if is_artist_catalog_request:
                # Behavior when printing ARTIST-sorted catalog requests only
                print(f'{ANSI.RESET} {key}')
            else:
                key_portion = f'{ANSI.BRIGHT_CYAN}  {key}{ANSI.RESET}'
                artist_name = f'{scrobs[0].get_track().get_artist()}'
                print(f'{key_portion} [{artist_name}]')
        print()

# =========== [3] Utility: ==================================================

    def __by_song(self, scrobble:Scrobble):
        return scrobble.get_track().get_song()

    def __by_artist(self, scrobble:Scrobble):
        return scrobble.get_track().get_artist()
    
    def __by_album(self, scrobble:Scrobble):
        return scrobble.get_track().get_album()

# =========== [4] Catalogs: =================================================
        
    def __make_daily_catalog(self):
        '''
        Generates a one-to-many daily catalog of Scrobbles (grouped by date).
        The internal data structure is an OrderedDict (maintains insertion
        order). The key is is a datetime object (the term) and the value is a
        list of Scrobbles. Catalog is sorted in chronological order, meaning 
        oldest Scrobbles come at the beginning of the catalog.
        '''
        self.__daily_catalog = OrderedDict()
        num_distinct_days = 0
        for scrob in reversed(self.__stnd_catalog):
            date = scrob.get_date()
            if date not in self.__daily_catalog:
                num_distinct_days += 1
                self.__daily_catalog[date] = []
            self.__daily_catalog[date].append(scrob)
        self.__num_distinct_days = num_distinct_days

    def __make_alphabetized_catalogs(self):
        '''
        Generates 3 new catalogs alphabetically-sorted by song name, artist
        name, and album name.
        '''
        # assign to local variables
        song_catalog = self.__make_alpha_catalog(self.__by_song)
        artist_catalog = self.__make_alpha_catalog(self.__by_artist)
        album_catalog = self.__make_alpha_catalog(self.__by_album)
        # assign to instance variables
        self.__alpha_song_catalog = song_catalog
        self.__alpha_artist_catalog = artist_catalog
        self.__alpha_album_catalog = album_catalog

    def __make_alpha_catalog(self, get_field):
        '''
        Returns a new catalog alphabetically-sorted by the specified get_field
        (either song, artist, or album name)
        '''
        temp_catalog = self.__stnd_catalog.copy()
        temp_catalog.sort(key=get_field)
        alpha_catalog = OrderedDict()
        for scrob in temp_catalog:
            item = get_field(scrob)
            if item not in alpha_catalog:
                alpha_catalog[item] = []
            alpha_catalog[item].append(scrob)
        return alpha_catalog
     