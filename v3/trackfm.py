from ansi import ANSI
from catalog import Catalog
from api_handler import get_path, fetch_scrobbled_data

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


def main():
    ''' Begins the text-based UI for the Trackfm program '''
    welcome_msg()
    if username == '':
        # default to the current user
        read_in_current_user()
        if username != '':
            # only proceed if we were able to locate the current user
            create_database()
    else:
        # begin the process of fetching user's scrobbled data
        fetch_scrobbled_data(username)


def welcome_msg():
    global username
    ansi_logo = f'{ANSI.BRIGHT_CYAN_BOLD}{LOGO}{ANSI.RESET}'
    print(f'\n{ansi_logo}\n')
    print('Enter your Last.fm username [or press `enter` to default to the '
          f'current user]: {ANSI.YELLOW}', end='')
    username = input()
    print(ANSI.RESET, end='')


def read_in_current_user():
    try:
        curr_user_path = get_path('user_info', 'current_user.txt')
        with open(curr_user_path, 'r') as f:
            global username
            username = f.read()
    except (FileNotFoundError, OSError):
        error_header = ' * ERROR: Default failed'
        bullet_1 = ('-> Please ensure you\'ve ran `python api_handler.py '
                    'fetch` before you attempt to run `python trackfm.py`')
        bullet_2 = ('-> Or, please enter your Last.fm username instead of '
                    'defaulting to the current user')
        print(f'\n{error_header}')
        print(f'     {bullet_1}')
        print(f'     {bullet_2}\n')


def create_database():
    global db
    file_path = get_path('scrobbled_data', f'{username}.txt')
    with open(file_path, 'r') as f:
        scrobbled_data = f.readlines()
        db = Catalog(username, scrobbled_data)


if __name__ == '__main__':
    main()
