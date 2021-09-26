"""
Name: Olichuuwon
Date: 15/06/2021
Note: MP4 & CSV to Plotted MP4
"""

import datetime
import os
import subprocess
from os.path import isfile, join

import cv2
import pandas as pd
from matplotlib import pyplot as plt

"""
PLEASE CHANGE / UPDATE
"""

# EG (30 or 59.94) (INT/FLOAT)
FPS = 59.94
# EG ('video_1') (MP4 ONLY)
VIDEO_NAME = 'video_1'
# EG ('file_1') (CSV ONLY)
CSV_NAME = 'file_1'
# EG (["green_hand x", "green_hand y", "orange_hand x", "orange_hand y"]) (LIST ONLY)
DATA_HEADER = ["green_hand x", "green_hand y", "orange_hand x", "orange_hand y"]

"""
NO NEED TOUCH
"""

# STATIC VARIABLES
ZFILL = 7
FILE_BROWSER_PATH = os.path.join(os.getenv('WINDIR'), 'explorer.exe')
CWD_DIR = os.getcwd()
NOW_TIME = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

# FOLDER NAME
WORKSPACE_FOLDER = 'video_generation_' + NOW_TIME
WORKSPACE_PATH = os.path.join(CWD_DIR, WORKSPACE_FOLDER)
os.mkdir(WORKSPACE_PATH)

# MAKE PLOTS FOLDER
PLOTS_FOLDER = os.path.join(WORKSPACE_PATH, "plots")
os.mkdir(PLOTS_FOLDER)
# plots_directory = WORKSPACE_PATH + "/plots/"

# MAKE FRAMES FOLDER
FRAME_FOLDER = os.path.join(WORKSPACE_PATH, "frames")
os.mkdir(FRAME_FOLDER)

# CSV FILE EXT
CSV_FILE = CSV_NAME + '.csv'
CSV_PATH = os.path.join(WORKSPACE_PATH, CSV_FILE)

# VIDEO FILE EXT
TARGET_VIDEO = VIDEO_NAME + '.mp4'
TARGET_VIDEO_PATH = os.path.join(WORKSPACE_PATH, TARGET_VIDEO)
OUTPUT_VIDEO = VIDEO_NAME + '_output.mp4'
OUTPUT_VIDEO_PATH = os.path.join(WORKSPACE_PATH, OUTPUT_VIDEO)


# OPEN EXPLORER TO DUMP CSV AND MP4
def explore(path):
    # explorer would choke on forward slashes
    path = os.path.normpath(path)
    if os.path.isdir(path):
        subprocess.run([FILE_BROWSER_PATH, path])
    elif os.path.isfile(path):
        subprocess.run([FILE_BROWSER_PATH, '/select,', os.path.normpath(path)])


# CONVERT VIDEO TO FRAMES
def video_to_frame():
    # get video
    video_capture = cv2.VideoCapture(TARGET_VIDEO_PATH)
    frame_number = 1
    if video_capture.isOpened():
        val, frame = video_capture.read()
    else:
        val = False
        print("ERROR: Video not captured")

    # get all frames
    try:
        while val:
            val, frame = video_capture.read()
            file_name = 'frame' + str(frame_number).zfill(ZFILL) + '.jpg'
            written_file = os.path.join(FRAME_FOLDER, file_name)
            cv2.imwrite(written_file, frame)
            print("DEBUG: Creating Frame -->", written_file)
            frame_number += 1
            cv2.waitKey(1)
        video_capture.release()
    except cv2.error:
        print("DEBUG: Reached end of video")


# CONVERT FRAME TO PLOT
def frames_to_plots():
    # data processing
    df_data = pd.read_csv(CSV_PATH, sep=",")
    df_data.columns = df_data.iloc[0] + " " + df_data.iloc[1]
    df_data = df_data[2:]
    df_data = df_data.reset_index(drop=True)
    df_data = df_data[DATA_HEADER]

    # numpy array
    x1 = df_data[DATA_HEADER[0]].to_numpy()
    y1 = df_data[DATA_HEADER[1]].to_numpy()
    x2 = df_data[DATA_HEADER[2]].to_numpy()
    y2 = df_data[DATA_HEADER[3]].to_numpy()

    # get plotted video
    for item in range(len(x1) - 1):
        frame_number = item + 1
        filename = "frame" + str(frame_number).zfill(ZFILL) + ".jpg"
        filename_path = os.path.join(WORKSPACE_PATH, "frames", filename)
        new_filename = "plot" + str(frame_number).zfill(ZFILL) + ".jpg"
        new_filename_path = os.path.join(WORKSPACE_PATH, "plots", new_filename)
        im = plt.imread(filename_path)
        plt.imshow(im)
        plt.scatter(float(x1[item]), float(y1[item]), c='red', s=40)
        plt.scatter(float(x2[item]), float(y2[item]), c='blue', s=40)
        plt.savefig(new_filename_path)
        plt.clf()
        print("DEBUG: Plotting Frame", frame_number, "--> Saved as", new_filename_path)


# CONVERT PLOTS TO VIDEO
def plots_to_video():
    # setting variables
    frame_array = []
    files = [f for f in os.listdir(PLOTS_FOLDER) if isfile(join(PLOTS_FOLDER, f))]

    # for sorting the file names properly
    files.sort(key=lambda x: x[5:-4])
    files.sort()

    # loop through frames
    for i in range(len(files)):
        filename = os.path.join(PLOTS_FOLDER, files[i])
        # reading each files
        img = cv2.imread(filename)
        height, width, layers = img.shape
        video_size = (width, height)
        # inserting the frames into an image array
        frame_array.append(img)
        print("DEBUG: Append into Image Array -->", filename)
    out = cv2.VideoWriter(OUTPUT_VIDEO_PATH, cv2.VideoWriter_fourcc(*'DIVX'), FPS, video_size)

    # write to video
    print("DEBUG: Finalising Video")
    for i in range(len(frame_array)):
        # writing to a image array
        out.write(frame_array[i])
    out.release()


def main():
    # reminder to update variables
    input("PLEASE: Press <ENTER> only after you have modified the variables at the top of the code!")

    # user pop out for easy usage
    input("PLEASE: Prepare to place your mp4 & csv files into the explorer pop out window, press <ENTER> to continue!")
    explore(WORKSPACE_PATH)
    input("PLEASE: Press <ENTER> key after placing csv and mp4 files!")

    # call functions
    video_to_frame()
    frames_to_plots()
    plots_to_video()

    # indicate the end
    print("YAY: End of Program")


if __name__ == "__main__":
    main()
