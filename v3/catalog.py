from comparators import Comparators
from scrobble import Scrobble
from collections import OrderedDict
from ansi import ANSI
from datetime import datetime, date, time
from typing import Callable


class Catalog(Comparators):
    '''
    A class to represent a catalog (collection) of Scrobbles
    '''

    '''
    TODO
     - make a list of all instance variables
     - make a list of all public method calls
    '''

    def __init__(self, sc):
        '''
        Create a new catalog of Scrobble obkects
        '''
        self.__stnd_catalog = []
        for line in sc:
            self.__stnd_catalog.append(Scrobble(line))
        self.__total_num_scrobbles = len(self.__stnd_catalog)

        # preemptively generate catalogs needed for future use
        self.__make_full_chrono_catalog()
        self.__make_date_chrono_catalog()
        self.__make_song_alpha_catalog()
        self.__make_artist_alpha_catalog()
        self.__make_album_alpha_catalog()

    def get_num_times_listened_to_song(self, song):
        return self.__num_listens(song, self.__alpha_song_catalog)
    
    def get_num_times_listened_to_artist(self, artist):
        return self.__num_listens(artist, self.__alpha_artist_catalog)
    
    def get_num_times_listened_to_album(self, album):
        return self.__num_listens(album, self.__alpha_album_catalog)

    def __num_listens(self, tgt:str, cat:OrderedDict):
        '''
        Helper method to reduce redundancy
        TODO FEATURE: equalsIgnoreCase()
		 *   - make it so that a user can type in "Don't Blame Me" or "don't blame me" and both would return the correct int answer
		 *   - make it so that Daylight by Taylor Swift and Daylight by Harry Styles don't both get added to the int answer
		 *        - maybe check that the artist name for every Scrobble in arr is all the same, if multiple then alert the user
		 *   - if I type in "Midnigh", ask the user: "Did you mean 'Midnights' or 'Midnights (3am Edition)'" aka autofill?
        '''
        streams = cat.get(tgt)
        return len(streams) if streams is not None \
            else self.__item_not_present(tgt)

    def __item_not_present(item):
        '''
        Prints a message informing the user that their input was not found
        within the user's catalog. This message is meant as a reminder for the
        user to check for typos and capitalization errors.
        '''
        print(ANSI.RESET)
        print(f' * {ANSI.BRIGHT_CYAN_BOLD}{item}{ANSI.RESET} was not found \
              within your Last.fm data')
        return 0
    
    def find_most_freq_song_on_date(self, month, day, year) -> list:
        '''
        Returns a list of song(s) which were the user's most listened to on
        a specific date
        '''
        freqs = {}  # intermediate storage container
        scrobs = self.get_scrobbles_on_date(month, day, year)
        # generate song frequencies
        for scrob in scrobs:
            song = scrob.get_track().get_song()
            if song not in freqs:
                freqs[song] = [0]
            freqs.get(song)[0] += 1
        return self.__list_of_most_freq(freqs)
    
    def find_most_freq_artist_on_date(self, month, day, year) -> list:
        '''
        Returns a list of artist(s) which were the user's most listened to on
        a specific date
        '''
        freqs = {}  # intermediate storage container
        scrobs = self.get_scrobbles_on_date(month, day, year)
        # generate artist frequencies
        for scrob in scrobs:
            artist = scrob.get_track().get_artist()
            if artist not in freqs:
                freqs[artist] = [0]
            freqs.get(artist)[0] += 1
        return self.__list_of_most_freq(freqs)
    
    def find_most_freq_album_on_date(self, month, day, year) -> list:
        '''
        Returns a list of album(s) which were the user's most listened to on
        a specific date
        '''
        freqs = {}  # intermediate storage container
        scrobs = self.get_scrobbles_on_date(month, day, year)
        # generate album frequencies
        for scrob in scrobs:
            album = scrob.get_track().get_album()
            if album not in freqs:
                freqs[album] = [0]
            freqs.get(album)[0] += 1
        return self.__list_of_most_freq(freqs)

    def __list_of_most_freq(self, freqs:map) -> list:
        '''
        Returns the most frequently occurring item(s) as a list
        '''
        result = []
        max_so_far = 0
        # iterate over freqs to find the most recurring item(s)
        for item, freq in freqs.items():
            curr = freq[0]
            if curr > max_so_far:
                max_so_far = curr
                result = [item]  # reset result with new max frequency item
            elif curr == max_so_far:
                result.append(item)  # add item to list of most frequent items
        # store the max freq into an instance variable
        self.__num_most_freq_on_date = freqs[result[0]][0] if result else 0
        return result

    def get_scrobbles_on_date(self, month, day, year):
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
        return self.__date_chrono_catalog.get(requested_date)

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
        print(f' * Sorry, but {ansi_req_date} is not within the range of your \
              scrobbled data:', end='')
        # print the formatted start and end range
        ansi_start_date = f'{ANSI.BRIGHT_CYAN}{formatted_start}{ANSI.RESET}'
        ansi_end_date = f'{ANSI.BRIGHT_CYAN}{formatted_end}{ANSI.RESET}'
        print(f'{ansi_start_date} - {ansi_end_date}.')

    ''' TODO check that these 3 still work!! '''
    def find_most_consecutive_song(self):
        return self.__find_most_consecutive(lambda track: track.get_song())

    def find_most_consecutive_artist(self):
        return self.__find_most_consecutive(lambda track: track.get_artist())

    def find_most_consecutive_album(self):
        return self.__find_most_consecutive(lambda track: track.get_album())

    def __find_most_consecutive(self, get_field:Callable):
        '''
        Returns a list of item names (song, artist, or album names) which the
        user has listened to the most consecutive number of times (i.e., most
        times listened to in a row).
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
            curr = get_field(self.__stnd_catalog[i].get_track())
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
                    '''
                    TODO FEATURE: what if before we discard the original array, we save it somewhere?
					 * 	 this way we will be able to see a list of most consecutively listened to songs
					 * 		- i.e. most consecutive (cellophane 56), second most consecutive, (don't blame me 49), ...
                    '''
                    result = [consec_item]  # update the result list
            elif self.__is_consecutive(i, second_length, second_item, 
                                       get_field):
                '''
                If we get here we now know curr item is NOT part of the longest
                consecutive streak. But, we do know that the curr item IS 
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
        self.__num_most_consecutive = longest_length  # store instance variable
        return result
                
    def __is_consecutive(self, i, length, field_val, get_field:Callable):
        if field_val != get_field(self.__stnd_catalog[i].get_track()):
            # the current item from stnd_catalog[i] breaks the chain of most
            # consecutively listened to song, artist, or album (field_val)
            return False
        # iterate over the length for the most consecutive item so far
        for offset in range(1, length):
            item1 = get_field(self.__stnd_catalog[i].get_track())
            item2 = get_field(self.__stnd_catalog[i - offset].get_track())
            if item1 != item2:
                return False
        return True

    ''' TODO check these 3 still work!! '''
    def most_listened_to_song(self):
        ''' Returns a list of most listened to song(s) name '''
        song = lambda track: track.get_song()
        catalog = self.__alpha_song_catalog
        return self.__most_listened_to(song, catalog)
    
    def most_listened_to_artist(self):
        ''' Returns a list of most listened to artist(s) name '''
        artist = lambda track: track.get_artist()
        catalog = self.__alpha_artist_catalog
        return self.__most_listened_to(artist, catalog)
    
    def most_listened_to_album(self):
        ''' Returns a list of most listened to album(s) name '''
        album = lambda track: track.get_album()
        catalog = self.__alpha_album_catalog
        return self.__most_listened_to(album, catalog)
    
    def __most_listened_to(self, get_field:Callable, alpha_catalog):
        result = []
        max_so_far = 0
        for _, scrobs in alpha_catalog.items():
            num_listens = len(scrobs)
            if num_listens > max_so_far:
                # we found a new max number of listens
                max_so_far = num_listens
                result = [get_field(scrobs[0].get_track())]
            elif num_listens == max_so_far:
                # at least 2 item fields (song, artist, or album) have the same
                # max number of listens, we want to record both in our result
                result.append(get_field(scrobs[0].get_track()))
        self.__num_most_listened_to = max_so_far  # store instance variable
        return result












    def __make_full_chrono_catalog(self):
        '''
        Generates a 1:1 chronologically-sorted catalog. The internal data
        structure is an OrderedDict (maintains insertion order). The key is
        is a datetime object (the term) and the value is a Scrobble. Oldest
        Scrobbles come at the beginning of the dict, newer come near the end.
        '''
        self.__full_chrono_catalog = OrderedDict()
        for index in range(self.__total_num_scrobbles - 1, -1, -1):
            scrob = self.__stnd_catalog[index]
            self.__full_chrono_catalog[scrob.get_term()] = scrob
        
    def __make_date_chrono_catalog(self):
        '''
        Generates a many-to-one grouped chronologically-sorted catalog
        '''
        self.__date_chrono_catalog = OrderedDict()
        num_distinct_days = 0
        for index in range(self.__total_num_scrobbles - 1, -1, -1):
            scrob = self.__stnd_catalog[index]
            date = scrob.get_date()
            if date not in self.__date_chrono_catalog:
                num_distinct_days += 1
                self.__date_chrono_catalog[date] = []
            # TODO check if this append works
            self.__date_chrono_catalog[date].append(scrob)
        self.__total_num_distinct_days = num_distinct_days

    def __make_song_alpha_catalog(self):
        '''
        Generates a new catalog alphabetically-sorted by song name
        '''
        temp_catalog = self.__stnd_catalog.copy()
        temp_catalog.sort(key=self.__song_key)
        self.__alpha_song_catalog = OrderedDict()
        for index in range(len(temp_catalog)):
            scrob = temp_catalog[index]
            song = scrob.get_track().get_song()
            if song not in self.__alpha_song_catalog:
                self.__alpha_song_catalog[song] = []
            self.__alpha_song_catalog[song].append(scrob)

    def __song_key(scrobble:Scrobble):
        return scrobble.get_track().get_song()
    
    def __make_artist_alpha_catalog(self):
        '''
        Generates a new catalog alphabetically-sorted by artist name
        '''
        temp_catalog = self.__stnd_catalog.copy()
        temp_catalog.sort(key=self.__artist_key)
        self.__alpha_artist_catalog = OrderedDict()
        for index in range(len(temp_catalog)):
            scrob = temp_catalog[index]
            artist = scrob.get_track().get_artist()
            if artist not in self.__alpha_artist_catalog:
                self.__alpha_artist_catalog[artist] = []
            self.__alpha_artist_catalog[artist].append(scrob)
    
    def __artist_key(scrobble:Scrobble):
        return scrobble.get_track().get_artist()
    
    def __make_album_alpha_catalog(self):
        '''
        Generates a new catalog alphabetically-sorted by album name
        '''
        temp_catalog = self.__stnd_catalog.copy()
        temp_catalog.sort(key=self.__album_key)
        self.__alpha_album_catalog = OrderedDict()
        for index in range(len(temp_catalog)):
            scrob = temp_catalog[index]
            album = scrob.get_track().get_album()
            if album not in self.__alpha_album_catalog:
                self.__alpha_album_catalog[album] = []
            self.__alpha_album_catalog[album].append(scrob)

    def __album_key(scrobble:Scrobble):
        return scrobble.get_track().get_album()

        

