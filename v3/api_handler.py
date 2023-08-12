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


# =========== [1] Fetch Scrobbled Data: =====================================

def fetch_scrobbled_data(username) -> bool:
    '''
    Begins the process of fetching all of the user's scrobbled data and saving
    it in a seperate text file stored at /scrobbled_data/{username}.txt
    '''
    if username == '':
        # only prompt the user for their username if we weren't provided one
        username = get_username()
    if is_valid_user(username):
        # error check to ensure the username is a valid Last.fm user
        init_user_info_file(username)
        get_recent_tracks(username)
        print_bytey()
        return True
    else:
        ansi_user = f'{ANSI.BRIGHT_RED}{username}{ANSI.RESET}'
        msg = (f'\n * Sorry, but it seems {ansi_user} is not a valid Last.fm '
               'user!\n')
        print(msg)
        return False


def get_username():
    print('\nWhat is your Last.fm username? ' + ANSI.YELLOW, end='')
    username = input()
    print(ANSI.RESET, end='')
    return username


def init_user_info_file(username):
    '''
    Uses the contents of the user.getInfo API request to write to a text file 
    to be used later on during the Trackfm program
    '''
    LABELS = ['age', 'album_count', 'artist_count', 'country', 'gender', 
              'playcount', 'playlists', 'realname', 'subscriber',
              'track_count', 'url']
    response = lastfm_get({
        'method': 'user.getInfo',
        'user': username
    })
    if is_api_error(response):
        print(' * ERROR: unable to initialize the user_info.txt file due to '
              'an API request issue')
        return
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
    

# TODO-- make it so that we only append NEW scrobbles if the txt file already has some
def get_recent_tracks(username):
    '''
    Fetches all of the user's scrobbled data using the Last.fm API
    '''
    # Inform the user the fetching process is about to begin
    ansi_msg = (f'\n{ANSI.BRIGHT_WHITE_BOLD}\"Please hold tight as I fetch '
                f'your data from Last.fm!\"{ANSI.RESET} -Bytey\n')
    print(ansi_msg)
    # Create the desired txt file to store scrobbled data
    scrobbled_data_path = get_path('scrobbled_data', f'{username}.txt')
    Path(scrobbled_data_path).touch()
    # Begin process of fetching data from Last.fm
    page = 1
    total_pages = get_num_total_pages(username)
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
        if is_api_error(response):
            break
        # loop through the tracks listed on this page
        j_recenttracks = response.json()['recenttracks']
        write_scrobbles_to_file(j_recenttracks, username)
        time.sleep(0.25)  # rate limit
        page += 1
    # end of while loop, terminate the progress bar
    prog_bar.close()


def write_scrobbles_to_file(j_recenttracks, username):
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
        if date != None:
            # disregards tracks that are currently being scrobbled
            date = date['#text']
            scrob = date + '\t' + artist + '\t' + album + '\t' + song
            # time to write scrob to the file!
            scrobbled_data_path = get_path('scrobbled_data', f'{username}.txt')
            with open(scrobbled_data_path, 'a') as f:
                f.write(f'{scrob}\n')
                f.close()


def get_num_total_pages(username):
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
    if is_api_error(response):
        return -1
    j_recenttracks = response.json()['recenttracks']
    return int(j_recenttracks['@attr']['totalPages'])


# =========== [2] Retrieve Track Duration Info: =============================

def fetch_duration_data_for(song_name, artist_name, username):
    '''
    Makes an API request to retreive the track length for the provided track
    and returns a datetime.time containing the track length (or None if the
    provided song and artist names do not result in a valid track)
    '''
    payload = {
        'method': 'track.getInfo',
        'track': song_name,
        'artist': artist_name,
        'username': username,
        'autocorrect': True
    }
    response = lastfm_get(payload)
    if not is_api_error(response) and 'track' in response.json():
        duration = response.json()['track']['duration']
        return create_time_obj_from_milliseconds(duration)
    else:
        return None


# =========== [3] Utility: ==================================================
    
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
    return not is_api_error(response)


def is_api_error(response):
    '''
    Returns a bool indicating if an API request was successful or not
    '''
    SUCCESS_STATUS_CODE = 200
    if response == None:
        return True
    elif response.status_code != SUCCESS_STATUS_CODE:
        # print('\n~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*\n')
        # print(f'\tAPI Request Error: {str(response.status_code)}')
        # print('\n~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*\n')
        return True
    return False


def create_time_obj_from_milliseconds(milliseconds) -> dt_time:
    '''
    Returns a datetime.time object based on the provided milliseconds
    '''
    total_seconds = int(milliseconds) / 1000
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return dt_time(int(hours), int(minutes), int(seconds))


def print_bytey():
    '''
    Prints Bytey the ascii-dog to the terminal
       ,'.-.'. 
       '\~ o/` ,,
        { @ } f
        /`-'\$ 
       (_/-\_) 
    Credit: https://www.asciiart.eu/animals/dogs
    '''
    print('\n,\'.-.\'.')
    print('\'\\~ o/` ,,')
    print(' { @ } f')
    print(' /`-\'\\$')
    print('(_/-\\_) \n')


def jprint(obj):
    '''
    Create a formatted string of the Python JSON object
    '''
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'fetch':
        # only run fetch_scrobbled_data() if explicitly asked to
        _ = fetch_scrobbled_data('')
    