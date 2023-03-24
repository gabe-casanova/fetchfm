/*
 * A class to store a Scrobble object's artist, album, and song info
 */
public class TrackInfo {
	
	private String artist;
	private String album;
	private String song;
	
	/*
	 * Creates a new TrackInfo object
	 */
	public TrackInfo(String artist, String album, String song) {
		this.artist = artist;
		this.album = album;
 		this.song = song;
	}

	// Returns the artist name
	public String getArtist() {
		return artist;
	}
	
	// Returns the album name
	public String getAlbum() {
		return album;
	}
	
	// Returns the song name
	public String getSong() {
		return song;
	}
	
	// Returns this TrackInfo represented as a string
	public String toString() {
		final String FORMAT = "%s    %s    %s";
		return String.format(FORMAT, artist, album, song);
	}
}