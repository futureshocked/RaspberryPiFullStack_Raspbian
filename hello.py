'''

FILE NAME
hello.py

1. WHAT IT DOES
Tests a new Flask installation.
 
2. REQUIRES
* Any Raspberry Pi

3. ORIGINAL WORK
Raspberry Full stack 2018, Peter Dalmaris

4. HARDWARE
None

5. SOFTWARE
Command line terminal
Simple text editor
Libraries:
from flask import Flask

6. WARNING!
None

7. CREATED 

8. TYPICAL OUTPUT
A simple web page served by this flask application in the user's browser.

 // 9. COMMENTS
--

 // 10. END

'''


from flask import Flask
app = Flask(__name__)

## RBP 2018-09-13
## Adding the following line ouputs the value
## of '__name__' on the command line.
## This code will print out the value of the __name__ variable as the program starts.
## Thank you to Richard Park for the suggestion to include it.
print("Value of '__name__' = ", __name__)

@app.route("/")
def hello():
    return "Hello World!"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
