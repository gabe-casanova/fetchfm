from ansi import ANSI
from api_handler import is_api_error, get_path, lastfm_get, jprint

'''

get_path: use to create v3/duration/track_durations.txt



'''

# Functions to make Last.fm API calls to retrieve track duration info

API_KEY = open('v3/admin/api_key.txt').read()
USER_AGENT = open('v3/admin/user_agent.txt').read()
HEADER_FORMAT = 'json'
SUCCESS_STATUS_CODE = 200
RATE_LIMITING_TIME = 0.25

username = open('v3/user_info/current_user.txt').read()


def main():
    payload = {
        'method': 'track.getInfo',
        'track': 'Toxic',
        'artist': 'Britney Spears',
        'username': username,
        'autocorrect': True
    }
    response = lastfm_get(payload)
    if not is_api_error(response):
        jprint(response.json())


if __name__ == '__main__':
    main()
