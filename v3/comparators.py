from scrobble import Scrobble


class Comparators:
    '''
    Defines logic for how to alphabetically sort Scrobbles (i.e., by either
    their song, artist, or album names)
    '''

    class AlphaSongComparator:
        @staticmethod
        def compare(s1:Scrobble, s2:Scrobble) -> int:
            song1 = s1.get_track().get_song().lower()
            song2 = s2.get_track().get_song().lower()
            return (song1 > song2) - (song1 < song2)

    class AlphaArtistComparator:
        @staticmethod
        def compare(s1:Scrobble, s2:Scrobble) -> int:
            artist1 = s1.get_track().get_artist().lower()
            artist2 = s2.get_track().get_artist().lower()
            return (artist1 > artist2) - (artist1 < artist2)

    class AlphaAlbumComparator:
        @staticmethod
        def compare(s1:Scrobble, s2:Scrobble) -> int:
            album1 = s1.get_track().get_album().lower()
            album2 = s2.get_track().get_album().lower()
            return (album1 > album2) - (album1 < album2)
        