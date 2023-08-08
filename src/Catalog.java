import java.util.*;
import java.time.*;
import java.time.format.*;

/*
 * A class to represent a collection/catalog of Scrobbles
 */
public class Catalog implements Comparators {
	
	private ArrayList<Scrobble> stdCatalog;

	private int totalNumScrobbles;
	private int totalNumDistinctDays;
	private int numMostListenedTo;		// i.e., most-listened-to-song-#-of-all-time
	private int numMostFreqOnDate;		// i.e., most-listened-to-song-#-on-this-date
	private int numLongestConsecutive;	// i.e., longest-conseq-listened-to-song-#

	private LinkedHashMap<LocalDateTime, Scrobble> fullChronoCatalog;
	private LinkedHashMap<LocalDate, ArrayList<Scrobble>> dateChronoCatalog;
	private LinkedHashMap<String, ArrayList<Scrobble>> alphaSongCatalog;
	private LinkedHashMap<String, ArrayList<Scrobble>> alphaArtistCatalog;
	private LinkedHashMap<String, ArrayList<Scrobble>> alphaAlbumCatalog;

	/*
	 * Create a new Catalog of Scrobble objects.
	 */
	public Catalog(Scanner sc) {
		stdCatalog = new ArrayList<Scrobble>();
		while (sc.hasNextLine()) {
			stdCatalog.add(new Scrobble(sc.nextLine()));
		}
		totalNumScrobbles = stdCatalog.size();  // todo-- this can also be obtained from user-info txt file?

		// generate various catalogs needed for future use
		makeFullChronoCatalog();
		makeDateChronoCatalog();
		makeSongAlphaCatalog();
		makeArtistAlphaCatalog();
		makeAlbumAlphaCatalog();
	}

	// Return the number of times the user has listened to a specific song overall
	public int getNumTimesListenedToSong(String song) {
		return getNumTimesListenedTo(song, alphaSongCatalog);
	}

	// Return the number of times the user has listened to a specific artist overall
	public int getNumTimesListenedToArtist(String artist) {
		return getNumTimesListenedTo(artist, alphaArtistCatalog);
	}

	// Return the number of times the user has listened to a specific album overall
	public int getNumTimesListenedToAlbum(String album) {
		return getNumTimesListenedTo(album, alphaAlbumCatalog);
	}

	/*
	 * Helper method used to reduce redundancy
	 */
	private int getNumTimesListenedTo(String input, LinkedHashMap<String, ArrayList<Scrobble>> cat) {
		/*
		 * FEATURE: equalsIgnoreCase()
		 *   - make it so that a user can type in "Don't Blame Me" or "don't blame me" and both would return the correct int answer
		 *   - make it so that Daylight by Taylor Swift and Daylight by Harry Styles don't both get added to the int answer
		 *        - maybe check that the artist name for every Scrobble in arr is all the same, if multiple then alert the user
		 *   - if I type in "Midnigh", ask the user: "Did you mean 'Midnights' or 'Midnights (3am Edition)'" aka autofill?
		 */
		ArrayList<Scrobble> arr = cat.get(input);
		return arr != null ? arr.size() : itemNotPresent(input);
	}

	/*
	 * Prints message that the user provided item was not found within the user's catalog
	 * This message is meant to serve as a reminder for the user to check for typos and capitalization errors
	 */
	private int itemNotPresent(String item) {
		System.out.println(ANSI.RESET);
		System.out.println(" * " + ANSI.BRIGHT_CYAN_BOLD + item + ANSI.RESET + " was not found within your Last.fm data.");
		return 0;
	}

	/*
	 * Returns a list of song(s) which the user listened to the most for a given date
	 */
	public ArrayList<String> findMostFreqSongAtDate(int month, int day, int year) throws InterruptedException {
		HashMap<String, int[]> map = new HashMap<>(); // intermediate storage container
	 	ArrayList<Scrobble> arr = getScrobblesAtDate(month, day, year);
		// iterate over arr so that we can generate frequencies for each song present
		for (int i = 0; i < arr.size(); i++) {
			String song = arr.get(i).getTrack().getSong();
			if (!map.containsKey(song)) {
				map.put(song, new int[1]);
			}
			map.get(song)[0]++;
		}
		return putIntoListMostFreq(map);
	}

	/*
	 * Returns a list of artist(s) which the user listened to the most for a given date
	 */
	public ArrayList<String> findMostFreqArtistAtDate(int month, int day, int year) throws InterruptedException {
		HashMap<String, int[]> map = new HashMap<>(); // intermediate storage container
	 	ArrayList<Scrobble> arr = getScrobblesAtDate(month, day, year);
		// iterate over arr so that we can generate frequencies for each artist present
		for (int i = 0; i < arr.size(); i++) {
			String artist = arr.get(i).getTrack().getArtist();
			if (!map.containsKey(artist)) {
				map.put(artist, new int[1]);
			}
			map.get(artist)[0]++;
		}
		return putIntoListMostFreq(map);
	}

	/*
	 * Returns a list of album(s) which the user listened to the most for a given date
	 */
	public ArrayList<String> findMostFreqAlbumAtDate(int month, int day, int year) throws InterruptedException {
		HashMap<String, int[]> map = new HashMap<>(); // intermediate storage container
	 	ArrayList<Scrobble> arr = getScrobblesAtDate(month, day, year);
		// iterate over arr so that we can generate frequencies for each album present
		for (int i = 0; i < arr.size(); i++) {
			String album = arr.get(i).getTrack().getAlbum();
			if (!map.containsKey(album)) {
				map.put(album, new int[1]);
			}
			map.get(album)[0]++;
		}
		return putIntoListMostFreq(map);
	}

	/*
	 * Helper method used to identify and return the highest frequency item(s) to the user
	 */
	private ArrayList<String> putIntoListMostFreq(HashMap<String, int[]> map) {
		ArrayList<String> result = new ArrayList<>();
		int maxSoFar = 0;
		// iterate over map to find the most recurring item(s)
		for (HashMap.Entry<String, int[]> entry : map.entrySet()) {
			String item = entry.getKey();
			int[] freq = entry.getValue();
			int curr = freq[0];
			if (curr > maxSoFar) {
				// curr is a new higher freq
				maxSoFar = curr;
				result = new ArrayList<>(); // reset
				result.add(item);
			} else if (curr == maxSoFar) {
				// curr has the same freq as maxSoFar, we want to add this item to our list
				result.add(item);
			}
		}
		numMostFreqOnDate = map.get(result.get(0))[0]; // store the max freq
		return result;
	}

	/*
	 * Returns a list of all Scrobbles listed for a specific date (M/D/Y)
	 * Pre-condition: date must be within range of valid Scrobble dates
	 */
	public ArrayList<Scrobble> getScrobblesAtDate(int month, int day, int year) throws InterruptedException {
		LocalDate startRange = stdCatalog.get(stdCatalog.size() - 1).getDate();
		LocalDate endRange = stdCatalog.get(0).getDate();

		if (!isValidDate(month, day, year)) {
			String invalidDate = month + "/" + day + "/" + year;
			System.out.println(" * Sorry, but " + ANSI.BRIGHT_CYAN_BOLD + invalidDate + ANSI.RESET + " is not a valid year!");
			return new ArrayList<>();
		}

		LocalDate requestedDate = LocalDate.of(year, month, day);

		// check that precondition is met
		if (!isWithinBounds(startRange, endRange, requestedDate)) {
			// if we get here, the requested date was not within range
			invalidDateErrorMessage(startRange, endRange, requestedDate);
			return new ArrayList<>();
		}

		return dateChronoCatalog.get(requestedDate);
	}

	/*
	 * Helper method to verify that the user inputted data is in fact a valid date
	 */
	private boolean isValidDate(int month, int day, int year) {
		if (month < 1 || day < 1 || year < 0 || month > 12 || day > 31) {
			// base case to check for obviously incorrect input
			return false;
		}

		if (isLeapYear(year)) {
			int[] daysInMonth = new int[] {31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};

			int maxDayInThisMonth = daysInMonth[month - 1];
			if (day <= maxDayInThisMonth) {
				return true;
			} else {
				return false;
			}

		} else {
			int[] daysInMonth = new int[] {31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};

			int maxDayInThisMonth = daysInMonth[month - 1];
			if (day <= maxDayInThisMonth) {
				return true;
			} else {
				return false;
			}
		}
	}

	/*
	 * Helper method to check if the given year is a leap year
	 */
	private boolean isLeapYear(int year) {
		if (year % 4 == 0) {
			// the year is divisible by 4
			if (year % 100 == 0) {
				// the year is a century
				if (year % 400 == 0) {
					return true;
				} else {
					return false;
				}
			} else {
				// the year is not a century
				return true;
			}
		} else {
			// the year is not divisible by 4
			return false;
		}
	}

	/* Helper method used to check precondition for getScrobblesAtDate() */
	private boolean isWithinBounds(LocalDate startRange, LocalDate endRange, LocalDate requestedDate) {
		boolean isAfterInclusive = requestedDate.isAfter(startRange) || requestedDate.isEqual(startRange);
		boolean isBeforeInclusive = requestedDate.isBefore(endRange) || requestedDate.isEqual(endRange);
		return isAfterInclusive && isBeforeInclusive;
	}

	/* Prints out to the console an error message that the requested date was not within range. */
	private void invalidDateErrorMessage(LocalDate startRange, LocalDate endRange, LocalDate requestedDate) throws InterruptedException {
		DateTimeFormatter myFormat = DateTimeFormatter.ofPattern("M/d/uuuu");
		System.out.print(" * Sorry, but " + ANSI.BRIGHT_CYAN_BOLD + requestedDate.format(myFormat) + ANSI.RESET + " is not within the range of your scrobbled data: ");
		System.out.println(ANSI.BRIGHT_CYAN + startRange.format(myFormat) + ANSI.RESET + " - " + ANSI.BRIGHT_CYAN + endRange.format(myFormat) + ANSI.RESET + ".");
	}







	





	/*
	 * Returns a list of song names, consisting of those which have the longest amount of consecutive listens.
	 */
	public ArrayList<String> findLongestConsecutiveSong() {
		ArrayList<String> result = new ArrayList<>();

		// variables used to keep track of our current longest consecutively listened to song
		int longestLengthSoFar = 0;
		String consecSong = "";

		// variables used to keep track of info needed when replacing the existing longestLengthSoFar and
		// consecSong variables (i.e. when a new, longer consecutively listened to song has been discovered)
		int secondLength = 0;
		String secondSong = "";

		// Iterate through the entire standard catalog (versus chronological order, but that's okay)
		for (int i = 0; i < stdCatalog.size(); i++) {
			String curr = stdCatalog.get(i).getTrack().getSong();
			if (i == 0) {
				// base case, only happens at the start of the iteration
				longestLengthSoFar = 1; // initialize
				consecSong = curr; 		// initialize
				result.add(consecSong);
			} else if (isConsecutiveSong(i, longestLengthSoFar, consecSong)) {
				// we know stdCatalog.get(i) is consecutive, incremement longestLengthSoFar++
				longestLengthSoFar++;
				if (longestLengthSoFar > secondLength) {
					// we only go in here when we've found a compeletely new, larger consecutive streak
					secondLength = 0; 	// reset
					secondSong = ""; 	// reset
					/*
					 * FEATURE: what if before we discard the original array, we save it somewhere?
					 * 			this way we will be able to see a list of most consecutively listened to songs
					 * 				- i.e. most consecutive (cellophane 56), second most consecutive, (don't blame me 49), ...
					 */
					result = new ArrayList<>(); // clear out the existing array
					result.add(consecSong);
				}
			} else if (isConsecutiveSong(i, secondLength, secondSong)) {
				// if we get here we know that stdCatalog.get(i) is not part of the consecutive streak.
				// we also know that curr is contributing to the "second" variables' consecutive streak.
				secondLength++;
				if (secondLength == longestLengthSoFar) {
					// we only go in here when our secondSong now has the same number of consecutive streaks as longestLengthSoFar
					consecSong = secondSong;
					result.add(secondSong);
				}
			} else {
				// if we get here, we need to initialize our "second" variables with their new values
				secondLength = 1;	// initialize
				secondSong = curr;	// initialize
			}
		}
		numLongestConsecutive = longestLengthSoFar;
		return result;
	}

	/*
	 * Returns a list of artist names, consisting of those which have the longest amount of consecutive listens.
	 */
	public ArrayList<String> findLongestConsecutiveArtist() {
		ArrayList<String> result = new ArrayList<>();

		// variables used to keep track of our current longest consecutively listened to artist
		int longestLengthSoFar = 0;
		String consecArtist = "";

		// variables used to keep track of info needed when replacing the existing longestLengthSoFar and
		// consecArtist variables (i.e. when a new, longer consecutively listened to artist has been discovered)
		int secondLength = 0;
		String secondArtist = "";

		// Iterate through the entire standard catalog (versus chronological order, but that's okay)
		for (int i = 0; i < stdCatalog.size(); i++) {
			String curr = stdCatalog.get(i).getTrack().getArtist();
			if (i == 0) {
				// base case, only happens at the start of the iteration
				longestLengthSoFar = 1; // initialize
				consecArtist = curr; 	// initialize
				result.add(consecArtist);
			} else if (isConsecutiveArtist(i, longestLengthSoFar, consecArtist)) {
				// we know stdCatalog.get(i) is consecutive, incremement longestLengthSoFar++
				longestLengthSoFar++;
				if (longestLengthSoFar > secondLength) {
					// we only go in here when we've found a compeletely new, larger consecutive streak
					secondLength = 0; 	// reset
					secondArtist = ""; 	// reset
					/*
					 * FEATURE: what if before we discard the original array, we save it somewhere?
					 * 			this way we will be able to see a list of most consecutively listened to artists
					 * 				- i.e. most consecutive (Taylor Swift 10,106), second most consecutive, (Billie Eilish 2,328), ...
					 */
					result = new ArrayList<>(); // clear out the existing array
					result.add(consecArtist);
				}
			} else if (isConsecutiveArtist(i, secondLength, secondArtist)) {
				// if we get here we know that stdCatalog.get(i) is not part of the consecutive streak.
				// we also know that curr is contributing to the "second" variables' consecutive streak.
				secondLength++;
				if (secondLength == longestLengthSoFar) {
					// we only go in here when our secondArtist now has the same number of consecutive streaks as longestLengthSoFar
					consecArtist = secondArtist;
					result.add(secondArtist);
				}
			} else {
				// if we get here, we need to initialize our "second" variables with their new values
				secondLength = 1;		// initialize
				secondArtist = curr;	// initialize
			}
		}
		numLongestConsecutive = longestLengthSoFar;
		return result;
	}

	/*
	 * Returns a list of album names, consisting of those which have the longest amount of consecutive listens.
	 */
	public ArrayList<String> findLongestConsecutiveAlbum() {
		ArrayList<String> result = new ArrayList<>();

		// variables used to keep track of our current longest consecutively listened to album
		int longestLengthSoFar = 0;
		String consecAlbum = "";

		// variables used to keep track of info needed when replacing the existing longestLengthSoFar and
		// consecAlbum variables (i.e. when a new, longer consecutively listened to album has been discovered)
		int secondLength = 0;
		String secondAlbum = "";

		// Iterate through the entire standard catalog (versus chronological order, but that's okay)
		for (int i = 0; i < stdCatalog.size(); i++) {
			String curr = stdCatalog.get(i).getTrack().getAlbum();
			if (i == 0) {
				// base case, only happens at the start of the iteration
				longestLengthSoFar = 1; // initialize
				consecAlbum = curr; 	// initialize
				result.add(consecAlbum);
			} else if (isConsecutiveAlbum(i, longestLengthSoFar, consecAlbum)) {
				// we know stdCatalog.get(i) is consecutive, incremement longestLengthSoFar++
				longestLengthSoFar++;
				if (longestLengthSoFar > secondLength) {
					// we only go in here when we've found a compeletely new, larger consecutive streak
					secondLength = 0; 	// reset
					secondAlbum = ""; 	// reset
					/*
					 * FEATURE: what if before we discard the original array, we save it somewhere?
					 * 			this way we will be able to see a list of most consecutively listened to albums
					 * 				- i.e. most consecutive (reputation 2,405), second most consecutive, (folklore 2,328), ...
					 */
					result = new ArrayList<>(); // clear out the existing array
					result.add(consecAlbum);
				}
			} else if (isConsecutiveAlbum(i, secondLength, secondAlbum)) {
				// if we get here we know that stdCatalog.get(i) is not part of the consecutive streak.
				// we also know that curr is contributing to the "second" variables' consecutive streak.
				secondLength++;
				if (secondLength == longestLengthSoFar) {
					// we only go in here when our secondAlbum now has the same number of consecutive streaks as longestLengthSoFar
					consecAlbum = secondAlbum;
					result.add(secondAlbum);
				}
			} else {
				// if we get here, we need to initialize our "second" variables with their new values
				secondLength = 1;		// initialize
				secondAlbum = curr;	// initialize
			}
		}
		numLongestConsecutive = longestLengthSoFar;
		return result;
	}

	/*
	 * REFACTOR:
	 * 		Can I reuse isConsecutive() for both song, artist, and album?
	 * 		To have less redundant code?
	 */

	/* Helper method used in findLongestConsecutiveSong() */
	private boolean isConsecutiveSong(int i, int length, String song) {
		if (!song.equals(stdCatalog.get(i).getTrack().getSong())) {
			// optimization check
			return false;
		}
		// iterate over the current length of consecutive song names
		for (int offset = 1; offset <= length; offset++) {
			String song1 = stdCatalog.get(i).getTrack().getSong();
			String song2 = stdCatalog.get(i - offset).getTrack().getSong();
			if (!song1.equals(song2)) {
				return false;
			}
		}
		return true;
	}	

	/* Helper method used in findLongestConsecutiveArtist() */
	private boolean isConsecutiveArtist(int i, int length, String artist) {
		if (!artist.equals(stdCatalog.get(i).getTrack().getArtist())) {
			// optimization check
			return false;
		}
		// iterate over the current length of consecutive artist names
		for (int offset = 1; offset <= length; offset++) {
			String artist1 = stdCatalog.get(i).getTrack().getArtist();
			String artist2 = stdCatalog.get(i - offset).getTrack().getArtist();
			if (!artist1.equals(artist2)) {
				return false;
			}
		}
		return true;
	}

	/* Helper method used in findLongestConsecutiveAlbum() */
	private boolean isConsecutiveAlbum(int i, int length, String album) {
		if (!album.equals(stdCatalog.get(i).getTrack().getAlbum())) {
			// optimization check
			return false;
		}
		// iterate over the current length of consecutive album names
		for (int offset = 1; offset <= length; offset++) {
			String album1 = stdCatalog.get(i).getTrack().getAlbum();
			String album2 = stdCatalog.get(i - offset).getTrack().getAlbum();
			if (!album1.equals(album2)) {
				return false;
			}
		}
		return true;
	}

	/*
	 * Returns an ArrayList of Strings which represents the most listened to song(s).
	 */
	public ArrayList<String> mostListenedToSong() {
		ArrayList<String> result = new ArrayList<>();
		int maxSoFar = 0;
		for (String key : alphaSongCatalog.keySet()) {
			ArrayList<Scrobble> arr = alphaSongCatalog.get(key);
			int numListens = arr.size();
			if (numListens > maxSoFar) {
				// new max number
				maxSoFar = numListens;
				result = new ArrayList<>();
				result.add(arr.get(0).getTrack().getSong());
			} else if (numListens == maxSoFar) {
				// at least 2 songs have the exact same max number of listens, we want to record both
				result.add(arr.get(0).getTrack().getSong());
			}
		}
		numMostListenedTo = maxSoFar;
		return result;
	}

	/*
	 * Returns an ArrayList of Strings which represents the most listened to artist(s).
	 */
	public ArrayList<String> mostListenedToArtist() {
		ArrayList<String> result = new ArrayList<>();
		int maxSoFar = 0;
		for (String key : alphaArtistCatalog.keySet()) {
			ArrayList<Scrobble> arr = alphaArtistCatalog.get(key);
			int numListens = arr.size();
			if (numListens > maxSoFar) {
				// new max number
				maxSoFar = numListens;
				result = new ArrayList<>();
				result.add(arr.get(0).getTrack().getArtist());
			} else if (numListens == maxSoFar) {
				// at least 2 songs have the exact same max number of listens, we want to record both
				result.add(arr.get(0).getTrack().getArtist());
			}
		}
		numMostListenedTo = maxSoFar;
		return result;
	}

	/*
	 * Returns an ArrayList of Strings which represents the most listened to album(s).
	 */
	public ArrayList<String> mostListenedToAlbum() {
		ArrayList<String> result = new ArrayList<>();
		int maxSoFar = 0;
		for (String key : alphaAlbumCatalog.keySet()) {
			ArrayList<Scrobble> arr = alphaAlbumCatalog.get(key);
			int numListens = arr.size();
			if (numListens > maxSoFar) {
				// new max number
				maxSoFar = numListens;
				result = new ArrayList<>();
				result.add(arr.get(0).getTrack().getAlbum());
			} else if (numListens == maxSoFar) {
				// at least 2 songs have the exact same max number of listens, we want to record both
				result.add(arr.get(0).getTrack().getAlbum());
			}
		}
		numMostListenedTo = maxSoFar;
		return result;
	}

	/* Generate the average number of Scrobbles listened to per day. */
	public int getAvgNumScrobblesPerDay() {
		return Math.round((float) totalNumScrobbles / totalNumDistinctDays); // rounds to nearest whole number
	}

	/* Get the total number of Scrobbles listed for this catalog. */
	public int getTotalNumScrobbles() {
		return totalNumScrobbles;
	}

	/* Get the total number of distinct days within user's data. */
	public int getTotalNumDistinctDays() {
		return totalNumDistinctDays;
	}

	/* Returns the number of listens recorded for the most listened to S/A/A. */
	public int getMostListenedToOfAllTime() {
		return numMostListenedTo;
	}

	/* Returns the number of listens recorded for the longest consecutively listened to S/A/A. */
	public int getNumOfLongestConsecutive() {
		return numLongestConsecutive;
	}

	/*	Returns the number of listens recorded for the most Scrobbled S/A/A for the user's provided date. */
	public int getNumMostFreqOnDate() {
		return numMostFreqOnDate;
	}

	/*
	 * Generate a 1-to-1 chronologically-based catalog.
	 * Internal data structure used is a LinkedHashMap (maintains insertion order)
	 * Key is a LocalDateTime object (date and time of the Scrobble). Value is a Scrobble.
	 * Oldest Scrobbles come at the beginning of the map, newer Scrobbles come near the end.
	 */
	private void makeFullChronoCatalog() {
		fullChronoCatalog = new LinkedHashMap<>(totalNumScrobbles);
		for (int index = totalNumScrobbles - 1; index >= 0; index--) {
			Scrobble s = stdCatalog.get(index);
			fullChronoCatalog.put(s.getTerm(), s);
		}
	}

	/*
	 * Generate a grouped chronologically-based catalog.
	 * Key is a LocalDate object.
	 * Maintains insertion order.
	 */
	private void makeDateChronoCatalog() {
		dateChronoCatalog = new LinkedHashMap<>();
		int numDistinctDays = 0;
		for (int index = totalNumScrobbles - 1; index >= 0; index--) {
			Scrobble s = stdCatalog.get(index);
			if (!dateChronoCatalog.containsKey(s.getDate())) {
				numDistinctDays++;
				dateChronoCatalog.put(s.getDate(), new ArrayList<>());
			}
			dateChronoCatalog.get(s.getDate()).add(s);
		}
		totalNumDistinctDays = numDistinctDays;
	}
	
	/*
	 * Generate a new catalog alphabetically ordered by song name.
	 */
	private void makeSongAlphaCatalog() {
		@SuppressWarnings("unchecked")
		ArrayList<Scrobble> tempCatalog = (ArrayList<Scrobble>) stdCatalog.clone();
		Collections.sort(tempCatalog, new AlphaSongComparator());
		
		alphaSongCatalog = new LinkedHashMap<>(totalNumScrobbles);
		for (int index = 0; index < tempCatalog.size(); index++) {
			Scrobble currentScrob = tempCatalog.get(index);
			String currentSong = currentScrob.getTrack().getSong();
			if (!alphaSongCatalog.containsKey(currentSong)) {
				alphaSongCatalog.put(currentSong, new ArrayList<>());
				alphaSongCatalog.get(currentSong).add(currentScrob);
			} else {
				alphaSongCatalog.get(currentSong).add(currentScrob);
			}
		}
	}

	/*
	 * Generate a new catalog alphabetically ordered by artist name.
	 */
	private void makeArtistAlphaCatalog() {
		@SuppressWarnings("unchecked")
		ArrayList<Scrobble> tempCatalog = (ArrayList<Scrobble>) stdCatalog.clone();
		Collections.sort(tempCatalog, new AlphaArtistComparator());
		
		alphaArtistCatalog = new LinkedHashMap<>(totalNumScrobbles);
		for (int index = 0; index < tempCatalog.size(); index++) {
			Scrobble currentScrob = tempCatalog.get(index);
			String currentArtist = currentScrob.getTrack().getArtist();
			if (!alphaArtistCatalog.containsKey(currentArtist)) {
				alphaArtistCatalog.put(currentArtist, new ArrayList<>());
			}
			alphaArtistCatalog.get(currentArtist).add(currentScrob);
		}
	}

	/*
	 * Generate a new catalog alphabetically ordered by album name.
	 */
	private void makeAlbumAlphaCatalog() {
		@SuppressWarnings("unchecked")
		ArrayList<Scrobble> tempCatalog = (ArrayList<Scrobble>) stdCatalog.clone();
		Collections.sort(tempCatalog, new AlphaAlbumComparator());
		
		alphaAlbumCatalog = new LinkedHashMap<>(totalNumScrobbles);
		for (int index = 0; index < tempCatalog.size(); index++) {
			Scrobble currentScrob = tempCatalog.get(index);
			String currentAlbum = currentScrob.getTrack().getAlbum();
			if (!alphaAlbumCatalog.containsKey(currentAlbum)) {
				alphaAlbumCatalog.put(currentAlbum, new ArrayList<>());
			}
			alphaAlbumCatalog.get(currentAlbum).add(currentScrob);
		}
	}	

	/* Print the Scrobbles listened to on a specific date (M/D/Y) */
	public void printScrobblesAtDate(int month, int day, int year) throws InterruptedException {
		ArrayList<Scrobble> arr = getScrobblesAtDate(month, day, year);
		if (arr == null) {
			System.out.println("You did not listen to any music on that day!");
		} else {
			for (int i = 0; i < arr.size(); i++) {
				System.out.println(arr.get(i));
				Thread.sleep(50);
			}
		}
	}
	
	/* Print LocalDateTime Catalog in chronological order. */
	public void printFullChronoCatalog() {
		System.out.println();
		for (LocalDateTime key : fullChronoCatalog.keySet()) {
			System.out.println(fullChronoCatalog.get(key));
		}
		System.out.println();
	}
	
	/* Print catalog info in alphabetical order based on song name. */
	public void printSongCatalog() {

		mostListenedToSong(); // throwaway to set the value of most listened to song num to its global variable (numMostListenedTo)
		int maxLength = numMostListenedTo;
		String maxLengthWithCommas = String.format("%,d", maxLength);
		maxLength = maxLengthWithCommas.length(); // take into account potential commas

		System.out.println();
		for (String key : alphaSongCatalog.keySet()) {
			ArrayList<Scrobble> arr = alphaSongCatalog.get(key);

			String numListensWithCommas = String.format("%,d", arr.size());
			String numFormat = "%" + maxLength + "s"; // generate the necessary first parameter for String.format()

			System.out.print(ANSI.BRIGHT_WHITE_BOLD + String.format(numFormat, numListensWithCommas)); // right-justified
			System.out.println(ANSI.BRIGHT_CYAN + "  " + key + ANSI.RESET + " [" + arr.get(0).getTrack().getArtist() + "]");
		}
		System.out.println();
	}

	/* Print catalog info in alphabetical order based on artist name. */
	public void printArtistCatalog() {

		mostListenedToArtist(); // throwaway to set the value of most listened to artist num to its global variable (numMostListenedTo)
		int maxLength = numMostListenedTo;
		String maxLengthWithCommas = String.format("%,d", maxLength);
		maxLength = maxLengthWithCommas.length(); // take into account potential commas

		System.out.println();
		for (String key : alphaArtistCatalog.keySet()) {
			ArrayList<Scrobble> arr = alphaArtistCatalog.get(key);

			String numListensWithCommas = String.format("%,d", arr.size());
			String numFormat = "%" + maxLength + "s"; // generate the necessary first parameter for String.format()

			System.out.print(ANSI.BRIGHT_WHITE_BOLD + String.format(numFormat, numListensWithCommas)); // right-justified
			System.out.println(ANSI.RESET + "  " + key);
		}
		System.out.println();
	}

	/* Print catalog info in alphabetical order based on album name. */
	public void printAlbumCatalog() {
		
		mostListenedToAlbum(); // throwaway to set the value of most listened to album num to its global variable (numMostListenedTo)
		int maxLength = numMostListenedTo;
		String maxLengthWithCommas = String.format("%,d", maxLength);
		maxLength = maxLengthWithCommas.length(); // take into account potential commas

		System.out.println();
		for (String key : alphaAlbumCatalog.keySet()) {
			ArrayList<Scrobble> arr = alphaAlbumCatalog.get(key);

			String numListensWithCommas = String.format("%,d", arr.size());
			String numFormat = "%" + maxLength + "s"; // generate the necessary first parameter for String.format()

			System.out.print(ANSI.BRIGHT_WHITE_BOLD + String.format(numFormat, numListensWithCommas)); // right-justified
			System.out.println(ANSI.BRIGHT_CYAN + "  " + key + ANSI.RESET + " [" + arr.get(0).getTrack().getArtist() + "]");
		}
		System.out.println();
	}
}