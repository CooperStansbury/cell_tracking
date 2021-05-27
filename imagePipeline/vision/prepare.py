"""
Individual wrappers around pre-processing tasks
"""

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


def adapt_hist(image, clip=0.01):
    """A function to correct image using adaptive histogram
    
    Parameters:
    -----------------------------
        : image (np.array): image 
        : clip (float): the clip limit 
        
    Returns:
    -----------------------------
        : image (np.array): image 
    """
    image = exposure.equalize_adapthist(image, clip_limit=clip)
    return image
    
    
def multi_otsu_filter(image):
    """A function to get the background value 
    
    Parameters:
    -----------------------------
        : image (np.array): image 
        
    Returns:
    -----------------------------
        : image (np.array): image post processing
    """
    thresholds = filters.threshold_multiotsu(image, classes=2)
    regions = np.digitize(image, bins=thresholds)
    return regions


def guassian_blur(image, sigma=3):
    """ A function to blur the image
    
    Parameters:
    -----------------------------
        : image (np.array): image 
        : sigma (int): the st. dev of the blur
        
    Returns:
    -----------------------------
        : image (np.array): image post processing
    """
    image = filters.gaussian(image, sigma=sigma, 
                             mode='reflect')
    return image


def contrast_correction(image, gain=1):
    """ contrast operations 
    
    Parameters:
    -----------------------------
        : image (np.array): image 
        : gain (int): the gain amount
        
    Returns:
    -----------------------------
        : image (np.array): image post processing 
    """
    image = exposure.adjust_log(image, gain=gain)
    return image


def static_dilation(image, h=0.1):
    """A function to dilate with a fixed seed
    
    Parameters:
    -----------------------------
        : image (np.array): image 
        : h (float): static value to dilate against
        
    Returns:
    -----------------------------
        : image (np.array): image post processing
    """
    seed = image - h
    dilated = reconstruction(seed, image, method='dilation')
    image = image - dilated
    return image
    

def dilation(image, box_size=1):
    """A function to dilate the image with variable 
    pixel region 
    
    Parameters:
    -----------------------------
        : image (np.array): image 
        : box_size (int): size of bounding box
        
    Returns:
    -----------------------------
        : image (np.array): image post processing
    """
    seed = np.copy(image)
    seed[box_size:-box_size, box_size:-box_size] = image.min()
    dilated = reconstruction(seed, image, method='dilation')
    image = image - dilated
    return image


