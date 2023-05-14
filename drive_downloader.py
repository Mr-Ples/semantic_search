import io
import json
import os
import shutil
import traceback

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

import constants

# Google Drive API setup
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
SERVICE_ACCOUNT_FILE = 'service_creds.json'
WHITELIST = os.path.join('data', 'whitelist.txt')
WL_FOLDERS = ["Archive"]

if not os.path.isfile(WHITELIST):
    open(WHITELIST, 'w+').close()


def download_documents_from_folder(service, folder_id, folder_path=''):
    query = f"'{folder_id}' in parents"
    results = service.files().list(q=query, fields="nextPageToken, files(id, name, mimeType)").execute()
    items = results.get('files', [])
    folder_path = "/".join([part.strip() for part in folder_path.split('/')])
    os.makedirs(folder_path, exist_ok=True)

    if not items:
        print('No files found.')
    else:
        for item in items:
            try:
                print()
                with open(WHITELIST, 'r') as ye:
                    wl = [line.strip() for line in ye.readlines()]
                item_id = item['id']
                print(folder_path)
                item_name = item['name'].strip() + '--' + item_id
                item_type = item['mimeType']
                print(item_type)
                item_path = os.path.join(folder_path, item_name)

                print(item_path)
                if any([wl_folder in folder_path.split('/') for wl_folder in WL_FOLDERS]):
                    print('Whitelisted')
                    continue
                if os.path.isfile(item_path + '.pdf'):
                    continue
                print(wl)
                if item_path + '.pdf' in wl:
                    continue

                # Retrieve file metadata, including file size
                file_metadata = service.files().get(fileId=item_id, fields='size').execute()
                file_size = int(file_metadata.get('size', 0))

                if item_type == 'application/vnd.google-apps.folder':
                    print(f"Folder: {item_path}")
                    return download_documents_from_folder(service, item_id, folder_path=item_path)

                # Check if the file is a Google Docs file
                if not item_type.startswith('application/vnd.google-apps'):
                    continue
                print(f"File: {item_path} ({item_type})")
                # Define the export size limit (e.g., 50 MB for Google Docs)
                export_size_limit = 50 * 1024 * 1024

                # Check if the file size is within the export limit
                if file_size >= export_size_limit:
                    print(f"Error: The file '{item_name}' is too large to be exported.")
                    with open(WHITELIST, 'a+') as yeet:
                        yeet.write("\n" + item_path.replace(".pdf", '') + '.pdf')
                    continue

                # Export Google Docs file as PDF
                request = service.files().export_media(fileId=item_id, mimeType='application/pdf')
                if item_type == 'application/vnd.google-apps.spreadsheet':
                    continue
                    item_path = os.path.splitext(item_path)[0] + '--spreadsheets' + '.pdf'
                else:
                    item_path = os.path.splitext(item_path)[0] + '--document' + '.pdf'
                # # Download the file directly
                # request = service.files().get_media(fileId=item_id)
                fh = io.BytesIO()
                downloader = MediaIoBaseDownload(fh, request, chunksize=10 * 1024 * 1024)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
                    print("Download %d%%." % int(status.progress() * 100))

                fh.seek(0)
                print(folder_path)
                print(item_path)
                with open(item_path, 'wb+') as f:
                    shutil.copyfileobj(fh, f)

                    print("File downloaded")
            except HttpError as error:
                error_details = json.loads(error.content.decode('utf-8'))
                error_reason = error_details['error']['errors'][0]['reason']
                if error_reason == 'exportSizeLimitExceeded':
                    print(f"Error: The file '{item_name}' is too large to be exported.")
                    with open(WHITELIST, 'a+') as yeet:
                        yeet.write("\n" + item_path.replace(".pdf", '') + '.pdf')
                else:
                    print(f"Error: {error}")
            except:
                traceback.print_exc()
                with open(WHITELIST, 'a+') as yeet:
                    yeet.write("\n" + item_path.replace(".pdf", '') + '.pdf')


def get_header_data(doc_id: str):
    print("Gettting header data")
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    service = build("docs", "v1", credentials=credentials)
    doc = service.documents().get(documentId=doc_id).execute()
    # Extract header data
    headers = {}
    maxs = doc['body']['content'][-1]['endIndex']

    for index, element in enumerate(doc['body']['content']):
        # {'startIndex': 98633, 'endIndex': 98647, 'paragraph': {'elements': [{'startIndex': 98633, 'endIndex': 98647, 'textRun': {'content': 'Mobile Navbar\n', 'textStyle': {}}}], 'paragraphStyle': {'headingId': 'h.il1fg9h8va2m', 'namedStyleType': 'HEADING_3', 'direction': 'LEFT_TO_RIGHT', 'pageBreakBefore': False}}}
        if 'paragraph' in element:
            paragraph = element['paragraph']
            # page_estimate = paragraph['elements'][0]['startIndex'] / maxs * 104

            # {'elements': [{'startIndex': 98633, 'endIndex': 98647, 'textRun': {'content': 'Mobile Navbar\n', 'textStyle': {}}}], 'paragraphStyle': {'headingId': 'h.il1fg9h8va2m', 'namedStyleType': 'HEADING_3', 'direction': 'LEFT_TO_RIGHT', 'pageBreakBefore': False}}
            try:
                url = 'https://docs.google.com/document/d/' + doc_id + '/edit#heading=' + paragraph['paragraphStyle']['headingId']
                if paragraph['elements'][0]['textRun']['content'] == "\n":
                    continue
                context = "".join([elem['textRun']['content'] for elem in doc['body']['content'][index + 1]['paragraph']['elements']]).strip()
                if not context:
                    continue
                if context == '\n':
                    continue
                context = ""
                for i in range(2):
                    context += "***"
                    context += "".join([elem['textRun']['content'] for elem in doc['body']['content'][index + i]['paragraph']['elements']]).strip()
                if doc['body']['content'][index + 1]['paragraph']['elements'][0]['textRun']['textStyle']:
                    continue
                header_name = "".join([elem['textRun']['content'] for elem in paragraph['elements']]).strip()
                headers[url] = {'name': header_name, 'context': context}
                # # https://docs.google.com/document/d/1bIZNvIwTo2Dh2tZAXXsacHkuZPrRLCX1nQfpJ0s1_UE/edit#heading=h.tec6ttmm7snv {'content': 'Mobile Bundle Buy Page\n', 'context': 'For the Mobile-version of the Bundle Buy-Page, we have a slightly different layout (see '}
                # print(url, {'name': header_name, 'context': context, 'page': page_estimate})
                # print()
            except:
                pass
    return headers


def main():
    print()
    print('Getting documents from drive')
    # Download documents
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    service = build('drive', 'v3', credentials=credentials)
    download_documents_from_folder(service, constants.COLLECTION_DRIVE_FOLDER_ID, './data')


if __name__ == "__main__":
    # main()
    get_header_data('1bIZNvIwTo2Dh2tZAXXsacHkuZPrRLCX1nQfpJ0s1_UE')
