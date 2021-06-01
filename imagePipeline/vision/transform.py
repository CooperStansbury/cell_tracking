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
    
    def __init__(self, params):
        """
        Parameters:
        -----------------------------
            : params (dict): user configs
        """
        self.params = params
    
    def fit_image(self, image):
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

    
    
