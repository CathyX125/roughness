from roughness.roughness import get_roughness
import sys
import glob, os
import csv
import matplotlib.pyplot as plt
import pickle
import numpy as np


def load_files(path_names):
    pwd = os.getcwd()

    R_a = []
    R_q = []
    R_dq = []
    Slop = []

    for path_name in path_names:
        os.chdir(path_name)

        ra = []
        rq = []
        rdq = []
        slop = []

        with open('results.csv') as csvfile:
            fieldnames = ['File_name', 'R_c', 'R_a', 'R_q', 'R_Sm', 'R_dq', 'slope']
            reader = csv.DictReader(csvfile)
            for row in reader:
                ra.append(float(row['R_a']))
                rq.append(float(row['R_q']))
                rdq.append(float(row['R_dq']))
                slop.append(float(row['slope']))

            R_a.append(ra)
            R_q.append(rq)
            R_dq.append(rdq)
            Slop.append(slop)

        os.chdir(pwd)

    return R_a, R_q, R_dq, Slop


def plot_box(path_names):
    R_a, R_q, R_dq, _ = load_files(path_names)
    Slop = load_slope_files(path_names)

    fig, axes = plt.subplots(2, 2)
    bp_dict = axes[0, 0].boxplot(R_a)
    for line in bp_dict['medians']:
        x0, y = line.get_xydata()[0] # left of median line
        x1, y = line.get_xydata()[1] # right of median line
        axes[0, 0].text((x0+x1)/2, y, '%.2f' % y, horizontalalignment='center') # draw above, centered
    axes[0, 0].set_title('$R_a$')
    axes[0, 0].set_ylabel("$\mu$m")
    axes[0, 0].set_ylim(0, 10)

    axes[0, 1].boxplot(R_q)
    axes[0, 1].set_title('$R_q$')
    axes[0, 1].set_ylabel("$\mu$m")
    axes[0, 1].set_ylim(0, 10)

    axes[1, 0].boxplot(R_dq)
    axes[1, 0].set_title('$R_{\Delta q}$')
    axes[1, 0].set_ylabel("$\mu$m")
    axes[1, 0].set_ylim(0, 1)

    axes[1, 1].boxplot(Slop)
    axes[1, 1].set_title('b/a')
    axes[1, 1].set_ylabel('')
    axes[1, 1].set_ylim(0, 1)

    for axe in axes:
        for ax in axe:
            ax.yaxis.grid(True)
            ax.set_xticks([y + 1 for y in range(len(R_a))])
            ax.set_xlabel('Exposure time (h)')
            
    plt.setp(axes, xticks=[y + 1 for y in range(len(R_a))], xticklabels=['0', '400', '800', '1300'])
    plt.show()


def load_slope_files(path_names):
    pwd = os.getcwd()
    slope = []
    for path_name in path_names:
        os.chdir(path_name)
        with open('slopes.pkl', 'rb') as f:
            slope.append(pickle.load(f))
        os.chdir(pwd)
    return slope


def plot_hist(path_names):
    Slop = load_slope_files(path_names)

    n_bins = np.arange(0, 1.0, 0.025)

    fig, axes = plt.subplots(2, 2)
    axes[0, 0].hist(Slop[0], bins=n_bins, density=True)
    axes[0, 1].hist(Slop[1], bins=n_bins, density=True)
    axes[1, 0].hist(Slop[2], bins=n_bins, density=True)
#    axes[1, 1].hist(Slop[3], bins=n_bins, density=True)
    axes[0, 0].set_title("0 h")
    axes[0, 1].set_title("400 h")
    axes[1, 0].set_title("800 h")
#    axes[1, 1].set_title("1300 h")

    for axe in axes:
        for ax in axe:
            ax.yaxis.grid(True)
            ax.set_xlim(0, 1.0)
            ax.set_ylim(0, 7.5)
            ax.set_xlabel('b/a')
            ax.set_ylabel('Density')

    plt.show()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Need to run for_all_images.py first")
        print("Usage: python {} paths".format(sys.argv[0]))
        exit(128)

    plot_hist(sys.argv[1:])
    plot_box(sys.argv[1:])
