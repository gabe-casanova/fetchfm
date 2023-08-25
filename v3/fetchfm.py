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
^^^^^^╚═╝░░░░░╚══════╝░░░╚═╝░░░░╚════╝░╚═╝░░╚═╝╚═╝╚═╝░░░░░╚═╝░░░░░╚═╝^^^^^^^^^^^^^^^^^
"""

USERNAME = ''
CATALOG = None
prev_user = ''
has_previous_user = False


# =========== [1] Main Program: =============================================

def main():
    display_logo()
    check_for_prev_user()  # sets the `has_previous_user` global variable
    username = get_username()
    if username.lower() == 'q':
        bytey_goodbye_msg()
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
        ANSI_USERNAME = ANSI.CYAN_BOLD + username + ANSI.RESET
        print(f'\n * Sorry, but {ANSI_USERNAME} is not a valid Last.fm username')
        username = get_username()
        if username.lower() == 'q' or (username == '' and has_previous_user):
            break
    # If we get here, the user has either entered a valid username, wishes to
    # us the previous user, or would like to quit out of the program
    if username.lower() == 'q':
        bytey_goodbye_msg()
    elif username == '' and has_previous_user:
        USERNAME = prev_user
        run_user_interface()
    else:
        # verify that the user wishes to proceed with this username (ie. typos)
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
            USERNAME = username
            fetch_scrobbled_data(username)
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
        MainMenuChoices.USER_INFO: print_fun_facts,
        MainMenuChoices.TIME_STATS: NotImplemented,
        MainMenuChoices.TRACK_STATS: NotImplemented,
        MainMenuChoices.PRINTING: NotImplemented
    }
    create_database()
    bytey_welcome_msg()
    while True:
        display_main_menu()
        my_choice = get_main_menu_choice()
        if my_choice == MainMenuChoices.QUIT:
            break
        MENU_FUNCTIONS[my_choice]()  # call corresponding function (switch)
    # if we get here, the user has terminated the program
    bytey_goodbye_msg()


def print_fun_facts():
    '''
    Prints Bytey's fun facts (i.e. user info) to the terminal
    '''
    total_num_days = CATALOG.get_total_num_distinct_days()
    most_streamed_days, num_streams = CATALOG.most_streamed_day_overall()
    # read in info from the user's user_info.txt file
    result = read_user_info_txt_file()
    if result is None:
        # TODO
        print('  * Hmm... Fetch seems to have gotten lost. Try again soon!')
        return
    realname, playcount, track_count, album_count, artist_count = result
    user = realname if realname is not None else USERNAME
    # format the output with ANSI and commas
    ansi_user = f'{ANSI.CYAN_BOLD}{user}{ANSI.RESET}'
    ansi_playcount = ansi_with_commas(playcount)
    ansi_track_count = ansi_with_commas(track_count)
    ansi_album_count = ansi_with_commas(album_count)
    ansi_artist_count = ansi_with_commas(artist_count)
    # calculate daily average and format w ANSI
    daily_avg = round(playcount / total_num_days) if total_num_days != 0 else 0
    ansi_daily_average = ansi_with_commas(daily_avg)
    ansi_num_days = ansi_with_commas(total_num_days)
    ''' Get Bytey the ASCII dog broken up into its individual lines '''
    BYTEY = get_ansi_bytey(ANSI.BRIGHT_CYAN_BOLD, True)
    # print the message to the screen
    print('____________________________')
    print(f'\n   {BYTEY[0]}')
    print(f'   {BYTEY[1]}Hey there, {ansi_user}! Here are some fun music stats I '
          'dug up about you--')
    print(f'   {BYTEY[2]} ⇒ you\'ve listened to {ansi_playcount} tracks over the '
          f'past {ansi_num_days} days, averaging {ansi_daily_average} tracks '
          'listened a day')
    print(f'   {BYTEY[3]} ⇒ you\'ve enjoyed {ansi_track_count} unique songs, '
          f'explored {ansi_album_count} different albums, and discovered '
          f'{ansi_artist_count} diverse artists')
    if num_streams == 0:
        # edge case
        print(f'   {BYTEY[4]}\n')
    else:
        # if we get here, we know most_streamed_days list is NOT empty
        formatted_date = most_streamed_days[0].strftime('%B %d, %Y')
        ansi_date = f'{ANSI.CYAN_BOLD}{formatted_date}{ANSI.RESET}'
        ansi_num_streams = ansi_with_commas(num_streams)
        print(f'   {BYTEY[4]} ⇒ on {ansi_date} you listened to a lot of music, with '
              f'{ansi_num_streams} total songs played (..the most for any day!)\n')
    print('‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾')
    

# =========== [2] Utility: ==================================================

def display_main_menu():
    '''
    Prints the Main Menu choices to the terminal for the user to read
    '''
    print(f'\n {ANSI.BRIGHT_CYAN_BOLD}Main Menu:{ANSI.RESET}')
    print_choice(1, 'Fetch\'s fun facts for you ♪♪♪')
    print_choice(2, 'explore your timing data')
    print_choice(3, 'explore your track-based stats')
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
        - `str`: realname
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
        result = tuple(user_info_dict.get(key) for key in desired_keys)
        return result
    else:
        return None


def bytey_welcome_msg():
    BYTEY = get_ansi_bytey(ANSI.BRIGHT_CYAN_BOLD, False)
    msg = f"""
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
"""
    print_text_animated(f'\n{msg}', 0.25)


def bytey_goodbye_msg():
    BYTEY = get_ansi_bytey(ANSI.BRIGHT_CYAN_BOLD, False)
    msg = f""" 
  /‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾\\
 |     Thanks for letting me tag along with you! See you again soon :)    |
  \\____________________________________   _______________________________/
                                       | /
                         {BYTEY[0]} |/
                         {BYTEY[1]}
                         {BYTEY[2]}
                         {BYTEY[3]}
                         {BYTEY[4]}
"""
    print_text_animated(f'{msg}', 0.25)
    print()
    print()


def print_text_animated(text, end_delay_in_secs):
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
    print(f'{hours}h {minutes}m {seconds}s spent listening')


def seconds_to_days(total_seconds):
    NUM_SECONDS_IN_DAY = 86400
    num_days = total_seconds / NUM_SECONDS_IN_DAY
    return num_days


if __name__ == '__main__':
    main()
