from enum import Enum

class MainMenuChoices(Enum):
    USER_INFO = 1
    TIME_STATS = 2
    TRACK_STATS = 3
    PRINTING = 4
    QUIT = 5

    '''
        1. USER_INFO
    
        2. TIME_BASED_STATS
            > SONG_LENGTH
            > LISTENING_TIME

        3. TRACK_BASED_STATS
            > BY_DATE
                NUM_PLAYS_ON_DATE
                MOST_PLAYED_ON_DATE
            > OVERALL
                NUM_PLAYS
                MOST_PLAYED
                MOST_CONSECUTIVE
                MOST_STREAMED_DAY_FOR_TRACK

        4. PRINT_SCROBBLES
            > PRINT_SCROBBLES_ON_DATE
            > PRINT_FULL_CHROLOGICAL
            > PRINT_ALPHABETIZED_SUMMARIES

        5. QUIT_PROGRAM
    '''
