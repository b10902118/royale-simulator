import cv2
import numpy as np
import matplotlib.pyplot as plt
from glob import glob
import os
import pickle


# Initialize ORB detector
orb = cv2.ORB_create()


def compute_orb_features(image_path):
    # Load image
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError(f"Image at {image_path} not found.")

    # Detect and compute features
    ft = orb.detectAndCompute(img, None)
    return ft


def batch_compute_orb_features(image_dir):
    output_dir = image_dir
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    dataset_image_paths = glob(os.path.join(image_dir, "*.png"))

    features = {}
    for image_path in dataset_image_paths:
        key = os.path.splitext(os.path.basename(image_path))[0]
        try:
            ft = compute_orb_features(image_path)
            features[key] = ft
        except Exception as e:
            print(f"Error processing {image_path}: {e}")

    output_path = os.path.join(output_dir, os.path.basename(image_path) + ".pkl")
    with open(output_path, "wb") as f:
        pickle.dump(features, f)


folders = ["giant", "musketeer", "mini_pekka", "minion", "goblin"]
for folder in folders:
    print(f"Processing {folder}...")
    batch_compute_orb_features(folder)
