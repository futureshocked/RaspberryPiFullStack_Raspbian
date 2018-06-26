'''
FILE NAME
lab_app.py
Version 10

1. WHAT IT DOES
This version adds support for Plotly.

2. REQUIRES
* Any Raspberry Pi

3. ORIGINAL WORK
Raspberry Full Stack 2018, Peter Dalmaris

4. HARDWARE
* Any Raspberry Pi
* DHT11 or 22
* 10KOhm resistor
* Breadboard
* Wires

5. SOFTWARE
Command line terminal
Simple text editor
Libraries:
from flask import Flask, request, render_template, sqlite3
Python 3

6. WARNING!
None

7. CREATED

8. TYPICAL OUTPUT
A simple web page served by this flask application in the user's browser.
The page contains the current temperature and humidity.
A second page that displays historical environment data from the SQLite3 database.
The historical records can be selected by specifying a date range in the request URL.
The user can now click on one of the date/time buttons to quickly select one of the available record ranges.
The user can use Jquery widgets to select a date/time range.
The user can explore historical data to Plotly for visualisation and processing.

 // 9. COMMENTS
--
 // 10. END
'''

from flask import Flask, request, render_template
import time
import datetime
import arrow
import sys
import Adafruit_DHT
import sqlite3
import plotly.plotly as py
from plotly.graph_objs import *

app = Flask(__name__)
app.debug = True # Make this False if you are no longer debugging

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/lab_temp")
def lab_temp():
    humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.AM2302, 17)
    if humidity is not None and temperature is not None:
        return render_template("lab_temp.html",temp=temperature,hum=humidity)
    else:
        return render_template("no_sensor.html")

@app.route("/lab_env_db", methods=['GET'])  #Add date limits in the URL #Arguments: from=2015-03-04&to=2015-03-05
def lab_env_db():
    temperatures, humidities, timezone, from_date_str, to_date_str = get_records()

    # Create new record tables so that datetimes are adjusted back to the user browser's time zone.
    time_adjusted_temperatures = []
    time_adjusted_humidities   = []
    for record in temperatures:
        local_timedate = arrow.get(record[0], "YYYY-MM-DD HH:mm").to(timezone)
        time_adjusted_temperatures.append([local_timedate.format('YYYY-MM-DD HH:mm'), round(record[2],2)])

    for record in humidities:
        local_timedate = arrow.get(record[0], "YYYY-MM-DD HH:mm").to(timezone)
        time_adjusted_humidities.append([local_timedate.format('YYYY-MM-DD HH:mm'), round(record[2],2)])

    print ("rendering lab_env_db.html with: %s, %s, %s" % (timezone, from_date_str, to_date_str))

    return render_template("lab_env_db.html",   timezone        = timezone,
                                                temp            = time_adjusted_temperatures,
                                                hum             = time_adjusted_humidities,
                                                from_date       = from_date_str,
                                                to_date         = to_date_str,
                                                temp_items      = len(temperatures),
                                                query_string    = request.query_string[0:len(request.query_string)], #This query string is used
																						#by the Plotly link
                                                hum_items       = len(humidities))

def get_records():
    from_date_str 	= request.args.get('from',time.strftime("%Y-%m-%d 00:00")) #Get the from date value from the URL
    to_date_str 	= request.args.get('to',time.strftime("%Y-%m-%d %H:%M"))   #Get the to date value from the URL
    timezone 		= request.args.get('timezone','Etc/UTC');
    range_h_form	= request.args.get('range_h','');  #This will return a string, if field range_h exists in the request
    range_h_int 	= "nan"  #initialise this variable with not a number

    print ("REQUEST:")
    print (request.args)
    print ("from: %s, to: %s, timezone: %s" % (from_date_str, to_date_str, timezone))

    try:
        range_h_int	= int(range_h_form)
    except:
        print ("range_h_form not a number")


    print ("Received from browser: %s, %s, %s, %s" % (from_date_str, to_date_str, timezone, range_h_int))

    if not validate_date(from_date_str):			# Validate date before sending it to the DB
        from_date_str 	= time.strftime("%Y-%m-%d 00:00")
    if not validate_date(to_date_str):
        to_date_str 	= time.strftime("%Y-%m-%d %H:%M")		# Validate date before sending it to the DB
    print ('2. From: %s, to: %s, timezone: %s' % (from_date_str,to_date_str,timezone))
    # Create datetime object so that we can convert to UTC from the browser's local time
    from_date_obj       = datetime.datetime.strptime(from_date_str,'%Y-%m-%d %H:%M')
    to_date_obj         = datetime.datetime.strptime(to_date_str,'%Y-%m-%d %H:%M')

	# If range_h is defined, we don't need the from and to times
    if isinstance(range_h_int,int):
        arrow_time_from = arrow.utcnow().replace(hours=-range_h_int)
        arrow_time_to   = arrow.utcnow()
        from_date_utc   = arrow_time_from.strftime("%Y-%m-%d %H:%M")
        to_date_utc     = arrow_time_to.strftime("%Y-%m-%d %H:%M")
        from_date_str   = arrow_time_from.to(timezone).strftime("%Y-%m-%d %H:%M")
        to_date_str	    = arrow_time_to.to(timezone).strftime("%Y-%m-%d %H:%M")
    else:
		#Convert datetimes to UTC so we can retrieve the appropriate records from the database
        from_date_utc   = arrow.get(from_date_obj, timezone).to('Etc/UTC').strftime("%Y-%m-%d %H:%M")
        to_date_utc     = arrow.get(to_date_obj, timezone).to('Etc/UTC').strftime("%Y-%m-%d %H:%M")

    conn 			    = sqlite3.connect('/var/www/lab_app/lab_app.db')
    curs 			    = conn.cursor()
    curs.execute("SELECT * FROM temperatures WHERE rDateTime BETWEEN ? AND ?", (from_date_utc.format('YYYY-MM-DD HH:mm'), to_date_utc.format('YYYY-MM-DD HH:mm')))
    temperatures 	    = curs.fetchall()
    curs.execute("SELECT * FROM humidities WHERE rDateTime BETWEEN ? AND ?", (from_date_utc.format('YYYY-MM-DD HH:mm'), to_date_utc.format('YYYY-MM-DD HH:mm')))
    humidities 		    = curs.fetchall()
    conn.close()

    return [temperatures, humidities, timezone, from_date_str, to_date_str]

@app.route("/to_plotly", methods=['GET'])  #This method will send the data to ploty.
def to_plotly():
	temperatures, humidities, timezone, from_date_str, to_date_str = get_records()

	# Create new record tables so that datetimes are adjusted back to the user browser's time zone.
	time_series_adjusted_temperatures   = []
	time_series_adjusted_humidities 	= []
	time_series_temperature_values 	    = []
	time_series_humidity_values 		= []

	for record in temperatures:
		local_timedate = arrow.get(record[0], "YYYY-MM-DD HH:mm").to(timezone)
		time_series_adjusted_temperatures.append(local_timedate.format('YYYY-MM-DD HH:mm'))
		time_series_temperature_values.append(round(record[2],2))

	for record in humidities:
		local_timedate = arrow.get(record[0], "YYYY-MM-DD HH:mm").to(timezone)
		time_series_adjusted_humidities.append(local_timedate.format('YYYY-MM-DD HH:mm')) #Best to pass datetime in text
																						  #so that Plotly respects it
		time_series_humidity_values.append(round(record[2],2))

	temp = Scatter(
        		x     = time_series_adjusted_temperatures,
        		y     = time_series_temperature_values,
        		name  = 'Temperature'
    				)
	hum = Scatter(
        		x     = time_series_adjusted_humidities,
        		y     = time_series_humidity_values,
        		name  = 'Humidity',
        		yaxis = 'y2'
    				)

	data = Data([temp, hum])

	layout = Layout(
					title  = "Temperature and humidity in Peter's lab",
				    xaxis  = XAxis(
				        type      = 'date',
				        autorange = True
				    ),
				    yaxis          = YAxis(
				    	title      = 'Celsius',
				        type       = 'linear',
				        autorange  = True
				    ),
				    yaxis2 = YAxis(
				    	title      = 'Percent',
				        type       = 'linear',
				        autorange  = True,
				        overlaying = 'y',
				        side       = 'right'
				    )

					)
	fig      = Figure(data = data, layout = layout)
	plot_url = py.plot(fig, filename = 'lab_temp_hum')

	return plot_url

def validate_date(d):
    try:
        datetime.datetime.strptime(d, '%Y-%m-%d %H:%M')
        return True
    except ValueError:
        return False

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
