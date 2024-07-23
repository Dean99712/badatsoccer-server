import io
import json
import os

import gspread as gs
import pandas as pd
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

import azure_services as azs

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


def get_data_from_sheet(sheet, start_column, end_column):

    range_str = f"{start_column}:{end_column}"
    data = sheet.get(range_str)

    df = pd.DataFrame(data[1:], columns=data[0], index=None)
    return df


def create_drive_service():
    creds_json = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS_JSON')
    creds = service_account.Credentials.from_service_account_info(
        json.loads(creds_json),
        scopes=['https://www.googleapis.com/auth/drive']
    )
    return build('drive', 'v3', credentials=creds)


def correct_extension(filename):
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.ico', 'HEIC']
    filename_lower = filename.lower()
    if any(filename_lower.endswith(ext) for ext in image_extensions):
        return filename
    else:
        return f"{filename}.jpg"


def transfer_files(folder_id, container_name):
    drive_service = create_drive_service()
    blob_service = azs.create_blob_service()
    container_client = azs.container_exists(blob_service, container_name)

    results = drive_service.files().list(
        q=f"'{folder_id}' in parents and trashed=false",
        fields="files(id, name)").execute()
    items = results.get('files', [])

    if not items:
        print('No files found.')
    else:
        for item in items:
            correct_name = correct_extension(item['name'])
            if not azs.blob_exists(container_client, correct_name):
                request = drive_service.files().get_media(fileId=item['id'])
                fh = io.BytesIO()
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                fh.seek(0)

                blob_client = container_client.get_blob_client(correct_name)
                blob_client.upload_blob(fh, blob_type="BlockBlob", overwrite=True)
                print(f'Uploaded {correct_name} to Azure Blob Storage.')
            else:
                print(f'File {correct_name} already exists. Not uploaded.')
