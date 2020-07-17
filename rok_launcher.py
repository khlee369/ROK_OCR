import cv2
import time
import matplotlib.pyplot as plt
import numpy as np
import sys
import win32api
import win32con
import win32gui
from util import *
from configs import *
from mss import mss

class NoxManager:
    def __init__(self, config, verbose=False):
        self.sct = mss()
        self.monitor = self.sct.monitors[0]
        self.nox_size = config['nox_size']
        self.nox_pos = self.get_nox_pos()
        # Double monitor Problem
        self.nox_pos[0] += self.monitor['top']
        self.nox_pos[1] += self.monitor['left']
        # Double monitor Problem
        self.nox_monitor = self.get_nox_monitor()

        self.capture_monitor = self.nox_monitor.copy()
        self.capture_monitor['left'] += 1340
        self.capture_monitor['top'] += 110
        self.capture_monitor['width'] = 60
        self.capture_monitor['height'] = 70
        self.capture_img = cv2.imread(img_dict['capture'])

        nm = get_screen(self.sct, self.nox_monitor)
        plt.imshow(nm)
        plt.show()
        # self.get_main_menu_pos()



    def get_nox_pos(self, verbose=False):
        print('-------------------------------------')
        input('Run Nox Application and Press Any Key')
        print('Now Find Nox Position')
        screen = get_screen(self.sct, self.sct.monitors[0])
        nox_img = cv2.imread(img_dict['nox'])
        nox_pos,_nox_diff = find_img_pos(screen, nox_img, interval=10, verbose=verbose)

        print('\n')
        print('Refining Nox Position')
        i, j = nox_img.shape[0:2]
        # Double Monitor Problem
        # if nox_pos[0] - i < 0:
        #     i = nox_pos[0]
        # if nox_pos[1] - j < 0:
        #     j = nox_pos[1]

        if nox_pos[0] - i < self.monitor['top']:
            i = self.monitor['top'] - nox_pos[0]
        if nox_pos[1] - j < self.monitor['left']:
            j = self.monitor['left'] - nox_pos[1]

        around_screen = screen[nox_pos[0]-i:nox_pos[0]+2*nox_img.shape[0],
                               nox_pos[1]-j:nox_pos[1]+2*nox_img.shape[1]]
        nox_pos -= np.array([i, j])
        nox_pos += find_img_pos(around_screen, nox_img,
                                interval=1, verbose=verbose)[0]
        nox_pos[0] += nox_img.shape[0]

        print('\n')
        print('Finished')

        return nox_pos

    def get_nox_monitor(self):
        nox_monitor = self.monitor.copy()
        nox_monitor['height'] = self.nox_size[0]
        nox_monitor['width'] = self.nox_size[1]
        nox_monitor['top'] = self.nox_pos[0]
        nox_monitor['left'] = self.nox_pos[1]
        return nox_monitor

    def get_relative_pos(self, img_path, dist=None, div=None, interval=5, verbose=False):
        screen = get_screen(self.sct, self.nox_monitor)
        img = cv2.imread(img_path)
        if type(img) is None:
            print('Can not find {}'.format(img_path))
            sys.exit(1)
        pos, img_diff = find_img_pos(screen, img, dist=dist, interval=interval, verbose=verbose)
        if div==None:
            pos += (np.array(img.shape[0:2])/2).astype('int')
        elif div == 1:
            pos += (np.array(img.shape[0:2])/4).astype('int')
        elif div == 2:
            pos += (np.array(img.shape[0:2])/8).astype('int')
            pos += np.array([0, img.shape[1]//8])
        return pos, img_diff

    def get_relative_mouse_pos(self):
        pos = get_mouse_pos() - self.nox_pos
        return pos

    def relative_drag(self, pos1, pos2, delay=0):
        drag(self.nox_pos+pos1, self.nox_pos+pos2, delay)

    def click_relative_pos(self, pos):
        # noisy_pos = self.nox_pos + pos + np.random.randint(-5, 5, 2)
        # click(noisy_pos)
        click(self.nox_pos + pos)

    def capture(self):
        screen = get_screen(self.sct, self.capture_monitor)
        _, img_diff = find_img_pos(screen, self.capture_img, dist=None, interval=1)
        if img_diff < 0.01:
            self.click_relative_pos(capture_pos)
            time.sleep(0.5)
        else:
            print("CAN NOT FIND CAPTURE, OPENING NOX MENU")
            self.click_relative_pos(nox_menu_pos)
            time.sleep(0.2)
            self.click_relative_pos(capture_pos)
            time.sleep(0.5)

    def caputer_members_all(self):
        print()
        print('------------------------------------------')
        input('Run Rise of Kingdoms and Open the menu to show alliance tab')
        print()
        input('open side bar of nox player to show captuer icon')
        print('------------------------------------------')
        print('Now start to capture')


        # R4 체크
        # 윗줄 Height : 355
        # 아랫줄 Height : 480
        # Width 1,2,3,4 : 220, 460, 700, 930
        # R3 이미지 위치 확인, Rel_pos Height < 500 이하면 R4 한줄
        # 정보창 팝업 안되도 계속 진행

        # R4 윗줄 캡쳐

        # R3 아이콘 위치 확인 후

        # R3 체크

        # R2 체크

        # R1 체크


    def get_main_menu_pos(self):
        print()
        print('------------------------------------------')
        input('Run Rise of Kingdoms and Open the menu to show alliance tab')
        print('Now Find Menu Positions')
        print()
        self.combat_pos = self.get_relative_pos(
            cv2.imread('./image_files/combat.PNG'))[0][0]
        print('Compat Pos Obtained')
        self.restore_pos = self.get_relative_pos(
            cv2.imread('./image_files/restore.PNG'))[0][0]
        print('Restore Pos Obtained')
        self.formation_pos = self.get_relative_pos(
            cv2.imread('./image_files/formation.PNG'))[0][0]
        print('Formation Pos Obtained')
        self.factory_pos = self.get_relative_pos(
            cv2.imread('./image_files/factory.PNG'))[0][0]
        print('Factory Pos Obtained')
        print()
        print('Finished')