import java.util.Comparator;

/*
 * Comparators used in Catalog.java to sort songs, artists, and albums by alphabetical order.
 */
public interface Comparators {

    /* Nested class for ordering Scrobbles alphabetically based on song name. */
	static class AlphaSongComparator implements Comparator<Scrobble> {
		public int compare(Scrobble s1, Scrobble s2) {
			String song1 = s1.getTrack().getSong();
			String song2 = s2.getTrack().getSong();
			return song1.compareToIgnoreCase(song2);
		}
	}

	/* Nested class for ordering Scrobbles alphabetically based on artist name. */
	static class AlphaArtistComparator implements Comparator<Scrobble> {
		public int compare(Scrobble s1, Scrobble s2) {
			String artist1 = s1.getTrack().getArtist();
			String artist2 = s2.getTrack().getArtist();
			return artist1.compareToIgnoreCase(artist2);
		}
	}

	/* Nested class for ordering Scrobbles alphabetically based on album name. */
	static class AlphaAlbumComparator implements Comparator<Scrobble> {
		public int compare(Scrobble s1, Scrobble s2) {
			String album1 = s1.getTrack().getAlbum();
			String album2 = s2.getTrack().getAlbum();
			return album1.compareToIgnoreCase(album2);
		}
	}
}
