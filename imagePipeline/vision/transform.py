"""
Master pre-processing functions used to wrap various processses
in `prepare.py`
"""

import sys
import numpy as np
import imagePipeline.vision.prepare as pr


############################################################
# MASTER FLOW CONTROL
############################################################


class Transformer():
    """a class to manage parameters """
    
    def __init__(self):
        pass
    
    def save_params(self):
        """A function to store the parameters used 

        Returns:
        -----------------------------
            : NA: prints confirmation or raises ValueError 
        """
    
    def fit(self, image):
        """ A master function to wrap individual processes 
        
        Parameters:
        -----------------------------
            : image (np.array): image 

        Returns:
        -----------------------------
            : image (np.array): image 
        """
        image = pr.rgb2gray(image)
        image = pr.contrast_correction(image)
        image = pr.dilation(image)
        return image

    
    
