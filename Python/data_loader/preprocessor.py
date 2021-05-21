import numpy as np
import skimage
from skimage import io
from skimage.color import rgb2gray
from skimage.morphology import reconstruction
from skimage import (
    color, feature, filters, measure, morphology, segmentation, util, exposure
)

class ImageProcessor():
    """A class to control preprocessing flow"""


    def __init__(self, image):
        self.image = rgb2gray(image)


    def transform(self):
        """returns the image after all processing steps

        returns:
            : img (np.array): image
        """
        img = self.contrast_correction(self.image)
        return img


    def contrast_correction(self, image):
        """ contrast operations """
        GAIN = 2
        BOX = 1

        image = self.image
        image = exposure.adjust_log(image, gain=GAIN)
        image = self._dilation(image, BOX)

        return image


    def _dilation(self, image, box_size):
        """A function to dilate the image with variable 
        pixel region 
        
        args:
            : image (np.array): image 
            : box_size (int): size of pixel region

        returns:
            : image (np.array): image 
        """
        seed = np.copy(image)
        seed[box_size:-box_size, box_size:-box_size] = image.min()
        mask = image
        image = image - reconstruction(seed, mask, method='dilation')
        return image
