import java.util.regex.Matcher;
import java.util.regex.Pattern;

/* A class to store the artist, album, and song names for a Scrobble object. */
public class TrackInfo {
	
	private String artist;
	private String album;
	private String song;
	
	/*
	 * Create a new TrackInfo object.
	 */
	public TrackInfo(String artist, String album, String song) {
		this.artist = artist;
		this.album = album;
 		this.song = checkForNumMonthBug(song);
	}

	/*
	 * The export website needed to obtain Scrobble info from user's Last.Fm contains a bug
	 * in which song names like "7/11" or "10/10" get converted into "11-Jul" and "10-Oct".
	 * This method checks for this number-month bug error, and corrects it if present.
	 */
	private String checkForNumMonthBug(String song) {

		// todo-- this might not be an issue after implementing my own API handler???
	
		String regex = ".*\\d.*"; 					// regex to check if song contains any numbers
        Pattern pattern = Pattern.compile(regex); 	// compiles the regex
        Matcher matcher = pattern.matcher(song); 	// find match between pattern and song
        boolean containsNums = matcher.matches();	// returns true if the song contains any numbers

		if (!containsNums || !song.contains("-") || song.contains(" ")) {
			return song;
		}

		int indexOfHyphen = song.indexOf("-");
		String month = song.substring(indexOfHyphen + 1);
		if (month.length() > 3) {
			// special check in case this song does not contain any letters (i.e. "19-2000" by Gorillaz)
			return song;
		}
		int num1 = convertMonthToInt(month);
		int num2 = Integer.parseInt(song.substring(0, indexOfHyphen));

		return num1 + "/" + num2;
	}

	/*
	 * Convert String representation of the month to its int equivalent.
	 * Jan = 1, ..., Dec = 12
	 */
	private int convertMonthToInt(String tgt) {
		final String[] MONTHS = new String[] {"", "Jan", "Feb", "Mar", "Apr", "May", "Jun",  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"};
		for (int index = 1; index < MONTHS.length; index++) {
			if (tgt.equals(MONTHS[index])) {
				return index;
			}
		}
		throw new IllegalStateException("Unable to successfully convert " + tgt + " to its month int equivalent.");
	}

	/* Return the artist for this TrackInfo object. */
	public String getArtist() {
		return artist;
	}
	
	/* Return the album for this TrackInfo object. */
	public String getAlbum() {
		return album;
	}
	
	/* Return the song for this TrackInfo object. */
	public String getSong() {
		return song;
	}
	
	/*
	 * Return this TrackInfo represented as a String.
	 */
	public String toString() {
		final String FORMAT = "%s    %s    %s";
		return String.format(FORMAT, artist, album, song);
	}
}