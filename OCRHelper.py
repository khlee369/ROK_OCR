import numpy as np
import matplotlib.pyplot as plt
import glob
import cv2
import pandas as pd
import datetime

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
        # detail
        self.kill_4T = -2
        self.kill_5T = -2
        self.death = -2
        self.gathering = -2
        self.assist = -2
    
    def __repr__(self):
        return self.name

    def __str__(self):
        name = "name : {}\n".format(self.name)
        power = "power : {}\n".format(self.power)
        kill = "kill : {}\n".format(self.kill)
        kill_4T = "kill_4T : {}\n".format(self.kill_4T)
        kill_5T = "kill_5T : {}\n".format(self.kill_5T)
        death = "death : {}\n".format(self.death)
        gathering = "gathering : {}\n".format(self.gathering)
        assist = "assist : {}\n".format(self.assist)
        output = name + power + kill + kill_4T + kill_5T + death + gathering + assist
        return output

    def __sub__(self, other):
        P = Player(self.ID, self.power, self.kill)
        P.name = self.name
        P.power = self.power - other.power
        P.kill = self.kill - other.kill
        P.kill_4T = self.kill_4T - other.kill_4T
        P.kill_5T = self.kill_5T - other.kill_5T
        P.death = self.death - other.death
        return P

def img_ocr(img, thr=145, inv=True):
    if inv:
        ret,thresh2 = cv2.threshold(img,thr,255,cv2.THRESH_BINARY_INV)
    elif not inv:
        ret,thresh2 = cv2.threshold(img,thr,255,cv2.THRESH_BINARY)
    ocr_result = pytesseract.image_to_string(thresh2)
    str_result = ocr_result.replace(',', '').replace('.', '').replace(' ','').strip()
    if str_result.isdigit():
        result = int(str_result)
    else:
        result = 0
    return result

def bin_inv(img, thr=145, show=False, inv=True):
    if inv:
        ret,thresh2 = cv2.threshold(img,thr,255,cv2.THRESH_BINARY_INV)
    elif not inv:
        ret,thresh2 = cv2.threshold(img,thr,255,cv2.THRESH_BINARY)
    # tesseract configuration, numbers only
    # config가 오히려 에러를 발견하기 힘들게 함
    # config = ''
    # config = '-c tessedit_char_whitelist=0123456789'
    ocr_result = pytesseract.image_to_string(thresh2)
    str_result = ocr_result.replace(',', '').replace('.', '').replace(' ','').strip()
    # 숫자가 0만 있는경우 np.mean 값이 255에 가까움
    if not str_result.isdigit() and np.mean(thresh2) > 248:
        ocr_result = '0'

    elif not str_result.isdigit():
        for offset in [-20, -10, 10, 20]:
            tmp_r = img_ocr(img, thr+offset, inv)
            if tmp_r:
                ocr_result = str(tmp_r)
                break

    if show:
        plt.imshow(thresh2, 'gray')
        plt.show()
        print(ocr_result)

    return thresh2, ocr_result

def str2num(strnum):
    # remove ',' and '.'
    result = strnum.replace(',', '').replace('.', '').replace(' ','').strip()
    if result.isdigit():
        return int(result)
    else:
        return -1

def load_id2name(file_path, id2name=None):
    # load xlsx file
    # xlsx format ex) ID : [1, 2, 3], name : ['a', 'b', 'c']
    # if you want to expand id2name with new xlsx,
    # then give argument like id2name=load_id2name('id2name.xlsx')

    try:
        df_id2name = pd.read_excel(file_path)
        print('Loaded {} as id2name'.format(file_path))
    except FileNotFoundError:
        print('No such file or directory {}'.format(file_path))
        print('Function will return empty dictionary')
        return dict([])
        
    if id2name==None:
        id2name = dict([])

    for i in range(len(df_id2name)):
        row = df_id2name.loc[i]
        if type(row['name']) is not str:
            id2name[row['ID']] = ''
        else:
            id2name[row['ID']] = row['name']
    
    return id2name

def ocr_profiles(profile_list, id2name=load_id2name('id2name.xlsx')):
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
        _, str_power = bin_inv(img_power, thr=150)
        _, str_kill = bin_inv(img_kill, thr=150)
        
        ID, power, kill = str2num(str_ID), str2num(str_power), str2num(str_kill)
        
        Players[ID] = Player(ID,power,kill)        
        Players[ID].path = fn.split('\\')[-1]
        
        try:
            Players[ID].name = id2name[ID]
        except KeyError:
            print('KeyError!! : checkt {}'.format(Players[ID].path))
            Players[ID].name = ''
    return Players

def ocr_profiles_detail(profile_list, id2name=load_id2name('id2name.xlsx')):
    Players = dict([])
    L = len(profile_list)
    for i in range(0, L, 2):
        print('{}/{} : profile processing'.format(i+1,L))
        fn = profile_list[i]
        fn_detail = profile_list[i+1]
        img = cv2.imread(fn,0)
        img_detail = cv2.imread(fn_detail,0)

        IDp = crop_dict['ID']
        powerp = crop_dict['power']
        killp = crop_dict['kill']
        
        img_ID = img[IDp[0]:IDp[1], IDp[2]:IDp[3]]
        img_power = img[powerp[0]:powerp[1], powerp[2]:powerp[3]]
        img_kill = img[killp[0]:killp[1], killp[2]:killp[3]]
        
        _, str_ID = bin_inv(img_ID)
        _, str_power = bin_inv(img_power, thr=150)
        _, str_kill = bin_inv(img_kill, thr=150)
        
        ID, power, kill = str2num(str_ID), str2num(str_power), str2num(str_kill)
        
        Players[ID] = Player(ID,power,kill)        
        Players[ID].path = fn.split('\\')[-1]
        
        try:
            Players[ID].name = id2name[ID]
        except KeyError:
            print('KeyError!! : checkt {}'.format(Players[ID].path))
            Players[ID].name = ''

        # detail
        print('{}/{} : detail processing'.format(i+2,L))
        kill_4Tp = crop_dict['kill_4T']
        kill_5Tp = crop_dict['kill_5T']
        deathp = crop_dict['death']
        # gatheringp = crop_dict['gathering']
        # assistp = crop_dict['assist']

        img_kill_4T = img_detail[kill_4Tp[0]:kill_4Tp[1], kill_4Tp[2]:kill_4Tp[3]]
        img_kill_5T = img_detail[kill_5Tp[0]:kill_5Tp[1], kill_5Tp[2]:kill_5Tp[3]]
        img_death = img_detail[deathp[0]:deathp[1], deathp[2]:deathp[3]]
        # img_gathering = img_detail[gatheringp[0]:gatheringp[1], gatheringp[2]:gatheringp[3]]
        # img_assist = img_detail[assistp[0]:assistp[1], assistp[2]:assistp[3]]

        _, str_kill_4T = bin_inv(img_kill_4T, thr=80, inv=False)
        _, str_kill_5T = bin_inv(img_kill_5T, thr=80, inv=False)
        _, str_death = bin_inv(img_death, thr=145)
        # _, str_gathering = bin_inv(img_gathering, thr=120)
        # _, str_assist = bin_inv(img_assist, thr=120)

        kill_4T, kill_5T, death = str2num(str_kill_4T), str2num(str_kill_5T), str2num(str_death)
        # gathering, assist = str2num(str_gathering), str2num(str_assist)

        Players[ID].kill_4T = kill_4T
        Players[ID].kill_5T = kill_5T
        Players[ID].death = death
        # Players[ID].gathering = gathering
        # Players[ID].assist = assist

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

def Players2df_detail(Players):
    df = {
    'ID' : [],
    'name' : [],
    'power' : [],
    'kill' : [],
    'kill_4T' : [],
    'kill_5T' : [],
    'death' : [],
    # 'gathering' : [],
    # 'assist' : [],
    'path' : [],
    }
    df = pd.DataFrame(df, dtype=int)

    L = len(Players)
    for ID, p in Players.items():
        df = df.append({
            'ID' : ID,
            'name' : p.name,
            'power' : p.power,
            'kill' : p.kill,
            'kill_4T' : p.kill_4T,
            'kill_5T' : p.kill_5T,
            'death' : p.death,
            # 'gathering' : p.gathering,
            # 'assist' : p.assist,
            'path' : p.path,
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

def load_profiles(file_path):
    try:
        df = pd.read_excel(file_path)
        print('Loaded {}'.format(file_path))
    except FileNotFoundError:
        print('No such file or directory {}'.format(file_path))
        print('Function will return empty dictionary')
        return dict([])
    
    Players = dict([])

    for i in range(len(df)):
        row = df.loc[i]
        P = Player(row['ID'], row['power'], row['kill'])
        P.name = row['name']
        P.kill_4T = row['kill_4T']
        P.kill_5T = row['kill_5T']
        P.death = row['death']

        Players[row['ID']] = P
    
    return Players

def calc_diff(curr_path, past_path):
    P_curr = load_profiles(curr_path)
    P_past = load_profiles(past_path)

    Players = dict([])
    News = dict([])

    for pid in P_curr.keys():
        if P_past.get(pid):
            Players[pid] = P_curr[pid] - P_past[pid]
            Players[pid].path = P_curr[pid].power
        else:
            News[pid] = P_curr[pid]

    df_Players = Players2df_detail(Players)
    df_News = Players2df_detail(News)

    return df_Players, df_News

def df2xlsx(df, name):
    dt = datetime.datetime.now()
    output_name = '-'.join([str(dt.year), str(dt.month), str(dt.day)])
    output_name = output_name + '-' + name
    df.to_excel(output_name + '.xlsx', index=False)
    print('{} is  Saved'.format(output_name))