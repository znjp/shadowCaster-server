import sys
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

web.config.debug = False  # This line causes this script to be somewhat unresponsive to ctrl-C
DEBUG = True

# SHADOWCASTER GLOBAL SETTINGS

# IMPORTANT: This must be set to the PWD of the python script if run as an init service
os.chdir("/home/pi/shadowcaster-server")

# Set the shadowcaster number here
SHADOWCASTER = 7

ENERGY = 100  # Initial energy
COLOR = "blue"  # Initial color
STUNDURATION = 120  # In seconds
FLAGDURATION = 120  # In seconds

# Global variables used for stunning
STUNNED = False
STUNTIME = 0

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
    print time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime()) + " No GPIO. Going to DEBUG mode."
    NOGPIO = True


# Our "database"
db = {}
last_sync = 0

render = web.template.render('templates/')
urls = ('/', 'admin',
        '/admin', 'admin',  # puzzle page
        '/stun', 'stun',  # stun the shadowcaster
        '/unstun', 'unstun',  # unstun the shadowcaster
        '/stunstatus', 'stunstatus',  # Is the shadowcaster stunned?
        '/login',  'login',  # login
        '/logout', 'logout',  # logout
        '/energy', 'energy',  # current energy level
        '/release', 'release')  # win
app = web.application(urls, globals())
session = web.session.Session(app, web.session.DiskStore('sessions'))


def init_leds():
    t = 5
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


def flaglights():
    global STUNNED
    global STUNTIME

    STUNNED = True
    STUNTIME = FLAGDURATION
    threading.Thread(target=countdown).start()
    now = time.time()
    # Turn off the lights
    if not NOGPIO:
        GPIO.output(RED, False)
        GPIO.output(GREEN, False)
        GPIO.output(BLUE, False)
    while(time.time() < now + FLAGDURATION and STUNNED):
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


def stunlights():
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
        if db[user]["solved"]:
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

        threading.Thread(target=flaglights).start()

        db[user]["solved"] = True
        sync_db()

        return render.release(SHADOWCASTER, db[user]["flag"])


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
            raise web.seeother('/admin')

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
        if db[user]["solved"]:
            return render.login(None, STUNTIME, SHADOWCASTER, COLOR, "agent light already released")

        session.logged_in = True
        session.user = user

        raise web.seeother('/admin')


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


class admin:
    global db
    global STUNNED
    global ENERGY
    global COLOR

    def GET(self):
        # Is the user logged in?
        if not session.get('logged_in'):
            raise web.seeother('/login')

        user = session.get('user')
        if db[user]["solved"]:
            return render.login(None, STUNTIME, SHADOWCASTER, COLOR, "agent light already released")

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
        threading.Thread(target=stunlights).start()
        return "Stunned!"


class unstun:
    def GET(self):
        global STUNNED
        global STUNTIME
        STUNNED = False
        STUNTIME = 0
        return "Unstunned!"


class stunstatus:
    def GET(self):
        global STUNNED
        return STUNNED


def init_users():
    global db
    # Generate user logins and flags
    db["znjp"] = {"password": "brak4pres", "solved": False,
                  "flag": hashlib.sha1("znjp" + "sc" + str(SHADOWCASTER)).hexdigest()}
    db["alpha"] = {"password": "ZnTkHA", "solved": False,
                   "flag": hashlib.sha1("alpha" + "sc" + str(SHADOWCASTER)).hexdigest()}
    db["bravo"] = {"password": "dTdRtLY", "solved": False,
                   "flag": hashlib.sha1("bravo" + "sc" + str(SHADOWCASTER)).hexdigest()}
    db["charlie"] = {"password": "dZUokZ", "solved": False, "flag": hashlib.sha1(
        "charlie" + "sc" + str(SHADOWCASTER)).hexdigest()}
    db["delta"] = {"password": "HewLwZ", "solved": False,
                   "flag": hashlib.sha1("delta" + "sc" + str(SHADOWCASTER)).hexdigest()}
    db["echo"] = {"password": "pRhzpa", "solved": False,
                  "flag": hashlib.sha1("echo" + "sc" + str(SHADOWCASTER)).hexdigest()}
    db["foxtrot"] = {"password": "djUTAm", "solved": False, "flag": hashlib.sha1(
        "foxtrot" + "sc" + str(SHADOWCASTER)).hexdigest()}
    db["golf"] = {"password": "DMTBQa", "solved": False,
                  "flag": hashlib.sha1("golf" + "sc" + str(SHADOWCASTER)).hexdigest()}
    db["hotel"] = {"password": "xokRDs", "solved": False,
                   "flag": hashlib.sha1("hotel" + "sc" + str(SHADOWCASTER)).hexdigest()}
    db["india"] = {"password": "PZEUXn", "solved": False,
                   "flag": hashlib.sha1("india" + "sc" + str(SHADOWCASTER)).hexdigest()}
    db["juliet"] = {"password": "gKZFQr", "solved": False,
                    "flag": hashlib.sha1("juliet" + "sc" + str(SHADOWCASTER)).hexdigest()}
    sync_db()
    return


def load_db(db_path):
    global db
    # Load any saved progress
    try:
        f = open(db_path)
        db = pickle.load(f)
        f.close()
        if DEBUG:
            print "LOAD DB", db
    except:
        if DEBUG:
            print "Error loading database. Creating a new one."
        init_users()
        return


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
