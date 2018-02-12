import RPi.GPIO as GPIO   ## Import GPIO Library
 
inPin = 8                 ## Switch connected to pin 8
GPIO.setmode(GPIO.BOARD)    ## Use BOARD pin numbering
GPIO.setup(inPin, GPIO.IN)  ## Set pin 8 to INPUT
  
while True:                 ## Do this forever
        value = GPIO.input(inPin) ## Read input from switch
        if value:                 ## If switch is released
            print("Not Pressed")
        else:                     ## Else switch is pressed
            print("Pressed")
                                           
GPIO.cleanup() 
