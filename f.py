import numpy as np
import cv2

def f(q):
    q.put([42, None, 'hello'])
    return

def get_image_difference(image_1, image_2):
    first_image_hist = cv2.calcHist([image_1], [0], None, [256], [0, 256])
    second_image_hist = cv2.calcHist([image_2], [0], None, [256], [0, 256])

    img_hist_diff = cv2.compareHist(first_image_hist, second_image_hist, cv2.HISTCMP_BHATTACHARYYA)
    img_template_probability_match = cv2.matchTemplate(first_image_hist, second_image_hist, cv2.TM_CCOEFF_NORMED)[0][0]
    img_template_diff = 1 - img_template_probability_match

    commutative_image_diff = (img_hist_diff / 10) + img_template_diff
    return commutative_image_diff

def find_img_pos_multi(screen, img, W_start, W_end, result, dist=None, interval=5, verbose=False):
    H, W = screen.shape[0:2]
    h, w = img.shape[0:2]
    min_diff = 10000
    W_min = min(W_end+1, W-w+1)
    for i in range(0, H-h+1, interval):
        for j in range(W_start, W_min, interval):
            image_diff = get_image_difference(img, screen[i:i+h, j:j+w])
            if min_diff > image_diff:
                min_diff = image_diff
                pos = np.array([i, j], dtype=np.int32)
                
    result.put((pos, min_diff))
    return

def find_img_pos_multi_target(screen, img, result, W_start, W_end, interval=5):
    H, W = screen.shape[0:2]
    h, w = img.shape[0:2]
    min_diff = 10000
    W_min = min(W_end+1, W-w+1)
    for i in range(0, H-h+1, interval):
        for j in range(W_start, W_min, interval):
            image_diff = get_image_difference(img, screen[i:i+h, j:j+w])
            if min_diff > image_diff:
                min_diff = image_diff
                pos = np.array([i, j], dtype=np.int32)
                
    result.put((pos, min_diff))
    return

def find_img_pos_single(screen, img, dist=None, interval=5, verbose=False):
    H, W = screen.shape[0:2]
    h, w = img.shape[0:2]
    min_diff = 10000
    pos = np.array([0,0])
    all_pixel_num = (H-h+1)*(W-w+1)
    for i in range(0, H-h+1, interval):
        for j in range(0, W-w+1, interval):
            image_diff = get_image_difference(img, screen[i:i+h, j:j+w])
            if min_diff > image_diff:
                min_diff = image_diff
                pos = np.array([i, j], dtype=np.int32)

            if verbose:
                current_pixel_num = i*(W-w)+j
                # sys.stdout.write('\ron scanning... {:.2f}%'.format(current_pixel_num/all_pixel_num*100))
                print('\ron scanning... {:.2f}%'.format(
                    current_pixel_num/all_pixel_num*100), end='')
    return pos, min_diff