from catalog import Catalog


USERNAME = 'gabriel844'
db = None  # initialize global catalog database variable


def main():
    ''' Begins the text-based UI for the Trackfm program '''
    read_in_scrobbled_data()


def read_in_scrobbled_data():
    global database
    file_name = f'scrobbled_data/{USERNAME}.txt'
    with open(file_name, "r") as f:
        scrobbled_data = f.readlines()
        db = Catalog(scrobbled_data)


if __name__ == '__main__':
    main()
