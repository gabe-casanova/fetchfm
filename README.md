# apollo-program

Apollo♯ is a java program that provides users with functionality to analyze their music listening patterns with data exported from Last.fm

Steps to correctly download your Last.fm data:
   1. log-in to your Last.gm account
        - click on your profile picture
        - click "Settings"
        - click "Privacy"
        - under the header "Recent listening", make sure that the feature "Hide recent listening information" is toggled off
   2. visit the website <https://mainstream.ghan.nl/export.html>
        - enter the following options:
            - 'Last.fm username': enter in your Last.fm username
            - 'select type': choose "Scrobbles"
            - 'select format': choose "CSV"
            - 'Previous timestamp': leave blank
        - click "Go" and wait for your pages to be retrieved
   3. open the CSV file in Microsoft Excel
        - fully delete the following columns titled:
            - "uts"
            - "artist_mbid"
            - "album_mbid"
            - "track_mbid"
        - save your updated CSV:
            - 'File format': change this to "Tab delimited Text (.txt)"
   4. save this text file to the directory where Apollo♯ will be run
        
