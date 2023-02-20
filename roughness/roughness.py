import sys
import cv2
import numpy as np
np.set_printoptions(threshold=sys.maxsize)
from scipy import signal
from scipy.ndimage import gaussian_filter1d
import math
import re
from matplotlib import pyplot as plt


global_scale = 1.0333  # pixels/um
radius = 10  # radius of the probe niddle in pixels 
cut_off = 650


debug_all_steps = False


def debug_img(img):
    if debug_all_steps:
        cv2.imshow("img", img)
        cv2.waitKey(0)


def cal_sigma(la):
    sigma = la * math.sqrt(math.log(2)) / math.sqrt(2) / math.pi
    return sigma


def build_niddle(rad):
    rad *= global_scale
    if rad % 2 == 0:
        rad = rad + 1
    rad = int(rad)

    img = np.zeros((rad*2+1, rad*2+1, 1), dtype=np.uint8)
    cv2.circle(img, (rad+1, rad), rad, 255, -1)
    cv2.rectangle(img,(0,0),(rad*2+1 ,rad), 255, -1)
    _, img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)

    debug_img(img)

    return img


def measure_surface(surface, rad):
    height, width = surface.shape
    niddle = build_niddle(rad)
    sur = np.asarray(surface)
    nid = np.asarray(niddle)
    grad = signal.convolve2d(sur, nid, boundary='symm', mode='same')
    res = []
    y = []
    for i in range(0, width):
        for j in range(0 ,height):
            if grad[j, i] > 0:
                res.append((i, j + rad))
                y.append(float(j) / global_scale)
                break
    return res, y


def roughness(file_name, surface, show_plot=False, save_plot=False):
    if surface[0][0] > 200:
        surface = (255-surface)

    height, width = surface.shape
    _, surface = cv2.threshold(surface, 200, 255, cv2.THRESH_BINARY)
    _, xn = measure_surface(surface, radius)
    xs = gaussian_filter1d(xn, cal_sigma(10))
    sigma_c = cal_sigma(cut_off)
    xc = gaussian_filter1d(xn, sigma_c)

    xr = []
    x0 = []
    a_max = 0
    xr_last = 0
    for i in range(len(xc)):
        a = xs[i] - xc[i]
        xr.append(a)
        if np.absolute(a) > a_max:
            a_max = a
        if xr_last > 0 and a <= 0:
            x0.append(i)
        if xr_last < 0 and a >= 0:
            x0.append(i)
        xr_last = a

    R_c = 0

    R_a = np.mean(np.absolute(xr))

    R_q = np.sqrt(np.mean(np.power(xr, 2)))

    R_Sm = 0

    dq = np.diff(xr)
    R_dq = np.sqrt(np.mean(np.power(dq, 2)))

    slopes = []
    for i in range(len(x0)-1):
        start_x = x0[i]
        end_x = x0[i+1]
        rms = np.sqrt(np.mean(np.power(xr[start_x:end_x], 2)))
        slopes.append(np.sqrt(2)*rms/(end_x - start_x))
    slope = np.sqrt(np.mean(np.power(slopes, 2)))

    if show_plot or save_plot:
        plt.figure(1, figsize=(22, 4), dpi=79)
        plt.subplot(211)
        plt.plot(xn, 'b--', alpha=0.75)
        plt.plot(xs, 'r', alpha=0.75)
        plt.plot(xc, 'g', alpha=0.75)
        plt.gca().invert_yaxis()
        plt.grid(True)

        plt.subplot(212)
        plt.plot(xr, 'r', alpha=0.75)
        plt.plot(np.zeros(len(xr)), 'g', alpha=0.75)
        plt.plot(x0, np.zeros(len(x0)), 'b+', alpha=0.75)
        plt.gca().invert_yaxis()
        plt.grid(True)

        if save_plot:
            plt.savefig(file_name[:-4]+".jpg", figsize=(20, 4), dpi=80)
            plt.clf()
        else:
            plt.show()

        if show_plot:
            slopes = ["Not showing slopes when debugging"]

    return R_c, R_a, R_q, R_Sm, R_dq, slope, slopes


def get_roughness(file_name):
    surface = cv2.imread(file_name, cv2.IMREAD_GRAYSCALE)
    return roughness(file_name, surface, False, True)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python {} file_name".format(sys.argv[0]))
        exit(128)

    file_name = sys.argv[1]
    surface = cv2.imread(file_name, cv2.IMREAD_GRAYSCALE)
    print(roughness(file_name, surface, True, True))

