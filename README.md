# apollo-program

Apollo♯ is a java program that provides users with functionality to analyze their music listening patterns with data exported from Last.fm

Steps to correctly download your Last.fm data needed for this application to run:
   1. visit the website <last.fm>
        - log-in to your Last.fm account
        - click on your profile picture in the top right corner of the webpage
        - click "Settings"
        - click "Privacy"
        - under the header "Recent listening", make sure that the feature "Hide recent listening information" is toggled off
   2. visit the website <https://mainstream.ghan.nl/export.html> and enter the following options
        - 'Last.fm username': enter in your Last.fm username
        - 'Last.fm username': enter in your Last.fm username
        - 'select type': choose "Scrobbles"
        - 'select format': choose "CSV"
        - 'Previous timestamp': leave blank
        - click "Go" and wait for your pages to be retrieved
    3. open the CSV file in Microsoft Excel
        - fully delete the columns titled: "uts", "artist_mbid", "album_mbid", and "track_mbid"
        - save your updated CSV
        - under 'File format', change this "Tab delimited Text (.txt)"
    4. move this new text file into the directory where Apollo♯ will be run
        
