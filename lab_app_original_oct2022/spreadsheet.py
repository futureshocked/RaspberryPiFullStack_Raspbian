import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pprint

scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('raspberry-pi-full-stack-1-f37054328cf5.json', scope)
client = gspread.authorize(creds)

sheet = client.open('Temperature and Humidity').sheet1

pp = pprint.PrettyPrinter()

records = sheet.get_all_records()
pp.pprint(records)
