import json
import os

import gspread as gs
import pandas as pd
from dotenv import load_dotenv
from google.oauth2 import service_account

load_dotenv()


def load_credentials():

    google_acc = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')

    if google_acc is None:
        raise ValueError(
            "Failed to find 'GOOGLE_APPLICATION_CREDENTIALS_JSON' environment variable. Make sure it is set in Azure Web App Configuration.")

    credentials_dict = json.loads(google_acc)
    print(credentials_dict)
    credentials = service_account.Credentials.from_service_account_info(credentials_dict)
    return credentials


def get_google_sheet(sheet_id):
    creds = load_credentials()
    client = gs.service_account(creds)
    worksheet = client.open_by_key(sheet_id).sheet1
    return worksheet


def get_data_from_sheet(sheet):
    start_column = 'A'
    end_column = 'L'

    range_str = f"{start_column}:{end_column}"
    data = sheet.get(range_str)

    df = pd.DataFrame(data[1:], columns=data[0], index=None)
    return df
