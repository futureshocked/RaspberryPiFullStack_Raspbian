'''

FILE NAME
blinky.py

1. WHAT IT DOES
Makes an LED blink using a Raspberry Pi.
 
2. REQUIRES
* Any Raspberry Pi
* A 5mm LED
* A 1KOhm resistor
* Jumper wires

3. ORIGINAL WORK
Raspberry Full stack 2018, Peter Dalmaris

4. HARDWARE
D07: LED

5. SOFTWARE
Command line terminal
Simple text editor
Libraries:
import RPi.GPIO as GPIO
import time (for 'sleep')

6. WARNING!
None

7. CREATED 

8. TYPICAL OUTPUT
LED blinks

 // 9. COMMENTS
--

 // 10. END

'''

import RPi.GPIO as GPIO         ## Import GPIO Library
import time                     ## Import 'time' library (for 'sleep')
 
pin = 7                         ## We're working with pin 7
GPIO.setmode(GPIO.BOARD)        ## Use BOARD pin numbering
GPIO.setup(pin, GPIO.OUT)       ## Set pin 7 to OUTPUT

for i in range (0, 20):         ## Repeat 20 times
	GPIO.output(pin, GPIO.HIGH) ## Turn on GPIO pin (HIGH)
	time.sleep(1)               ## Wait 1 second
	GPIO.output(pin, GPIO.LOW)  ## Turn off GPIO pin (LOW)
	time.sleep(1)               ## Wait 1 second
 
GPIO.cleanup()
