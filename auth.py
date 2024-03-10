import gspread as gs
import pandas as pd


def get_google_sheet(sheet_id):
    client = gs.service_account(filename='credentials.json')
    worksheet = client.open_by_key(sheet_id).sheet1
    return worksheet


def get_data_from_sheet(sheet):
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        return df
