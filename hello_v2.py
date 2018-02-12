'''

FILE NAME
hello_v2.py

1. WHAT IT DOES
Serves a web page by applying a template to the user's web browser.
 
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
from flask import render_template

6. WARNING!
None

7. CREATED 

8. TYPICAL OUTPUT
A web page

 // 9. COMMENTS
--

 // 10. END

'''



from flask import Flask
from flask import render_template

app = Flask(__name__)
app.debug = True
@app.route("/")
def hello():
    return render_template('hello.html', message="Hello World!")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
