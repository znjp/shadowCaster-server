
# SHADOWCASTER GLOBAL SETTINGS

def init():
    global DEBUG
    global NOGPIO
    global DBFILE

    global COLOR
    
    global STUNNED
    global RELEASING
    global IDLE
    global STUNTIME

    global LEDS

    DEBUG = True
    NOGPIO = False
    DBFILE = "./scdb.sql"

    COLOR = "blue"

    # Global variables used for stunning/releasing
    STUNNED = False
    RELEASING = False
    IDLE = True
    STUNTIME = 0

def init_db_settings(config):

    global SHADOWCASTER
    global TOTALPUZZLES
    global ENERGY
    global STUNDURATION
    global RELEASEDURATION
    global SECRET

    SHADOWCASTER = config["scnum"]  # SC Number
    TOTALPUZZLES = config["total"]  # Total Number of Puzzles
    ENERGY = config["energy"]  # Energy level
    STUNDURATION = config["stun"]  # Stun duration in seconds
    RELEASEDURATION = config["release"]  # Release duration In seconds
    SECRET = config["secret"] #Game secret


    
    
    
