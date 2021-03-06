import cv2
import time
import matplotlib.pyplot as plt
import numpy as np
import sys
import win32api, win32con, win32gui
from util import *
from configs import *
from mss.tools import to_png
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

        self.rank_monitor = self.nox_monitor.copy()
        self.rank_monitor['left'] += 160
        self.rank_monitor['top'] += 220
        self.rank_monitor['width'] = 80
        self.rank_monitor['height'] = 480

        self.r1_monitor = self.nox_monitor.copy()
        self.r1_monitor['left'] += 170
        self.r1_monitor['top'] += 610
        self.r1_monitor['width'] = 400
        self.r1_monitor['height'] = 80

        self.r1_monitor10 = self.r1_monitor.copy()
        self.r1_monitor10['left'] -= 10
        self.r1_monitor10['top'] -= 10
        self.r1_monitor10['width'] += 10
        self.r1_monitor10['height'] += 10

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
        nox_pos,_nox_diff = find_img_pos(screen, nox_img, interval=10)

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
        nox_pos += find_img_pos(around_screen, nox_img, interval=1)[0]
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

    def get_relative_pos(self, img_path, div=None, interval=5, single=True, half=None):
        screen = get_screen(self.sct, self.nox_monitor)
        if half=='left':
            screen = screen[:,:640,:]
        elif half=='right':
            screen = screen[:,640:,:]
        
        img = cv2.imread(img_path)
        if type(img) is None:
            print('Can not find {}'.format(img_path))
            sys.exit(1)

        pos, img_diff = (0,0), 1000
        if single:
            pos, img_diff = find_img_pos(screen, img, interval=interval)
        else:
            pos, img_diff = find_img_pos_multi(screen, img)
        if half=='right':
            pos[1] += 640

        if div==None:
            pos += (np.array(img.shape[0:2])/2).astype('int')
        elif div == 1:
            pos += (np.array(img.shape[0:2])/4).astype('int')
        elif div == 2:
            pos += (np.array(img.shape[0:2])/8).astype('int')
            pos += np.array([0, img.shape[1]//8])
        elif div == 3:
            pos += (np.array(img.shape[0:2])/4).astype('int')
            pos += np.array([0, img.shape[1]//4])
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
        _, img_diff = find_img_pos(screen, self.capture_img, interval=1)
        if img_diff < 0.01:
            self.click_relative_pos(capture_pos)
            time.sleep(0.5)
        else:
            print("CAN NOT FIND CAPTURE, OPENING NOX MENU")
            self.click_relative_pos(nox_menu_pos)
            time.sleep(0.2)
            self.click_relative_pos(capture_pos)
            time.sleep(0.5)

    # rank == 'leader' or 'R4' or 'R3' or 'R2' or 'R1'
    def capture_members(self, pos_list, img_path, rank, div, 
            diff_thr=0.04, verbose=False, single=False, detail=False, first=False):
        tbound, bbound = 0, 700
        if first:
            tbound, bbound = self.check_bound(rank)
        print(tbound, bbound)
        for m_pos in pos_list:
            # bound checking
            if m_pos[0] - tbound < 60 or m_pos[0] - bbound > 60 or bbound - tbound < 100:
                continue
            self.click_relative_pos(m_pos)
            time.sleep(0.5)
            half = None
            if m_pos[1] == MW_left:
                half = 'left'
            elif m_pos[1] == MW_right:
                half = 'right'
            profile_pos, diff = self.get_relative_pos(img_path, div=div, single=single, half=half)
            if verbose:
                print('profile_diff: ', diff)
            # print('profile_diff: ', diff)
            if diff < diff_thr:
                print('CAPTURE!')
                self.click_relative_pos(profile_pos)
                time.sleep(0.5)
                self.capture()
                time.sleep(0.5)
                if detail:
                    self.click_relative_pos(more_info_pos)
                    time.sleep(0.5)
                    self.click_relative_pos(kill_info_pos)
                    time.sleep(0.2)
                    self.capture()
                    time.sleep(0.5)
                    self.click_relative_pos(detail_close_pos)
                    time.sleep(0.5)
                self.click_relative_pos(profile_close_pos)
                time.sleep(0.5)

    def capture_leader(self, other=False, detail=False):
        menus = '4menus'
        div = 1
        if other:
            menus = '2menus'
            div = 3

        self.capture_members([leader_pos], img_dict[menus], 'leader', div=div, detail=detail)

    def capture_R4(self, other=False, single=False, detail=False):
        menus = '4menus'
        div = 1
        if other:
            menus = '2menus'
            div = 3

        self.capture_members(R4_pos_U, img_dict[menus], 'R4', div=div, single=single, detail=detail)
        R3_pos, R3_diff = self.get_relative_pos(img_dict['R3'])
        if R3_pos[0] > R3_thr:
            self.capture_members(R4_pos_D, img_dict[menus], 'R4', div=div, single=single, detail=detail)

    def capture_R3(self, dragged=False, other=False, single=False, detail=False):
        menus = '7menus'
        div = 2
        if other:
            menus = '2menus'
            div = 3

        if not dragged:
            R3_pos, R3_diff = self.get_relative_pos(img_dict['R3'])
            self.click_relative_pos(R3_pos)
            time.sleep(0.3)
            self.relative_drag(R3_pos, np.array([r3r2_H_to, R3_pos[1]]), delay=1.0)

        last_line = False
        max_cnt = 20
        cnt = 0

        self.capture_members(members_pos, img_dict[menus], 'R3', div=div, single=single, detail=detail, first=True)
        last_line = self.check_lastline(drag=4)
        # 멤버수가 4명,6명 보다 적은경우 에러가 날 수 있음
        while(not last_line and cnt < max_cnt):
            self.capture_members(members_pos, img_dict[menus], 'R3', div=div, single=single, detail=detail)
            # self.relative_drag(md_drag_from4, md_drag_to4, delay=1.0)
            # R1_pos, R1_diff = self.get_relative_pos(img_dict['R1'])
            # print('R1 diff : ', R1_diff)
            # if R1_diff < diff_thr:
            #     last_line = True
            #     self.capture_members(members_pos, img_dict[menus], div=div, single=single, detail=detail)
            last_line = self.check_lastline(drag=4)
            # if last_line:
            #     self.capture_members(members_pos, img_dict[menus], div=div, single=single, detail=detail)
            cnt += 1

    def capture_R2(self, dragged=False, other=False, single=False, detail=False):
        menus = '7menus'
        div = 2
        if other:
            menus = '2menus'
            div = 3

        if not dragged:
            R2_pos, R2_diff = self.get_relative_pos(img_dict['R2'])
            self.click_relative_pos(R2_pos)
            time.sleep(0.3)
            self.relative_drag(R2_pos, np.array([r3r2_H_to, R2_pos[1]]), delay=1.0)

        last_line = False
        max_cnt = 20
        cnt = 0

        self.capture_members(members_pos, img_dict[menus], 'R2', div=div, single=single, detail=detail, first=True)
        last_line = self.check_lastline(drag=4)
        while(not last_line and cnt < max_cnt):
            self.capture_members(members_pos, img_dict[menus], 'R2', div=div, single=single, detail=detail)
            # self.relative_drag(md_drag_from4, md_drag_to4, delay=1.0)
            # R1_pos, R1_diff = self.get_relative_pos(img_dict['R1'])
            # print('R1 diff : ', R1_diff)
            # if R1_diff < diff_thr:
            #     last_line = True
            #     self.capture_members(members_pos, img_dict[menus], div=div, single=single, detail=detail)
            last_line = self.check_lastline(drag=4)
            # if last_line:
            #     self.capture_members(members_pos, img_dict[menus], div=div, single=single, detail=detail)
            cnt += 1

        # 맨마지막줄은 캡쳐가 안됨으로 추가
        last_members = [[MHs[4], MW_left], [MHs[4], MW_right]]
        self.capture_members(last_members, img_dict[menus], 'R2', div=div, single=single, detail=detail, first=True)

    def capture_R1(self, dragged=False, other=False, single=False, detail=False):
        menus = '7menus'
        div = 2
        if other:
            menus = '2menus'
            div = 3


        if not dragged:
            R1_pos, R1_diff = self.get_relative_pos(img_dict['R1'])
            self.click_relative_pos(R1_pos)
            time.sleep(0.3)
            self.relative_drag(R1_pos, np.array([r3r2_H_to, R1_pos[1]]), delay=1.0)

        last_line = False
        max_cnt = 20
        cnt = 0

        extend6 = [[MHs[4], MW_left],
                    [MHs[5], MW_left],
                    [MHs[4], MW_right],
                    [MHs[5], MW_right]]
        members6_pos = np.vstack([members_pos, extend6])


        self.capture_members(members6_pos, img_dict[menus], 'R1', div=div, single=single, detail=detail, first=True)
        last_line = self.check_lastline(drag=6)
        while(not last_line and cnt < max_cnt):
            self.capture_members(members6_pos, img_dict[menus], 'R1', div=div, single=single, detail=detail)

            # 마지막줄 캡쳐 -> 드래그 -> 비교
            # sct_img = self.sct.grab(self.r1_monitor)
            # to_png(sct_img.rgb, sct_img.size, output=img_dict['r1_lastline'])
            
            # self.relative_drag(md_drag_from6, md_drag_to6, delay=1.0)
            # time.sleep(1.0)

            # screen = get_screen(self.sct, self.r1_monitor10)
            # r1_lastline_img = cv2.imread(img_dict['r1_lastline'])
            # _, lastline_diff = find_img_pos(screen, r1_lastline_img, interval=1)

            # if lastline_diff < 0.005:
            #     last_line = True
            last_line = self.check_lastline(drag=6)
            cnt += 1

    def check_lastline(self, drag=6):
        print('CHECKING LAST LINE')
        last_line = False
        sct_img = self.sct.grab(self.r1_monitor)
        to_png(sct_img.rgb, sct_img.size, output=img_dict['r1_lastline'])
        
        if drag == 6:
            self.relative_drag(md_drag_from6, md_drag_to6, delay=1.0)
        else:
            self.relative_drag(md_drag_from4, md_drag_to4, delay=1.0)
        time.sleep(1.0)

        screen = get_screen(self.sct, self.r1_monitor10)
        r1_lastline_img = cv2.imread(img_dict['r1_lastline'])
        _, lastline_diff = find_img_pos(screen, r1_lastline_img, interval=1)

        if lastline_diff < 0.005:
            last_line = True
        return last_line

    def check_bound(self, rank):
        time.sleep(0.4)
        s = time.time()
        print('Check bound')
        screen = get_screen(self.sct, self.rank_monitor)
        # diff_thr = 0.023
        tbound, bbound = 0, 700
        if rank == 'R3':
            R3_pos, R3_diff = find_img_pos(screen, cv2.imread(img_dict['R3']), interval=2, offset=rank_offset)
            R2_pos, R2_diff = find_img_pos(screen, cv2.imread(img_dict['R2']), interval=2, offset=rank_offset)
            print('T DIFF : {}'.format(R3_diff))
            print('B DIFF : {}'.format(R2_diff))
            if R3_diff < diff_thr:
                tbound = R3_pos[0]
            if R2_diff < diff_thr:
                bbound = R2_pos[0]
        elif rank == 'R2':
            R2_pos, R2_diff = find_img_pos(screen, cv2.imread(img_dict['R2']), interval=2, offset=rank_offset)
            R1_pos, R1_diff = find_img_pos(screen, cv2.imread(img_dict['R1']), interval=2, offset=rank_offset)
            print('T DIFF : {}'.format(R2_diff))
            print('B DIFF : {}'.format(R1_diff))
            if R2_diff < diff_thr:
                tbound = R2_pos[0]
            if R1_diff < diff_thr:
                bbound = R1_pos[0]
        elif rank == 'R1':
            R1_pos, R1_diff = find_img_pos(screen, cv2.imread(img_dict['R1']), interval=2, offset=rank_offset)
            print('T DIFF : {}'.format(R1_diff))
            if R1_diff < diff_thr:
                tbound = R1_pos[0]
        print('Check bound TIME : {}'.format(time.time()- s))

        return tbound, bbound
    def capture_members_all(self, other=False, single=True, detail=False):
        print()
        print('------------------------------------------')
        input('Run Rise of Kingdoms and Open the menu to show alliance tab')
        print()
        input('Click members tab to show members')
        print()
        input('Open side bar of nox player to show captuer icon')
        print('------------------------------------------')
        print('Now start to capture')

        self.capture_leader(other=other, detail=detail)
        self.capture_R4(other=other, single=single, detail=detail)
        self.capture_R3(other=other, single=single, detail=detail)
        self.capture_R2(other=other, single=single, detail=detail)
        self.capture_R1(other=other, single=single, detail=detail)


    # def get_main_menu_pos(self):
    #     print()
    #     print('------------------------------------------')
    #     input('Run Rise of Kingdoms and Open the menu to show alliance tab')
    #     print('Now Find Menu Positions')
    #     print()
    #     self.combat_pos = self.get_relative_pos(
    #         cv2.imread('./image_files/combat.PNG'))[0][0]
    #     print('Compat Pos Obtained')
    #     self.restore_pos = self.get_relative_pos(
    #         cv2.imread('./image_files/restore.PNG'))[0][0]
    #     print('Restore Pos Obtained')
    #     self.formation_pos = self.get_relative_pos(
    #         cv2.imread('./image_files/formation.PNG'))[0][0]
    #     print('Formation Pos Obtained')
    #     self.factory_pos = self.get_relative_pos(
    #         cv2.imread('./image_files/factory.PNG'))[0][0]
    #     print('Factory Pos Obtained')
    #     print()
    #     print('Finished')
