import web
from web import form
import hashlib, os, os.path, threading, string, time, math, sqlite3

# Experimental LED matrix implementation:
import ledFuncs

# This line causes this script to be somewhat unresponsive to ctrl-C
web.config.debug = False

# SHADOWCASTER GLOBAL SETTINGS
DEBUG = False

# IMPORTANT: This must be set to the PWD of the python script if run as an init service
#os.chdir("/home/pi/shadowCaster-server")
DBFILE = "./scdb.sql"

#DATABASE STUFF
#Initialize the the database, should it not exist
if os.path.isfile(DBFILE) == False:
    connection = sqlite3.connect(DBFILE)
    cursor = connection.cursor()
    #Login Names
    agents = ["alpha","bravo","charlie","delta","echo","foxtrot","golf","hotel","india","juliet"]
    #Total Number of puzzles
    total = 13
    #Per-caster secret (UNUSED)
    secret = str(os.urandom(16)).encode("base64")

    print "Creating agents...",
    sql_command = """
        CREATE TABLE agents (
            agent VARCHAR(20) PRIMARY KEY,
            password VARCHAR(20),
            solved INTEGER,
            flag VARCHAR(20),
            admin INTEGER);"""
    try:
        cursor.execute(sql_command)
        for agent in agents:
            password = hashlib.sha256(agent).digest().encode("base64")[:8]
            flag = hashlib.sha256("sc1"+agent).digest().encode("base64")[:10]
            format_str = """INSERT INTO agents (agent, password, solved, flag, admin)
            VALUES ("{agent}", "{password}" , 0, "{flag}", 0);"""
            sql_command = format_str.format(agent=agent, password=password, flag=flag)
            cursor.execute(sql_command)
    except Exception as e:
        print "Failed to create agents table: ", str(e)
        quit()

    #Add special users
    sql_command = """INSERT INTO agents (agent, password, solved, flag, admin)
    VALUES ("znjp", "brak4pres" , 0, "flag", 1);"""
    cursor.execute(sql_command)
    print "Done."

    print "Create SC configs...",
    sql_command = """
        CREATE TABLE IF NOT EXISTS sc (
            scnum INTEGER PRIMARY KEY,
            total INTEGER,
            energy INTEGER,
            stun INTEGER,
            release INTEGER,
            secret VARCHAR(16));"""
    cursor.execute(sql_command)

    format_str = """INSERT INTO sc (scnum, total, energy, stun, release, secret)
    VALUES (1, "{total}", 100, 100, 100, "{secret}");"""
    sql_command = format_str.format(total=total, secret=secret)
    try:
        cursor.execute(sql_command)
    except Exception as e:
        print "Failed to create SC configs table: ", str(e)
        quit()
    print "Done."

    print "Creating sessions table..."
    sql_command = """
        CREATE TABLE sessions (
            session_id char(128) UNIQUE NOT NULL,
            atime timestamp NOT NULL default current_timestamp,
            data text
        );
    """
    try:
        cursor.execute(sql_command)
    except Exception as e:
        print "Unable to create sessions table.", str(e)
        quit()
    print "Done."
    connection.commit()
    connection.close()

#Try opening the database
try:
    db = web.database(dbn='sqlite', db=DBFILE)
    result = db.select('sc')
    config = dict(result[0])
except:
    print "Database error: This is no database!"
    quit()

SHADOWCASTER = config["scnum"]  # SC Number
TOTALPUZZLES = config["total"]  # Total Number of Puzzles
ENERGY = config["energy"]  # Energy level
STUNDURATION = config["stun"]  # Stun duration in seconds
RELEASEDURATION = config["release"]  # Release duration In seconds
SECRET = config["secret"] #Game secret

COLOR = "blue" #TODO!!!

# Global variables used for stunning/releasing
STUNNED = False
RELEASING = False
STUNTIME = 0  # Stun time remaining
mutex = threading.Lock()

# GPIO Settings
##NOGPIO = True
### Pin outs for LEDs
##RED = 11
##GREEN = 13
##BLUE = 15
#GRD = 6, 9, 14

##try:
##    import RPi.GPIO as GPIO
##    GPIO.setmode(GPIO.BOARD)
##    GPIO.setup(RED, GPIO.OUT)
##    GPIO.setup(GREEN, GPIO.OUT)
##    GPIO.setup(BLUE, GPIO.OUT)
##    # Set the initial color
##    GPIO.output(BLUE, True)
##    NOGPIO = False
##except:
##    print time.strftime("%a, %d %b %Y %H:%M:%S",
##                        time.localtime()) + " No GPIO. Going to DEBUG mode."
##    NOGPIO = True

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
        #Admin realted interfaces
        '/admin', 'admin',  # Main administration panel
        '/testRelease', 'testRelease',
        '/testStun', 'testStun',
        '/setPuzzleNum', 'setPuzzleNum',
        '/setStunTime', 'setStunTime',
        '/setReleaseTime', 'setReleaseTime',
        '/setEnergyLevel', 'setEnergyLevel',
        '/printTeams', 'printTeams')
app = web.application(urls, globals())
store = web.session.DBStore(db, 'sessions')
session = web.session.Session(app, store, initializer={'logged_in':False, 'user':""})


def init_leds(t=5):
    global leds
    global COLOR
##    while t:
##        GPIO.output(RED, True)
##        time.sleep(.25)
##        GPIO.output(RED, False)
##        time.sleep(.25)
##        GPIO.output(GREEN, True)
##        time.sleep(.25)
##        GPIO.output(GREEN, False)
##        time.sleep(.25)
##        GPIO.output(BLUE, True)
##        time.sleep(.25)
##        GPIO.output(BLUE, False)
##        time.sleep(.25)
##        GPIO.output(RED, True)
##        GPIO.output(GREEN, True)
##        GPIO.output(BLUE, True)
##        time.sleep(.25)
##        GPIO.output(RED, False)
##        GPIO.output(GREEN, False)
##        GPIO.output(BLUE, False)
##        time.sleep(.25)
##        t -= 1
##    GPIO.output(BLUE, True)
##    GPIO.output(GREEN, False)
##    GPIO.output(RED, False)

    #NB: A mutex is another term for a lock. I think it makes sense
    # to put a lock around the use of the LEDs, meaning only one
    # thread at a time. There are two kinds of locks: blocking and unblocking,
    # blocking is where a thread will wait until an acquired lock is unlocked
    # and unblocking is where it will just fail. I think we want unblocking
    # and have any led requests fail. I THINK. Keep this in mind as you
    # make your updates.

    # Acquire the LED lock; if it's already locked, then just return
    if mutex.acquire(False) == False:
        return # LED operation fails

    try:
        leds = ledFuncs.LedHandler()
        leds.color = COLOR
    finally:
        mutex.release()

def releaseLights():
    global STUNNED
    global STUNTIME
    global RELEASING
    global leds

    STUNNED = True
    RELEASING = True
    STUNTIME = RELEASEDURATION
    leds.releaseTime = RELEASEDURATION
    threading.Thread(target=countdown).start()
    
    # Acquire the LED lock; if it's already locked, then just return
    if mutex.acquire(False) == False:
        return # LED operation fails

    try:
        leds.startRelease()
    finally:
        mutex.release()

    #NB: I'm not sure what this is doing. Can't this function just return?
    # Maybe it's to wait setting those sentinal values at the bottom?
    # If so, that should be handled by the LED thread, I think.
    now = time.time()
##    # Turn off the lights
##    if not NOGPIO:
##        GPIO.output(RED, False)
##        GPIO.output(GREEN, False)
##        GPIO.output(BLUE, False)
    while(time.time() < now + RELEASEDURATION and STUNNED):
        time.sleep(1)
##        if DEBUG and NOGPIO:
##            print "WIN!"
##            time.sleep(.6)
##        # Sparkle the lights
##        else:
##            GPIO.output(RED, True)
##            time.sleep(.1)
##            GPIO.output(RED, False)
##            time.sleep(.1)
##            GPIO.output(GREEN, True)
##            time.sleep(.1)
##            GPIO.output(GREEN, False)
##            time.sleep(.1)
##            GPIO.output(BLUE, True)
##            time.sleep(.1)
##            GPIO.output(BLUE, False)
##            time.sleep(.1)
##    # Set the original color
##    if not NOGPIO:
##        if COLOR == "red":
##            GPIO.output(RED, True)
##            GPIO.output(GREEN, False)
##            GPIO.output(BLUE, False)
##        if COLOR == "green":
##            GPIO.output(GREEN, True)
##            GPIO.output(RED, False)
##            GPIO.output(BLUE, False)
##        if COLOR == "blue":
##            GPIO.output(BLUE, True)
##            GPIO.output(GREEN, False)
##            GPIO.output(RED, False)
    STUNNED = False
    RELEASING = False


def countdown():
    global STUNTIME
    while STUNTIME:
        STUNTIME -= 1
        if DEBUG:
            print STUNTIME,
        time.sleep(1)


def stunLights():
    global STUNNED
    global STUNTIME
    global leds
    now = time.time()

    STUNNED = True
    STUNTIME = STUNDURATION
    leds.stunTime = STUNDURATION
    threading.Thread(target=countdown).start()

    # Acquire the LED lock; if it's already locked, then just return
    if mutex.acquire(False) == False:
        return # LED operation fails

    try:
        leds.startStun()
    finally:
        mutex.release()
    
##    # Turn off the lights
##    if not NOGPIO:
##        GPIO.output(RED, False)
##        GPIO.output(GREEN, False)
##        GPIO.output(BLUE, False)
##    # Flash the lights

    #NB: Same thing here. Remove and move sentinel operations elsewhere.
    while(time.time() < now + STUNDURATION and STUNNED):
        time.sleep(1)
        
##        if DEBUG and NOGPIO:
##            print "STUN."
##            time.sleep(.3)
##        else:
##            GPIO.output(RED, True)
##            time.sleep(.25)
##            GPIO.output(RED, False)
##            time.sleep(.25)
##            GPIO.output(RED, True)
##            time.sleep(.25)
##            GPIO.output(RED, False)
##            time.sleep(.25)
##    # Set the original color
##    if not NOGPIO:
##        if COLOR == "red":
##            GPIO.output(RED, True)
##            GPIO.output(GREEN, False)
##            GPIO.output(BLUE, False)
##        if COLOR == "green":
##            GPIO.output(GREEN, True)
##            GPIO.output(RED, False)
##            GPIO.output(BLUE, False)
##        if COLOR == "blue":
##            GPIO.output(BLUE, True)
##            GPIO.output(GREEN, False)
##            GPIO.output(RED, False)
            
    STUNNED = False

def setColor():
    global ENERGY
    global COLOR
    global leds

    if ENERGY <= 100 and ENERGY > 70:
        COLOR = "blue"
    if ENERGY < 70 and ENERGY > 30:
        COLOR = "green"
    if ENERGY < 30:
        COLOR = "red"
    if DEBUG:
        print "Color is now", COLOR
    # if not NOGPIO:
    #     if COLOR == "red":
    #         GPIO.output(RED, True)
    #         GPIO.output(GREEN, False)
    #         GPIO.output(BLUE, False)
    #     if COLOR == "green":
    #         GPIO.output(GREEN, True)
    #         GPIO.output(RED, False)
    #         GPIO.output(BLUE, False)
    #     if COLOR == "blue":
    #         GPIO.output(BLUE, True)
    #         GPIO.output(GREEN, False)
    #         GPIO.output(RED, False)       
    

    #NB: Does this actully set the color, or just a set a value
    # that's read? If it's the former, we probably need to add 
    # a lock here. If it's the latter, probably not.
    leds.color = COLOR

class energy:
    def GET(self):
        global ENERGY
        return ENERGY


class release:
    global db

    def GET(self):
        global COLOR
        global ENERGY
        global RELEASING

        if not session.get('logged_in'):
            if DEBUG:
                print "Not logged in."
            raise web.seeother('/login')

        #Get the user from the database
        user = session.get('user')
        vars = dict(agent=user)
        try:
            result = db.select('agents', where="agent = $agent", vars=vars, limit=1)
            agent = dict(result[0])
        except Exception as e:
            if DEBUG:
                print "User not in database:" + str(e)
            raise web.seeother('/login')

        if agent["solved"] == 1 and RELEASING == True:
            #return render.login(None, 0, SHADOWCASTER, COLOR, "agent light already released", agent["flag"])
            return render.release(SHADOWCASTER, COLOR, False, agent["flag"])
        if agent["solved"] == 1 and RELEASING == False:
            return render.release(SHADOWCASTER, COLOR, True, agent["flag"])

        # Get solved key and validate
        user_data = web.input(e="", _unicode=False)
        if SHADOWCASTER != 8 and user_data.e != hashlib.sha1("sc" + str(SHADOWCASTER)).hexdigest():
            #Render a login page so stunning still works
            return render.login(None, STUNTIME, SHADOWCASTER, COLOR, "agent key invalid", None)

        # SHADOWCATER 8 requires a special key generated by the players
        if SHADOWCASTER == 8 and user_data.e != hashlib.sha1(user).hexdigest():
            #Render a login page so stunning still works
            return render.login(None, STUNTIME, SHADOWCASTER, COLOR, "agent key invalid", None)

        ENERGY = ENERGY - 10
        setColor()
        num_updated = db.update('sc', where='scnum = ' + str(SHADOWCASTER), energy = ENERGY)        
        if num_updated != 1 and DEBUG:
            print "Error updating energy level"

        #NB: I don't think this needs to be a thread any more, if your LED 
        # library creates its own thread.
        threading.Thread(target=releaseLights).start()

        num_updated  = db.update('agents', where='agent = "' + agent["agent"] +'"', solved = 1)
        if num_updated != 1 and DEBUG:
            print "Error updating solved status for agent."

        #Release is an unsuntable page (as releasing stuns)
        return render.release(SHADOWCASTER, COLOR, False, agent["flag"]) 


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
        global STUNTIME

        # If we have a logged in user, redirect them to the puzzle
        if session.get('logged_in'):
            raise web.seeother('/sc')

        # else, have them login
        return render.login(self.loginForm(), STUNTIME, SHADOWCASTER, COLOR, "", None)

    def POST(self):
        form = self.loginForm()

        if not form.validates():
            return render.login(self.loginForm(), STUNTIME, SHADOWCASTER, COLOR, "XXX", None)

        user = str(form.d.user).lower()
        password = form.d.password

        #Get the user from the database
        vars = dict(agent=user)
        try:
            result = db.select('agents', where="agent = $agent", vars=vars, limit=1)
            agent = dict(result[0])
        except Exception as e:
            if DEBUG:
                print "User not in database."
            return render.login(self.loginForm(), STUNTIME, SHADOWCASTER, COLOR, "XXX", None)
        
        # Is it a valid user?
        if password != agent["password"]:
            return render.login(self.loginForm(), STUNTIME, SHADOWCASTER, COLOR, "XXX", None)
        if agent["solved"] == 1:
            return render.login(None, STUNTIME, SHADOWCASTER, COLOR, "agent light already released", agent["flag"])

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
            db.update('agents', where='agent = "znjp"', solved = 0)
        raise web.seeother("/")


class sc:
    global db
    global ENERGY
    global COLOR
    global RELEASING

    def GET(self):
        # Is the user logged in?
        if not session.get('logged_in'):
            raise web.seeother('/login')

        #Get the user from the db
        user = session.get('user')
        vars = dict(agent=user)
        try:
            result = db.select('agents', where="agent = $agent", vars=vars, limit=1)
            agent = dict(result[0])
        except Exception as e:
            if DEBUG:
                print "User not in database."
            raise web.seeother('/login')

        #Has the agent already solved the puzzle?
        if agent["solved"] == 1 and RELEASING == True:
            return render.release(SHADOWCASTER, COLOR, False, agent["flag"])
        if agent["solved"] == 1 and RELEASING == False:
            return render.release(SHADOWCASTER, COLOR, True, agent["flag"])       
            #return render.login(None, STUNTIME, SHADOWCASTER, COLOR, "agent light already released", agent["flag"])

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
        elif SHADOWCASTER == 10:
            return render.picture(STUNTIME)
        elif SHADOWCASTER == 11:
            return render.logicGrid2(STUNTIME)
        elif SHADOWCASTER == 12:
            return render.lightsout(STUNTIME)
        elif SHADOWCASTER == 13:
            return render.wheel(STUNTIME)

        return render.login(None, STUNTIME, SHADOWCASTER, COLOR, "error: no puzzle", None)


class stun:
    def GET(self):
        return """<html>
        <head><link href='/static/font.css' rel='stylesheet'></head>
        <body bgcolor="black">
        <center>
        <form method='POST' action='/stun'>
        <button style="height:200px;width:200px;background-color: #ccc;border: 2px solid red;font-family: 'Quantico'" type='submit' value='Stun'><font color="red"><h1>Stun</h1></font></button>
        </form>
        <p>
        <form method='POST' action='/unstun'>
        <button style="height:200px;width:200px;background-color: #ccc;font-family: 'Quantico'" type='submit' value='Unstun'><h1>Unstun!</h1></button>
        </form>
        </center></body></html>"""

    def POST(self):
        #NB: Does this need to be threaded here? I don't think so anymore.
        threading.Thread(target=stunLights).start()
        referer = web.ctx.env.get('HTTP_REFERER', '/')
        raise web.seeother(referer)


class unstun:
    def GET(self):
        global STUNNED
        global STUNTIME
        global RELEASING
        global leds
        #NB: This needs to work with your code now.
        STUNNED = False
        leds.stunned = False
        RELEASING = False
        STUNTIME = 0
        referer = web.ctx.env.get('HTTP_REFERER', '/')
        raise web.seeother(referer)

    def POST(self):
        global STUNNED
        global STUNTIME
        global RELEASING
        global leds
        STUNNED = False
        leds.stunned = False
        RELEASING = False
        STUNTIME = 0
        referer = web.ctx.env.get('HTTP_REFERER', '/')
        raise web.seeother(referer)


class stunstatus:
    def GET(self):
        global STUNNED
        return STUNNED


########## ADMIN FUNCTIONS ###############
#NB: make sure these all work with your LED code now.

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

printTeamsForm = form.Form(
    form.Button("Print",
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

def isAdmin(user=None):

        vars = dict(agent=user)
        try:
            result = db.select('agents', where="agent = $agent", vars=vars, limit=1)
            agent = dict(result[0])
        except Exception as e:
            if DEBUG:
                print "User not in database:" + str(e)
            return False


        if agent["admin"] != 1:
            if DEBUG:
                print "User not admin."
            return False
        
        return agent["admin"] == 1

class testRelease:
    def GET(self):

        user = session.get('user')
        if not isAdmin(user):
            raise web.seeother('/login')

        #NB: Does this need to be threaded here any more?
        threading.Thread(target=releaseLights).start()
        raise web.seeother('/admin')

    def POST(self):

        user = session.get('user')
        if not isAdmin(user):
            raise web.seeother('/login')

        #NB: Does this need to be threaded here any more?
        threading.Thread(target=releaseLights).start()
        raise web.seeother('/admin')


class testStun:
    def GET(self):
        user = session.get('user')
        if not isAdmin(user):
            raise web.seeother('/login')

        #NB: Does this need to be threaded here any more?
        threading.Thread(target=stunLights).start()
        raise web.seeother('/admin')

    def POST(self):
        user = session.get('user')
        if not isAdmin(user):
            raise web.seeother('/login')

        #NB: Does this need to be threaded here any more?
        threading.Thread(target=stunLights).start()
        raise web.seeother('/admin')


class setPuzzleNum:
    def POST(self):
        global SHADOWCASTER
        global STUNNED
        global STUNTIME
        global ENERGY
        global leds

        user = session.get('user')
        if not isAdmin(user):
            raise web.seeother('/login')
        
        form = puzzlenumForm()

        if not form.validates():
            raise web.seeother('/admin?status=Bad puzzle number')

        #Update the puzzle number.
        num_updated = db.update('sc', where='scnum = ' + str(SHADOWCASTER), scnum = int(form["mydrop"].value), energy=100)
        if num_updated != 1 and DEBUG:
            print "Error updating puzzle number"
            raise web.seeother('/admin?status=Error')

        SHADOWCASTER = int(form["mydrop"].value)
        ENERGY=100
        setColor()
        STUNNED = False
        STUNTIME = 0
        leds.stunned = False
        leds.release = False

        #Reset all solved states
        num_updated = db.query('UPDATE agents set solved = 0')
        if DEBUG:
            print "Updated solved states for", num_updated, "teams."
        
        #Change all the flags in the database sha256(sc# + agent).b64[:10]
        agents = db.select('agents')
        for agent in agents:
            flag = hashlib.sha256("sc"+str(SHADOWCASTER)+agent["agent"]).digest().encode("base64")[:10]
            num_updated = db.update('agents', where='agent = "' + agent["agent"]  + '"', flag=flag)
            if num_updated != 1 and DEBUG:
                print "Error updating agent flag for", agent["agent"]
                raise web.seeother('/admin?status=Error')

        raise web.seeother('/admin?status=Success')


class setStunTime:
    def POST(self):
        global STUNDURATION
        global leds

        user = session.get('user')
        if not isAdmin(user):
            raise web.seeother('/login')

        form = setStunTimeForm()
        if not form.validates():
            raise web.seeother('/admin?status=Not a number')

        STUNDURATION = int(form["time"].value)
        leds.stunTime = STUNDURATION
        num_updated = db.update('sc', where='scnum = ' + str(SHADOWCASTER), stun = STUNDURATION)        
        if num_updated != 1 and DEBUG:
            print "Error updating stun duration"
            raise web.seeother('/admin?status=Error')      

        raise web.seeother('/admin?status=Success')


class setReleaseTime:
    def POST(self):
        global RELEASEDURATION
        global leds

        user = session.get('user')
        if not isAdmin(user):
            raise web.seeother('/login')

        form = setReleaseTimeForm()
        if not form.validates():
            raise web.seeother('/admin?status=Not a number')

        RELEASEDURATION = int(form["time"].value)
        leds.releaseTime = RELEASEDURATION
        num_updated = db.update('sc', where='scnum = ' + str(SHADOWCASTER), release = RELEASEDURATION)        
        if num_updated != 1 and DEBUG:
            print "Error updating stun duration"
            raise web.seeother('/admin?status=Error')          

        raise web.seeother('/admin?status=Success')


class setEnergyLevel:
    def POST(self):
        global ENERGY

        user = session.get('user')
        if not isAdmin(user):
            raise web.seeother('/login')
        
        form = setEnergyLevelForm()
        if not form.validates():
            raise web.seeother('/admin?status=Not a number')

        ENERGY = int(form["level"].value)
        setColor()
        num_updated = db.update('sc', where='scnum = ' + str(SHADOWCASTER), energy = ENERGY)        
        if num_updated != 1 and DEBUG:
            print "Error updating energy level"
            raise web.seeother('/admin?status=Error')  

        raise web.seeother('/admin?status=Success')

class printTeams:
    def GET(self):
        user = session.get('user')
        if not isAdmin(user):
            raise web.seeother('/login')

        try:
            agents = db.select('agents')
        except Exception as e:
            if DEBUG:
                print "User not in database."
            raise web.seeother('/admin?status=Database failure')
        
        return render.teams(agents)

class admin:
    def GET(self):
        user = session.get('user')
        if not isAdmin(user):
            raise web.seeother('/login')

        data = web.input(status="")
        status = str(data.status)
        puzzlenumForm["mydrop"].value = str(SHADOWCASTER)
        setStunTimeForm["time"].value = str(STUNDURATION)
        setReleaseTimeForm["time"].value = str(RELEASEDURATION)
        setEnergyLevelForm["level"].value = str(ENERGY)
        
        return render.admin(SHADOWCASTER, puzzlenumForm, setEnergyLevelForm, setStunTimeForm, setReleaseTimeForm, testReleaseForm, testStunForm, printTeamsForm, COLOR, status)


def notfound():
    global COLOR
    return web.notfound(render.fourohfour(COLOR))


if __name__ == "__main__":
    app.notfound = notfound
    #load_db()
    #if not NOGPIO:
    init_leds()
    app.run()
##    if not NOGPIO:
##        print "Shutting down."
##        GPIO.output(BLUE, False)
##        GPIO.output(GREEN, False)
##        GPIO.output(RED, False)
##        GPIO.cleanup()
