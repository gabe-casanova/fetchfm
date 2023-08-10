from catalog import Catalog
from api_handler import get_path
from datetime import date

db = None  # initialize global catalog database variable
username = open('v3/user_info/current_user.txt').read()


def main():
    ''' Begins the text-based UI for the Trackfm program '''
    read_in_scrobbled_data()
    testing()


def testing():
    pass


def read_in_scrobbled_data():
    global db
    file_path = get_path('scrobbled_data', f'{username}.txt')
    with open(file_path, 'r') as f:
        scrobbled_data = f.readlines()
        db = Catalog(scrobbled_data)


if __name__ == '__main__':
    main()
