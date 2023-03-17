import java.util.*;
import java.time.*;
import java.time.format.*;

/* A class to represent a Scrobble object (contains track and term info). */
public class Scrobble {
		
	private TrackInfo track;
	private LocalDateTime term;
	private LocalDate date;
	private LocalTime time;
	
	/*
	 * Build a new Scrobble object.
	 */
	public Scrobble(String input) {
		Scanner sc = new Scanner(input);

		// todo-- more than likely I will have to redo how I am parsing this info
		
		int day = Integer.parseInt(sc.next().substring(1, 3));
		int month = convertMonthToInt(sc.next());
		int year = Integer.parseInt(sc.next().substring(0, 4));
		
		String time = sc.next();
		int hour = Integer.parseInt(time.substring(0,2));
		int minute = Integer.parseInt(time.substring(3,5));
		
		term = LocalDateTime.of(year, month, day, hour, minute);
		date = LocalDate.of(year, month, day);
		this.time = LocalTime.of(hour, minute);
		
		sc.useDelimiter("\t");
		String artist = getNextToken(sc);
		String album = getNextToken(sc);
		String song = getNextToken(sc);
		
		track = new TrackInfo(artist, album, song);
		
		sc.close();
	}
	
	/* 
	 * Return the next token in the Scanner. Uses tab delimiting.
	 * Removes any single quote characters from the String.
	 */
	private String getNextToken(Scanner sc) {
		return sc.next().replace("\"", "");
	}
	
	/*
	 * Convert String representation of the month to its int equivalent.
	 * Jan = 1, ..., Dec = 12
	 */
	private int convertMonthToInt(String tgt) {
		final String[] MONTHS = new String[] {"", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"};
		for (int index = 1; index < MONTHS.length; index++) {
			if (tgt.equals(MONTHS[index])) {
				return index;
			}
		}
		throw new IllegalStateException("Unable to successfully convert " + tgt + " to its month int equivalent.");
	}
	
	/* Get the track for this Scrobble (artist, album, song). */
	public TrackInfo getTrack() {
		return track;
	}

	/* Get the term for this Scrobble (time and date). */
	public LocalDateTime getTerm() {
		return term;
	}

	/* Get the date for this Scrobble (month, day, year). */
	public LocalDate getDate() {
		return date;
	}

	/* Get the time for this Scrobble (hour and minute). */
	public LocalTime getTime() {
		return time;
	}
	
	/*
	 * Represent this Scrobble as a String.
	 */
	public String toString() {
		DateTimeFormatter myFormatter = DateTimeFormatter.ofPattern("d MMM uuuu, h:mm a");
		return String.format("%s\t%s", term.format(myFormatter), track);
	}
}