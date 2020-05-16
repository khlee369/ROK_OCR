import os
import glob
import matplotlib.pyplot as plt

from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from googleapiclient.http import MediaFileUpload
from googleapiclient.http import MediaIoBaseDownload

import io

token_dict = {
    'SCOPES': ['https://www.googleapis.com/auth/drive'],
    'CLIENT_SECRET': 'upload_test_cred.json'
}

class GHelper:
    def __init__(self, SCOPES=token_dict['SCOPES'], CLIENT_SECRET=token_dict['CLIENT_SECRET']):
        self.SCOPES = SCOPES
        self.CLIENT_SECRET = CLIENT_SECRET
        self.service = self.get_service(self.SCOPES, self.CLIENT_SECRET)


    def get_service(self, SCOPES=token_dict['SCOPES'], CLIENT_SECRET=token_dict['CLIENT_SECRET']):
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    CLIENT_SECRET, SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        service = build('drive', 'v3', credentials=creds)

        return service

    def create_folder(self, folder_name, verbose=False):
        file_metadata = {
            'name': folder_name,  # 폴더 명
            'mimeType': 'application/vnd.google-apps.folder'
        }
        file = self.service.files().create(body=file_metadata, fields='id').execute()  # 폴더 실행문
        if verbose:
            print('Folder ID: %s' % file.get('id'))

        return file.get('id')

    def delete(self, file_id):
        self.service.files().delete(fileId=file_id).execute()

    def upload(self, file_name, file_path='./', folder_id=[], as_docs=False, verbose=False):
        # parents 는 리스트 형태로 받아야함
        if isinstance(folder_id, str):
            folder_id = [folder_id]
        file_metadata = {
            'name' : file_name,
            'parents' : folder_id
        }
        if as_docs:
            file_metadata['mimeType'] = 'application/vnd.google-apps.document'
        media = MediaFileUpload(file_path + file_name, resumable=True)
        file = self.service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        if verbose:
            print('File ID: %s' % file.get('id'))
        
        return file.get('id')


    def download(self, file_id, file_path='./', verbose=False):
        file_name = self.service.files().get(fileId=file_id).execute()['name']
        mimeType = self.service.files().get(fileId=file_id).execute()['mimeType']
        request = self.service.files().get_media(fileId=file_id)
        if mimeType == 'application/vnd.google-apps.document':
            request = self.service.files().export_media(fileId=file_id, mimeType='text/plain')
            file_name += '.txt'
        fh = io.FileIO(file_path + file_name, 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            if verbose:
                print(file_name, "Download %d%%." % int(status.progress() * 100))
        fh.close()


    def print_file_metadata(self, file_id):
        file = self.service.files().get(fileId=file_id).execute()
        print("name : {}".format(file['name']))
        print("MIME Type : {}".format(file['mimeType']))



def preprocess_pngs(data_path, save_path, verbose=False):
    png_list = glob.glob(data_path + '*.png')
    thr = 200
    try:
        os.mkdir(save_path)
    except FileExistsError:
        pass
    for file_path in png_list:
        img = cv2.imread(file_path,0)
        img = img[230:850,335:1400]
        ret,thresh2 = cv2.threshold(img,thr,255,cv2.THRESH_BINARY_INV)
        png_name = file_path.split('\\')[-1]
        save_name = save_path + png_name[:-4] + "_BINARY_INV.png"
        if verbose:
            print("FROM : {}".format(file_path))
            print("TO : {}".format(save_name))
        cv2.imwrite(save_name, thresh2)

def seperate_rows(data_path, save_path, verbose=False):
    png_list = glob.glob(data_path + '*.png')
    try:
        os.mkdir(save_path)
    except FileExistsError:
        pass
    for file_path in png_list:
        img = cv2.imread(file_path,0)
        height, width = img.shape
        
        # height sep
        for x in range(1,6):
            line_idx = int(x * height/6)
            img[line_idx] = [1]*width
        
        png_name = file_path.split('\\')[-1]
        save_name = save_path + png_name[:-4] + "_sep.png"
        if verbose:
            print("FROM : {}".format(file_path))
            print("TO : {}".format(save_name))
        cv2.imwrite(save_name_name, img)

def seperate_pngs(data_path, save_path, verbose=False):
    png_list = glob.glob(data_path + '*.png')
    try:
        os.mkdir(save_path)
    except FileExistsError:
        pass
    for file_path in png_list:
        img = cv2.imread(file_path,0)
        height, width = img.shape
        
        # height sep
        for x in range(1,6):
            line_idx = int(x * height/6)
            img[line_idx] = [1]*width
            
        # width sep
        img_name = img[:,:width//2]
        img_power = img[:,width//2:]
        
        png_name = file_path.split('\\')[-1]
        save_name_name = save_path + png_name[:-4] + "_name.png"
        save_name_power= save_path + png_name[:-4] + "_power.png"
        if verbose:
            print("FROM : {}".format(file_path))
            print("TO : {}".format(save_name_name))
            print("TO : {}".format(save_name_power))
        cv2.imwrite(save_name_name, img_name)
        cv2.imwrite(save_name_power, img_power)


def seperate1x1(data_path, save_path, verbose=False):
    png_list = glob.glob(data_path + '*.png')
    try:
        os.mkdir(save_path)
    except FileExistsError:
        pass
    id_num = 0
    for file_path in png_list:
        img = cv2.imread(file_path, 0)
        height, width = img.shape

        png_name = file_path.split('\\')[-1]
        save_name = save_path + png_name[:-4]

        # height sep
        for x in range(6):
            fidx = int(x * height/6)
            eidx = int((x+1) * height/6)
            plt.imshow(img[fidx:eidx, :], 'gray')

            if verbose:
                print("FROM : {}".format(file_path))
                print("TO : {}".format(save_name + "_{}.png".format(id_num)))
            cv2.imwrite(save_name + "_{}.png".format(id_num), img[fidx:eidx, :])
            id_num += 1
