# import sys
import web
import hashlib
import os
import random
import string
import time
import pickle
from web import form
import threading
import signal
import json

# This line causes this script to be somewhat unresponsive to ctrl-C
web.config.debug = False
DEBUG = True

# SHADOWCASTER GLOBAL SETTINGS

# IMPORTANT: This must be set to the PWD of the python script if run as an init service
# os.chdir("/home/pi/shadowcaster-server")

# Load the configuration file
with open('scconfig.json', 'r') as f:
    config = json.load(f)
# And set the initial values
SHADOWCASTER = config["SHADOWCASTER"]  # SC Number
TOTALPUZZLES = config["TOTALPUZZLES"]  # Total Number of Puzzles
ENERGY = config["ENERGY"]  # Energy level
STUNDURATION = config["STUNDURATION"]  # Stun duration in seconds
RELEASEDURATION = config["RELEASEDURATION"]  # Release duration In seconds
f.close()

COLOR = "blue"  # Initial color

# Global variables used for stunning
STUNNED = False
STUNTIME = 0  # Stun time remaining

# GPIO Settings
NOGPIO = True
# Pin outs for LEDs
RED = 11
GREEN = 13
BLUE = 15


try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(RED, GPIO.OUT)
    GPIO.setup(GREEN, GPIO.OUT)
    GPIO.setup(BLUE, GPIO.OUT)
    # Set the initial color
    GPIO.output(BLUE, True)
    NOGPIO = False
except:
    print time.strftime("%a, %d %b %Y %H:%M:%S",
                        time.localtime()) + " No GPIO. Going to DEBUG mode."
    NOGPIO = True


# Our "database"
db = {}
# db = web.database(dbn='postgres', usr='username', pw='password', db='dbname')
last_sync = 0

render = web.template.render('templates/')
urls = ('/', 'sc',
        '/sc', 'sc',  # puzzle page
        '/stun', 'stun',  # stun the shadowcaster
        '/unstun', 'unstun',  # unstun the shadowcaster
        '/stunstatus', 'stunstatus',  # Is the shadowcaster stunned?
        '/login',  'login',  # login
        '/logout', 'logout',  # logout
        '/energy', 'energy',  # current energy level
        '/release', 'release',  # win
        '/admin', 'admin',  # SC administration panel
        '/testRelease', 'testRelease',
        '/testStun', 'testStun',
        '/setPuzzleNum', 'setPuzzleNum',
        '/setStunTime', 'setStunTime',
        '/setReleaseTime', 'setReleaseTime',
        '/setEnergyLevel', 'setEnergyLevel')
app = web.application(urls, globals())

session = web.session.Session(app, web.session.DiskStore('sessions'))


def init_leds(t=5):
    while t:
        GPIO.output(RED, True)
        time.sleep(.25)
        GPIO.output(RED, False)
        time.sleep(.25)
        GPIO.output(GREEN, True)
        time.sleep(.25)
        GPIO.output(GREEN, False)
        time.sleep(.25)
        GPIO.output(BLUE, True)
        time.sleep(.25)
        GPIO.output(BLUE, False)
        time.sleep(.25)
        GPIO.output(RED, True)
        GPIO.output(GREEN, True)
        GPIO.output(BLUE, True)
        time.sleep(.25)
        GPIO.output(RED, False)
        GPIO.output(GREEN, False)
        GPIO.output(BLUE, False)
        time.sleep(.25)
        t -= 1
    GPIO.output(BLUE, True)
    GPIO.output(GREEN, False)
    GPIO.output(RED, False)


def releaseLights():
    global STUNNED
    global STUNTIME

    STUNNED = True
    STUNTIME = RELEASEDURATION
    threading.Thread(target=countdown).start()
    now = time.time()
    # Turn off the lights
    if not NOGPIO:
        GPIO.output(RED, False)
        GPIO.output(GREEN, False)
        GPIO.output(BLUE, False)
    while(time.time() < now + RELEASEDURATION and STUNNED):
        if DEBUG and NOGPIO:
            print "WIN!"
            time.sleep(.6)
        # Sparkle the lights
        else:
            GPIO.output(RED, True)
            time.sleep(.1)
            GPIO.output(RED, False)
            time.sleep(.1)
            GPIO.output(GREEN, True)
            time.sleep(.1)
            GPIO.output(GREEN, False)
            time.sleep(.1)
            GPIO.output(BLUE, True)
            time.sleep(.1)
            GPIO.output(BLUE, False)
            time.sleep(.1)
    # Set the original color
    if not NOGPIO:
        if COLOR == "red":
            GPIO.output(RED, True)
            GPIO.output(GREEN, False)
            GPIO.output(BLUE, False)
        if COLOR == "green":
            GPIO.output(GREEN, True)
            GPIO.output(RED, False)
            GPIO.output(BLUE, False)
        if COLOR == "blue":
            GPIO.output(BLUE, True)
            GPIO.output(GREEN, False)
            GPIO.output(RED, False)
    STUNNED = False


def countdown():
    global STUNTIME
    while STUNTIME:
        STUNTIME -= 1
        if DEBUG:
            print STUNTIME
        time.sleep(1)


def stunLights():
    global STUNNED
    global STUNTIME
    now = time.time()

    STUNNED = True
    STUNTIME = STUNDURATION
    threading.Thread(target=countdown).start()
    # Turn off the lights
    if not NOGPIO:
        GPIO.output(RED, False)
        GPIO.output(GREEN, False)
        GPIO.output(BLUE, False)
    # Flash the lights
    while(time.time() < now + STUNDURATION and STUNNED):
        if DEBUG and NOGPIO:
            print "STUN."
            time.sleep(.3)
        else:
            GPIO.output(RED, True)
            time.sleep(.25)
            GPIO.output(RED, False)
            time.sleep(.25)
            GPIO.output(RED, True)
            time.sleep(.25)
            GPIO.output(RED, False)
            time.sleep(.25)
    # Set the original color
    if not NOGPIO:
        if COLOR == "red":
            GPIO.output(RED, True)
            GPIO.output(GREEN, False)
            GPIO.output(BLUE, False)
        if COLOR == "green":
            GPIO.output(GREEN, True)
            GPIO.output(RED, False)
            GPIO.output(BLUE, False)
        if COLOR == "blue":
            GPIO.output(BLUE, True)
            GPIO.output(GREEN, False)
            GPIO.output(RED, False)
    STUNNED = False


class energy:
    def GET(self):
        global ENERGY
        return ENERGY


class release:
    global db

    def GET(self):
        global COLOR
        global ENERGY
        global STUNNED

        if not session.get('logged_in'):
            raise web.seeother('/login')

        user = session.get('user')
        # if db[user]["solved"]:
        if db[user]["solved"][str(config["SHADOWCASTER"])]:
            return render.login(None, STUNTIME, SHADOWCASTER, COLOR, "agent light already released")

        # Get solved key and validate
        user_data = web.input(e="", _unicode=False)
        if SHADOWCASTER != 8 and user_data.e != hashlib.sha1("sc" + str(SHADOWCASTER)).hexdigest():
            return render.login(None, STUNTIME, SHADOWCASTER, COLOR, "agent key invalid")

        # SHADOWCATER 8 requires a special key generated by the players
        if SHADOWCASTER == 8 and user_data.e != hashlib.sha1(user).hexdigest():
            return render.login(None, STUNTIME, SHADOWCASTER, COLOR, "agent key invalid")

        ENERGY = ENERGY - 10
        if ENERGY < 100 and ENERGY > 70:
            COLOR = "blue"
        if ENERGY < 70 and ENERGY > 30:
            COLOR = "green"
        if ENERGY < 30:
            COLOR = "red"
        if DEBUG:
            print "Color is now", COLOR

        threading.Thread(target=releaseLights).start()

        db[user]["solved"][str(config["SHADOWCASTER"])] = True
        sync_db()

        return render.release(SHADOWCASTER, db[user]["flag"][str(config["SHADOWCASTER"])])


# ADMIN FUNCTIONS
puzzlenumForm = form.Form(
    form.Dropdown('mydrop', zip(range(1, TOTALPUZZLES + 1), range(1,
                                                                  TOTALPUZZLES + 1)), style="font-family: Quantico; font-size: 30px;"),
    form.Button("Change",
                description="Change",
                style="font-family: Quantico; font-size: 30px;"))

testReleaseForm = form.Form(
    form.Button("Test LEDs",
                description="",
                style="font-family: Quantico; font-size: 30px; align: center;"))

testStunForm = form.Form(
    form.Button("Test LEDs",
                description="",
                style="font-family: Quantico; font-size: 30px; align: center;"))

setStunTimeForm = form.Form(
    form.Textbox("time",
                 form.notnull,
                 form.regexp('^-?\d+$', 'Not a number.'),
                 size="12",
                 maxlength="4",
                 width="12",
                 description=""),
    form.Button("Change",
                description="Change",
                style="font-family: Quantico; font-size: 30px;")
)
setReleaseTimeForm = form.Form(
    form.Textbox("time",
                 form.notnull,
                 form.regexp('^-?\d+$', 'Not a number.'),
                 size="12",
                 maxlength="4",
                 width="12",
                 description=""),
    form.Button("Change",
                description="Change",
                style="font-family: Quantico; font-size: 30px;")
)

setEnergyLevelForm = form.Form(
    form.Textbox("level",
                 form.notnull,
                 form.regexp('^-?\d+$', 'Not a number.'),
                 size="12",
                 maxlength="4",
                 width="12",
                 description=""),
    form.Button("Change",
                description="Change",
                style="font-family: Quantico; font-size: 30px;")
)


class testRelease:
    def GET(self):
        threading.Thread(target=releaseLights).start()
        raise web.seeother('/admin')

    def POST(self):
        threading.Thread(target=releaseLights).start()
        raise web.seeother('/admin')


class testStun:
    def GET(self):
        threading.Thread(target=stunLights).start()
        raise web.seeother('/admin')

    def POST(self):
        threading.Thread(target=stunLights).start()
        raise web.seeother('/admin')


class setPuzzleNum:
    def POST(self):
        global SHADOWCASTER

        form = puzzlenumForm()

        if not form.validates():
            raise web.seeother('/admin?status=Bad puzzle number')
            # return render.admin(SHADOWCASTER, puzzlenumForm, testLightsForm, setStunTimeForm, COLOR, "ERROR")
        SHADOWCASTER = int(form["mydrop"].value)
        config["SHADOWCASTER"] = SHADOWCASTER
        with open("scconfig.json", "w") as f:
            f.write(json.dumps(config))
            f.close()
        raise web.seeother('/admin?status=Success')


class setStunTime:
    def POST(self):
        global STUNDURATION
        form = setStunTimeForm()
        if not form.validates():
            raise web.seeother('/admin?status=Not a number')
            # return render.admin(SHADOWCASTER, puzzlenumForm, testLightsForm, setStunTimeForm, COLOR, "ERROR: Not a number.")
        STUNDURATION = int(form["time"].value)
        config["STUNDURATION"] = STUNDURATION
        with open("scconfig.json", "w") as f:
            f.write(json.dumps(config))
            f.close()
        raise web.seeother('/admin?status=Success')


class setReleaseTime:
    def POST(self):
        global RELEASEDURATION
        form = setReleaseTimeForm()
        if not form.validates():
            raise web.seeother('/admin?status=Not a number')
            # return render.admin(SHADOWCASTER, puzzlenumForm, testLightsForm, setStunTimeForm, COLOR, "ERROR: Not a number.")
        RELEASEDURATION = int(form["time"].value)
        config["RELEASEDURATION"] = RELEASEDURATION
        with open("scconfig.json", "w") as f:
            f.write(json.dumps(config))
            f.close()
        raise web.seeother('/admin?status=Success')


class setEnergyLevel:
    def POST(self):
        global ENERGY
        form = setEnergyLevelForm()
        if not form.validates():
            raise web.seeother('/admin?status=Not a number')
            # return render.admin(SHADOWCASTER, puzzlenumForm, testLightsForm, setStunTimeForm, COLOR, "ERROR: Not a number.")
        ENERGY = int(form["level"].value)
        config["ENERGY"] = ENERGY
        with open("scconfig.json", "w") as f:
            f.write(json.dumps(config))
            f.close()
        raise web.seeother('/admin?status=Success')


class admin:

    def GET(self):
        data = web.input(status="")
        status = str(data.status)
        puzzlenumForm["mydrop"].value = str(SHADOWCASTER)
        setStunTimeForm["time"].value = str(STUNDURATION)
        setReleaseTimeForm["time"].value = str(RELEASEDURATION)
        setEnergyLevelForm["level"].value = str(ENERGY)
        return render.admin(SHADOWCASTER, puzzlenumForm, setEnergyLevelForm, setStunTimeForm, setReleaseTimeForm, testReleaseForm, testStunForm, COLOR, status)


class login:
    global db

    loginForm = form.Form(
        form.Textbox("user",
                     form.notnull,
                     pre="<div class='concernForm'><font color=white><b>Agent ID:</b></div>",
                     description=""),
        form.Password("password",
                      form.notnull,
                      pre="<div class='concernForm'><font color=white><b>Password:</b></div>",
                      description=""),
        form.Button("Login",
                    description="Login",
                    style="font-family: Quantico; font-size: 30px;"))

    def GET(self):
        global COLOR
        global STUNNED
        global STUNTIME

        # If we have a logged in user, redirect them to the puzzle
        if session.get('logged_in'):
            raise web.seeother('/sc')

        # else, have them login
        return render.login(self.loginForm(), STUNTIME, SHADOWCASTER, COLOR, "")

    def POST(self):
        form = self.loginForm()

        if not form.validates():
            return render.login(self.loginForm(), STUNTIME, SHADOWCASTER, COLOR, "XXX")

        user = str(form.d.user).lower()
        password = form.d.password

        # Is it a valud user
        if user not in db or password != db[user]["password"]:
            return render.login(self.loginForm(), STUNTIME, SHADOWCASTER, COLOR, "XXX")
        if db[user]["solved"][str(config["SHADOWCASTER"])]:
            return render.login(None, STUNTIME, SHADOWCASTER, COLOR, "agent light already released")

        session.logged_in = True
        session.user = user

        raise web.seeother('/sc')


class logout:
    global db

    def GET(self):

        session.logged_in = False
        session.user = ""
        session.kill()
        if DEBUG:
            db["znjp"]["solved"] = False
            sync_db()
        raise web.seeother('/login')


class sc:
    global db
    global STUNNED
    global ENERGY
    global COLOR

    def GET(self):
        # Is the user logged in?
        if not session.get('logged_in'):
            raise web.seeother('/login')

        user = session.get('user')
        if db[user]["solved"][str(config["SHADOWCASTER"])]:
            return render.login(None, STUNTIME, SHADOWCASTER, COLOR, "agent light already released")

        print "SC", SHADOWCASTER

        if SHADOWCASTER == 1:
            return render.intswitch(STUNTIME)
        elif SHADOWCASTER == 2:
            return render.hexswitch(STUNTIME)
        elif SHADOWCASTER == 3:
            return render.dragdropone(STUNTIME)
        elif SHADOWCASTER == 4:
            return render.dragdroptwo(STUNTIME)
        elif SHADOWCASTER == 5:
            return render.toggleone(STUNTIME)
        elif SHADOWCASTER == 6:
            return render.toggletwo(STUNTIME)
        elif SHADOWCASTER == 7:
            return render.simon(STUNTIME)
        elif SHADOWCASTER == 8:
            return render.sc8(STUNTIME)
        elif SHADOWCASTER == 9:
            return render.eqnswitch(STUNTIME)

        return render.login(None, STUNTIME, SHADOWCASTER, COLOR, "error: no puzzle")


class stun:
    def GET(self):
        threading.Thread(target=stunLights).start()
        return "Stunned!"

    def POST(self):
        threading.Thread(target=stunLights).start()
        web.seeother('/admin')


class unstun:
    def GET(self):
        global STUNNED
        global STUNTIME
        STUNNED = False
        STUNTIME = 0
        return "Unstunned!"

    def POST(self):
        global STUNNED
        global STUNTIME
        STUNNED = False
        STUNTIME = 0
        web.seeother('/admin')


class stunstatus:
    def GET(self):
        global STUNNED
        return STUNNED


def init_users():
    global db
    # Generate user logins and flags
    config["TOTALPUZZLES"]
    db["znjp"] = {"password": "brak4pres", "solved": db_build_helper(config["TOTALPUZZLES"]),
                  "flag": db_build_helper_for_flag_gen(config["TOTALPUZZLES"], 'znjp'), "admin": True}
    db["alpha"] = {"password": "ZnTkHA", "solved": db_build_helper(config["TOTALPUZZLES"]),
                   "flag": db_build_helper_for_flag_gen(config["TOTALPUZZLES"], 'aplha'), "admin": False}
    db["bravo"] = {"password": "dTdRtLY", "solved": db_build_helper(config["TOTALPUZZLES"]),
                   "flag": hashlib.sha1("bravo" + "sc" + str(SHADOWCASTER)).hexdigest(), "admin": False}
    db["charlie"] = {"password": "dZUokZ", "solved": db_build_helper(
        config["TOTALPUZZLES"]), "flag": db_build_helper_for_flag_gen(config["TOTALPUZZLES"], 'charlie'), "admin": False}
    db["delta"] = {"password": "HewLwZ", "solved": db_build_helper(config["TOTALPUZZLES"]),
                   "flag": db_build_helper_for_flag_gen(config["TOTALPUZZLES"], 'delta'), "admin": False}
    db["echo"] = {"password": "pRhzpa", "solved": db_build_helper(config["TOTALPUZZLES"]),
                  "flag": db_build_helper_for_flag_gen(config["TOTALPUZZLES"], 'echo'), "admin": False}
    db["foxtrot"] = {"password": "djUTAm", "solved": db_build_helper(
        config["TOTALPUZZLES"]), "flag": db_build_helper_for_flag_gen(config["TOTALPUZZLES"], 'foxtrot'), "admin": False}
    db["golf"] = {"password": "DMTBQa", "solved": db_build_helper(config["TOTALPUZZLES"]),
                  "flag": db_build_helper_for_flag_gen(config["TOTALPUZZLES"], 'golf'), "admin": False}
    db["hotel"] = {"password": "xokRDs", "solved": db_build_helper(config["TOTALPUZZLES"]),
                   "flag": db_build_helper_for_flag_gen(config["TOTALPUZZLES"], 'hotel'), "admin": False}
    db["india"] = {"password": "PZEUXn", "solved": db_build_helper(config["TOTALPUZZLES"]),
                   "flag": db_build_helper_for_flag_gen(config["TOTALPUZZLES"], 'india'), "admin": False}
    db["juliet"] = {"password": "gKZFQr", "solved": db_build_helper(config["TOTALPUZZLES"]),
                    "flag": db_build_helper_for_flag_gen(config["TOTALPUZZLES"], 'juliet'), "admin": False}
    db["1"] = {"password": "1", "solved": db_build_helper(config["TOTALPUZZLES"]),
               "flag": db_build_helper_for_flag_gen(config["TOTALPUZZLES"], '1'), "admin": False}
    db["2"] = {"password": "2", "solved": db_build_helper(config["TOTALPUZZLES"]),
               "flag": db_build_helper_for_flag_gen(config["TOTALPUZZLES"], '2'), "admin": False}
    sync_db()
    return


def db_build_helper_for_solved_status(numOfPuzzles):
    # assumes shadowcaster index starts at 1
    toReturn = dict()
    for i in range(1, numOfPuzzles + 1):
        toReturn[str(i)] = False
    return toReturn


def db_build_helper_for_flag_gen(numOfPuzzles, username):
    # assumes shadowcaster index starts at 1
    toReturn = dict()
    for i in range(1, numOfPuzzles + 1):
        toReturn[str(i)] = hashlib.sha1(
            username + "sc" + str(SHADOWCASTER)).hexdigest()
    return toReturn


def load_db(db_path):
    global db
    # Load any saved progress
    try:
        f = open(db_path)
        db = pickle.load(f)
        f.close()
        # Saved progress is overated
        # os.remove(db_path)
        # init_users()
        if DEBUG:
            print "LOAD DB", db
    except:
        if DEBUG:
            print "Error loading database. Creating a new one."
        init_users()
        return

    # init_users()


def sync_db():
    global db
    global last_sync

    now = time.time()

    # Write DB every 5 seconds
    if (now - last_sync) > 5:
        if DEBUG:
            print "SYNCHING!"

        f = open("./password.db", "wb")
        pickle.dump(db, f)
        f.close()
        last_sync = now


def notfound():
    global COLOR
    return web.notfound(render.fourohfour(COLOR))


if __name__ == "__main__":
    app.notfound = notfound
    load_db("./password.db")
    if not NOGPIO:
        init_leds()
    app.run()
    if not NOGPIO:
        print "Shutting down."
        GPIO.output(BLUE, False)
        GPIO.output(GREEN, False)
        GPIO.output(RED, False)
        GPIO.cleanup()
