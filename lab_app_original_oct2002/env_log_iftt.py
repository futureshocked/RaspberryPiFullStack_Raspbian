#!/usr/bin/env python

'''

FILE NAME
env_log.py

1. WHAT IT DOES
Takes a reading from a DHT sensor and records the values in an SQLite3 database using a Raspberry Pi.

2. REQUIRES
* Any Raspberry Pi
* A DHT sensor
* A 10kOhm resistor
* Jumper wires

3. ORIGINAL WORK
Raspberry Full stack 2015, Peter Dalmaris

4. HARDWARE
D17: Data pin for sensor

5. SOFTWARE
Command line terminal
Simple text editor
Libraries:
import sqlite3
import sys
import Adafruit_DHT

6. WARNING!
None

7. CREATED

8. TYPICAL OUTPUT
No text output. Two new records are inserted in the database when the script is executed

 // 9. COMMENTS
--

 // 10. END

'''



import sqlite3
import sys
import Adafruit_DHT
from time import gmtime, strftime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import RPi.GPIO as GPIO     	## Import GPIO Library
import requests


def log_values(sensor_id, temp, hum):
        GPIO.output(pin, GPIO.HIGH)  ## Turn on GPIO pin (HIGH)
        conn=sqlite3.connect('/var/www/lab_app/lab_app.db')  #It is important to provide an
							     #absolute path to the database
							     #file, otherwise Cron won't be
							     #able to find it!
        curs=conn.cursor()
        curs.execute("""INSERT INTO temperatures values(datetime(CURRENT_TIMESTAMP, 'localtime'), (?), (?))""", (sensor_id,temp))  #This will store the new record at UTC
        curs.execute("""INSERT INTO humidities values(datetime(CURRENT_TIMESTAMP, 'localtime'), (?), (?))""", (sensor_id,hum))     #This will store the new record at UTC
        conn.commit()
        conn.close()
        # Create a new record in the Google Sheet
        scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('/var/www/lab_app/raspberry-pi-full-stack-1-f37054328cf5.json', scope)
        client = gspread.authorize(creds)
        sheet = client.open('Temperature and Humidity').sheet1
        row = [strftime("%Y-%m-%d %H:%M:%S", gmtime()),sensor_id,round(temp,2),round(hum,2)]
        sheet.append_row(row)

        if temp > 38 or hum > 55:
            email_alert(sensor_id, temp, hum)

        GPIO.output(pin, GPIO.LOW)   ## Turn off GPIO pin (LOW)

def email_alert(device_id, temp, hum):
    report = {}
    report["value1"] = device_id
    report["value2"] = round(temp,2)
    report["value3"] = round(hum,2)
    requests.post("https://maker.ifttt.com/trigger/RPiFS_report/with/key/hxHjeWBmcmtmMLmbXKuYBBawyIsYu_IjKEKbGHDsIzj", data=report)

GPIO.setwarnings(False)
pin = 7                     	## We're working with pin 7
GPIO.setmode(GPIO.BOARD)    	## Use BOARD pin numbering
GPIO.setup(pin, GPIO.OUT)   	## Set pin 7 to OUTPUT

humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.AM2302, 17)
# If you don't have a sensor but still wish to run this program, comment out all the
# sensor related lines, and uncomment the following lines (these will produce random
# numbers for the temperature and humidity variables):
# import random
# humidity = random.randint(1,100)
# temperature = random.randint(10,30)
if humidity is not None and temperature is not None:
	log_values("1", temperature, humidity)
else:
	log_values("1", -999, -999)
