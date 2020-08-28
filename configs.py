# Rise of Kingdoms fixed position
# NOX Player resolution : H x W == 720 x 1280

import numpy as np

nox_size = (720, 1280)
diff_thr = 0.023

capture_pos = np.array([145, 1372])
profile_close_pos = np.array([89, 1091])
nox_menu_pos = np.array([469, 1311])
leader_pos = np.array([149, 443])
more_info_pos = np.array([544, 308])
kill_info_pos = np.array([130, 865])
detail_close_pos = np.array([46, 1116])

# h, w
rank_offset = (220, 160)

R4_H1 = 355
R4_H2 = 480
R4_Ws = [220, 460, 700, 930]

R3_thr = 500

MW_left = 200
MW_right = 680

# 멤버를 총 6명 선택할수 있으나 맨밑에서 예외처리가 발생
# R3, R2, R1 아이콘이 눌리는 경우가 있기 떄문에 4명만 누르도록 함

MHs = [258, 338, 413, 497, 575, 654]

members_pos = [[MHs[0], MW_left],
               [MHs[1], MW_left],
               [MHs[2], MW_left],
               [MHs[3], MW_left],
               [MHs[0], MW_right],
               [MHs[1], MW_right],
               [MHs[2], MW_right],
               [MHs[3], MW_right]]
members_pos = np.array(members_pos)

R4_pos_U = [[R4_H1, R4_Ws[0]],
            [R4_H1, R4_Ws[1]],
            [R4_H1, R4_Ws[2]],
            [R4_H1, R4_Ws[3]]]
R4_pos_U = np.array(R4_pos_U)

R4_pos_D = [[R4_H2, R4_Ws[0]],
            [R4_H2, R4_Ws[1]],
            [R4_H2, R4_Ws[2]],
            [R4_H2, R4_Ws[3]]]
R4_pos_D = np.array(R4_pos_D)

img_path = './images/'
img_dict = {
    'nox': img_path + 'nox.PNG',
    'menu': img_path + 'menu.PNG',
    'alliance': img_path + 'alliance.PNG',
    'R1': img_path + 'R1.PNG',
    'R2': img_path + 'R2.PNG',
    'R3': img_path + 'R3.PNG',
    'R4': img_path + 'R4.PNG',
    'info': img_path + 'info.PNG',
    '2menus': img_path + '2menus.PNG',
    '4menus': img_path + '4menus.PNG',
    '7menus': img_path + '7menus.PNG',
    'capture': img_path + 'capture.PNG',
    'r1_lastline': img_path + 'r1_lastline.PNG', # this is changable
}

# R3, R2 드래그 해서 올리기 할때
# manager.relative_drag(img_pos, np.array([170, img_pos[1]]), delay=1.0)
# img_pos == R3 image pos

r3r2_H_to = 170

md_drag_from6 = np.array([510, 200])
md_drag_to6 = np.array([15, 200])

md_drag_from4 = np.array([500, 200])
md_drag_to4 = np.array([170, 200])


# caputre 아이콘이 없는 경우 체크해봐야됨
# form np.array([120, 1340])
# to   np.array([170, 1400])
# tmp_monitor = manager.nox_monitor.copy()
# tmp_monitor['left'] += 1340
# tmp_monitor['top'] += 110
# tmp_monitor['width'] = 60
# tmp_monitor['height'] = 70

# screen = get_screen(manager.sct, tmp_monitor)


# R1은 마지막 줄 체크를 다르게
# r1_monitor = manager.nox_monitor.copy()
# r1_monitor['left'] += 170
# r1_monitor['top'] += 610
# r1_monitor['width'] = 400
# r1_monitor['height'] = 80

# screen = get_screen(manager.sct, r1_monitor)
# plt.imshow(screen)

# sct_img = manager.sct.grab(r1_monitor)
# mss.tools.to_png(sct_img.rgb, sct_img.size, output='./images/r1_lastline.PNG')

# r1_monitor10 = r1_monitor.copy()
# r1_monitor10['left'] -= 10
# r1_monitor10['top'] -= 10
# r1_monitor10['width'] += 10
# r1_monitor10['height'] += 10

# 스크린샷 위치 : C:\Users\KH_Home\Nox_share\ImageShare\Screenshots
tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# pytesseract.pytesseract.tesseract_cmd = tesseract_path
profile_path = './Screenshots/'

crop_dict = {
    'ID' : np.array([185, 216, 595, 672], dtype=int),
    'power' : np.array([290, 320, 705, 880], dtype=int),
    'kill' : np.array([290, 320, 880, 1050], dtype=int),
    'kill_4T' : np.array([250, 270, 887, 988], dtype=int),
    'kill_5T' : np.array([282, 302, 764, 867], dtype=int),
    'death' : np.array([360, 390, 890, 1060], dtype=int),
    'gathering' : np.array([490, 520, 890, 1060], dtype=int),
    'assist' : np.array([540, 570, 890, 1060], dtype=int),
}