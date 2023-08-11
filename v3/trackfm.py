from ansi import ANSI
from catalog import Catalog
from api_handler import get_path, fetch_scrobbled_data, is_valid_user

# Credit: https://fsymbols.com/text-art/
LOGO = """
████████╗██████╗░░█████╗░░█████╗░██╗░░██╗░░░███████╗███╗░░░███╗
╚══██╔══╝██╔══██╗██╔══██╗██╔══██╗██║░██╔╝░░░██╔════╝████╗░████║
░░░██║░░░██████╔╝███████║██║░░╚═╝█████═╝░░░░█████╗░░██╔████╔██║
░░░██║░░░██╔══██╗██╔══██║██║░░██╗██╔═██╗░░░░██╔══╝░░██║╚██╔╝██║
░░░██║░░░██║░░██║██║░░██║╚█████╔╝██║░╚██╗██╗██║░░░░░██║░╚═╝░██║
░░░╚═╝░░░╚═╝░░╚═╝╚═╝░░╚═╝░╚════╝░╚═╝░░╚═╝╚═╝╚═╝░░░░░╚═╝░░░░░╚═╝
"""

db = None  # global catalog
username = ''


# =========== [1] User Interface: ===========================================

def main():
    ''' Begins the text-based UI for the Trackfm program '''
    welcome_msg()  # sets global username variable
    if username == '':
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
    create_database()


# =========== [2] Miscellaneous: ============================================

def welcome_msg():
    global username
    ansi_logo = f'{ANSI.BRIGHT_CYAN_BOLD}{LOGO}{ANSI.RESET}'
    print(f'\n{ansi_logo}\n')
    print('Enter your Last.fm username [or press `enter` to default to the '
          f'current user]: {ANSI.YELLOW}', end='')
    username = input()
    print(ANSI.RESET, end='')


def get_default_user() -> tuple[bool, str]:
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
    global db
    file_path = get_path('scrobbled_data', f'{username}.txt')
    with open(file_path, 'r') as f:
        scrobbled_data = f.readlines()
        db = Catalog(username, scrobbled_data)


if __name__ == '__main__':
    main()
