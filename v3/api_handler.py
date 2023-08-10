import json
import os
import time
import ansi
import requests
from tqdm import tqdm
from datetime import datetime

# This code was written following the tutorial steps taken from this site:
# https://www.dataquest.io/blog/last-fm-api-python/

API_KEY = open('v3/admin/api_key.txt').read()
USER_AGENT = open('v3/admin/user_agent.txt').read()
HEADER_FORMAT = 'json'
SUCCESS_STATUS_CODE = 200
RATE_LIMITING_TIME = 0.25

username = ''
total_num_scrobs = 0


def main():
    '''
    Prompts the user for their Last.fm username, generates API requests,
    and populates the user's scrobbled_data.txt file
    '''
    # tqdm.pandas()  # useful for displaying progress bar
    get_username()
    init_user_info()
    get_scrobbled_data()
    print_bytey()


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
    print()
    print(',\'.-.\'.')
    print('\'\\~ o/` ,,')
    print(' { @ } f')
    print(' /`-\'\\$')
    print('(_/-\\_) ')
    print()


def get_scrobbled_data():
    '''
    Acquires all of the scrobbled data for the user, using the Last.fm API
    '''
    page = 1
    total_pages = get_total_pages()
    show_bytey_msg_1()
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
        get_scrobs_from_page(j_recenttracks)
        time.sleep(RATE_LIMITING_TIME)
        page += 1
    # end of while loop
    prog_bar.close()


def show_bytey_msg_1():
    '''
    Prints a message from Bytey the ascii-dog to inform the user to wait
    as the program fetches their data from the Last.fm API
    '''
    print()
    print(ansi.ANSI.BRIGHT_WHITE_BOLD, end='')
    print('\"Please hold tight as I fetch your data from Last.fm!\"', end='')
    print(ansi.ANSI.RESET + ' -Bytey')
    print()


def get_total_pages():
    '''
    Helper function to get the totalPages field of API response. Used
    because we need to know the total number of pages for the progress bar.
    Side effect of this fxn is that it ALSO sets the global total_num_scrobs
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
    global total_num_scrobs
    total_num_scrobs = j_recenttracks['@attr']['total']  # side effect
    return int(j_recenttracks['@attr']['totalPages'])


def is_api_error(response) -> bool:
    '''
    Returns a bool indicating if an API request was successful or not
    '''
    if response == None:
        print('\'response == None\'')
        return True
    elif response.status_code != SUCCESS_STATUS_CODE:
        print('API Request Error: ' + response.status_code)
        return True
    return False


def get_scrobs_from_page(j_recenttracks):
    '''
    Helper function to gather the scrobbles from the current API request and
    write the data generated to a txt file in the scrobbled_data/ directory
    '''
    j_tracks = j_recenttracks['track']
    for track in j_tracks:
        album = track['album']['#text']
        artist = track['artist']['#text']
        song = track['name']
        date = track.get('date')  # check that this scrob contains 'date' key
        if date != None:
            # disregards tracks that are currently being scrobbled
            #   todo-- find a solution that avoids this?
            date = date['#text']
            scrob = date + '\t' + artist + '\t' + album + '\t' + song
            # time to write scrob to the file!
            scrobbled_data_path = get_path('scrobbled_data', f'{username}.txt')
            with open(scrobbled_data_path, 'a') as f:
                f.write(f'{scrob}\n')
                f.close()


def get_username():
    '''
    Prompts the user for their Last.fm username
    '''
    print()
    print('What is your Last.fm username? ' + ansi.ANSI.YELLOW, end='')
    global username
    username = input()
    print(ansi.ANSI.RESET, end='')


def init_user_info():
    '''
    Make a call to Last.fm API to obtain info pertaining to the user. Once
    you make a successful request, populate the contents of the request into
    a text file to be used later on in the Trackfm program.
    '''
    response = lastfm_get({
        'method': 'user.getInfo',
        'user': username
    })
    labels = ['age', 'album_count', 'artist_count', 'country', 'gender', 
              'playcount', 'playlists', 'realname', 'subscriber', 
              'track_count', 'url']
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
        for i, label in enumerate(labels):
            f.write(f'{label}\t{user_info[i]}\n')
        f.close()
    # write the current username to a text file in subdir user_info/
    username_path = get_path('user_info', 'current_user.txt')
    with open(username_path, 'w') as f:
        f.write(username)


def get_path(subdir, file) -> str:
    '''
    Returns the abs path for a newly created file in the specified subdirectory
    '''
    v3_path = os.path.dirname(__file__)
    subdir_path = os.path.join(v3_path, subdir)
    # If the subdirectory doesn't exist, create it dynamically
    if not os.path.exists(subdir_path):
        os.makedirs(subdir_path)
    return os.path.join(subdir_path, file)
    

def lastfm_get(payload) -> requests:
    '''
    Generalized function for making a Last.fm API request.
    Code inspired from the tutorial linked at top of file.
    '''
    # Define headers and URL
    headers = {'user-agent': USER_AGENT}
    url = 'https://ws.audioscrobbler.com/2.0/'
    # Add API key and format to the payload
    payload['api_key'] = API_KEY
    payload['format'] = HEADER_FORMAT
    # Generate the request
    response = requests.get(url, headers=headers, params=payload)
    if is_api_error(response):
        return None
    return response


def jprint(obj):
    '''
    Create a formatted string of the Python JSON object.
    Code inspired from the tutorial linked at top of file.
    '''
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)


if __name__ == '__main__':
    main()