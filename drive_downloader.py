import io
import json
import os
import shutil
import traceback
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

import constants

# Google Drive API setup
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
SERVICE_ACCOUNT_FILE = 'service_creds.json'
WHITELIST = os.path.join('data', 'whitelist.txt')
WL_FOLDERS = [
    "Archive",
    "Blacklisted Words - Profanity Filter--1qia8vhRegNAoizOz_rfzJzTCwMuXmnHN",
    "OUTDATED",
    "OLD DOCUMENTS"
]

if not os.path.isfile(WHITELIST):
    open(WHITELIST, 'w+').close()


def download_documents_from_folder(service, folder_id, folder_path=''):
    query = f"'{folder_id}' in parents"
    results = service.files().list(q=query, fields="nextPageToken, files(id, name, mimeType)").execute()
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
                # request = service.files().get_media(fileId=item_id)
                continue
            if item_type == 'application/vnd.google-apps.spreadsheet':
                print("Skipping spreadsheets")
                continue
            if item_type == 'application/vnd.google-apps.folder':
                item_path = item['name'].strip() + '--' + item_id
                print(f"item_path:", item_path)
                print("Its a folder. Going deeper.")
                download_documents_from_folder(service, item_id, folder_path=item_path)
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
            if os.path.isfile(item_path):
                print("File exists!")
                continue
            if any([item_path in wl for wl in wls]):
                print('Whitelisted File!')
                continue

            # Retrieve file metadata, including file size
            file_metadata = service.files().get(fileId=item_id, fields='size').execute()
            file_size = int(file_metadata.get('size', 0))
            # Define the export size limit (e.g., 50 MB for Google Docs)
            export_size_limit = 50 * 1024 * 1024
            # Check if the file size is within the export limit
            if file_size >= export_size_limit:
                print(f"Error: The file '{item_name}' is too large to be exported.")
                with open(WHITELIST, 'a+') as yeet:
                    yeet.write("\n" + item_path)
                continue

            # Export Google Docs file as PDF
            request = service.files().export_media(fileId=item_id, mimeType='application/pdf')
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
                print("File pdf export downloaded!")
        except HttpError as error:
            error_details = json.loads(error.content.decode('utf-8'))
            error_reason = error_details['error']['errors'][0]['reason']
            if error_reason == 'exportSizeLimitExceeded':
                print(f"Error: The file '{item_name}' is too large to be exported.")
                with open(WHITELIST, 'a+') as yeet:
                    yeet.write("\n" + item_path)
            else:
                print(f"Error: {error}")
        except:
            traceback.print_exc()
            with open(WHITELIST, 'a+') as yeet:
                yeet.write("\n" + item_path)


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
                for i in range(10):
                    if i < 2:
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
# data  = get_header_data('1-O92HWMo5m63awq44Qf7Dwedu6d0MTiA-B1w4hjm5l8')
# print(data)
# print()
#
#
#
# print()
# print(context[250:])
#
# exit()
def find_document_id(documentname, drivefolderid = constants.DESIGN_DOCUMENTS_DRIVE_FOLDER_ID):
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    service = build('drive', 'v3', credentials=credentials)

    def search_file(document_name):
        query = f"'1fFNdrhD5ZbkVTb1uX4-tWuDiU-T4odCS' in parents"
        # if folder_id:
        #     query += f" and '{folder_id}' in parents"

        results = []
        page_token = None
        while True:
            try:
                response = service.files().list(
                    q=query,
                    spaces='drive',
                    fields='nextPageToken, files(id, name, mimeType, parents)',
                    pageToken=page_token
                ).execute()
                results.extend(response.get('files', []))
                page_token = response.get('nextPageToken', None)
                if page_token is None:
                    break
            except HttpError as error:
                print(f'An error occurred: {error}')
                break
        return results

    def find_document_in_folder(folder_id, document_name):
        ids = []
        files = search_file(document_name)
        print(files)
        for file in files:
            ids.append((file['name'], file['id']))
            # if file['name'] == document_name:
            #     ids.append(file['id'])
        print(ids)
        if len(files) > 1:
            print("=========", document_name)
        largest_file = None
        largest_size = 0
        for id in ids:
            file_metadata = service.files().get(fileId=id, fields='size').execute()
            file_size = int(file_metadata.get('size', 0))
            if (not largest_file) or file_size > largest_size:
                largest_file = id
                largest_size = file_size

        return largest_file

    document_name = documentname

    document_id = find_document_in_folder(drivefolderid, document_name)
    if document_id:
        print(f'Document found: {document_name}, ID: {document_id}')
        return document_id
    else:
        print('Document not found in the specified folder.')
        raise Exception('Document not found in the specified folder.')



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
    find_document_id('yee')
    exit()
    get_header_data('1bIZNvIwTo2Dh2tZAXXsacHkuZPrRLCX1nQfpJ0s1_UE')
