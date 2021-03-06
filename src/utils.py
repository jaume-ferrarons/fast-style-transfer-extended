from __future__ import print_function
import scipy.misc
import numpy as np
import os
import sys
import random
import subprocess
import shutil


def save_img(out_path, img):
    img = np.clip(img, 0, 255).astype(np.uint8)
    scipy.misc.imsave(out_path, img)


def scale_img(style_path, style_scale):
    scale = float(style_scale)
    o0, o1, o2 = scipy.misc.imread(style_path, mode='RGB').shape
    scale = float(style_scale)
    new_shape = (int(o0 * scale), int(o1 * scale), o2)
    style_target = get_img(style_path, img_size=new_shape)
    return style_target


def get_media(src):
    if os.path.isdir(src):
        return get_images(src)
    elif src[-4:] == ".mp4":
        return sample_video(src)
    else:
        print("Reading image %s" % src)
        return [get_img(src)]


def get_img(src, img_size=False):
    img = scipy.misc.imread(src, mode='RGB')  # misc.imresize(, (256, 256, 3))
    if not (len(img.shape) == 3 and img.shape[2] == 3):
        img = np.dstack((img, img, img))
    if img_size != False:
        img = scipy.misc.imresize(img, img_size)
    return img


def exists(p, msg):
    assert os.path.exists(p), msg


def list_files(in_path):
    files = []
    for (dirpath, dirnames, filenames) in os.walk(in_path):
        files.extend(filenames)
        break

    return files


def duration_to_seconds(duration):
    """Duration is of the form: 00:21:19.50"""
    (hms, millis) = duration.split('.')
    (h, m, s) = list(map(lambda x: int(x), hms.split(':')))
    return h * 3600 + m * 60 + s


def get_images(dir_path):
    """Loads all images in the path"""
    images_path = [dir_path + fname for fname in list_files(dir_path)]
    print("Loading %s" % images_path)
    return list(map(get_img, images_path))

def sample_video(in_path, n_samples=20):
    """Extracts the samples from provided video and returns them"""
    TMP_VIDEO_DIR = '.tmp/'
    TMP_VIDEO_SAMPLES = TMP_VIDEO_DIR + 'samples/'
    DURATION_FILE = TMP_VIDEO_DIR + 'duration'
    # Create TMP_VIDEO_DIR if doesn't exsist
    if not os.path.exists(TMP_VIDEO_SAMPLES):
        os.makedirs(TMP_VIDEO_SAMPLES)
    # Get the duration of the video
    cmd = ' '.join(["ffmpeg -i", in_path,
                    "2>&1 | grep Duration | awk '{print $2}' | tr -d , >", DURATION_FILE])
    subprocess.call(cmd, shell=True)
    duration = open(DURATION_FILE, 'r').readline().strip()
    print("Video duration: %s" % duration)
    seconds = duration_to_seconds(duration)
    sample_cmd = ' '.join(["ffmpeg -i", in_path, '-vf fps=%d/%d' %
                           (n_samples, seconds), TMP_VIDEO_SAMPLES + "out%d.png"])
    print("Taking sample")
    subprocess.call(sample_cmd, shell=True)
    return get_images(TMP_VIDEO_SAMPLES)
