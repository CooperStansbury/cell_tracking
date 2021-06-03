"""
Master pre-processing functions used to wrap various processses
in `prepare.py`
"""

import sys
import numpy as np
import multiprocessing as mp

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import skimage
from skimage import io
from skimage.color import rgb2gray
from skimage.morphology import reconstruction
from skimage import (
    color, feature, filters, measure, morphology, segmentation, exposure, restoration, util
)


class ParallelTransformer():
    """a class to manage parameters """
    
    def __init__(self, params, metadata):
        """
        Parameters:
        -----------------------------
            : params (dict): user configs
            : metadata (dict): metdata from for the czi
        """
        self.params = params
        self.metadata = metadata
        self.channels = self._get_channel_indices()
        self.chain = self.params['process_chain']
                                  
        self.ops = {
            'ball' : self.ball,
            'dilate' : self.dilate,
            'dilate_s' : self.dilate_s,
            'rescale' : self.rescale,
            'eq_hist' : self.eq_hist,
            'eq_ada_hist' : self.adapt_hist,
            'log' : self.log,
            'blur' : self.blur,
            'gamma' : self.gamma,
            'otsu' : self.otsu,
        }

    #############################################
    # preprocessing operations
    #############################################
    def rescale(self, image):
        """A function to rescale the pixel intensities of the image

        Parameters:
        -----------------------------
            : image (np.array): image 

        Returns:
        -----------------------------
            : image (np.array): image 
        """
        scale_range = tuple(self.params['intensity_rescale_range'])
        image = exposure.rescale_intensity(image,  out_range=scale_range)
        return image


    def adapt_hist(self, image):
        """A function to correct image using adaptive histogram

        Parameters:
        -----------------------------
            : image (np.array): image 

        Returns:
        -----------------------------
            : image (np.array): image 
        """
        clip = self.params['adaptive_hist_clip']
        k = self.params['adaptive_hist_kernel_size']
        image = exposure.equalize_adapthist(image, 
                                            clip_limit=clip,
                                            kernel_size=k)
        return image


    def eq_hist(self, image):
        """A function to eq image histogram

        Parameters:
        -----------------------------
            : image (np.array): image 

        Returns:
        -----------------------------
            : image (np.array): image 
        """
        image = exposure.equalize_hist(image)
        return image


    def otsu(self, image):
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


    def blur(self, image):
        """ A function to blur the image

        Parameters:
        -----------------------------
            : image (np.array): image 

        Returns:
        -----------------------------
            : image (np.array): image post processing
        """
        s = self.params['gaussian_blur_sigma']
        image = filters.gaussian(image, sigma=s, 
                                 mode='reflect')
        return image


    def gamma(self, image):
        """ A function wrap gamma correciton

        Parameters:
        -----------------------------
            : image (np.array): image 

        Returns:
        -----------------------------
            : image (np.array): image post processing
        """
        g = self.params['gamma_correction']
        image = exposure.adjust_gamma(image, gamma=g)
        return image


    def log(image):
        """ contrast operations 

        Parameters:
        -----------------------------
            : image (np.array): image 

        Returns:
        -----------------------------
            : image (np.array): image post processing 
        """
        gain = self.params['contrast_correction_gain']
        image = exposure.adjust_log(image, gain=gain)
        return image


    def dilate_s(self, image):
        """A function to dilate with a fixed seed (static)

        Parameters:
        -----------------------------
            : image (np.array): image 

        Returns:
        -----------------------------
            : image (np.array): image post processing
        """
        h = self.params['static_dilation_h']
        if h=='m':
            print('')
            h = np.median(image)

        seed = image - h
        dilated = reconstruction(seed, image, method='dilation')
        image = image - dilated
        return image


    def dilate(self, image):
        """A function to dilate the image with variable 
        pixel region 

        Parameters:
        -----------------------------
            : image (np.array): image 

        Returns:
        -----------------------------
            : image (np.array): image post processing
        """
        box_size = self.params['dilation_box_size']
        seed = np.copy(image)
        seed[box_size:-box_size, box_size:-box_size] = image.min()
        dilated = reconstruction(seed, image, method='dilation')
        image = image - dilated
        return image


    def ball(self, image):
        """A function to subtract the backgroun

        Parameters:
        -----------------------------
            : image (np.array): image 

        Returns:
        -----------------------------
            : image (np.array): image post processing
        """
        radius = self.params['rolling_ball_radius']
        background = restoration.rolling_ball(image)
        image = image - background
        return image
        
    #############################################
    # utilities
    #############################################    
    def _get_channel_indices(self):
        """A function to return the channel indices in the czi
        file
        
        Returns:
        -----------------------------
            : indices (list of int): the indices of the channels
            to be processed    
        """
        indices = []
        for chan in self.params['process_channels']:
            idx = self.metadata['channel_map'][chan]
            indices.append(idx)
        return indices
    
    
    #############################################
    # flow control: parallelizing operations
    #############################################
    def _process_image(self, image):
        """ A master function to wrap individual processes 
        
        Parameters:
        -----------------------------
            : image (np.array): image 

        Returns:
        -----------------------------
            : image (np.array): image 
        """
        for func in self.chain:
            image = self.ops[func](image)
        return image
    
    
    def single_channel_process(self, M):
        """A function to parallel processes over a single 
        channel (all time points, all tiles)
        
        Parameters:
        -----------------------------
            : M (list of 23 array): list of all tiles by time for a single channel

        Returns:
        -----------------------------
            : M_new (np.array): array with (tile, image_y, image_x) shape 
        """
        M_new = np.zeros(M.shape)
        
        for i in range(M.shape[0]):
            M_new[i] = self._process_image(M[i])
        return M_new
            

    def process(self, czi_data):
        """A function to process a czi czi_array 
        
        NOTES:
        -----------------------------
            (1) it is assumed that each czi with be a single scene file
            (2) it is assumed that all time points may be processed independently        
        
        Parameters:
        -----------------------------
            : czi_data (np.array): image: NOTE: this function does not
            take in a aicsimageio.readers.czi_reader.CziReader object.

        Returns:
        -----------------------------
            : processed_data (np.array): a preprocessed image where each channel is 
            either processed (if specified in config), or processed
        """
        scene = czi_data[0] # first channel is a stub for mutliple scenes
        img_shape = self.metadata['image_shape']
        
        # move channels to make assignment easier
        scene = np.moveaxis(scene, 1, 0)
        
        processed_data = np.zeros(scene.shape)

        # process the channels specified, pass others
        for c in range(scene.shape[0]):
            if c in self.channels:
                # convert to list of 3d mats (all times)
                T = list(scene[c, :, :, :, :])
                
                pool = mp.Pool()
                new_T = pool.map(self.single_channel_process, T)
                processed_data[c] = np.asarray(new_T)
            else:
                processed_data[c] = scene[c]
            
        # reshape the processed data and reset the scene
        processed_data = np.moveaxis(processed_data, 0, 1)
        processed_data = np.expand_dims(processed_data, 0)
        return processed_data
    
    
    #############################################
    # stitchting and global processing
    #############################################
    def stitch(self, czi_data):
        """A function to stich together mutliple tiles
        
        NOTE: this impacts the metadata.
        
        Parameters:
        -----------------------------
            : czi_data (np.array): data array with separate tiles
            
        Returns:
        -----------------------------
            : czi_data (np.array): without the tiles dimension (stub 1)
        """
        # (ntiles_row, ntiles_column)
        grid_shape = tuple(self.params['grid_shape'])
        
        scene = czi_data[0] # first channel is a stub for mutliple scenes
        
        new_shape = (scene.shape[0], # time
                     scene.shape[1], # channel
                     1,              # tiles (stub dim)
                     scene.shape[3] * grid_shape[0], # new image y
                     scene.shape[4] * grid_shape[1]) # new image x
        
        stitched_data = np.zeros((new_shape))
        
        for t in range(scene.shape[0]):
            for c in range(scene.shape[1]):
                tiles = scene[t, c, :, :, :]
                stitched = util.montage(tiles, grid_shape=grid_shape)               
                stitched_data[t, c, 0, :, :] = stitched

        return stitched_data
    
    
        
        

    
    
