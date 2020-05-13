from oauth2client.service_account import ServiceAccountCredentials
import gspread
import pprint
import os
from os import environ

"""
check this, in case you are not 
familiar with google spreadsheets

https://github.com/burnash/gspread
"""

# return one of two spreadsheets
def spreadsheet(worksheet: int) -> object:
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    path = 'Vargan-API.json'
    full_path = os.path.abspath(os.path.expanduser(
            os.path.expandvars(path)))
    creds = ServiceAccountCredentials.from_json_keyfile_name(full_path, scope)
    client = gspread.authorize(creds)

    table = "19fwEUoAxep9WQb5ehIfKK3_aTukahfohf8CHMhmsgag"
    sheet = client.open_by_key(table)
    sheet = sheet.get_worksheet(worksheet)
    return sheet


# update after_chat feedback
def after_chat(reason: str, mood: str,) -> None:
    sheet = spreadsheet(0)
    feedback = sheet.get_all_values()
    feedback_len = len(feedback)+1
    new_feedback = [[reason, mood]]
    sheet.update(f"A{feedback_len}", new_feedback)

# update payment_refused feedback
def payment_refused(reason: str) -> None:
    sheet = spreadsheet(1)
    feedback = sheet.get_all_values()
    feedback_len = len(feedback)+1
    new_feedback = [[reason]]
    sheet.update(f"A{feedback_len}", new_feedback)
    


if __name__ == "__main__":
    print(after_chat("teest", "test"))
    print(payment_refused("teest"))