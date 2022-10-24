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

# CE Pin, CSN Pin, SPI Speed

# Setup for GPIO 22 CE and GPIO 25 CSN with SPI Speed @ 1Mhz
# radio = radio(RPI_V2_GPIO_P1_22, RPI_V2_GPIO_P1_18, BCM2835_SPI_SPEED_1MHZ)

# Setup for GPIO 22 CE and CE0 CSN with SPI Speed @ 4Mhz
# radio = RF24(RPI_V2_GPIO_P1_15, BCM2835_SPI_CS0, BCM2835_SPI_SPEED_4MHZ)

# Setup for GPIO 22 CE and CE1 CSN with SPI Speed @ 8Mhz
# radio = RF24(RPI_V2_GPIO_P1_15, BCM2835_SPI_CS0, BCM2835_SPI_SPEED_8MHZ)

# Setup for GPIO 22 CE and CE0 CSN for RPi B+ with SPI Speed @ 8Mhz
# radio = RF24(RPI_BPLUS_GPIO_J8_22, RPI_BPLUS_GPIO_J8_24, BCM2835_SPI_SPEED_8MHZ)

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
        #ms, number = unpack('<LL', bytes(payload))
        #print('Received payload ', number, ' at ', ms, ' from ', oct(header.from_node))
        print(payload.decode())
        values = payload.decode().split(",")

        #print("--------")
        #print("Temperature: ", values[1], "°C")
        #print("Humidity: ", values[0], " %")
        #print("Sensor ID: ", header.from_node)
        #print("Header Type: ", str((chr(header.type))))


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
        #log_values(header.from_node, values[1], values[0])
        print("---------")
    time.sleep(1)
