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


# =========== [1] Main Program/UI: ==========================================

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
    ''' Creates the global database object and begins the text-based UI '''
    CHOICE_FUNCTIONS = {
        MainMenuChoices.USER_DATA: print_user_data,
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
    print(f'Thanks for using {ANSI.BRIGHT_CYAN_BOLD}Track.fm{ANSI.RESET}!\n')


def print_user_data():
    '''
    Prints the following user info to the terminal:
        - MOST_STREAMED_DAY_OVERALL
        - AVERAGE_NUM_DAILY_SCROBBLES
        - TOTAL_NUM_SCROBBLES
        - TOTAL_NUM_DISTINCT_DAYS
    '''
    print('hi')


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
    print_menu_option('  ', 1, 'user data')
    print_menu_option('  ', 2, 'time-based stats')
    print_menu_option('  ', 3, 'track-based stats')
    print_menu_option('  ', 4, 'get scrobbles')
    print_menu_option('  ', 5, 'quit')
    print()


def print_menu_option(indent, key, msg):
    print(f'{indent}{ANSI.BRIGHT_BLUE}{key}{ANSI.RESET} ⇒ {msg}')


def get_main_menu_choice():
    '''
    Retrieves the user's Main Menu choice (as an int) from the terminal
    '''
    MENU_CHOICES = list(MainMenuChoices)
    ansi_enter = f' {ANSI.BRIGHT_BLUE_BOLD}Enter Choice:{ANSI.RESET} '
    while True:
        user_input = input(f'{ansi_enter}')
        if user_input.isdigit() and 1 <= int(user_input) <= len(MENU_CHOICES):
            print()
            break
        # if we get here, the user did not type in an int. display message
        ansi_input = f'{ANSI.BRIGHT_CYAN_BOLD}{user_input}{ANSI.RESET}'
        print(f'\n  * {ansi_input} isn\'t a valid choice\n')
    return MENU_CHOICES[int(user_input) - 1]


# =========== [3] Utility: ==================================================

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
