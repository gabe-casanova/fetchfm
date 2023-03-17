import java.io.*;
import java.time.*;
import java.util.*;

/* A program to analyze music listening trends and patterns. */
public class Apollo {

    public static Scanner keyboard;
    public static Catalog database;
        
    public static void main(String[] args) throws InterruptedException {
        // todo-- update the logic here to reflect API request/ api_handler.py
        // https://stackoverflow.com/questions/27267391/running-a-py-file-from-java
        keyboard = new Scanner(System.in);
        String fileName = welcome();
        Scanner fileScanner = getFileScanner(fileName);
        database = new Catalog(fileScanner);
        fileScanner.close();
        runOptions();
    }

    /*
     * Prints a welcome message to the console.
     * Returns the name of the text file to analyze for the user.
     */
    private static String welcome() {
        System.out.println();
        System.out.println("Welcome to " + ANSI.BRIGHT_CYAN_BOLD + "Apollo♯" + ANSI.RESET + ", a tool to analyze your Last.fm music listening habits!");
        System.out.println();
        return askForFileName();
    }

    /*
     * Helper method that asks the user for the name of the text file they wish to analyze.
     */
    private static String askForFileName() {
        System.out.print("What text file would you like to analyze? " + ANSI.BRIGHT_CYAN);
        String fileName = keyboard.nextLine();
        System.out.print(ANSI.RESET);
        return fileName;
    }

    /*
     * Main UI
     */
    private static void runOptions() throws InterruptedException {
        MenuChoices[] menuChoices = MenuChoices.values();
        MenuChoices myChoice;
        do {
            showMenu();
            myChoice = menuChoices[readIn(keyboard)]; // readIn method obtains a valid MenuChoice from the user
            switch (myChoice) {
                case GET_SCROBBLES_FROM_DATE: runChoice1(); break;
                case GET_NUM_TIMES_LISTENED_TO: runChoice2(); break;
                case MOST_LISTENED_FROM_DATE: runChoice3(); break;
                case MOST_LISTENED_OF_ALL_TIME: runChoice4(); break;
                case LONGEST_CONSECUTIVELY: runChoice5(); break;
                case AVERAGE_NUM_SCROBS_PER_DAY: runChoice6(); break;
                case GET_TOTAL_NUM_SCROBS: runChoice7(); break;
                case GET_TOTAL_NUM_DAYS: runChoice8(); break;
                case PRINT_ALPHABETIZED_SUMMARY: runChoice9(); break;
                case PRINT_ALL_CHRONOLOGICALLY: runChoice10(); break;
                case QUIT: break;
            }
        } while (myChoice != MenuChoices.QUIT);
        keyboard.close();
        System.out.println();
        System.out.println("Thanks for using " + ANSI.BRIGHT_CYAN_BOLD + "Apollo♯" + ANSI.RESET + ", we hope to see you back soon!");
        System.out.println();
    }

    /*
     * Display the menu options to the console for the user.
     */
    private static void showMenu() {
        System.out.println();
        System.out.printf("%sAvailable Options:%s\n", ANSI.YELLOW_BOLD, ANSI.RESET);
        printMenu(" 1", "to get the scrobbles you've listened to on a specific date");
        printMenu(" 2", "to get the total number of times you've listened to a track or artist");
        printMenu(" 3", "to get your most listened to track or artist for a specific date");
        printMenu(" 4", "to get your most listened to track or artist of all time");
        printMenu(" 5", "to get your longest consecutively listened to track or artist");
        printMenu(" 6", "to calculate the average number of scrobbles you log per day");
        printMenu(" 7", "to calculate the overall number of scrobbles you've listened to");
        printMenu(" 8", "to calculate the total number of days you've scrobbled on");
        printMenu(" 9", "to print an alphabetized summary of all your scrobbles");
        printMenu("10", "to print all your scrobbles in chronological order");
        printMenu("11", "to quit the program");
        System.out.println();
    }

    /*
     * Print the provided menu option to the screen.
     */
    private static void printMenu(String key, String msg) {
        System.out.printf(" Enter %s %s %s %s\n", ANSI.YELLOW, key, ANSI.RESET, msg);
    }

	/*
     * CHOICE #1: get user's Scrobbles for a specific date
     */
    private static void runChoice1() throws InterruptedException {
        System.out.println();
        int[] date = getDate();
        System.out.println();
        database.printScrobblesAtDate(date[0], date[1], date[2]);
    }

    /*
     * CHOICE #2: get the overall number of times user has listened to a song, artist, or album
     */
    private static void runChoice2() throws InterruptedException {
        // Prompt user for request type (song, artist, or album)
        String request = askForInput();
        String req2 = request.toLowerCase().replaceAll(" ", "");

        // Handle request type and prompt the user with appropriate query
        if (req2.equals("song")) {
            System.out.print("What song would you like to search for? " + ANSI.BRIGHT_CYAN);
            String songName = keyboard.nextLine();
            int numListens = database.getNumTimesListenedToSong(songName);
            printOutChoice2Output(numListens, songName, "You've listened to the song ");

        } else if (req2.equals("artist")) {
            System.out.print("What artist would you like to search for? " + ANSI.BRIGHT_CYAN);
            String artistName = keyboard.nextLine();
            int numListens = database.getNumTimesListenedToArtist(artistName);
            printOutChoice2Output(numListens, artistName, "You've listened to the artist ");

        } else if (req2.equals("album")) {
            System.out.print("What album would you like to search for? " + ANSI.BRIGHT_CYAN);
            String albumName = keyboard.nextLine();
            int numListens = database.getNumTimesListenedToAlbum(albumName);
            printOutChoice2Output(numListens, albumName, "You've listened to the album ");

        } else {
            System.out.println(" * Sorry, but " + ANSI.BRIGHT_CYAN_BOLD + request + ANSI.RESET + " is not valid input!");
            runChoice2();
        }
    }

    /*
     * Helper method to help format the output for choice #2. Helps reduce redundancy.
     */
    private static void printOutChoice2Output(int numListens, String trackInfo, String startOutputWith) {
        if (numListens != 0) {
            System.out.println();
			String numListensWithCommas = String.format("%,d", numListens);
            System.out.print(ANSI.RESET + startOutputWith + trackInfo + " " + ANSI.BRIGHT_CYAN_BOLD + numListensWithCommas + ANSI.RESET);
            if (numListens == 1) {
                System.out.println(" time!");
            } else if (numListens > 1) {
                System.out.println(" times!");
            }
        }
    }

    /*
     * CHOICE #3: for a specific date, get the user's most listened to song, artist, or album
     */
    private static void runChoice3() throws InterruptedException {
        // Prompt user for request type (song, artist, or album)
        String request = askForInput();
        String req2 = request.toLowerCase().replaceAll(" ", "");

        // Handle potential request formatting issue and prompt the user with appropriate query
        if (req2.equals("song")) {
            int[] date = getDate();
            ArrayList<String> result = database.findMostFreqSongAtDate(date[0], date[1], date[2]);
            int numListens = database.getNumMostFreqOnDate();
            printOutChoice3Output(req2, result, numListens);

        } else if (req2.equals("artist")) {
            int[] date = getDate();
            ArrayList<String> result = database.findMostFreqArtistAtDate(date[0], date[1], date[2]);
            int numListens = database.getNumMostFreqOnDate();
            printOutChoice3Output(req2, result, numListens);

        } else if (req2.equals("album")) {
            int[] date = getDate();
            ArrayList<String> result = database.findMostFreqAlbumAtDate(date[0], date[1], date[2]);
            int numListens = database.getNumMostFreqOnDate();
            printOutChoice3Output(req2, result, numListens);

        } else {
            System.out.println(" * Sorry, but " + ANSI.BRIGHT_CYAN_BOLD + request + ANSI.RESET + " is not valid input!");
            runChoice3();
        }
    }

    /*
     * Helper method to help format the output for choice #3. Helps reduce redundancy.
     */
    private static void printOutChoice3Output(String request, ArrayList<String> result, int numListens) {
        System.out.println();
        if (numListens == 0) {
            // edge case check
            System.out.println("You did not listen to any music on that day!");
        } else if (result.size() == 1) {
            // our results array only contained 1 element, so we don't need to print out a list
            if (request.equals("artist")) {
                // for artists we want to use "them" instead of "it"
                System.out.print("Your most listened to artist was " + ANSI.BRIGHT_CYAN_BOLD + result.get(0) + ANSI.RESET + ". ");
                printNumListensInfo(numListens, "them");
            } else {
                // song or album name
                System.out.print("Your most listened to " + request + " was " + ANSI.BRIGHT_CYAN_BOLD + result.get(0) + ANSI.RESET + ". ");
                printNumListensInfo(numListens, "it");
            }
        } else {
            // our results array contained more than 1 element, so we need to print out the full list
            System.out.print("Your most listened to " + request + " included: ");
            printArrResults(result);
			System.out.println(". ");
            String input = "these " + request + "s each"; // not a pronoun, but we still can use the helper method (so let's do it)
            printNumListensInfo(numListens, input);
        }
    }

    /*
     * CHOICE #4: get user's most listened to S/A/A of all time
     */
    private static void runChoice4() {
        String request = askForInput();
        String req2 = request.toLowerCase().replaceAll(" ", "");
        // Handle request type and prompt the user with appropriate query
        if (req2.equals("song")) {
            printOutChoice4Output(req2, database.mostListenedToSong(), database.getMostListenedToOfAllTime());
        } else if (req2.equals("artist")) {
			printOutChoice4Output(req2, database.mostListenedToArtist(), database.getMostListenedToOfAllTime());
        } else if (req2.equals("album")) {
			printOutChoice4Output(req2, database.mostListenedToAlbum(), database.getMostListenedToOfAllTime());
        } else {
            System.out.println(" * Sorry, but " + ANSI.BRIGHT_CYAN_BOLD + request + ANSI.RESET + " is not valid input!");
            runChoice4();
        }
    }

	/*
	 * Helper method to help format the output for choice #4. Helps reduce redundancy.
	 */
    private static void printOutChoice4Output(String request, ArrayList<String> result, int numListens) {
		System.out.print("Your most listened to " + request);
		if (result.size() == 1) {
			System.out.print(" is " + ANSI.BRIGHT_CYAN_BOLD + result.get(0) + ANSI.RESET);
		} else {
			// since we have more than 1 item, we need to generate a list to print out
			System.out.print(" includes: ");
			printArrResults(result);
		}
		String numListensWithCommas = String.format("%,d", numListens);
		System.out.println("; for a total of " + ANSI.BRIGHT_CYAN_BOLD + numListensWithCommas + ANSI.RESET + " streams!");
	}

    /*
	 * CHOICE #5: see user's longest consecutively listened to S/A/A
	 */
	private static void runChoice5() {
        // Prompt user for request type (song, artist, or album)
        String request = askForInput();
        String req2 = request.toLowerCase().replaceAll(" ", "");
        // Handle request type and prompt the user with appropriate query
        if (req2.equals("song")) {
            printOutChoice5Output(req2, database.findLongestConsecutiveSong(), database.getNumOfLongestConsecutive());
        } else if (req2.equals("artist")) {
            printOutChoice5Output(req2, database.findLongestConsecutiveArtist(), database.getNumOfLongestConsecutive());
        } else if (req2.equals("album")) {
            printOutChoice5Output(req2, database.findLongestConsecutiveAlbum(), database.getNumOfLongestConsecutive());
        } else {
            System.out.println(" * Sorry, but " + ANSI.BRIGHT_CYAN_BOLD + request + ANSI.RESET + " is not valid input!");
            runChoice5();
        }
	}

    /*
     * Helper method to help format the output for choice #5. Helps reduce redundancy.
     */
    private static void printOutChoice5Output(String request, ArrayList<String> result, int numListens) {
        if (result.size() == 1) {
            // our results array only contained 1 element, so we don't need to print out a list
            if (request.equals("artist")) {
                // for artists we want to use "them" instead of "it"
                System.out.print("Your longest consecutively listened to artist was " + ANSI.BRIGHT_CYAN_BOLD + result.get(0) + ANSI.RESET + ". ");
                printNumListensInfo(numListens, "them");
            } else {
                // song or album name
                System.out.print("Your longest consecutively listened to " + request + " was " + ANSI.BRIGHT_CYAN_BOLD + result.get(0) + ANSI.RESET + ". ");
                printNumListensInfo(numListens, "it");
            }
        } else {
            // our results array contained more than 1 element, so we need to print out the full list
            System.out.print("Your longest consecutively listened to " + request + " included: ");
            printArrResults(result);
			System.out.println(". ");
            String input = "these " + request + "s each"; // not a pronoun, but we still can use the helper method (so let's do it)
            printNumListensInfo(numListens, input);
        }
    }

	/*
	 * CHOICE #6: get user's calculated average number of Scrobbles tracked per day
	 */
	private static void runChoice6() {
		String averageWithCommas = String.format("%,d", database.getAvgNumScrobblesPerDay());
		System.out.println();
		System.out.println("On average, you track " + ANSI.BRIGHT_CYAN_BOLD + averageWithCommas + ANSI.RESET + " scrobbles per day!");
	}

	/*
	 * CHOICE #7: get the overall number of Scrobbles user has listened to
	 */
	private static void runChoice7() {
		String totalNumWithCommas = String.format("%,d", database.getTotalNumScrobbles());
		System.out.println();
		System.out.println("You've listened to a total of " + ANSI.BRIGHT_CYAN_BOLD + totalNumWithCommas + ANSI.RESET + " scrobbles!");
	}

	/*
	 * CHOICE #8: get the total number of days the user has Scrobbled
	 */
	private static void runChoice8() {
		String totalDaysWithCommas = String.format("%,d", database.getTotalNumDistinctDays());
		System.out.println();
		System.out.println("You've scrobbled for a total of " + ANSI.BRIGHT_CYAN_BOLD + totalDaysWithCommas + ANSI.RESET + " days!");
	}

    /*
	 * CHOICE #9: print all of user's Scrobbles in alphabetical order
	 */
	private static void runChoice9() {
        // Prompt user for request type (song, artist, or album) to alphabetize
        System.out.println();
        System.out.println("Would you like to alphabetize your summary by song, artist, or album name?");
        System.out.print("Type " + ANSI.BRIGHT_CYAN_BOLD + "song " + ANSI.RESET + "to sort by song name, " +  ANSI.BRIGHT_CYAN_BOLD
            + "artist " + ANSI.RESET + "for artist name, or " + ANSI.BRIGHT_CYAN_BOLD + "album " + ANSI.RESET + "for album name: " + ANSI.BRIGHT_CYAN);
        String request = keyboard.nextLine();
        System.out.println(ANSI.RESET);
        // Handle request type and prompt the user with appropriate query
        String req2 = request.toLowerCase().replaceAll(" ", "");
        if (req2.equals("song")) {
            database.printSongCatalog();
        } else if (req2.equals("artist")) {
            database.printArtistCatalog();
        } else if (req2.equals("album")) {
            database.printAlbumCatalog();
        } else {
            System.out.println(" * Sorry, but " + ANSI.BRIGHT_CYAN_BOLD + request + ANSI.RESET + " is not valid input!");
            runChoice9();
        }
	}

	/*
	 * CHOICE #10: print all of user's Scrobbles in chronological order
	 */
    private static void runChoice10() {
		database.printFullChronoCatalog();
	}

    /*
     * Ask the user for a valid date. If the user provides an invalid date, repeatedly ask the user for new input.
     */
    private static int[] getDate() throws InterruptedException {
        int[] date = askForDateInput();
        while (date == null) {
            date = askForDateInput();
        }
        return date;
    }

	/*
     * Helper method which prompts user to enter a valid date.
     * Necessary to help reduce redundancy in code.
     */
    private static int[] askForDateInput() throws InterruptedException {
        LocalDate today = LocalDate.now();
        String exampleDate = today.getMonthValue() + "/" + today.getDayOfMonth() + "/" + today.getYear();
        System.out.print("Please enter your date (" + ANSI.BRIGHT_CYAN_BOLD + "i.e., " + exampleDate + ANSI.RESET + ") now: " + ANSI.BRIGHT_CYAN);
        String dateInput = keyboard.nextLine();

        // try-with-resource is needed for proper resource cleanup
        try (Scanner parser = new Scanner(dateInput).useDelimiter("/")) {
            System.out.print(ANSI.RESET);
            int[] result;
            try {
                int month = parser.nextInt();
                int day = parser.nextInt();
                int year = parser.nextInt();
                result = new int[] {month, day, year};
            } catch (InputMismatchException e) {
                System.out.println();
                System.out.println(" * Sorry, but " + ANSI.BRIGHT_CYAN_BOLD + dateInput + ANSI.RESET + " is not valid input!");
                System.out.println();
                result = null;
            } catch (NoSuchElementException e) {
                System.out.println();
                System.out.println(" * Sorry, but " + ANSI.BRIGHT_CYAN_BOLD + dateInput + ANSI.RESET + " is not valid input!");
                System.out.println();
                result = null;
            }
            return result;
        }
    }

    /*
     * Helper method which prompts user to enter a valid S/A/A request.
     * Necessary to help reduce redundancy in code.
     */
    private static String askForInput() {
        System.out.println();
        System.out.print("Type " + ANSI.BRIGHT_CYAN_BOLD + "song " + ANSI.RESET + "to search for a song, " +  ANSI.BRIGHT_CYAN_BOLD
            + "artist " + ANSI.RESET + "for an artist, or " + ANSI.BRIGHT_CYAN_BOLD + "album " + ANSI.RESET + "for an album: " + ANSI.BRIGHT_CYAN);
        String result = keyboard.nextLine();
        System.out.println(ANSI.RESET);
        return result;
    }

    /*
     * Helper method to help format the output for choice #3. Helps reduce redundancy.
     */
    private static void printNumListensInfo(int numListens, String pronoun) {
        if (numListens == 1) {
            System.out.println("You listened to " + pronoun + " " + ANSI.BRIGHT_CYAN_BOLD + "1" + ANSI.RESET + " time!");
        } else {
			String numListensWithCommas = String.format("%,d", numListens);
            System.out.println("You listened to " + pronoun + " " + ANSI.BRIGHT_CYAN_BOLD + numListensWithCommas + ANSI.RESET + " times!");
        }
    }

    /*
     * Prints out the contents of an array. Uses special ANSI colors.
     */
    private static void printArrResults(ArrayList<String> arr) {
        if (arr.size() == 2) {
            // fence post check
            System.out.print(ANSI.BRIGHT_CYAN + arr.get(0) + ANSI.RESET + " and " + ANSI.BRIGHT_CYAN + arr.get(1) + ANSI.RESET);
        } else {
            for (int i = 0; i < arr.size(); i++) {
                if (i == (arr.size() - 1)) {
                    // fence post check: we are at the last element of the list
                    System.out.print("and " + ANSI.BRIGHT_CYAN + arr.get(i) + ANSI.RESET);
                } else {
                    System.out.print(ANSI.BRIGHT_CYAN + arr.get(i) + ANSI.RESET + ", ");
                }
            }
        }
    }

    /* 
     * Read in the user's valid choice from the keyboard.
     */
    private static int readIn(Scanner keyboard) {
        final int MAX_CHOICE = MenuChoices.QUIT.ordinal() + 1; // +1 due to zero-based indexing of enums, but 1-based indexing of MenuChoices
        int choice = getInt(keyboard);
        keyboard.nextLine(); // safety check to clear out the current keyboard line
        while (choice < 1  || choice > MAX_CHOICE) {
            System.out.println();
            System.out.println(" * Sorry, but " + ANSI.BRIGHT_CYAN_BOLD + choice + ANSI.RESET + " is not a valid choice!");
            System.out.println();
            choice = getInt(keyboard);
            keyboard.nextLine();  // safety check to clear out the current keyboard line
        }
        return choice - 1; // zero-based indexing
    }

    /*
     * Ensure that the user entered an int into the keyboard.
     */
    private static int getInt(Scanner sc) {
        System.out.print(ANSI.WHITE_UNDERLINED + "Enter Choice:" + ANSI.RESET + " " + ANSI.YELLOW);
        while (!sc.hasNextInt()) {
            String invalidResult = sc.next();
            System.out.println(ANSI.RESET);
            System.out.println(" * Sorry, but " + ANSI.BRIGHT_CYAN_BOLD + invalidResult + ANSI.RESET + " is not a valid choice!");
            System.out.println();
            System.out.print(ANSI.WHITE_UNDERLINED + "Enter Choice:" + ANSI.RESET + " " + ANSI.YELLOW);
        }
        System.out.print(ANSI.RESET);
        return sc.nextInt();
    }

    /* 
     * Create a Scanner and return connected to a File with the given name.
     */
    private static Scanner getFileScanner(String fileName) {
        Scanner sc = null;
        try {
            sc = new Scanner(new File(fileName));
        } catch (FileNotFoundException e) {
            System.out.println();
            String currentDir = System.getProperty("user.dir");
            System.out.println(" * Please try again! We couldn't find the file " + ANSI.BRIGHT_CYAN + fileName + ANSI.RESET 
                + " in the current folder: " + ANSI.BRIGHT_CYAN + currentDir + ANSI.RESET);
            System.out.println();
            sc = null;
        }
        if (sc == null) {
            fileName = askForFileName();
            sc = getFileScanner(fileName);
        }
        return sc;
    }

    /*
     * An enum type to represent the menu choices for the Apollo program.
     */
    private static enum MenuChoices {
        GET_SCROBBLES_FROM_DATE, GET_NUM_TIMES_LISTENED_TO, MOST_LISTENED_FROM_DATE, MOST_LISTENED_OF_ALL_TIME, LONGEST_CONSECUTIVELY, 
        AVERAGE_NUM_SCROBS_PER_DAY, GET_TOTAL_NUM_SCROBS, GET_TOTAL_NUM_DAYS, PRINT_ALPHABETIZED_SUMMARY, PRINT_ALL_CHRONOLOGICALLY, QUIT;
    }
}