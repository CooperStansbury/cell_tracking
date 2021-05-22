import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import skimage
from skimage import io
from skimage.color import rgb2gray
from skimage.morphology import reconstruction
from skimage import (
    color, feature, filters, measure, morphology, segmentation, util, exposure
)

############################################################
# MASTER FLOW CONTROL
############################################################


def transform(image, binarize=False):
    """A master function to wrap individual processes.
    
        args:
        : image (np.array): image 
        
    returns:
        : image (np.array): image 
    """
    image = rgb2gray(image)
    image = contrast_correction(image)
    
    if binarize:
        image = guassian_blur(image)
        image = multi_otsu_filter(image)
        
    image = dilation(image)
    return image


############################################################
# UTILITIES
############################################################


def multi_otsu_filter(image):
    """A function to get the background value 
    
    args:
        : image (np.array): image 
        
    returns:
        : image (np.array): image 
    """
    thresholds = filters.threshold_multiotsu(image, classes=2)
    regions = np.digitize(image, bins=thresholds)
    return regions


def guassian_blur(image):
    """ A function to blur the image
    args:
        : image (np.array): image 
        
    returns:
        : image (np.array): image 
    """
    image = filters.gaussian(image, sigma=3, 
                             mode='reflect')
    return image


def contrast_correction(image):
    """ contrast operations 
    
    args:
        : image (np.array): image 
        
    returns:
        : image (np.array): image 
    """
    GAIN = 2
    image = exposure.adjust_log(image, gain=GAIN)
    return image


def dilation(image):
    """A function to dilate the image with variable 
    pixel region 
    
    args:
        : image (np.array): image 
        
    returns:
        : image (np.array): image 
    """
    BOX_SIZE = 5
    seed = np.copy(image)
    seed[BOX_SIZE:-BOX_SIZE, BOX_SIZE:-BOX_SIZE] = image.min()
    mask = image
    image = image - reconstruction(seed, mask, method='dilation')
    return image


def plot_contour(image):
    """A function to plot the contour of an image"""
    fig, ax = plt.subplots(figsize=(5, 5))
    qcs = ax.contour(image, origin='image')

