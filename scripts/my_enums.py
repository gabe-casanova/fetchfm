from enum import Enum


class MainMenuChoices(Enum):
    FUN_FACTS = 1
    TIMING_DATA = 2
    TRACK_STATS = 3
    SCROBBLES = 4


class QueryType(Enum):
    SONG = 1
    ARTIST = 2
    ALBUM = 3


    '''
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
    '''
