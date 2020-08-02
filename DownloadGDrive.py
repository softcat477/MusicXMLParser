from __future__ import print_function

import io
import sys
import argparse
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseDownload

from GDrive.Folder import Folder

parser = argparse.ArgumentParser()
parser.add_argument("--ID", type=str, required=True)
args = parser.parse_args()
ID = args.ID

"""
Download credentials.json from https://developers.google.com/drive/api/v3/quickstart/python
"""

p_base = "GDrive"

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']

def getCreds():
    """
    from https://developers.google.com/drive/api/v3/quickstart/python

    Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(os.path.join(p_base, 'token.pickle')):
        with open(os.path.join(p_base, 'token.pickle'), 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                os.path.join(p_base, 'credentials.json'), SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(os.path.join(p_base, 'token.pickle'), 'wb') as token:
            pickle.dump(creds, token)
    return creds



def main():
    # 1. Get credits
    creds = getCreds()
    # 2. Build services
    service = build('drive', 'v3', credentials=creds)
    # 3. Parse files
    # TODO : Past the ID of the folder you want to download.
    folder = Folder(service)
    if folder.readFolder() == False:
        print ("Read folder from the google drive")
        # Read the folder structure from google drive
        folder.parse(name="Score", ID=ID)
        folder.saveFolder()
    else:
        # Read the folder structure from json
        print ("Read from folder")
        print(folder)
    # 4. Download
    folder.download()

if __name__ == '__main__':
    try:
        main()
    except FileNotFoundError as e:
        print ("Download credentials.json from https://developers.google.com/drive/api/v3/quickstart/python")
        raise e
    except Exception as e:
        raise e
