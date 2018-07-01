import sqlite3, os, hashlib

#Login Names
agents = ["alpha","bravo","charlie","delta","echo","foxtrot","golf","hotel","india","juliet"]
#Total Number of puzzles
total = 13
#Per-game secret
secret = str(os.urandom(16)).encode("base64")


connection = sqlite3.connect("scdb.sql")
cursor = connection.cursor()

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
print "Done."

#Add special users
sql_command = """INSERT INTO agents (agent, password, solved, flag, admin)
VALUES ("znjp", "brak4pres" , 0, "flag", 1);"""
cursor.execute(sql_command)
sql_command = """INSERT INTO agents (agent, password, solved, flag, admin)
VALUES ("admin", "admin" , 0, "flag", 1);"""
#cursor.execute(sql_command)

print "AGENTS"
cursor.execute("SELECT * FROM agents")
result = cursor.fetchall()
for r in result:
    print r

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
cursor.execute(sql_command)
print "Done."

print "CONFIGS"
cursor.execute("SELECT * FROM sc")
result = cursor.fetchall()
for r in result:
    print r

connection.commit()

connection.close()