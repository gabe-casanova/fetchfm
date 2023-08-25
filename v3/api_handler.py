import json
import os
import sys
import time
import requests
from tqdm import tqdm
from datetime import datetime, time as dt_time
from pathlib import Path
from ansi import ANSI

API_KEY:str = open('v3/admin/api_key.txt').read()        #  ** Replace with your API_KEY **
USER_AGENT:str = open('v3/admin/user_agent.txt').read()  #  ** Replace with your USER_AGENT **

song_length_cache = {}


# =========== [1] Fetch Scrobbled Data: =====================================

def fetch_scrobbled_data(username):
    '''
    Handles the process of fetching all of the user's scrobbled data and 
    storing it in a seperate text file stored at /scrobbled_data/{username}.txt
    '''
    if username == '':
        # we only get here when doing the explicit `getdata` command while 
        # running api_handler.py (we must prompt the user for their Last.fm 
        # as since we aren't passed one in)
        username = __get_username()
        while username.isspace() or not is_valid_user(username):
            ANSI_USERNAME = ANSI.CYAN_BOLD + username + ANSI.RESET
            print(f'\n * Sorry, but {ANSI_USERNAME} is not a valid Last.fm '
                  'username')
            username = __get_username()
            if username.lower() == 'q':
                break
        if username.lower() == 'q':
            print()
            return
    # if we get here, we have a valid Last.fm username
    init_user_info_file(username)
    get_recent_tracks(username)


def init_user_info_file(username):
    '''
    Uses the contents of the user.getInfo API request to write to a text file 
    to be used later on during the fetchfm program
    '''
    LABELS = ['age', 'album_count', 'artist_count', 'country', 'gender', 
              'playcount', 'playlists', 'realname', 'subscriber',
              'track_count', 'url']
    response = lastfm_get({
        'method': 'user.getInfo',
        'user': username
    })
    if response is None:
        return  # early return
    # if we get here, we know the API request was successful
    j_user = response.json()['user']
    user_info = [j_user['age'], j_user['album_count'], j_user['artist_count'],
                 j_user['country'], j_user['gender'], j_user['playcount'],
                 j_user['playlists'], j_user['realname'], j_user['subscriber'],
                 j_user['track_count'], j_user['url']]
    # time to write to our user_info text file
    user_info_path = get_path('user_info', f'{username}.txt')
    with open(user_info_path, 'w') as f:
        # get the current datetime and format it
        current_datetime = datetime.now()
        formatted_date = current_datetime.strftime('%d %b %Y')
        twelve_hour_time = current_datetime.strftime('%I:%M %p')
        # timestamp file + append the user_info received via API call
        f.write(f'timestamp\t{formatted_date} {twelve_hour_time}\n')
        f.write(f'username\t{username}\n')
        for i, label in enumerate(LABELS):
            f.write(f'{label}\t{user_info[i]}\n')
        f.close()
    # write the current username to a text file in subdir user_info/
    username_path = get_path('user_info', 'current_user.txt')
    with open(username_path, 'w') as f:
        f.write(username)
    

def get_recent_tracks(username):
    '''
    Fetches all of the user's scrobbled data using the Last.fm API
    '''
    # Inform the user the fetching process is about to begin
    ansi_msg = (f'\n{ANSI.CYAN_BOLD}\"Please hold tight as I fetch '
                f'your data from Last.fm!\"{ANSI.RESET} -Fetch\n')
    print(ansi_msg)
    # Create the desired txt file to store scrobbled data
    scrobbled_data_path = get_path('scrobbled_data', f'{username}.txt')
    Path(scrobbled_data_path).touch()
    # Begin process of fetching data from Last.fm
    page = 1
    total_pages = __get_num_total_pages(username)
    prog_bar = tqdm(total=total_pages)
    while page <= total_pages:
        prog_bar.update(1)
        payload = {
            'method': 'user.getRecentTracks',
            'limit': 200,
            'user': username,
            'page': page
        }
        response = lastfm_get(payload)
        if response is None:
            break
        # loop through the tracks listed on this page
        j_recenttracks = response.json()['recenttracks']
        __write_scrobbles_to_file(j_recenttracks, username)
        time.sleep(0.25)  # rate limit
        page += 1
    # end of while loop, terminate the progress bar
    prog_bar.close()


def __get_username():
    ANSI_USER = ANSI.CYAN_BOLD + 'username' + ANSI.RESET
    ANSI_Q = ANSI.CYAN_BOLD + '`q`' + ANSI.RESET
    prompt = f'Provide your Last.fm {ANSI_USER}; to exit, type {ANSI_Q}: '
    print(f'\n{prompt}{ANSI.CYAN}', end='')
    user_input = input()
    print(ANSI.RESET, end='')  # resets ansi back to default
    return user_input


def __write_scrobbles_to_file(j_recenttracks, username):
    '''
    Helper function to gather the scrobbles from the current API request and
    write the data generated into a text file in the scrobbled_data/ directory
    '''
    j_tracks = j_recenttracks['track']
    for track in j_tracks:
        album = track['album']['#text']
        artist = track['artist']['#text']
        song = track['name']
        date = track.get('date')  # check that this scrob contains 'date' key
        if date is not None:
            # disregards tracks that are currently being scrobbled
            date = date['#text']
            scrob = date + '\t' + artist + '\t' + album + '\t' + song
            # time to write scrob to the file!
            scrobbled_data_path = get_path('scrobbled_data', f'{username}.txt')
            with open(scrobbled_data_path, 'a') as f:
                f.write(f'{scrob}\n')
                f.close()


def __get_num_total_pages(username):
    '''
    Returns the user's overall `totalPages` used to instantiate progress bar
    '''
    payload = {
        'method': 'user.getRecentTracks',
        'limit': 200,
        'user': username,
        'page': 1
    }
    response = lastfm_get(payload)
    if response is None:
        return -1
    j_recenttracks = response.json()['recenttracks']
    return int(j_recenttracks['@attr']['totalPages'])


# =========== [2] artist.getCorrection: =====================================

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
    response = lastfm_get(payload)
    if response is None:
        return artist, False
    # Now let's check if the JSON response actually contains desired fields
    j_res = response.json()
    if 'corrections' not in j_res or 'correction' not in j_res['corrections']:
        return artist, False
    # If we get here, we have a valid JSON response with desired fields
    formatted_artist = j_res['corrections']['correction']['artist']['name']
    return formatted_artist, True
    

# =========== [3] Fetch Song/Album Duration: ================================
    
def fetch_song_duration(song, artist, user) -> tuple[str, str, dt_time]:
    '''
    Makes an API request to retrieve the song length for the provided track.
    -----
    Returns a tuple containing...
        - `str`: song name (formatted correctly if found)
        - `str`: artist name (formatted correctly if found)
        - `dt_time`: track length (as a datetime.time object)
    '''
    # check the track length cache to see if we've made this request before
    if song_length_cache:
        for (cache_song, cache_artist), time_obj in song_length_cache.items():
            if (cache_song.lower() == song.lower() and
                    cache_artist.lower() == artist.lower()):
                # we found a match for the given request
                return cache_song, cache_artist, time_obj
    ''' if we get here, make an API request for a track we haven't cached '''
    j_response = fetch_song_metadata(song, artist, user)
    if j_response is None:
        return song, artist, None
    ''' if we get here, we know we have a valid json format '''
    duration = j_response['track']['duration']
    # store corrected names (without any misspellings) into cache dict
    retrieved_song = j_response['track']['name']
    retrieved_artist = j_response['track']['artist']['name']
    time_obj = __create_time_obj_from_milliseconds(duration)
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
    j_response = fetch_album_metadata(album, artist, user)
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
        result[song_name] = create_time_obj_from_seconds(song_duration)
    corrected_album = j_album['name']
    corrected_artist = j_album['artist']
    userplaycount = j_album['userplaycount']
    return corrected_album, corrected_artist, result, userplaycount


def create_time_obj_from_seconds(seconds):
    '''
    Returns a datetime.time object based on the provided amount of seconds
    '''
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return dt_time(int(hours), int(minutes), int(seconds))


def __create_time_obj_from_milliseconds(milliseconds):
    '''
    Returns a datetime.time object based on the provided milliseconds
    '''
    total_seconds = int(milliseconds) / 1000
    return create_time_obj_from_seconds(total_seconds)


# =========== [4] Fetch Song/Album Metadata: ================================

def fetch_song_metadata(song, artist, user):
    return __fetch_metadata('track.getInfo', song, artist, user)
    

def fetch_album_metadata(album, artist, user):
    return __fetch_metadata('album.getInfo', album, artist, user)


def __fetch_metadata(method, item, artist, user) -> json:
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
    response = lastfm_get(payload)
    if response is None or item_key not in response.json():
        return None
    return response.json()


# =========== [5] Utility: ==================================================
    
def lastfm_get(payload) -> requests:
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
    if is_api_error(response):
        return None
    return response


def get_path(subdir, file) -> str:
    '''
    Returns the abs path for a newly created file in the specified 
    subdirectory
    '''
    v3_path = os.path.dirname(__file__)
    subdir_path = os.path.join(v3_path, subdir)
    # If the subdirectory doesn't exist, create it dynamically
    if not os.path.exists(subdir_path):
        os.makedirs(subdir_path)
    return os.path.join(subdir_path, file)


def is_valid_user(username) -> bool:
    '''
    Returns a bool indicating if the given username is a valid Last.fm user
    '''
    payload = {
        'method': 'user.getInfo',
        'user': username
    }
    response = lastfm_get(payload)
    return False if response is None else True


def is_api_error(response):
    '''
    Returns a bool indicating if the API request was successful
    '''
    SUCCESS_STATUS_CODE = 200
    if response is None or response.status_code != SUCCESS_STATUS_CODE:
        return True
    return False


def get_ansi_bytey(ansi, aligned) -> list:
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


def jprint(obj):
    '''
    Create a formatted string of the Python JSON object
    '''
    output = json.dumps(obj, sort_keys=True, indent=4)
    print(output)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'getdata':
        # only run fetch_scrobbled_data() if explicitly asked to
        fetch_scrobbled_data('')
    