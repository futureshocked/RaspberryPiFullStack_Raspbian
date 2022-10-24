#!/usr/bin/env python

#
# Simplest possible example of using the HC12 transceiver,
#
#  RECEIVER NODE
#  Listens for messages from the transmitter and prints them out.
#

from __future__ import print_function
import time
import serial
import os
from twilio.rest import Client
import sqlite3
import sys
from time import gmtime, strftime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
import RPi.GPIO as GPIO     	## Import GPIO Library

def text_alert(device_id, temp, hum):
    account_sid = os.environ["TWILIO_ACCOUNT_SID"]
    auth_token = os.environ["TWILIO_AUTH_TOKEN"]
    my_twilio_phone_number = os.environ["TWILIO_PHONE_NUMBER"]
    receive_phone_number = os.environ["MY_PHONE_NUMBER"]
    deg_sign = u"\N{DEGREE SIGN}"
    report = f'Device {device_id} reported a temperature of {temp}{deg_sign}C and {hum}% humidity.'
    client = Client(account_sid, auth_token)
    client.messages.create(to = receive_phone_number,
                           from_ = my_twilio_phone_number,
                           body = report)



def log_values(sensor_id, temp, hum):
        GPIO.output(pin, GPIO.HIGH)  ## Turn on GPIO pin (HIGH)

        conn=sqlite3.connect('/var/www/lab_app/lab_app.db')  #It is important to provide an
							                                 #absolute path to the database
                                                             #file, otherwise Cron won't be
                                                             #able to find it!
        curs=conn.cursor()
        print("Update database...")
        curs.execute("INSERT INTO temperatures values(datetime(CURRENT_TIMESTAMP, 'localtime'), ?, ?)", (sensor_id,float(temp)))

        curs.execute("INSERT INTO humidities values(datetime(CURRENT_TIMESTAMP, 'localtime'), ?, ?)", (sensor_id,float(hum)))
        conn.commit()
        conn.close()

        # Create a new record in the Google Sheet
        print("Update Google Sheet...")
        scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('/var/www/lab_app/raspberry-pi-full-stack-1-f37054328cf5.json', scope)
        client = gspread.authorize(creds)
        sheet = client.open('Temperature and Humidity').sheet1
        row = [strftime("%Y-%m-%d %H:%M:%S", gmtime()),sensor_id,temp,hum]  # Not using round because temp and hum are already strings
        sheet.append_row(row)

        print("Email and text alert if needed...")
        if temp > 25 or hum > 70: # convert string to floats so we can do this test
            email_alert(sensor_id, temp, hum)
            text_alert(sensor_id, temp, hum)

        GPIO.output(pin, GPIO.LOW)   ## Turn off GPIO pin (LOW)

def email_alert(device_id, temp, hum):
    report = {}
    report["value1"] = device_id
    report["value2"] = temp
    report["value3"] = hum
    requests.post("https://maker.ifttt.com/trigger/RPiFS_report/with/key/goXeg0lGQxyRfD7FnHguUl7f2GHrAgEacnwB5z_q_G3", data=report)

GPIO.setwarnings(False)
pin = 7                     	## We're working with pin 7
GPIO.setmode(GPIO.BOARD)    	## Use BOARD pin numbering
GPIO.setup(pin, GPIO.OUT)   	## Set pin 7 to OUTPUT

ser = serial.Serial(
            port = '/dev/ttyS0',
            baudrate = 9600,
            timeout=1.5
                )

time.sleep(2)

ser.flushInput()

time.sleep(0.1)

packets_sent = 0
last_sent = 0

while 1:
    line = ser.readline()

    print("Received: ")
    print(line)
    ser.write(line + '\n'.encode("ascii"))
    #print("Received: " + line.decode())

    if line:
      # Check if the screen is busy before writting to it
      file_r = open('flag.txt')
      try:
          decoded_line = line_received.decode()
          message_parts = decoded_line.split(",")
          # print the string
          print(message_parts)
          temperature = (float)message_parts[1]
          humidity = (float)message_parts[2]
          from_id = 2
          print("--------")
          print("Temperature: ", temperature)
          print("Humidity: ", humidity)
          print("Sensor ID: ", from_id)
          print("--------")
      except:
          temperature = -99.0
          humidity = -99.0
          from_id = 2
          print("Unable to process the data received from node ", from_id, ". Data: ", line )
      log_values(from_id, temperature, humidity)
      print("---------")
    time.sleep(1)
