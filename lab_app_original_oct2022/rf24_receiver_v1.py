#!/usr/bin/env python

#
# Simplest possible example of using RF24Network,
#
#  RECEIVER NODE
#  Listens for messages from the transmitter and prints them out.
#

from __future__ import print_function
import time
from struct import *
from RF24 import *
from RF24Network import *

import sqlite3
import sys
from time import gmtime, strftime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import RPi.GPIO as GPIO     	## Import GPIO Library


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

        GPIO.output(pin, GPIO.LOW)   ## Turn off GPIO pin (LOW)

GPIO.setwarnings(False)
pin = 7                     	## We're working with pin 7
GPIO.setmode(GPIO.BOARD)    	## Use BOARD pin numbering
GPIO.setup(pin, GPIO.OUT)   	## Set pin 7 to OUTPUT

# CE Pin, CSN Pin, SPI Speed

radio = RF24(RPI_V2_GPIO_P1_26, RPI_V2_GPIO_P1_24, BCM2835_SPI_SPEED_8MHZ)
network = RF24Network(radio)

millis = lambda: int(round(time.time() * 1000))
octlit = lambda n: int(n, 8)

# Address of our node in Octal format (01, 021, etc)
this_node = octlit("00")

# Address of the other node
other_node = octlit("01")

radio.begin()
time.sleep(0.1)
network.begin(90, this_node)  # channel 90
radio.printDetails()
packets_sent = 0
last_sent = 0

while 1:
    network.update()
    while network.available():
        header, payload = network.read(12) #8
        print("payload length ", len(payload))
        values = payload.decode().split(",")

        print("--------")
        print("Temperature: ", values[1], "°C")
        print("Humidity: ", values[0], " %")
        print("Sensor ID: ", header.from_node)
        print("Header Type: ", str((chr(header.type))))


        # Save these values in the database
        # To make sure we have proper numbers, we'll convert the strings to numbers.
        # If the conversion succeeds, we'll record in the database and the Google Sheet.
        #temperature = values[1]
        #humidity = values[0]
        try:
            print("--------")
            print("Temperature: ", values[1])
            print("Humidity: ", values[0])
            print("Sensor ID: ", header.from_node)
            print("Header Type: ", str((chr(header.type))))
            print("--------")
            temperature = float(values[1][0:5])
            humidity = float(values[0][0:5])
            log_values(header.from_node, temperature, humidity)
        except:
            print("Unable to process the data received from node ", header.from_node, ". Data: ", values )
        print("---------")
    time.sleep(1)
