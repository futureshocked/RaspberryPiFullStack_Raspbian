'''
FILE NAME
lab_app.py
Version 2

1. WHAT IT DOES
Implements the first version of the project's Flask application.
This version contains adds a page that displays sensor readings from the database.
 
2. REQUIRES
* Any Raspberry Pi

3. ORIGINAL WORK
Raspberry Full Stack 2018, Peter Dalmaris

4. HARDWARE
* Any Raspberry Pi
* DHT11 or 22
* 10KOhm resistor
* Breadboard
* Wires

5. SOFTWARE
Command line terminal
Simple text editor
Libraries:
from flask import Flask, request, render_template, sqlite3

6. WARNING!
None

7. CREATED 

8. TYPICAL OUTPUT
A simple web page served by this flask application in the user's browser.
The page contains the current temperature and humidity.
A second page that displays historical environment data from the SQLite3 database.

 // 9. COMMENTS
--
 // 10. END
'''

from flask import Flask, request, render_template
import sys
import Adafruit_DHT
import sqlite3

app = Flask(__name__)
app.debug = True # Make this False if you are no longer debugging

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/lab_temp")
def lab_temp():
	humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.AM2302, 17)
	if humidity is not None and temperature is not None:
		return render_template("lab_temp.html",temp=temperature,hum=humidity)
	else:
		return render_template("no_sensor.html")

@app.route("/lab_env_db")
def lab_env_db():
	conn=sqlite3.connect('/var/www/lab_app/lab_app.db')
	curs=conn.cursor()
	curs.execute("SELECT * FROM temperatures")
	temperatures = curs.fetchall()
	curs.execute("SELECT * FROM humidities")
	humidities = curs.fetchall()
	conn.close()
	return render_template("lab_env_db.html",temp=temperatures,hum=humidities)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
