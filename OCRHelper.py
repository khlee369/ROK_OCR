import numpy as np
import matplotlib.pyplot as plt
import glob
import cv2
import pandas as pd

from configs import *

import pytesseract
# tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
pytesseract.pytesseract.tesseract_cmd = tesseract_path

# profile_path = './Screenshots/'
# profile_list = glob.glob(profile_path + '*.png')

class Player():
    def __init__(self, ID, power, kill):
        self.ID = ID
        self.power = power
        self.kill = kill
        self.name = None
        self.path = None
    
    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

def bin_inv(img, thr=140, show=False):
    ret,thresh2 = cv2.threshold(img,thr,255,cv2.THRESH_BINARY_INV)
    ocr_result = pytesseract.image_to_string(thresh2)
    if show:
        plt.imshow(thresh2, 'gray')
        plt.show()
        print(ocr_result)
    return thresh2, ocr_result

def str2num(strnum):
    # remove ',' and '.'
    result = strnum.replace(',', '').replace('.', '')
    if result.isdigit():
        return int(result)
    else:
        return 0

def load_id2name(file_path, id2name=None):
    # load xlsx file
    # xlsx format ex) ID : [1, 2, 3], name : ['a', 'b', 'c']
    # if you want to expand id2name with new xlsx,
    # then give argument like id2name=load_id2name('id2name.xlsx')

    df_id2name = pd.read_excel(file_path)
    print('Loaded {} as id2name'.format(file_path))
    if id2name==None:
        id2name = dict([])

    for i in range(len(df_id2name)):
        row = df_id2name.loc[i]
        if type(row['name']) is not str:
            id2name[row['ID']] = ''
        else:
            id2name[row['ID']] = row['name']
    
    return id2name

def ocr_profiles(profile_list=profile_list, id2name=load_id2name('id2name.xlsx')):
    Players = dict([])
    L = len(profile_list)
    for i, fn in enumerate(profile_list):
        print('{}/{}'.format(i+1,L))
        img = cv2.imread(fn,0)

        IDp = crop_dict['ID']
        powerp = crop_dict['power']
        killp = crop_dict['kill']
        
        img_ID = img[IDp[0]:IDp[1], IDp[2]:IDp[3]]
        img_power = img[powerp[0]:powerp[1], powerp[2]:powerp[3]]
        img_kill = img[killp[0]:killp[1], killp[2]:killp[3]]
        
        _, str_ID = bin_inv(img_ID)
        _, str_power = bin_inv(img_power)
        _, str_kill = bin_inv(img_kill)
        
        ID, power, kill = str2num(str_ID), str2num(str_power), str2num(str_kill)
        
        Players[ID] = Player(ID,power,kill)        
        Players[ID].path = fn.split('\\')[-1]
        
        try:
            Players[ID].name = id2name[ID]
        except KeyError:
            print('KeyError!! : checkt {}'.format(Players[ID].path))
            Players[ID].name = ''
    return Players

def Players2df(Players):
    df = {
    'ID' : [],
    'name' : [],
    'power' : [],
    'kill' : [],
    'path' : []
    }
    df = pd.DataFrame(df, dtype=int)

    L = len(Players)
    for ID, p in Players.items():
        df = df.append({
            'ID' : ID,
            'name' : p.name,
            'power' : p.power,
            'kill' : p.kill,
            'path' : p.path
        }, ignore_index=True)

    return df

def save_id2name(id2name, filename='id2name_new.xlsx'):
    df_xlsx = {
        'ID' : [],
        'name' : [],
    }
    df_xlsx = pd.DataFrame(df_xlsx, dtype=int)

    for ID, name in id2name.items():
        df_xlsx = df_xlsx.append({
            'ID' : ID,
            'name' : name
        }, ignore_index=True)
    
    df_xlsx.to_excel(filename, index=False)    
    print('Save id2name as {}'.format(filename))
    return df_xlsx