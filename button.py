'''

FILE NAME
button.py

1. WHAT IT DOES
Reads the status of a button using a Raspberry Pi.
 
2. REQUIRES
* Any Raspberry Pi
* A pushbutton
* A 10kOhm resistor
* Jumper wires
* A breadboard

3. ORIGINAL WORK
Raspberry Full stack 2018, Peter Dalmaris

4. HARDWARE
D08: Button

5. SOFTWARE
Command line terminal
Simple text editor
Libraries:
import RPi.GPIO as GPIO

6. WARNING!
None

7. CREATED 

8. TYPICAL OUTPUT
Button status in the command line terminal.

 // 9. COMMENTS
--

 // 10. END

'''



import RPi.GPIO as GPIO   ## Import GPIO Library
import time               ## Import the time library
 
inPin = 8                 ## Switch connected to pin 8
GPIO.setwarnings(False)     ## Disable warnings
GPIO.setmode(GPIO.BOARD)    ## Use BOARD pin numbering
GPIO.setup(inPin, GPIO.IN)  ## Set pin 8 to INPUT
 
while True:                 ## Do this forever
    value = GPIO.input(inPin) ## Read input from switch
    if value:                 ## If switch is released
        print ("Not Pressed")
    else:                     ## Else switch is pressed
        print ("Pressed")
    time.sleep(0.1)           ## the delay is needed for the Raspberry Pi 3 because of its cpu speed
GPIO.cleanup() 
