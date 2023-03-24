import java.util.*;
import java.time.*;
import java.time.format.*;

/*
 * A class to represent a Scrobble object (contains track and term info)
 */
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
		
		int day = Integer.parseInt(sc.next());
		int month = convertMonthToInt(sc.next());
		int year = Integer.parseInt(sc.next().substring(0,4));

		String time = sc.next();

		int hour = Integer.parseInt(time.substring(0,2));
		int minute = Integer.parseInt(time.substring(3,5));
		
		term = LocalDateTime.of(year, month, day, hour, minute);
		date = LocalDate.of(year, month, day);
		this.time = LocalTime.of(hour, minute);
		
		sc.useDelimiter("\t");

		String artist = sc.next();
		String album = sc.next();
		String song = sc.next();

		track = new TrackInfo(artist, album, song);
		
		sc.close();
	}
	
	/*
	 * Convert string representation of the month to its int equivalent.
	 * Jan = 1, ..., Dec = 12
	 */
	private int convertMonthToInt(String tgt) {
		final String[] MONTHS = new String[] {"", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"};
		for (int index = 1; index < MONTHS.length; index++) {
			if (tgt.equals(MONTHS[index])) {
				return index;
			}
		}
		return -1;
	}
	
	// Get the track for this Scrobble (artist, album, song)
	public TrackInfo getTrack() {
		return track;
	}

	// Get the term for this Scrobble (time and date)
	public LocalDateTime getTerm() {
		return term;
	}

	// Get the date for this Scrobble (month, day, year)
	public LocalDate getDate() {
		return date;
	}

	// Get the time for this Scrobble (hour and minute)
	public LocalTime getTime() {
		return time;
	}
	
	/*
	 * Represent this Scrobble as a string.
	 */
	public String toString() {
		DateTimeFormatter myFormatter = DateTimeFormatter.ofPattern("d MMM uuuu, h:mm a");
		return String.format("%s\t%s", term.format(myFormatter), track);
	}
}