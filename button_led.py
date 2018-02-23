'''
FILE NAME
button_led.py

1. WHAT IT DOES
Reads the status of a button and controls an LED using a Raspberry Pi.

2. REQUIRES
* Any Raspberry Pi
* A pushbutton
* A 10kOhm resistor
* A 1KOhm resistor
* Jumper wires
* A breadboard

3. ORIGINAL WORK
Raspberry Full Stack 2018, Peter Dalmaris

4. HARDWARE
D08: Button
D07: LED

5. SOFTWARE
Command line terminal
Simple text editor
Libraries:
import RPi.GPIO as GPIO

6. WARNING!
None

7. CREATED

8. TYPICAL OUTPUT
Pressing the button will turn on the LED.

 // 9. COMMENTS
--

 // 10. END

'''

import RPi.GPIO as GPIO       ## Import GPIO Library
import time
inPin = 8                     ## Switch connected to pin 8
ledPin = 7                    ## LED connected to pin 7
GPIO.setwarnings(False)       ## Turn off warnings
GPIO.setmode(GPIO.BOARD)      ## Use BOARD pin numbering
GPIO.setup(inPin, GPIO.IN)    ## Set pin 8 to INPUT
GPIO.setup(ledPin, GPIO.OUT)  ## Set pin 7 to OUTPUT
while True:                   ## Do this forever
    value = GPIO.input(inPin) ## Read input from switch
    print(value)
    if value:                 ## If switch is released
        print("Pressed")
        GPIO.output(ledPin, GPIO.HIGH)  ## Turn LED on
    else:                     ## Else switch is pressed
        print("Not Pressed")
        GPIO.output(ledPin, GPIO.LOW)   ## Turn LED off
    time.sleep(0.1)

GPIO.cleanup()
