from roughness.roughness import get_roughness
import sys
import glob, os
import csv
import numpy as np
import matplotlib.pyplot as plt
import pickle

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python {} paths".format(sys.argv[0]))
        exit(128)

    pwd = os.getcwd()

    for path_name in sys.argv[1:]:
        os.chdir(path_name)
        file_list = []
        slopes_all = []

        for file_name in glob.glob("*.png"):
            file_list.append(file_name)

        with open('results.csv', 'w') as csvfile:
            fieldnames = ['File_name', 'R_c', 'R_a', 'R_q', 'R_Sm', 'R_dq', 'slope']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            ra = []
            rq = []
            rdq = []
            slop = []
            for file_name in file_list:
                print("File: ", file_name)
                R_c, R_a, R_q, R_sm, R_dq, slope, all_slope = get_roughness(file_name)
                ra.append(R_a)
                rq.append(R_q)
                rdq.append(R_dq)
                slop.append(slope)
                for item in all_slope:
                    slopes_all.append(item)

                print("R_c, R_a, R_q, R_sm, R_dq, slope in um: ", R_c, R_a, R_q, R_sm, R_dq, slope)

                writer.writerow({'File_name': file_name, 'R_c': R_c, 'R_a': R_a, 'R_q': R_q, 'R_Sm': R_sm, 'R_dq': R_dq, 'slope': slope})

            print(np.median(ra), np.median(rq), np.median(rdq), np.median(slop))

        with open('slopes.pkl', 'wb') as slope_file:
            pickle.dump(slopes_all, slope_file)

        os.chdir(pwd)
    
