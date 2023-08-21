from os import path
from ansi import ANSI
from catalog import Catalog
from api_handler import get_path, fetch_scrobbled_data, is_valid_user
from menu_choices import MainMenuChoices

# Credit: https://fsymbols.com/text-art/
LOGO = """
████████╗██████╗░░█████╗░░█████╗░██╗░░██╗░░░███████╗███╗░░░███╗
╚══██╔══╝██╔══██╗██╔══██╗██╔══██╗██║░██╔╝░░░██╔════╝████╗░████║
░░░██║░░░██████╔╝███████║██║░░╚═╝█████═╝░░░░█████╗░░██╔████╔██║
░░░██║░░░██╔══██╗██╔══██║██║░░██╗██╔═██╗░░░░██╔══╝░░██║╚██╔╝██║
░░░██║░░░██║░░██║██║░░██║╚█████╔╝██║░╚██╗██╗██║░░░░░██║░╚═╝░██║
░░░╚═╝░░░╚═╝░░╚═╝╚═╝░░╚═╝░╚════╝░╚═╝░░╚═╝╚═╝╚═╝░░░░░╚═╝░░░░░╚═╝
"""

db = None  # global catalog obj
username = ''


# =========== [1] Main Program: =============================================

def main():
    ''' Initializes starting components for the Track.fm program '''
    welcome_msg()  # sets global username variable
    if username == '':
        # the user has decided to default to the current user
        found, error_msg = get_default_user()
        if found:
            if is_valid_user(username):
                run_trackfm()
            else:
                ansi_user = f'{ANSI.BRIGHT_RED}{username}{ANSI.RESET}'
                msg = (f' * Sorry, but it seems the default user, {ansi_user},'
                    ' is not a valid Last.fm user!\n')
                print(f'\n{msg}')
        else:
            print(error_msg)
    else:
        # begin the process of fetching user's scrobbled data
        success = fetch_scrobbled_data(username)
        if success:
            run_trackfm()


def run_trackfm():
    ''' Creates the global database object and begins the UI '''
    CHOICE_FUNCTIONS = {
        MainMenuChoices.USER_INFO: print_user_info,
        MainMenuChoices.TIME_STATS: NotImplemented,
        MainMenuChoices.TRACK_STATS: NotImplemented,
        MainMenuChoices.PRINTING: NotImplemented
    }
    create_database()
    while True:
        display_main_menu()
        my_choice = get_main_menu_choice()
        if my_choice == MainMenuChoices.QUIT:
            break
        CHOICE_FUNCTIONS[my_choice]()  # call corresponding function (switch)
    # if we get here, the user has terminated the program
    print(f'Thanks for using {ANSI.BRIGHT_CYAN_BOLD}Track.fm{ANSI.RESET} ^.^\n')


def print_user_info():
    '''
    Prints Bytey's fun facts (i.e. user info) to the terminal
    '''
    total_num_days = db.get_total_num_distinct_days()
    most_streamed_days, num_streams = db.most_streamed_day_overall()
    # read in info from the user's user_info.txt file
    result = read_user_info_txt_file()
    if result is None:
        # TODO
        return
    realname, playcount, track_count, album_count, artist_count = result
    user = realname if realname is not None else username
    # format the output with ANSI and commas
    ansi_user = f'{ANSI.CYAN_BOLD}{user}{ANSI.RESET}'
    ansi_playcount = ansi_commas(playcount)
    ansi_track_count = ansi_commas(track_count)
    ansi_album_count = ansi_commas(album_count)
    ansi_artist_count = ansi_commas(artist_count)
    # calculate daily average and format w ANSI
    daily_average = round(playcount / total_num_days)
    ansi_daily_average = ansi_commas(daily_average)
    ansi_num_days = ansi_commas(total_num_days)
    ''' Get Bytey the ASCII dog broken up into its individual lines '''
    BYTEY = get_bytey_ansi_parts()
    # print the message to the screen
    print(BYTEY[0])
    print(f'{BYTEY[1]}Hey there, {ansi_user}! Here are some fun music stats I '
          'dug up about you--')
    print(f'{BYTEY[2]} ⇒ you\'ve listened to {ansi_playcount} tracks over the '
          f'past {ansi_num_days} days, averaging {ansi_daily_average} tracks '
          'listened a day')
    print(f'{BYTEY[3]} ⇒ you\'ve enjoyed {ansi_track_count} unique songs, '
          f'explored {ansi_album_count} different albums, and discovered '
          f'{ansi_artist_count} diverse artists')
    if num_streams == 0:
        # edge case
        print(BYTEY[4])
        return
    # if we get here, we know most_streamed_days list is NOT empty
    formatted_date = most_streamed_days[0].strftime('%B %d, %Y')
    ansi_date = f'{ANSI.CYAN_BOLD}{formatted_date}{ANSI.RESET}'
    ansi_num_streams = ansi_commas(num_streams)
    print(f'{BYTEY[4]} ⇒ on {ansi_date} you listened to a lot of music, with '
          f'{ansi_num_streams} total songs played (..the most of any day!)')
    

# =========== [2] Miscellaneous: ============================================

def welcome_msg():
    global username
    ansi_logo = f'{ANSI.BRIGHT_CYAN_BOLD}{LOGO}{ANSI.RESET}'
    ansi_lastfm = f'{ANSI.CYAN_BOLD}Last.fm username{ANSI.RESET}'
    ansi_enter = f'{ANSI.BRIGHT_WHITE_BOLD}`enter`{ANSI.RESET}'
    print(f'\n{ansi_logo}\n')
    print(f'Enter your {ansi_lastfm} or press {ansi_enter} to default to '
          f'the current user: {ANSI.BRIGHT_BLUE}', end='')
    username = input()
    print(ANSI.RESET, end='')


def get_default_user():
    '''
    Returns a bool indicating if the current_user.txt file was successfully
    located. If unsuccessful, the str will contain the error message to print
    '''
    try:
        curr_user_path = get_path('user_info', 'current_user.txt')
        with open(curr_user_path, 'r') as f:
            global username
            username = f.read()
        return True, ''
    except (FileNotFoundError, OSError):
        error_header = ' * ERROR: Default failed'
        bullet_1 = ('-> Please ensure you\'ve ran `python api_handler.py '
                    'fetch` before you attempt to run `python trackfm.py`')
        bullet_2 = ('-> Or, please enter your Last.fm username instead of '
                    'defaulting to the current user')
        error_msg = f'\n{error_header}\n     {bullet_1}\n     {bullet_2}\n\n'
        return False, error_msg


def create_database():
    '''
    Creates the global catalog object ('db')
    '''
    global db
    file_path = get_path('scrobbled_data', f'{username}.txt')
    with open(file_path, 'r') as f:
        scrobbled_data = f.readlines()
        db = Catalog(username, scrobbled_data)


def display_main_menu():
    '''
    Prints the Main Menu choices to the terminal for the user to read
    '''
    print()
    print(f' {ANSI.BRIGHT_BLUE_BOLD}Main Menu:{ANSI.RESET}')
    print_menu_choice('  ', 1, 'Bytey\'s fun facts :3')
    print_menu_choice('  ', 2, 'explore your timing data')
    print_menu_choice('  ', 3, 'explore track-based stats')
    print_menu_choice('  ', 4, 'delve into your scrobbles')
    print_menu_choice('  ', 5, 'quit program')
    print()


def print_menu_choice(indent, key, msg):
    print(f'{indent}Opt {ANSI.BRIGHT_BLUE}{key}{ANSI.RESET} ⇒ {msg}')


def get_main_menu_choice():
    '''
    Retrieves the user's Main Menu choice (as an int) from the terminal
    '''
    MENU_CHOICES = list(MainMenuChoices)
    ansi_enter = f' {ANSI.BRIGHT_BLUE_BOLD}Enter Option #:{ANSI.RESET} '
    while True:
        user_input = input(f'{ansi_enter}')
        if user_input.isdigit() and 1 <= int(user_input) <= len(MENU_CHOICES):
            print()
            break
        # if we get here, the user did not type in an int. display message
        ansi_input = f'{ANSI.BRIGHT_CYAN_BOLD}{user_input}{ANSI.RESET}'
        print(f'\n  * {ansi_input} isn\'t a valid choice\n')
    return MENU_CHOICES[int(user_input) - 1]


def read_user_info_txt_file():
    '''
    Extracts information from the user's user_info.txt file. If the file does 
    not exist, return None; else, the returned tuple will include:
        - `str`: realname
        - `int`: playcount
        - `int`: track_count
        - `int`: album_count
        - `int`: artist_count
    '''
    user_info_path = get_path('user_info', f'{username}.txt')
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
        result = tuple(user_info_dict.get(key) for key in desired_keys)
        return result
    else:
        return None


# =========== [3] Utility: ==================================================

def print_seconds_human_readable(total_seconds):
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    print(f'{hours}h {minutes}m {seconds}s spent listening')


def seconds_to_days(total_seconds):
    NUM_SECONDS_IN_DAY = 86400
    num_days = total_seconds / NUM_SECONDS_IN_DAY
    return num_days


def ansi_commas(num):
    '''
    Formats the given number with commas and displays it in ANSI
    '''
    return f'{ANSI.CYAN_BOLD}{format(num, ",")}{ANSI.RESET}'


def get_bytey_ansi_parts() -> list:
    BYTEY_1 = '_     /)---(\\   '
    BYTEY_2 = '\\\\   (/ . . \\)  '
    BYTEY_3 = ' \\\\__)-\\(*)/    '
    BYTEY_4 = ' \\_       (_    '
    BYTEY_5 = ' (___/-(____)   '
    temp_list = [BYTEY_1, BYTEY_2, BYTEY_3, BYTEY_4, BYTEY_5]
    ansi_bytey = [f'{ANSI.WHITE_BOLD}{line}{ANSI.RESET}' for line in temp_list]
    return ansi_bytey


if __name__ == '__main__':
    main()
