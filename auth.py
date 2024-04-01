import json
import os

import gspread as gs
import pandas as pd
from dotenv import load_dotenv

load_dotenv()


def load_credentials():
    credentials_json_str = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS_JSON')
    creds = json.loads(credentials_json_str)
    return creds


def get_google_sheet(sheet_id):
    creds = load_credentials()
    client = gs.service_account_from_dict(creds)
    worksheet = client.open_by_key(sheet_id).sheet1
    return worksheet


def get_data_from_sheet(sheet):
    start_column = 'A'
    end_column = 'L'

    range_str = f"{start_column}:{end_column}"
    data = sheet.get(range_str)

    df = pd.DataFrame(data[1:], columns=data[0], index=None)
    return df
