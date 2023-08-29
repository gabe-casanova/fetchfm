# Fetch.fm

Fetch.fm is a python program with two uses:
    1. running `python api_handler.py fetch` will allow users to export their Last.fm data to a text file
    2. running `python fetchfm.py` will allow uers to analyze their Last.fm music listening data via the Fetch.fm UI

In order to successfully run Fetch.fm, please follow the following steps:
    1. When logged into Last.fm, ensure that the checkbox "Hide recent listening information" is unchecked (<https://www.last.fm/settings/privacy>)
    2. Create an API key (<https://www.last.fm/api/authentication>)
    3. Update line 11 in `api_handler.py` with your API key
    4. Update line 12 in `api_handler.py` with your Last.fm username