import sqlite3

print('import DataBase...')
conn = sqlite3.connect("EyeTrack.db")  
cursor = conn.cursor()

def addTable():
    cursor.execute("""CREATE TABLE "ratio" (
	                "id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	                "averageRatio"	REAL)""")
    cursor.execute("""CREATE TABLE "calibration" (
                    "id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	                "Threshold"	INTEGER)""")

def addValue(g):
    g = str(g)
    cursor.execute("INSERT INTO ratio (averageRatio) VALUES ("+ g +");")
    conn.commit()

def addCalibr(calibr):
    calibr = str(calibr)
    cursor.execute("INSERT INTO calibration (Threshold) VALUES ("+ calibr +");")

def getCalibr():
    cursor.execute("""SELECT Threshold FROM calibration
                    ORDER BY id DESC
                    LIMIT 1;""")
    ([calibr]) = cursor.fetchall()
    conn.commit()
    return calibr[0]

def getLast():
    cursor.execute("""SELECT averageRatio
                    FROM ratio
                    ORDER BY id DESC
                    LIMIT 1;""")
    ([ratio]) = cursor.fetchall()
    conn.commit()
    return ratio[0]

def closeCursor():
    cursor.close()
    print('db closed')

