from __future__ import print_function
import os.path as osp
import json
import os
import io
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseDownload

def mkdir(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
    
class Folder():
    def __init__(self, service):
        self.service=service

    def download(self, item=None, path="./"):
        if item == None:
            item = self.folder
        name = item['Name']
        ID = item["ID"]
        children = item["Next"]

        if len(children) != 0:
            # Get a folder, create the folder and parse the next level
            path = osp.join(path, name)
            mkdir(path)
            for child in children:
                self.download(item=child, path=path)
        else:
            # Get a file, download it
            filename = osp.join(path, name)

            request = self.service.files().get_media(fileId=ID)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                print ("{} Download {}.".format(filename, status.progress() * 100))

            # and write
            with open(filename, "wb") as fp:
                fp.write(fh.getbuffer())

            fh.close()

    def __str__(self):
        out = ""
        item = self.folder
        outStr=self._mStr(item=item, outStr="", offset="")
        return outStr

    def _mStr(self, item, outStr, offset):
        outStr += "{}{} {}\n".format(offset, item["Name"], item["ID"])
        for i in item["Next"]:
            #self.print(item=i, offset=offset+" ")
            outStr = self._mStr(item=i, outStr=outStr, offset=offset+" ")
        return outStr

    def saveFolder(self):
        with open("GDrive/folder.json", "w") as fp:
            json.dump(self.folder, fp, indent=4)

    def readFolder(self):
        """
        Read the folder structure from folder.json
        """
        if osp.isfile("GDrive/folder.json"):
            with open("GDrive/folder.json", "r") as fp:
                self.folder = json.load(fp)
            return True
        else:
            return False

    def parse(self, name, ID):
        self.folder = self._parse(name=name, ID=ID)

    def _parse(self, name, ID, offset=""):
        """
        Read the folder structure from the google drive.
        {
            name : name
            ID   : ID
            Naxt :
                [ 
                    {
                        name : name,
                        ID   : ID,
                        Next : [{...}, {...}, ...]
                    },
                    {
                        name : name,
                        ID   : ID,
                        Next : []
                    }
                ]
        }
        """
        # Get items
        results = self.service.files().list(q="\'" + ID + "\'" + " in parents",
                                    spaces="drive",
                                    fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])

        mini_folder = []
        for item in items:
            _name = item['name']
            _id = item['id']
            print ("{}Parse {:<20} {:<20}".format(offset, _name, _id))
            mini_folder.append(self._parse(name=_name, ID=_id, offset=offset+" "))
        return {"Name":name, "ID":ID, "Next":mini_folder}
        
