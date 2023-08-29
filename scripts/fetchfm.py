from os import path
from time import sleep
from ansi import ANSI
from catalog import Catalog
from my_enums import MainMenuChoices, QueryType
from api_handler import get_path, fetch_scrobbled_data, is_valid_user, \
    get_ansi_bytey

LOGO = """
      ███████╗███████╗████████╗░█████╗░██╗░░██╗░░░███████╗███╗░░░███╗  _ ♪   /)---(\\
      ██╔════╝██╔════╝╚══██╔══╝██╔══██╗██║░░██║░░░██╔════╝████╗░████║  \\\\ ♪ (/ . . \\)
      █████╗░░█████╗░░░░░██║░░░██║░░╚═╝███████║░░░█████╗░░██╔████╔██║ ♪ \\\\__)-\\(*)/
      ██╔══╝░░██╔══╝░░░░░██║░░░██║░░██╗██╔══██║░░░██╔══╝░░██║╚██╔╝██║   \\_       (_
      ██║░░░░░███████╗░░░██║░░░╚█████╔╝██║░░██║██╗██║░░░░░██║░╚═╝░██║   (___/-(____)
^^^^^^╚═╝░░░░░╚══════╝░░░╚═╝░░░░╚════╝░╚═╝░░╚═╝╚═╝╚═╝░░░░░╚═╝░░░░░╚═╝^^^^^^^^^^^^^^^^^ \
"""

USERNAME = ''
CATALOG = None
prev_user = ''
has_previous_user = False

_DEBUGGING = False


# =========== [1] Main Program: =============================================

def main():
    _display_logo()
    _check_for_prev_user()  # sets the `has_previous_user` global variable
    print()
    username = _get_username()
    if username.lower() == 'q':
        print()
        return
    elif username == '' and has_previous_user:
        # previous user route
        global USERNAME
        USERNAME = prev_user
        run_user_interface()
    else:
        # new user route
        _check_lastfm_user(username)


def run_user_interface():
    '''
    Manages the Fetch.fm UI
    '''
    if not _DEBUGGING:
        fetch_scrobbled_data(USERNAME)
    _create_catalog()
    _bytey_welcome_msg()
    MENU_FUNCTIONS = {
        MainMenuChoices.FUN_FACTS: option_1,
        MainMenuChoices.TIMING_DATA: option_2,
        MainMenuChoices.TRACK_STATS: not_implemented,
        MainMenuChoices.SCROBBLES: not_implemented
    }
    MAIN_MENU_CHOICES = list(MainMenuChoices)
    ansi = ANSI.BRIGHT_CYAN_BOLD
    while True:
        display_main_menu()
        my_choice = get_choice(MAIN_MENU_CHOICES, ansi)
        if my_choice == 'q':
            break
        MENU_FUNCTIONS[my_choice]()  # call corresponding function (switch)


def display_main_menu():
    '''
    Prints a list of the Main Menu choices for the user to choose from
    '''
    ansi = ANSI.BRIGHT_CYAN
    ANSI_MUSIC = f'{ANSI.GREEN}♪{ANSI.BLUE}♪{ANSI.BRIGHT_PURPLE}♪{ANSI.RESET}'
    print(f' {ANSI.BRIGHT_CYAN_BOLD}Main Menu:{ANSI.RESET}')
    print_menu_choice(1, ansi, f'fun facts for {USERNAME} {ANSI_MUSIC}')
    print_menu_choice(2, ansi, 'explore your timing data')
    print_menu_choice(3, ansi, 'explore your track stats')
    print_menu_choice(4, ansi, 'delve into your scrobbles')
    print_menu_choice(5, ansi, 'quit program\n')


def option_1():
    '''
    Reads in user_info.txt data and prints the result/fun facts to the screen
    '''
    res = _read_user_info_txt_file()
    if res is None:
        print('  * Hmm... Fetch seems to have gotten lost. Try again soon!')
        return
    # `res` -> (realname, playcount, track_count, album_count, artist_count)
    total_n_days = CATALOG.get_total_num_distinct_days()
    most_streamed_days, num_streams = CATALOG.most_streamed_day_overall()
    daily_avg = round(res[1] / total_n_days) if total_n_days != 0 else 0
    ''' Generate ANSI symbols (i.e. Bytey list, arrows) '''
    BYTEY = get_ansi_bytey(ANSI.RESET, True)
    ARROWS = [
        ANSI.GREEN + '⇒' + ANSI.RESET,
        ANSI.BLUE + '⇒' + ANSI.RESET,
        ANSI.BRIGHT_PURPLE + '⇒' + ANSI.RESET
    ]
    ''' Now, format the user info using ANSI and commas (if numeric). When
        completed, `ansi` will be a tuple of the structure:
            -> (realname, playcount, track_count, album_count, artist_count,
                daily_avg, total_n_days, num_streams)
    '''
    ansi = _get_opt1_ansi_tuple(res[0], res[1], res[2], res[3], res[4],
                               daily_avg, total_n_days, num_streams)
    # Time to print to the screen
    _print_fun_facts(BYTEY, ARROWS, ansi, num_streams, most_streamed_days)


def option_2():
    '''
    Provides the user the oppurtunity to query their Last.fm timing data
    '''
    _display_option_2_menu()
    my_choice = get_choice(list(QueryType), ANSI.BRIGHT_GREEN_BOLD)
    if my_choice == QueryType.SONG:
        _run_option_2_for_songs()
    elif my_choice == QueryType.ARTIST:
        _run_option_2_for_artists()
    elif my_choice == QueryType.ALBUM:
        _run_option_2_for_albums()
    else:
        return  # my_choice == 'q'
    option_2()


def not_implemented():
    # TODO
    print(' >> Work in progress\n')


# =========== [2] Utility: ==================================================

def get_choice(menu_choices, ansi):
    '''
    Retrieves the user's menu choice from the provided list of choices
    '''
    result = None
    ansi_enter = f' {ansi}Enter Option #:{ANSI.RESET} '
    while True:
        choice = input(ansi_enter)
        if choice.isdigit():
            if int(choice) == len(menu_choices) + 1:
                result = 'q'
                break
            if 1 <= int(choice) <= len(menu_choices):
                result = menu_choices[int(choice) - 1]
                break
        # if we get here, the user did not type in an int. display message
        print(f'\n  * {choice} isn\'t a valid choice\n')
    print()
    return result


def print_menu_choice(choice, ansi, choice_description):
    '''
    Prints the provided menu-choice selection correctly formatted
    '''
    print(f'  ‣ {ansi}{choice}{ANSI.RESET}  {choice_description}')


def print_text_animated(text, end_delay_in_secs):
    if _DEBUGGING:
        print(text, end='')
    else:
        LAST_INDEX = len(text) - 1
        for i, ch in enumerate(text):
            if i == LAST_INDEX:
                sleep(end_delay_in_secs)
            elif ch != ' ':
                # only sleep for visible chars
                sleep(0.009)
            print(ch, end='', flush=True)


def format_num(ansi, num):
    '''
    Formats the given number with commas and displays it with ANSI
    '''
    return f'{ansi}{format(num, ",")}{ANSI.RESET}'


def format_time(total_seconds, ansi):
    '''
    Formats the given time tuple (hr, min, sec) with ANSI abbreviations
    '''
    time_tuple = get_seconds_human_readable(total_seconds)
    hr, min, sec = time_tuple  # unpack
    ansi_hr = f'{format_num(ansi, hr)}{ansi}h{ANSI.RESET}'
    ansi_min = f'{format_num(ansi, min)}{ansi}m{ANSI.RESET}'
    ansi_sec = f'{format_num(ansi, sec)}{ansi}s{ANSI.RESET}'
    return ansi_hr, ansi_min, ansi_sec


def get_seconds_human_readable(total_seconds):
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return int(hours), int(minutes), int(seconds)


def seconds_to_days(total_seconds):
    NUM_SECONDS_IN_DAY = 86400
    num_days = total_seconds / NUM_SECONDS_IN_DAY
    return num_days


# =========== [3] Miscellaneous: ============================================

def _display_logo():
    '''
    Displays the Fetch.fm logo to the screen
    '''
    ansi_logo = f'{ANSI.BRIGHT_CYAN_BOLD}{LOGO}{ANSI.RESET}'
    print_text_animated(f'\n{ansi_logo}', 1)


def _check_for_prev_user():
    '''
    Checks to see if there exists a valid Last.fm username stored in the
    current_user.txt file. Flips the global `has_previous_user` variable to
    True in the case that one is found, left as False otherwise
    '''
    current_user_path = get_path('user_info', 'current_user.txt')
    if path.exists(current_user_path):
        with open(current_user_path, 'r') as f:
            text = f.read()
            if is_valid_user(text):
                global has_previous_user
                has_previous_user = True
                global prev_user
                prev_user = text


def _get_username():
    '''
    Prompts the user to enter their Last.fm username, default to the previous
    user (if available), or quit. Does NOT check if the user input is a valid
    Last.fm username.
    '''
    ANSI_ACCENT = ANSI.CYAN_BOLD
    prompt = f'Provide your Last.fm {ANSI_ACCENT}username{ANSI.RESET}'
    if has_previous_user:
        ANSI_PREV_USER = ANSI.BRIGHT_WHITE_BOLD + prev_user + ANSI.RESET
        prompt += (f' (or to default to {ANSI_PREV_USER}, press'
                   f' {ANSI_ACCENT}`enter`{ANSI.RESET})')
    prompt += f'; to exit, type {ANSI_ACCENT}`q`{ANSI.RESET}: {ANSI.CYAN}'
    # print the full prompt to the screen
    print(f'\n{prompt}', end='')
    user_input = input()
    print(ANSI.RESET, end='')  # reset ansi back to default
    return user_input


def _check_lastfm_user(username):
    '''
    Prompts the user for their Last.fm username until a valid one is given. 
    Once a valid username is provided, fetches the user's scrobbled data and
    runs the Fetch.fm UI
    '''
    global USERNAME
    while username.isspace() or not is_valid_user(username):
        ANSI_USER = ANSI.CYAN_BOLD + username + ANSI.RESET
        print(f'\n * Sorry, but {ANSI_USER} is not a valid Last.fm username')
        username = _get_username()
        if username.lower() == 'q' or (username == '' and has_previous_user):
            break
    # If we get here, the user has either entered a valid username, wishes to
    # us the previous user (if available), or would like to quit the program
    if username.lower() == 'q':
        print()
        return
    elif username == '' and has_previous_user:
        USERNAME = prev_user
        run_user_interface()
    else:
        # verify w user that there's no typos in the provided VALID username
        ANSI_USER = ANSI.CYAN_BOLD + username + ANSI.RESET
        ANSI_Y = ANSI.CYAN_BOLD + '`y`' + ANSI.RESET
        ANSI_ENTER = ANSI.CYAN_BOLD + '`enter`' + ANSI.RESET
        print(f'\nYour Last.fm username is currently set to {ANSI_USER}. Type '
              f'{ANSI_Y} to make edits, else hit {ANSI_ENTER} to continue: ' 
              + ANSI.CYAN, end='')
        user_input = input()
        print(ANSI.RESET, end='')  # reset ansi back to default
        if user_input.lower() == 'y' or user_input.lower() == 'yes':
            # the user would like to make changes to their username
            ANSI_Q = ANSI.CYAN_BOLD + '`q`' + ANSI.RESET
            print(f'  -> Provide new username, or type {ANSI_Q} to quit: ' 
                  + ANSI.CYAN, end='')
            user_input = input()
            print(ANSI.RESET, end='')  # reset ansi back to default
            _check_lastfm_user(user_input)
        else:
            # the user would like to proceed with the current username
            USERNAME = username
            run_user_interface()


def _bytey_welcome_msg():
    BYTEY = get_ansi_bytey(ANSI.BRIGHT_CYAN_BOLD, False)
    GRASS = f'{ANSI.BRIGHT_CYAN_BOLD}^^^^^^^^^^^^^^^{ANSI.RESET}'
    msg = f""" \
 /‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾\\
 |                              Welcome to Fetch.fm!                                  |
 |                                                                                    |
 |   My name's Bytetholomew, but you can call me `Fetch` for short! I'm the company   |
 |  mascot, but today's my day off so I thought I'd spend it tagging along with you.  |
 |                                                                                    |
 |   Please select one of the following menu options to get started using Fetch.fm!   |
  \\__________________________________________   _____________________________________/
                                             | /
                               {BYTEY[0]} |/
                               {BYTEY[1]}
                               {BYTEY[2]}
                               {BYTEY[3]}
                               {BYTEY[4]}
                              {GRASS}
"""
    print_text_animated(f'\n{msg}\n', 0)


def _create_catalog():
    '''
    Creates the user's global catalog object
    '''
    global CATALOG
    file_path = get_path('scrobbled_data', f'{USERNAME}.txt')
    with open(file_path, 'r') as f:
        scrobbled_data = f.readlines()
        CATALOG = Catalog(USERNAME, scrobbled_data)


def _read_user_info_txt_file():
    '''
    Extracts information from the user's user_info.txt file. If the file does 
    not exist, return None; else, the returned tuple will include:
        - `str`: realname (defaults to USERNAME if realname not present)
        - `int`: playcount
        - `int`: track_count
        - `int`: album_count
        - `int`: artist_count
    '''
    user_info_path = get_path('user_info', f'{USERNAME}.txt')
    if path.exists(user_info_path):
        with open(user_info_path, 'r') as f:
            lines = f.readlines()
        user_info_dict = {}
        for line in lines:
            key_value = line.strip().split('\t')
            if len(key_value) == 2:
                key, value = key_value
                user_info_dict[key] = value
            else:
                # edge case where their is a missing value (i.e. realname)
                key = key_value[0]
                user_info_dict[key] = None
        # convert numeric values from strings to integers
        numeric_keys = ['playcount', 'track_count', 'album_count', 
                        'artist_count']
        for key in numeric_keys:
            if user_info_dict[key] is not None:
                user_info_dict[key] = int(user_info_dict[key])
        # return only select fields from the user info dictionary
        desired_keys = ['realname'] + numeric_keys
        # verify that the realname field is not None, if so default to USERNAME
        realname = user_info_dict['realname']
        user_info_dict['realname'] = USERNAME if realname is None else realname
        result = tuple(user_info_dict.get(key) for key in desired_keys)
        return result
    else:
        return None


def _get_opt1_ansi_tuple(realname, playcount, track_count, album_count, 
                        artist_count, daily_avg, total_n_days, num_streams):
    '''
    Returns a tuple containing the following information formatted with ANSI 
    and commas (if it's a numeric value):
        * realname
        * playcount
        * track_count
        * album_count
        * artist_count
        * daily_avg
        * total_n_days
        * num_streams
    '''
    ansi = ANSI.CYAN_BOLD
    ansi_name = f'{ansi}{realname}{ANSI.RESET}'
    ansi_playcount = format_num(ansi, playcount)
    ansi_n_tracks = format_num(ansi, track_count)
    ansi_n_albums = format_num(ansi, album_count)
    ansi_n_artists = format_num(ansi, artist_count)
    ansi_avg = format_num(ansi, daily_avg)
    ansi_n_days = format_num(ansi, total_n_days)
    ansi_n_streams = format_num(ansi, num_streams)
    return (ansi_name, ansi_playcount, ansi_n_tracks, ansi_n_albums, 
            ansi_n_artists, ansi_avg, ansi_n_days, ansi_n_streams)


def _print_fun_facts(BYTEY, ARROWS, ansi, n_streams, most_streamed_days):
    if n_streams == 0:
        bytey_4 = f'{BYTEY[4]}'
    else:
        # expected behavior
        f_date = most_streamed_days[0].strftime('%B %d, %Y')  # TODO
        ansi_date = f'{ANSI.CYAN_BOLD}{f_date}{ANSI.RESET}'
        bytey_4 = (f'{BYTEY[4]} {ARROWS[2]} you listened to the most music on '
                   f'{ansi_date} with {ansi[7]} total songs played')
    # Construct the message
    msg = f"""\
   {BYTEY[0]}
   {BYTEY[1]}Hey there, {ansi[0]}! Here are some fun music stats I dug up \
about you--
   {BYTEY[2]} {ARROWS[0]} you've listened to {ansi[1]} tracks over the past \
{ansi[6]} days, averaging {ansi[5]} tracks listened a day
   {BYTEY[3]} {ARROWS[1]} you\'ve enjoyed {ansi[2]} unique songs, explored \
{ansi[3]} different albums, and discovered {ansi[4]} diverse artists
   {bytey_4}
  ^^^^^^^^^^^^^^^
"""
    print(msg)


def _display_option_2_menu():
    '''
    Prints a list of choices available for option 2 for the user to select
    '''
    ansi = ANSI.BRIGHT_GREEN
    print(f' {ANSI.BRIGHT_GREEN_BOLD}Timing Menu:{ANSI.RESET}')
    print_menu_choice(1, ansi, 'search for song')
    print_menu_choice(2, ansi, 'search for artist')
    print_menu_choice(3, ansi, 'search for album')
    print_menu_choice(4, ansi, 'return to main menu\n')


def _run_option_2_for_songs():
    # request user input
    prompt = ('"Please provide the song and artist name you\'d like to search'
              ' for" -Fetch')
    song, artist, result = _get_opt2_listening_time(prompt, QueryType.SONG)
    if result[2] == 0:  # checks total_seconds val
        if song == '' or artist == '':
            print('\n * No data found for provided input\n')
        else:
            print(f'\n * No data found for "{song}" by {artist}\n')
        return
    # if we get here, the user has relevant listening time data
    song, artist, total_seconds = result
    playcount = CATALOG.num_plays_for_song(song)
    _print_opt2_output(playcount, total_seconds, f'{song} by {artist}')


def _run_option_2_for_artists():
    # request user input
    prompt = ('"Please provide the artist name you\'d like to search for" '
              '-Fetch')
    artist, result = _get_opt2_listening_time(prompt, QueryType.ARTIST)
    if result[1] == 0:  # checks total_seconds val
        if artist == '':
            print('\n * No data found for provided input\n')
        else:
            print(f'\n * No data found for "{artist}"\n')
        return
    # if we get here, the user has relevant listening time data
    artist, total_seconds, _ = result
    playcount = CATALOG.num_plays_for_artist(artist) 
    _print_opt2_output(playcount, total_seconds, artist)


def _run_option_2_for_albums():
    # request user input
    prompt = ('"Please provide the album and artist name you\'d like to search'
              ' for\" -Fetch')
    album, artist, result = _get_opt2_listening_time(prompt, QueryType.ALBUM)
    if result[2] == 0:  # checks total_seconds val
        if album == '' or artist == '':
            print('\n * No data found for provided input\n')
        else:
            print(f'\n * No data found for "{album}" by {artist}\n')
        return
    # if we get here, the user has relevant listening time data
    album, artist, total_seconds, playcount, _ = result
    _print_opt2_output(playcount, total_seconds, f'{album} by {artist}')


def _get_opt2_listening_time(prompt, type):
    '''
    Prompts the user for input relevant for the desired query type, then
    generates the listening time for the given input data
    '''
    print(f' {prompt}\n')
    if type == QueryType.SONG:
        # prompt user for song and artist name
        print(f'   ⇒ {ANSI.BRIGHT_GREEN}Song{ANSI.RESET}: ', end='')
        song = input()
        print(f'   ⇒ {ANSI.BRIGHT_GREEN}Artist{ANSI.RESET}: ', end='')
        artist = input()
        result = (song, artist, CATALOG.song_listening_time(song, artist))
    elif type == QueryType.ARTIST:
        # prompt user for artist name
        print(f'   ⇒ {ANSI.BRIGHT_GREEN}Artist{ANSI.RESET}: ', end='')
        artist = input()
        result = (artist, CATALOG.artist_listening_time(artist))
    else:
        # prompt user for album and artist name
        assert(type == QueryType.ALBUM)
        print(f'   ⇒ {ANSI.BRIGHT_GREEN}Album{ANSI.RESET}: ', end='')
        album = input()
        print(f'   ⇒ {ANSI.BRIGHT_GREEN}Artist{ANSI.RESET}: ', end='')
        artist = input()
        result = (album, artist, CATALOG.album_listening_time(album, artist))
    return result


def _print_opt2_output(playcount, total_seconds, item):
    '''
    Prints the generated output for option_2() to the screen
    '''
    ansi = ANSI.BRIGHT_GREEN_BOLD
    ANSI_PLAYCOUNT = format_num(ansi, playcount)
    ANSI_HR, ANSI_MIN, ANSI_SEC = format_time(total_seconds, ansi)
    print(f'\n  You\'ve listened to {item} {ANSI_PLAYCOUNT} times; totaling '
          f'{ANSI_HR}, {ANSI_MIN}, {ANSI_SEC}!\n')

    
if __name__ == '__main__':
    main()
