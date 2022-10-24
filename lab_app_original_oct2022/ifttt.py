import requests

def email_alert(first, second, third):
    report = {}
    report["value1"] = first
    report["value2"] = second
    report["value3"] = third
    requests.post("https://maker.ifttt.com/trigger/RPiFS_report/with/key/?????", data=report)    

print("Choose your first string.")
a = "one"
print("Choose your second string.")
b = "two"
print("Choose your third string.")
c = "three"
email_alert(a, b, c)
