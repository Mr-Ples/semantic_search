import io
import json
import os
import shutil
import traceback

import requests
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

import constants

# Google Drive API setup
DOC_SERVICE = None
DRIVE_SERVICE = None
SCOPES = [
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/documents'
]
SERVICE_ACCOUNT_FILE = 'service_creds.json'
WHITELIST = os.path.join('data', 'whitelist.txt')
WL_FOLDERS = [
    "Archive",
    "Blacklisted Words - Profanity Filter--1qia8vhRegNAoizOz_rfzJzTCwMuXmnHN",
    "OUTDATED",
    "OLD DOCUMENTS",
    "comment bot ids"
]
TOO_LARGE = []

if not os.path.isfile(WHITELIST):
    open(WHITELIST, 'w+').close()


def get_doc_service():
    global DOC_SERVICE
    if DOC_SERVICE:
        return DOC_SERVICE
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    DOC_SERVICE = build("docs", "v1", credentials=credentials)
    return DOC_SERVICE


def get_drive_service():
    global DRIVE_SERVICE
    if DRIVE_SERVICE:
        return DRIVE_SERVICE
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    DRIVE_SERVICE = build("drive", "v3", credentials=credentials)
    return DRIVE_SERVICE


def get_file_name(peth):
    current_path = ''
    for index, part in enumerate(peth.split('/')):
        if not index:
            current_path = os.path.join(current_path, part)
            continue
        if os.path.exists(os.path.join(current_path, part)) and '.pdf' not in part:
            current_path = os.path.join(current_path, part)
            continue
        else:
            return peth.replace(current_path + '/', '').replace('.pdf', '')


def get_export_links(file_id):
    """Get the export links for a Google Drive file.
    Args:
        file_id: ID of the Google Drive file.
    Returns:
        A dictionary containing the export links.
    """
    file = get_drive_service().files().get(fileId=file_id, fields='exportLinks').execute()
    return file.get('exportLinks')


def download_exported_file(export_link, file_name):
    """Download an exported file using its export link.
    Args:
        export_link: The export link of the file to download.
        file_name: The name to save the downloaded file as.
        credentials: The credentials object to authenticate the request.
    """

    response = requests.get(export_link, headers={}, stream=True)

    if response.status_code == 200:
        with open(file_name, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"Downloaded file: {file_name}")
    else:
        print(f"Failed to download file: {response.status_code}")


def export_doc(docid, outputpath, itemname, indx=0):
    indx += 1
    try:
        request = get_drive_service().files().export_media(fileId=docid, mimeType='application/pdf')
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request, chunksize=10 * 1024 * 1024)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print("Download %d%%." % int(status.progress() * 100))
        fh.seek(0)
        print(outputpath)
        with open(outputpath, 'wb+') as f:
            shutil.copyfileobj(fh, f)
            print("File pdf export downloaded!")
    except HttpError as error:
        error_details = json.loads(error.content.decode('utf-8'))
        error_reason = error_details['error']['errors'][0]['reason']
        if error_reason == 'exportSizeLimitExceeded':
            print(f"Error: The file '{itemname}' is too large to be exported.")
            with open(WHITELIST, 'a+') as yeet:
                yeet.write("\n" + itemname)
            export_links = get_export_links(docid)
            print(export_links)
            text_export_link = export_links["text/plain"]
            download_exported_file(text_export_link, outputpath.replace('.pdf', '.txt'))


def download_documents_from_folder(folder_id, folder_path=''):
    while True:
        query = f"'{folder_id}' in parents"
        results = get_drive_service().files().list(q=query, fields="nextPageToken, files(id, name, mimeType)").execute()
        items = results.get('files', [])
        folder_path = './data/' + "/".join([part.strip() for part in folder_path.split('/')])
        print("folder path:", folder_path)
        os.makedirs(folder_path, exist_ok=True)
        print(items)

        if not items:
            print('No files found.')
            return

        for item in items:
            try:
                print()
                with open(WHITELIST, 'r') as ye:
                    wls = [line.strip() for line in ye.readlines()]
                # print('wls:', wls)
                item_id = item['id']
                item_type = item['mimeType']
                if not item_type.startswith('application/vnd.google-apps'):
                    print("File not a doc!")
                    # # Download the file directly
                    # request = get_drive_service().files().get_media(fileId=item_id)
                    continue
                if item_type == 'application/vnd.google-apps.spreadsheet':
                    print("Skipping spreadsheets")
                    continue
                if item_type == 'application/vnd.google-apps.folder':
                    item_path = item['name'].strip() + '--' + item_id
                    print(f"item_path:", item_path)
                    print("Its a folder. Going deeper.")
                    download_documents_from_folder(item_id, folder_path=item_path)
                    continue

                url_type = 'document' if item_type == 'application/vnd.google-apps.document' else 'spreadsheets'
                item_name = item['name'].strip() + '--' + item_id + '--' + url_type + '.pdf'
                print("url_type:", url_type)
                print("item_type:", item_type)
                print("item_name:", item_name)
                item_path = os.path.join(folder_path, item_name)
                print("item_path:", item_path)
                if any([any([wl_folder.lower() in elem.strip().lower() for elem in item_path.split('/')]) for wl_folder in WL_FOLDERS]):
                    print('Whitelisted folder')
                    continue
                if os.path.isfile(item_path) or os.path.isfile(item_path.replace('.pdf', '.txt')):
                    print("File exists!")
                    continue
                if any([item_path in wl for wl in wls]):
                    print('Whitelisted File!')
                    continue

                print(folder_path)
                export_doc(item_id, item_path, item_name)
            except:
                traceback.print_exc()
                with open(WHITELIST, 'a+') as yeet:
                    yeet.write("\n" + item_path)

        page_token = results.get('nextPageToken', None)
        if page_token is None:
            break


def get_header_data(doc_id: str):
    print("Gettting header data")
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    service = build("docs", "v1", credentials=credentials)
    doc = get_drive_service().documents().get(documentId=doc_id).execute()
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
    download_documents_from_folder(constants.COLLECTION_DRIVE_FOLDER_ID, './data')


if __name__ == "__main__":
    main()
    print()
    print(TOO_LARGE)
    # get_header_data('1bIZNvIwTo2Dh2tZAXXsacHkuZPrRLCX1nQfpJ0s1_UE')
