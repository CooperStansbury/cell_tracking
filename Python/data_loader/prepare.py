import numpy as np
import skimage
from skimage import io
from skimage.color import rgb2gray
from skimage.morphology import reconstruction
from skimage import (
    color, feature, filters, measure, morphology, segmentation, util, exposure
)


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


def transform(image):
    """A master function to wrap individual processes.
    
        args:
        : image (np.array): image 
        
    returns:
        : image (np.array): image 
    """
    image = rgb2gray(image)
    image = contrast_correction(image)
    image = dilation(image)
    return image

