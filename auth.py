import gspread as gs
import pandas as pd


def get_google_sheet(sheet_id):
    client = gs.service_account(filename='credentials.json')
    worksheet = client.open_by_key(sheet_id).sheet1
    return worksheet


def get_data_from_sheet(sheet):
    start_column = 'A'
    end_column = 'L'

    range_str = f"{start_column}:{end_column}"
    data = sheet.get(range_str)

    df = pd.DataFrame(data[1:], columns=data[0], index=None)
    return df
