import json
import requests
from tqdm import tqdm
from sys import argv
from time import sleep
from os import path, makedirs, replace
from datetime import datetime, time
from pathlib import Path
from ansi import ANSI

API_KEY:str = open('admin/api_key.txt').read()        #  ** Replace with your API_KEY **
USER_AGENT:str = open('admin/user_agent.txt').read()  #  ** Replace with your USER_AGENT **

USERNAME = ''
song_length_cache = {}


# =========== [1] fetch_scrobbled_data() ====================================

def fetch_scrobbled_data(username):
    '''
    Handles the process of fetching all of the user's Last.fm data
    '''
    if username == '':
        # only occurs when user ran 'python api_handler.py fetch'
        while True:
            username = _get_username()
            if username.lower() == 'q':
                print()
                return
            if is_valid_user(username):
                break  # exit the while loop
            ANSI_USERNAME = ANSI.CYAN_BOLD + username + ANSI.RESET
            print(f'\n * Sorry, but {ANSI_USERNAME} is not a valid Last.fm '
                  'username')
    # if we get here, we have a valid Last.fm username
    global USERNAME
    USERNAME = username
    _init_user_info_file()
    _get_recent_tracks()
    print()


def _init_user_info_file():
    '''
    Makes the `user.getInfo` API request to retrieve/store relevant user info
    '''
    LABELS = ['age', 'album_count', 'artist_count', 'country', 'gender', 
              'playcount', 'playlists', 'realname', 'subscriber',
              'track_count', 'url']
    response = _lastfm_get({
        'method': 'user.getInfo',
        'user': USERNAME
    })
    if response is None:
        return
    # if we get here, we know the API request was successful
    j_user = response.json()['user']
    keys_to_extract = ['age', 'album_count', 'artist_count', 'country',
                       'gender', 'playcount', 'playlists', 'realname',
                       'subscriber', 'track_count', 'url']
    user_info = [j_user[key] for key in keys_to_extract]
    # time to write to the user_info text file
    user_info_txt_file = get_path('user_info', f'{USERNAME}.txt')
    with open(user_info_txt_file, 'w') as f:
        # timestamp the user info txt file
        current_datetime = datetime.now()
        formatted_date = current_datetime.strftime('%d %b %Y')
        twelve_hour_time = current_datetime.strftime('%I:%M %p')
        f.write(f'timestamp\t{formatted_date} {twelve_hour_time}\n')
        # append the retrieved user info to the txt file
        f.write(f'username\t{USERNAME}\n')
        for label, val in zip(LABELS, user_info):
            f.write(f'{label}\t{val}\n')
    # write the current username to current_user.txt
    current_user_txt_file = get_path('user_info', 'current_user.txt')
    with open(current_user_txt_file, 'w') as f:
        f.write(USERNAME)
    

def _get_recent_tracks():
    '''
    Retrieves all of the user's scrobbled data and stores it to a text file
    '''
    # Inform the user the fetching process is about to begin
    print(f'\n >> {ANSI.WHITE_UNDERLINED}Please hold tight as we fetch '
          f'{USERNAME}\'s data from Last.fm!{ANSI.RESET}\n')
    # Ensure we've created the user's scrobbled_data text file
    scrobbled_data_txt_file = get_path('scrobbled_data', f'{USERNAME}.txt')
    Path(scrobbled_data_txt_file).touch()
    ''' Begin the process of fetching data from Last.fm '''
    page = 1
    total_pages = _get_num_total_pages()
    last_saved_scrob, reached = _get_last_saved_scrob(scrobbled_data_txt_file)
    prog_bar = tqdm(total=total_pages)  # creates instance of the progress bar
    while page <= total_pages and not reached:
        prog_bar.update(1)
        payload = {
            'method': 'user.getRecentTracks',
            'limit': 200,
            'user': USERNAME,
            'page': page
        }
        response = _lastfm_get(payload)
        if response is None:
            break
        # loop through the tracks listed on this page
        j_tracks = response.json()['recenttracks']['track']
        reached = _write_scrobs_to_file(j_tracks, last_saved_scrob)
        if reached:
            ''' we've reached the last saved scrobble. now let's combine the
                new scrobbles with the old scrobbles into a single text file
            '''
            temp_file = get_path('scrobbled_data', 'temp.txt')
            with open(scrobbled_data_txt_file, 'r') as f:
                old_scrobbles = f.read()
            with open(temp_file, 'a') as f:
                f.write(old_scrobbles)
            replace(temp_file, scrobbled_data_txt_file)
        else:
            ''' proceed as normal '''
            sleep(0.25)  # rate limiting
            page += 1
    ''' end of while-loop, terminate the progress bar '''
    if page != total_pages:
        # we were able to speed up the process by caching old scrobs
        prog_bar.update(total_pages - page)
    prog_bar.close()


def _get_username():
    '''
    Prompts the user for their Last.fm username
    '''
    ANSI_USER = ANSI.CYAN_BOLD + 'username' + ANSI.RESET
    ANSI_Q = ANSI.CYAN_BOLD + '`q`' + ANSI.RESET
    prompt = f'Provide your Last.fm {ANSI_USER}; to exit, type {ANSI_Q}: '
    print(f'\n{prompt}{ANSI.CYAN}', end='')
    user_input = input()
    print(ANSI.RESET, end='')  # resets ansi back to default
    return user_input


def _write_scrobs_to_file(j_tracks, last_saved_scrob):
    '''
    Receives as input a list of tracks (in json) and aims to convert each into
    the 'scrobble' format and write it into the user's scrobbled_data txt file
    '''
    for track in j_tracks:
        album = track['album']['#text']
        artist = track['artist']['#text']
        song = track['name']
        date = track.get('date')  # check that this scrob contains 'date' key
        if date is not None:
            # this disregards tracks that are currently being scrobbled
            date = date['#text']
            scrob = date + '\t' + artist + '\t' + album + '\t' + song
            if last_saved_scrob is None:
                # case 1: append scrobbles to user's txt file as expected
                scrobbled_data_txt_file = get_path('scrobbled_data', 
                                                   f'{USERNAME}.txt')
                with open(scrobbled_data_txt_file, 'a') as f:
                    f.write(f'{scrob}\n')   
            else:
                # case 2: append new scrobbles to a temp txt file until the
                #           current scrob equals the last_saved_scrob
                if scrob == last_saved_scrob:
                    return True
                temp_txt_file = get_path('scrobbled_data', 'temp.txt')
                with open(temp_txt_file, 'a') as f:
                    f.write(f'{scrob}\n')
    return False


def _get_num_total_pages():
    '''
    Returns the user's overall `totalPages` used to instantiate progress bar
    '''
    payload = {
        'method': 'user.getRecentTracks',
        'limit': 200,
        'user': USERNAME,
        'page': 1
    }
    response = _lastfm_get(payload)
    if response is None:
        return -1
    j_recenttracks = response.json()['recenttracks']
    return int(j_recenttracks['@attr']['totalPages'])


def _get_last_saved_scrob(scrobbled_data_txt_file):
    '''
    In order to only make API calls for those scrobbles which we don't already
    have saved in the user's scrobbled_data txt file, let's store the 'last 
    saved scrobble' into a variable so that we can check if we've reached the
    point in the fetching process where we can stop making API calls since we
    already have the rest of the remaining scrobbled data
    '''
    with open(scrobbled_data_txt_file, 'r') as f:
        last_saved = f.readline().strip()
    if last_saved == '':
        return None, False
    # we assume that the read-in scrobble is formatted correctly
    return last_saved, False


# =========== [2] artist.getCorrection ======================================

def fetch_artist_name_corrected(artist) -> tuple[str, bool]:
    '''
    Makes an API request to check if the supplied artist has a correction to a 
    canonical Last.fm artist
    -----
    Returns a tuple containing...
        - `str`: artist name (formatted correctly if found)
        - `bool`: indicates if the returned artist name is formatted correctly
    '''
    payload = {
        'method': 'artist.getCorrection',
        'artist': artist
    }
    response = _lastfm_get(payload)
    if response is None:
        return artist, False
    # Now let's check if the JSON response actually contains desired fields
    j_res = response.json()
    if 'corrections' not in j_res or 'correction' not in j_res['corrections']:
        return artist, False
    # If we get here, we have a valid JSON response with desired fields
    formatted_artist = j_res['corrections']['correction']['artist']['name']
    return formatted_artist, True
    

# =========== [3] track.getInfo / album.getInfo =============================
    
def fetch_song_duration(song, artist, user) -> tuple[str, str, time]:
    '''
    Makes an API request to retrieve the song length for the provided track.
    -----
    Returns a tuple containing...
        - `str`: song name (formatted correctly if found)
        - `str`: artist name (formatted correctly if found)
        - `time`: track length (as a datetime.time object)
    '''
    # check the track length cache to see if we've made this request before
    if song_length_cache:
        for (cache_song, cache_artist), time_obj in song_length_cache.items():
            if (cache_song.lower() == song.lower() and
                    cache_artist.lower() == artist.lower()):
                # we found a match for the given request
                return cache_song, cache_artist, time_obj
    ''' if we get here, make an API request for a track we haven't cached '''
    j_response = _fetch_song_metadata(song, artist, user)
    if j_response is None:
        return song, artist, None
    ''' if we get here, we know we have a valid json format '''
    duration = j_response['track']['duration']
    # store corrected names (without any misspellings) into cache dict
    retrieved_song = j_response['track']['name']
    retrieved_artist = j_response['track']['artist']['name']
    time_obj = _create_time_obj_from_milliseconds(duration)
    # store the successful track length info into the cache
    song_length_cache[(retrieved_song, retrieved_artist)] = time_obj
    return retrieved_song, retrieved_artist, time_obj
    

def fetch_album_duration(album, artist, user) -> tuple[str, str, dict, int]:
    '''
    Makes an API request to retrieve the album duration for the provided album.
    -----
    Returns a tuple containing...
        - `str`: album name (formatted correctly if found)
        - `str`: artist name (formatted correctly if found)
        - `dict`: track listings of the form {song_name: datetime.time obj}
        - `int`: user's playcount for the album
    '''
    j_response = _fetch_album_metadata(album, artist, user)
    if j_response is None:
        return album, artist, None, 0
    ''' if we get here, we know we have a valid json format '''
    j_album = j_response['album']
    track_list = j_album['tracks']['track']  # python list
    result = {}
    for track in track_list:
        # find the duration of each track in the track list
        song_name = track['name']
        song_duration = 0 if track['duration'] is None else track['duration']
        result[song_name] = _create_time_obj_from_seconds(song_duration)
    corrected_album = j_album['name']
    corrected_artist = j_album['artist']
    userplaycount = j_album['userplaycount']
    return corrected_album, corrected_artist, result, userplaycount


def _fetch_song_metadata(song, artist, user):
    return _fetch_metadata('track.getInfo', song, artist, user)
    

def _fetch_album_metadata(album, artist, user):
    return _fetch_metadata('album.getInfo', album, artist, user)


def _fetch_metadata(method, item, artist, user) -> json:
    '''
    Makes an API request to retrieve the Last.fm metadata for the given item; 
    currently item must either be a 'song' or 'album' name
    '''
    item_key = 'track' if method == 'track.getInfo' else 'album'
    formatted_artist = fetch_artist_name_corrected(artist)[0]
    payload = {
        'method': method,
        item_key: item,
        'artist': formatted_artist,
        'username': user,
        'autocorrect': True
    }
    response = _lastfm_get(payload)
    if response is None or item_key not in response.json():
        return None
    return response.json()


def _create_time_obj_from_seconds(seconds):
    '''
    Returns a datetime.time object based on the provided amount of seconds
    '''
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return time(int(hours), int(minutes), int(seconds))


def _create_time_obj_from_milliseconds(milliseconds):
    '''
    Returns a datetime.time object based on the provided milliseconds
    '''
    total_seconds = int(milliseconds) / 1000
    return _create_time_obj_from_seconds(total_seconds)


# =========== [4] Utility ===================================================
    
def get_path(subdir, file):
    '''
    Returns the absolute path for a newly created file in the specified 
    subdirectory
    '''
    scripts_dir = path.dirname(__file__)
    parent_path = path.abspath(path.join(scripts_dir, '..'))
    subdir_path = path.join(parent_path, subdir)
    if not path.exists(subdir_path):
        # If the subdirectory doesn't exist, create it dynamically
        makedirs(subdir_path)
    return path.join(subdir_path, file)


def is_valid_user(username):
    '''
    Returns a bool indicating if the given username is a valid Last.fm user
    '''
    payload = {
        'method': 'user.getInfo',
        'user': username
    }
    response = _lastfm_get(payload)
    return False if response is None else True


def get_ansi_bytey(ansi, aligned):
    '''
    Returns a list in which each element is a particular line of ansi Bytey
    '''
    if aligned:
        alignment = ['   ', '  ', '    ', '    ', '   ']
    else:
        alignment = ['', '', '', '', '']
    # construct bytey now
    BYTEY = [
        '_     /)---(\\' + alignment[0],
        '\\\\   (/ . . \\)' + alignment[1],
        ' \\\\__)-\\(*)/' + alignment[2],
        ' \\_       (_' + alignment[3],
        ' (___/-(____)' + alignment[4]
    ]
    ansi_bytey = [f'{ansi}{line}{ANSI.RESET}' for line in BYTEY]
    return ansi_bytey


def _lastfm_get(payload):
    '''
    Generalized function for making a Last.fm API request
    '''
    # Define headers and URL
    headers = {'user-agent': USER_AGENT}
    url = 'https://ws.audioscrobbler.com/2.0/'
    # Add API key and format to the payload
    payload['api_key'] = API_KEY
    payload['format'] = 'json'
    # Generate the request
    response = requests.get(url, headers=headers, params=payload)
    if _is_api_error(response):
        return None
    return response


def _is_api_error(response):
    '''
    Returns a bool indicating if the API request was successful
    '''
    SUCCESS_STATUS_CODE = 200
    if response is None or response.status_code != SUCCESS_STATUS_CODE:
        return True
    return False


if __name__ == '__main__':
    if len(argv) > 1 and argv[1] == 'fetch':
        fetch_scrobbled_data('')
    