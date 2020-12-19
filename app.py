from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse
from datetime import date
import config

#spreadsheet
import gspread
from oauth2client.service_account import ServiceAccountCredentials

ALEX = config.ALEX
DAVID = config.DAVID
JOSH = config.JOSH

names_dict = config.names_dict

AMOUNT = 1
DESCRIPTION = 2
NOTES = 3



def get_date():
    today = date.today()
    # dd/mm/YY
    d = today.strftime("%m/%d/%Y")
    return d

def get_name(number):
    return (names_dict[number])

def break_message_down(input):
    input_processed = input.split(";", 4)

    for item in input_processed:
        item = item.lower()
        item = item.strip()

    return input_processed

def send_sheet_data(name, data):
    #setting up spreadsheet
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name("client_secret_apartment.json", scope)
    client = gspread.authorize(credentials)
    gc = gspread.authorize(credentials)

    sh = gc.open('Apartment Expenses')

    Josh_expenses = sh.get_worksheet(1)
    David_expenses = sh.get_worksheet(2)
    Alex_expenses = sh.get_worksheet(3)

    if (name == "Josh"):
        sheet = Josh_expenses
    if (name == "David"):
        sheet = David_expenses
    if (name == "Alex"):
        sheet = Alex_expenses

    date = get_date()
    insertRow = [data[AMOUNT], date, data[DESCRIPTION], data[NOTES]]

    sheet.insert_row(insertRow, 4)



def get_instructions():
    instructions = "To send purchase data, text: 1) the word \'Purchase\', 2) the amount, 3)The description of your purchase, and 4) Any additional notes.  Note: All parts must be separated by a semicolon (;)."
    return instructions


app = Flask(__name__)

# Your Account Sid and Auth Token from twilio.com/console
# DANGER! This is insecure. See http://twil.io/secure
account_sid = config.account_sid
auth_token = config.auth_token

@app.route("/sms", methods=['GET', 'POST'])
def sms_reply():
    
    resp = MessagingResponse()

    number = request.form['From']
    message_body = request.form['Body']

    message_body = message_body.lower()

    info = break_message_down(message_body)

    if ("instructions" in message_body):
        response = get_instructions()
    if ("purchase" in info):
        send_sheet_data(get_name(number), info)
        response = "Thanks for the response"

    resp.message(response)


    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)
