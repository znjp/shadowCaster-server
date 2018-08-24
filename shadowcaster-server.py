import web
from web import form
import hashlib, os, os.path, threading, string, time, math, sqlite3

# import all global vars
import settings
settings.init()

# import led package
import ledFuncs


# This line causes this script to be somewhat unresponsive to ctrl-C
web.config.debug = False


# IMPORTANT: This must be set to the PWD of the python script if run as an init service
# os.chdir("/home/pi/shadowCaster-server")

#DATABASE STUFF
#Initialize the the database, should it not exist
if os.path.isfile(settings.DBFILE) == False:
    connection = sqlite3.connect(settings.DBFILE)
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
    db = web.database(dbn='sqlite', db=settings.DBFILE)
    result = db.select('sc')
    config = dict(result[0])
except:
    print "Database error: This is no database!"
    quit()


settings.init_db_settings(config)

mutex = threading.Lock()

render = web.template.render('templates/')
urls = ('/', 'sc',
        '/sc', 'sc',  # puzzle page
        '/stun', 'stun',  # stun the shadowcaster
        '/unstun', 'unstun',  # unstun the shadowcaster
        '/status', 'status',  # Is the shadowcaster stunned or releasing?
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
        setColor()
        settings.LEDS = ledFuncs.LedHandler()
    finally:
        mutex.release()

def releaseLights():

    
    # Acquire the LED lock; if it's already locked, then just return
    if mutex.acquire(False) == False:
        return # LED operation fails

    settings.RELEASING = True
    settings.IDLE = False
    settings.STUNNED = False

    settings.STUNTIME = 0
    settings.RELEASTIME = 0
    time.sleep(0.1)
    settings.RELEASETIME = settings.RELEASEDURATION

    threading.Thread(target=countdown).start()

    try:
        threading.Thread(target=settings.LEDS.releaseLED).start()
    finally:
        mutex.release()


def countdown():
    
    if settings.STUNNED:
        while settings.STUNTIME:
            settings.STUNTIME -= 1
            if settings.DEBUG:
                print settings.STUNTIME
            time.sleep(1)
    elif settings.RELEASING:
        while settings.RELEASETIME:
            settings.RELEASETIME -= 1
            if settings.DEBUG:
                print settings.RELEASETIME
            time.sleep(1)
        


def stunLights():

    # Acquire the LED lock; if it's already locked, then just return
    if mutex.acquire(False) == False:
        return # LED operation fails

    settings.STUNNED = True
    settings.RELEASING = False
    settings.IDLE = False

    settings.STUNTIME = 0
    settings.RELEASETIME = 0
    time.sleep(0.1)
    settings.STUNTIME = settings.STUNDURATION

    threading.Thread(target=countdown).start()

    try:
        threading.Thread(target=settings.LEDS.stunnedLED).start()
    finally:
        mutex.release()

        
def setColor():

    if settings.ENERGY <= 100 and settings.ENERGY > 70:
        settings.COLOR = "blue"
    if settings.ENERGY < 70 and settings.ENERGY > 30:
        settings.COLOR = "green"
    if settings.ENERGY < 30 and settings.ENERGY > 0:
        settings.COLOR = "red"
    if settings.ENERGY == 0:
        settings.COLOR = "empty"
    if settings.DEBUG:
        print "Color is now", settings.COLOR
        

class energy:
    def GET(self):
        return settings.ENERGY


class release:
    global db

    def GET(self):

        if not session.get('logged_in'):
            if settings.DEBUG:
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

        if agent["solved"] == 1 and settings.RELEASING == True:
            #return render.login(None, 0, SHADOWCASTER, COLOR, "agent light already released", agent["flag"])
            return render.release(settings.SHADOWCASTER, settings.COLOR, False, agent["flag"])
        if agent["solved"] == 1 and settings.RELEASING == False:
            return render.release(settings.SHADOWCASTER, settings.COLOR, True, agent["flag"])

        # Get solved key and validate
        user_data = web.input(e="", _unicode=False)
        if settings.SHADOWCASTER != 8 and user_data.e != hashlib.sha1("sc" + str(settings.SHADOWCASTER)).hexdigest():
            #Render a login page so stunning still works
            return render.login(None, settings.STUNTIME, settings.RELEASETIME, settings.SHADOWCASTER, settings.COLOR, "agent key invalid", None)

        # SHADOWCATER 8 requires a special key generated by the players
        if settings.SHADOWCASTER == 8 and user_data.e != hashlib.sha1(user).hexdigest():
            #Render a login page so stunning still works
            return render.login(None, settings.STUNTIME, settings.RELEASETIME, settings.SHADOWCASTER, settings.COLOR, "agent key invalid", None)

        settings.ENERGY = settings.ENERGY - 10
        setColor()
        num_updated = db.update('sc', where='scnum = ' + str(settings.SHADOWCASTER), energy = settings.ENERGY)        
        if num_updated != 1 and settings.DEBUG:
            print "Error updating energy level"

        releaseLights()

        num_updated  = db.update('agents', where='agent = "' + agent["agent"] +'"', solved = 1)
        if num_updated != 1 and settings.DEBUG:
            print "Error updating solved status for agent."

        #Release is an unsuntable page (as releasing stuns)
        return render.release(settings.SHADOWCASTER, settings.COLOR, False, agent["flag"]) 


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

        # If we have a logged in user, redirect them to the puzzle
        if session.get('logged_in'):
            raise web.seeother('/sc')

        # else, have them login
        return render.login(self.loginForm(), settings.STUNTIME, settings.RELEASETIME, settings.SHADOWCASTER, settings.COLOR, "", None)

    def POST(self):
        form = self.loginForm()

        if not form.validates():
            return render.login(self.loginForm(), settings.STUNTIME, settings.RELEASETIME, settings.SHADOWCASTER, settings.COLOR, "XXX", None)

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
            return render.login(self.loginForm(), settings.STUNTIME, settings.RELEASETIME, settings.SHADOWCASTER, settings.COLOR, "XXX", None)
        
        # Is it a valid user?
        if password != agent["password"]:
            return render.login(self.loginForm(), settings.STUNTIME, settings.RELEASETIME, settings.SHADOWCASTER, settings.COLOR, "XXX", None)
        if agent["solved"] == 1:
            return render.login(None, settings.STUNTIME, settings.RELEASETIME, settings.SHADOWCASTER, settings.COLOR, "agent light already released", agent["flag"])

        session.logged_in = True
        session.user = user

        raise web.seeother('/sc')


class logout:
    global db

    def GET(self):
        session.logged_in = False
        session.user = ""
        session.kill()
        if settings.DEBUG:
            db.update('agents', where='agent = "znjp"', solved = 0)
        raise web.seeother("/")


class sc:

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
        if agent["solved"] == 1 and settings.RELEASING == True:
            return render.release(settings.SHADOWCASTER, settings.COLOR, False, agent["flag"])
        if agent["solved"] == 1 and settings.RELEASING == False:
            return render.release(settings.SHADOWCASTER, settings.COLOR, True, agent["flag"])       
            #return render.login(None, STUNTIME, SHADOWCASTER, COLOR, "agent light already released", agent["flag"])

        if settings.SHADOWCASTER == 1:
            return render.intswitch(settings.STUNTIME, settings.RELEASETIME)
        elif settings.SHADOWCASTER == 2:
            return render.hexswitch(settings.STUNTIME, settings.RELEASETIME)
        elif settings.SHADOWCASTER == 3:
            return render.dragdropone(settings.STUNTIME, settings.RELEASETIME)
        elif settings.SHADOWCASTER == 4:
            return render.dragdroptwo(settings.STUNTIME, settings.RELEASETIME)
        elif settings.SHADOWCASTER == 5:
            return render.toggleone(settings.STUNTIME, settings.RELEASETIME)
        elif settings.SHADOWCASTER == 6:
            return render.toggletwo(settings.STUNTIME, settings.RELEASETIME)
        elif settings.SHADOWCASTER == 7:
            return render.simon(settings.STUNTIME, settings.RELEASETIME)
        elif settings.SHADOWCASTER == 8:
            return render.sc8(settings.STUNTIME, settings.RELEASETIME)
        elif settings.SHADOWCASTER == 9:
            return render.eqnswitch(settings.STUNTIME, settings.RELEASETIME)
        elif settings.SHADOWCASTER == 10:
            return render.picture(settings.STUNTIME, settings.RELEASETIME)
        elif settings.SHADOWCASTER == 11:
            return render.logicGrid2(settings.STUNTIME, settings.RELEASETIME)
        elif settings.SHADOWCASTER == 12:
            return render.lightsout(settings.STUNTIME, settings.RELEASETIME)
        elif settings.SHADOWCASTER == 13:
            return render.wheel(settings.STUNTIME, settings.RELEASETIME)

        return render.login(None, settings.STUNTIME, settings.RELEASETIME, settings.SHADOWCASTER, settings.COLOR, "error: no puzzle", None)


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
        stunLights()
        referer = web.ctx.env.get('HTTP_REFERER', '/')
        raise web.seeother(referer)


class unstun:
    def GET(self):
        #NB: This needs to work with your code now.
        settings.STUNNED = False
        settings.RELEASING = False
        settings.STUNTIME = 0
        referer = web.ctx.env.get('HTTP_REFERER', '/')
        raise web.seeother(referer)

    def POST(self):
        settings.STUNNED = False
        settings.RELEASING = False
        settings.STUNTIME = 0
        referer = web.ctx.env.get('HTTP_REFERER', '/')
        raise web.seeother(referer)


class status:
    def GET(self):
        return settings.STUNNED or settings.RELEASING


########## ADMIN FUNCTIONS ###############
#NB: make sure these all work with your LED code now.

puzzlenumForm = form.Form(
    form.Dropdown('mydrop', zip(range(1, settings.TOTALPUZZLES + 1), range(1,
                                                                  settings.TOTALPUZZLES + 1)), style="font-family: Quantico; font-size: 30px;"),
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
            if settings.DEBUG:
                print "User not in database:" + str(e)
            return False


        if agent["admin"] != 1:
            if settings.DEBUG:
                print "User not admin."
            return False
        
        return agent["admin"] == 1

class testRelease:
    def GET(self):

        user = session.get('user')
        if not isAdmin(user):
            raise web.seeother('/login')

        releaseLights()
        raise web.seeother('/admin')

    def POST(self):

        user = session.get('user')
        if not isAdmin(user):
            raise web.seeother('/login')

        releaseLights()
        raise web.seeother('/admin')


class testStun:
    def GET(self):
        user = session.get('user')
        if not isAdmin(user):
            raise web.seeother('/login')

        stunLights()
        raise web.seeother('/admin')

    def POST(self):
        user = session.get('user')
        if not isAdmin(user):
            raise web.seeother('/login')

        stunLights()
        raise web.seeother('/admin')


class setPuzzleNum:
    def POST(self):

        user = session.get('user')
        if not isAdmin(user):
            raise web.seeother('/login')
        
        form = puzzlenumForm()

        if not form.validates():
            raise web.seeother('/admin?status=Bad puzzle number')

        #Update the puzzle number.
        num_updated = db.update('sc', where='scnum = ' + str(settings.SHADOWCASTER), scnum = int(form["mydrop"].value), energy=100)
        if num_updated != 1 and settings.DEBUG:
            print "Error updating puzzle number"
            raise web.seeother('/admin?status=Error')

        settings.SHADOWCASTER = int(form["mydrop"].value)
        settings.ENERGY=100
        setColor()
        settings.STUNNED = False
        settings.RELEASING = False
        settings.STUNTIME = 0

        #Reset all solved states
        num_updated = db.query('UPDATE agents set solved = 0')
        if settings.DEBUG:
            print "Updated solved states for", num_updated, "teams."
        
        #Change all the flags in the database sha256(sc# + agent).b64[:10]
        agents = db.select('agents')
        for agent in agents:
            flag = hashlib.sha256("sc"+str(settings.SHADOWCASTER)+agent["agent"]).digest().encode("base64")[:10]
            num_updated = db.update('agents', where='agent = "' + agent["agent"]  + '"', flag=flag)
            if num_updated != 1 and settings.DEBUG:
                print "Error updating agent flag for", agent["agent"]
                raise web.seeother('/admin?status=Error')

        raise web.seeother('/admin?status=Success')


class setStunTime:
    def POST(self):

        user = session.get('user')
        if not isAdmin(user):
            raise web.seeother('/login')

        form = setStunTimeForm()
        if not form.validates():
            raise web.seeother('/admin?status=Not a number')

        settings.STUNDURATION = int(form["time"].value)
        settings.LEDS.stunTime = settings.STUNDURATION
        num_updated = db.update('sc', where='scnum = ' + str(settings.SHADOWCASTER), stun = settings.STUNDURATION)        
        if num_updated != 1 and settings.DEBUG:
            print "Error updating stun duration"
            raise web.seeother('/admin?status=Error')      

        raise web.seeother('/admin?status=Success')


class setReleaseTime:
    def POST(self):

        user = session.get('user')
        if not isAdmin(user):
            raise web.seeother('/login')

        form = setReleaseTimeForm()
        if not form.validates():
            raise web.seeother('/admin?status=Not a number')

        settings.RELEASEDURATION = int(form["time"].value)
        settings.LEDS.releaseTime = settings.RELEASEDURATION
        num_updated = db.update('sc', where='scnum = ' + str(settings.SHADOWCASTER), release = settings.RELEASEDURATION)        
        if num_updated != 1 and DEBUG:
            print "Error updating stun duration"
            raise web.seeother('/admin?status=Error')          

        raise web.seeother('/admin?status=Success')


class setEnergyLevel:
    def POST(self):

        user = session.get('user')
        if not isAdmin(user):
            raise web.seeother('/login')
        
        form = setEnergyLevelForm()
        if not form.validates():
            raise web.seeother('/admin?status=Not a number')

        settings.ENERGY = int(form["level"].value)
        setColor()
        num_updated = db.update('sc', where='scnum = ' + str(settings.SHADOWCASTER), energy = settings.ENERGY)        
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
        puzzlenumForm["mydrop"].value = str(settings.SHADOWCASTER)
        setStunTimeForm["time"].value = str(settings.STUNDURATION)
        setReleaseTimeForm["time"].value = str(settings.RELEASEDURATION)
        setEnergyLevelForm["level"].value = str(settings.ENERGY)
        
        return render.admin(settings.SHADOWCASTER, puzzlenumForm, setEnergyLevelForm, setStunTimeForm, setReleaseTimeForm, testReleaseForm, testStunForm, printTeamsForm, settings.COLOR, status)


def notfound():
    return web.notfound(render.fourohfour(settings.COLOR))


if __name__ == "__main__":
    app.notfound = notfound
    #load_db()
    init_leds()
    app.run()
    if not settings.NOGPIO:
        print "Shutting down."

