import cv2
import numpy as np
import argparse
import sys
from tqdm import tqdm
import os
from os import path as osp
import csv
from glob import glob
import torch
import flowiz as fz
import matplotlib as plt

# get root directory
import re
reg = '^.*/AquaPose'
project_root = re.findall(reg, osp.dirname(osp.abspath(sys.argv[0])))[0]
sys.path.append(project_root)

from lib.utils.visual_utils import plot_optical_vectors

def flo_to_numpy(flo_url):
    with open(flo_url, mode='r') as flo:
        tag = np.fromfile(flo, np.float32, count=1)[0]
        width = np.fromfile(flo, np.int32, count=1)[0]
        height = np.fromfile(flo, np.int32, count=1)[0]
        nbands = 2
        tmp = np.fromfile(flo, np.float32, count= nbands * width * height)
        flow = np.resize(tmp, (int(height), int(width), int(nbands)))
    return flow

# dictionary with key = img_number and value = x_start, width
def get_image_cut_coordinates(dataset_root):
    filename = osp.join(dataset_root, 'stitched', 'stitched.csv')

    cut_coordinates = {}
    with open(filename, 'r') as file:
        for line in file.readlines():
            fields = line.split(',')
            cut_coordinates[fields[0].split('.')[0]] = [int(fields[1]), int(fields[2])]
    return cut_coordinates

def get_optical_vectors(dataset_root, img_id, coordinate_dict, plot=False):
    img_id = str(int(img_id.item()))
    cut_co = coordinate_dict[img_id]
    flo_url = osp.join(dataset_root,'stitched_optical_vectors', str(img_id).zfill(6) + '.flo')

    try:
        flo_np = flo_to_numpy(flo_url)
    except: 
        print('flow files {} not found'.format(flo_url))
        return None

    # cut out right part
    flo_np = flo_np[:,cut_co[0]:cut_co[0]+cut_co[1], :]
    
    if plot:
        plot_optical_vectors(flo_url, cut_co)

    return flo_np