from time import sleep
from os import path
from ansi import ANSI
from catalog import Catalog
from api_handler import get_path, fetch_scrobbled_data, is_valid_user, \
    get_ansi_bytey
from menu_choices import MainMenuChoices

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

__DEBUGGING = True


# =========== [1] Main Program: =============================================

def main():
    display_logo()
    check_for_prev_user()  # sets the `has_previous_user` global variable
    print()
    username = get_username()
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
        check_lastfm_user(username)


def display_logo():
    '''
    Displays the Fetch.fm logo to the screen
    '''
    ansi_logo = f'{ANSI.BRIGHT_CYAN_BOLD}{LOGO}{ANSI.RESET}'
    print_text_animated(f'\n{ansi_logo}', 1)


def check_for_prev_user():
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


def get_username():
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


def check_lastfm_user(username):
    '''
    Prompts the user for their Last.fm username until a valid one is given. 
    Once a valid username is provided, fetches the user's scrobbled data and
    runs the Fetch.fm UI
    '''
    global USERNAME
    while username.isspace() or not is_valid_user(username):
        ANSI_USER = ANSI.CYAN_BOLD + username + ANSI.RESET
        print(f'\n * Sorry, but {ANSI_USER} is not a valid Last.fm username')
        username = get_username()
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
            check_lastfm_user(user_input)
        else:
            # the user would like to proceed with the current username
            USERNAME = username
            run_user_interface()


def create_database():
    '''
    Creates the global catalog object
    '''
    global CATALOG
    file_path = get_path('scrobbled_data', f'{USERNAME}.txt')
    with open(file_path, 'r') as f:
        scrobbled_data = f.readlines()
        CATALOG = Catalog(USERNAME, scrobbled_data)


def run_user_interface():
    '''
    Manages the Fetch.fm UI
    '''
    MENU_FUNCTIONS = {
        MainMenuChoices.FUN_FACTS: option_1,
        MainMenuChoices.TIMING_DATA: option_2,
        MainMenuChoices.TRACK_STATS: NotImplemented,
        MainMenuChoices.SCROBBLES: NotImplemented
    }
    fetch_scrobbled_data(USERNAME)  # update with user's new scrobbles
    create_database()
    bytey_welcome_msg()
    while True:
        display_main_menu()
        my_choice = get_main_menu_choice()
        if my_choice == MainMenuChoices.QUIT:
            break
        MENU_FUNCTIONS[my_choice]()  # call corresponding function (switch)


def option_2():
    '''
    Provides the user the oppurtunity to query their timing data
    '''
    result = CATALOG.artist_listening_time('Lana Del Rey')
    total_seconds = result[1]
    print(result)
    print_seconds_human_readable(total_seconds)
    pass


def option_1():
    '''
    Reads in user_info.txt data and prints the result/fun facts to the screen
    '''
    res = read_user_info_txt_file()
    if res is None:
        print('  * Hmm... Fetch seems to have gotten lost. Try again soon!')
        return
    # `res` -> (realname, playcount, track_count, album_count, artist_count)
    total_n_days = CATALOG.get_total_num_distinct_days()
    most_streamed_days, num_streams = CATALOG.most_streamed_day_overall()
    daily_avg = round(res[1] / total_n_days) if total_n_days != 0 else 0
    ''' Generate ANSI symbols (i.e. Bytey list, arrows) '''
    BYTEY = get_ansi_bytey(ANSI.BRIGHT_CYAN_BOLD, True)
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
    ansi = get_opt1_ansi_tuple(res[0], res[1], res[2], res[3], res[4],
                               daily_avg, total_n_days, num_streams)
    # Time to print to the screen
    print_fun_facts(BYTEY, ARROWS, ansi, num_streams, most_streamed_days)


def get_opt1_ansi_tuple(realname, playcount, track_count, album_count, 
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
    ansi_name = f'{ANSI.CYAN_BOLD}{realname}{ANSI.RESET}'
    ansi_playcount = ansi_with_commas(playcount)
    ansi_n_tracks = ansi_with_commas(track_count)
    ansi_n_albums = ansi_with_commas(album_count)
    ansi_n_artists = ansi_with_commas(artist_count)
    ansi_avg = ansi_with_commas(daily_avg)
    ansi_n_days = ansi_with_commas(total_n_days)
    ansi_n_streams = ansi_with_commas(num_streams)
    return (ansi_name, ansi_playcount, ansi_n_tracks, ansi_n_albums, 
            ansi_n_artists, ansi_avg, ansi_n_days, ansi_n_streams)


def print_fun_facts(BYTEY, ARROWS, ansi, n_streams, most_streamed_days):
    if n_streams == 0:
        bytey_4 = f'{BYTEY[4]}'
    else:
        # expected behavior
        f_date = most_streamed_days[0].strftime('%B %d, %Y')  # TODO
        ansi_date = f'{ANSI.CYAN_BOLD}{f_date}{ANSI.RESET}'
        bytey_4 = (f'{BYTEY[4]} {ARROWS[2]} you listened to the most music on '
                   f'{ansi_date}, with {ansi[7]} total songs played!')
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
  {ANSI.BRIGHT_CYAN_BOLD}^^^^^^^^^^^^^^^{ANSI.RESET} \
"""
    print(msg)
    

# =========== [2] Utility: ==================================================

def display_main_menu():
    '''
    Prints the Main Menu choices to the terminal for the user to read
    '''
    ANSI_MUSIC = f'{ANSI.GREEN}♪{ANSI.BLUE}♪{ANSI.BRIGHT_PURPLE}♪{ANSI.RESET}'
    print(f'\n {ANSI.BRIGHT_CYAN_BOLD}Main Menu:{ANSI.RESET}')
    print_choice(1, f'fun facts for {USERNAME} {ANSI_MUSIC}')
    print_choice(2, 'explore your timing data')
    print_choice(3, 'explore your track stats')
    print_choice(4, 'delve into your scrobbles')
    print_choice(5, 'quit program\n')


def print_choice(num, choice_description):
    '''
    Formats and prints the given menu-choice selection
    '''
    print(f'  ‣ {ANSI.BRIGHT_CYAN}{num}{ANSI.RESET}  {choice_description}')


def get_main_menu_choice():
    '''
    Retrieves the user's Main Menu choice (as an int) from the terminal
    '''
    MENU_CHOICES = list(MainMenuChoices)
    ansi_enter = f' {ANSI.BRIGHT_CYAN_BOLD}Enter Option #:{ANSI.RESET} '
    while True:
        user_input = input(f'{ansi_enter}')
        if user_input.isdigit() and 1 <= int(user_input) <= len(MENU_CHOICES):
            print()
            break
        # if we get here, the user did not type in an int. display message
        print(f'\n  * {user_input} isn\'t a valid choice\n')
    return MENU_CHOICES[int(user_input) - 1]


def read_user_info_txt_file():
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


def bytey_welcome_msg():
    BYTEY = get_ansi_bytey(ANSI.BRIGHT_CYAN_BOLD, False)
    GRASS = f'{ANSI.BRIGHT_CYAN_BOLD}^^^^^^^^^^^^^^^{ANSI.RESET}'
    msg = f""" \
  /‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾\\
 |                              Welcome to Fetch.fm!                                  |
 |                                                                                    |
 |   My name's Bytetholomew, but you can call me `Fetch` for short! I'm the company   |
 |  mascot, but today's my day off so I thought I'd spend it tagging along with you!  |
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
    print_text_animated(f'\n{msg}', 0)


def print_text_animated(text, end_delay_in_secs):
    if __DEBUGGING:
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


def ansi_with_commas(num):
    '''
    Formats the given number with commas and displays it with ANSI
    '''
    return f'{ANSI.CYAN_BOLD}{format(num, ",")}{ANSI.RESET}'


def print_seconds_human_readable(total_seconds):
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    print(f'{int(hours)}h {int(minutes)}m {int(seconds)}s spent listening')


def seconds_to_days(total_seconds):
    NUM_SECONDS_IN_DAY = 86400
    num_days = total_seconds / NUM_SECONDS_IN_DAY
    return num_days


if __name__ == '__main__':
    main()
