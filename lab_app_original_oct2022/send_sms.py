import os
from twilio.rest import Client

account_sid = os.environ["TWILIO_ACCOUNT_SID"]
auth_token = os.environ["TWILIO_AUTH_TOKEN"]
my_twilio_phone_number = os.environ["TWILIO_PHONE_NUMBER"]
receive_phone_number = os.environ["MY_PHONE_NUMBER"]
test_text = "Hello from my Raspberry Pi!"
client = Client(account_sid, auth_token)
client.messages.create(to = receive_phone_number,
                       from_ = my_twilio_phone_number,
                       body = test_text)

