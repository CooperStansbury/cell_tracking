import sys
import numpy as np
import multiprocessing as mp
from numba import jit
from functools import partial
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import skimage
from skimage import io
from skimage.color import rgb2gray
from skimage.morphology import reconstruction
from skimage import (
    color, feature, filters, measure, morphology, segmentation, exposure, restoration, util, transform
)



class ParallelTransformer():
    """a class to manage parameters """
    
    __slots__ = [
        'adaptive_hist_clip',
        'adaptive_hist_kernel_size',
        'channels',
        'log_correction_gain',
        'data_directory',
        'dilation_box_size',
        'files',
        'gamma_correction',
        'gaussian_blur_sigma',
        'grid_shape',
        'input_type',
        'local_eq_radius',
        'metadata',
        'ops',
        'output_directory',
        'parameter_input_path',
        'params',
        'process_channels',
        'quilt_resize_factor',
        'resize_quilt',
        'resize_tiles',
        'rolling_ball_radius',
        'static_dilation_h',
        'tile_resize_factor',
        'parallel_procs',
        'stitch_processing'
    ]
    
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
        
        # make each an attribute, so re-tweakable
        for key in self.params:
                setattr(self, key, self.params[key])
                                  
        self.ops = {
            'ball' : self.ball,
            'dilate' : self.dilate,
            'dilate_s' : self.dilate_s,
            'eq_hist' : self.eq_hist,
            'ada_hist' : self.adapt_hist,
            'log' : self.log,
            'blur' : self.blur,
            'gamma' : self.gamma,
            'otsu' : self.otsu,
            'local_eq' : self.local_eq,
            'resize' : self._resize,
            'rescale': self._rescale,
            'stretch': self.stretch
        }

    #############################################
    # preprocessing operations
    #############################################
    def adapt_hist(self, image):
        """A function to correct image using adaptive histogram

        Parameters:
        -----------------------------
            : image (np.array): image 

        Returns:
        -----------------------------
            : image (np.array): image 
        """
        clip = self.adaptive_hist_clip
        k = self.adaptive_hist_kernel_size
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
    
    
    def local_eq(self, image):
        """A function to eq image histogram

        Parameters:
        -----------------------------
            : image (np.array): image 

        Returns:
        -----------------------------
            : image (np.array): image 
        """
        selem = morphology.disk(self.local_eq_radius)
        image = filters.rank.equalize(image, selem=selem)
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
        s = self.gaussian_blur_sigma
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
        g = self.gamma_correction
        image = exposure.adjust_gamma(image, gamma=g)
        return image
    
    
    def stretch(self, image):
        """ A function wrap contrast stretching

        Parameters:
        -----------------------------
            : image (np.array): image 

        Returns:
        -----------------------------
            : image (np.array): image post processing
        """
        v_min, v_max = np.percentile(image, (0.2, 99.8))
        image = exposure.rescale_intensity(image, in_range=(v_min, v_max))
        return image


    def log(self, image):
        """ contrast operations 

        Parameters:
        -----------------------------
            : image (np.array): image 

        Returns:
        -----------------------------
            : image (np.array): image post processing 
        """
        gain = self.log_correction_gain
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
        h = self.static_dilation_h
        if h=='m':
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
        box_size = self.dilation_box_size
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
        radius = self.rolling_ball_radius
        background = restoration.rolling_ball(image)
        image = image - background
        return image
    
    
    def _resize(self, image):
        """a function to resize the input
        
        Parameters:
        -----------------------------
            : image (np.array): image 

        Returns:
        -----------------------------
            : image (np.array): image post processing
        """
        rf = self.tile_resize_factor
        
        output_shape = (image.shape[0] // rf, image.shape[1] // rf)
        image = transform.resize(image, output_shape)
        return image
    
    
    def _rescale(self, image):
        """A function to rescale pizel intensities between 0 and 1
                
        Parameters:
        -----------------------------
            : image (np.array): image 

        Returns:
        -----------------------------
            : image (np.array): image post processing
        """
        image = exposure.rescale_intensity(image, out_range=(0, 1))
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
    
    
    def _get_channel_name(self, idx):
        """A function to return the channel name
        
        Parameters:
        -----------------------------
            : idx (int): index of channel

        Returns:
        -----------------------------
            : channel_name (str): the channel name
        """
        l = dict(zip(self.metadata['channel_map'].values(),self.metadata['channel_map'].keys()))
        return l[idx]
        
    
    def _get_new_size(self, scene):
        """A function to return an array with correct dimensions after resizing 
        
        Parameters:
        -----------------------------
            : scene (np.array): input image

        Returns:
        -----------------------------
            : new_size (tuple): correct dimensions for the new array
        """
        
        new_shape = list(scene.shape)
        img_shape = self.metadata['image_shape']
        
        if self.resize_tiles:
            rf = self.tile_resize_factor
            new_shape[-2] = img_shape[0] // rf
            new_shape[-1] = img_shape[1] // rf
            
        new_shape[0] = len(self.channels)
        return tuple(new_shape)
        
        
    
    #############################################
    # flow control: parallelizing operations
    #############################################
    def _process_image(self, image, func_list):
        """A master function to wrap individual processes 
        
        Parameters:
            : image (np.array): image 
            : func_list (list of callable): the channel's pipelin 

        Returns:
        -----------------------------
            : image (np.array): image 
        """
        for func in func_list:
            image = self.ops[func](image)
        return image
    
        
    def process_tiles(self, czi_data):
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
        
        # move channels to make assignment easier
        scene = np.moveaxis(scene, 1, 0)
        
        new_shape = self._get_new_size(scene)
        processed_data = np.zeros(new_shape)
        
        for i, c in enumerate(self.channels): 
            channel_shape = scene[c].shape
            T = scene[c].reshape(channel_shape[0] * channel_shape[1], 
                                 channel_shape[2], 
                                 channel_shape[3])
            T = list(T)
            
            channel_name = self._get_channel_name(c)
            print(f"processing: {channel_name}")
                                
            pool = mp.Pool(int(self.parallel_procs))
            func_list = self.process_channels[channel_name]
            new_T = pool.map(partial(self._process_image, func_list=func_list), T)
            
            new_T = np.asarray(new_T).reshape(channel_shape[0], 
                                              channel_shape[1], 
                                              new_shape[-2], 
                                              new_shape[-1])
            processed_data[i] = new_T

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
        rf = self.quilt_resize_factor
        
        scene = czi_data[0] # first channel is a stub for mutliple scenes
        
        new_shape = (scene.shape[0], # time
                     scene.shape[1], # channel
                     1,              # tiles (stub dim)
                     ((scene.shape[3] * grid_shape[0]) // rf), # new image y
                     ((scene.shape[4] * grid_shape[1]) // rf)) # new image x
        
        stitched_data = np.zeros((new_shape))
        
        for t in range(scene.shape[0]):
            for c in range(scene.shape[1]):
                tiles = scene[t, c, :, :, :]
                stitched = util.montage(tiles, grid_shape=grid_shape)  
                
                output_shape = (stitched.shape[0] // rf, stitched.shape[1] // rf)
                stitched = transform.resize(stitched, output_shape)

                stitched_data[t, c, 0, :, :] = stitched
        
        stitched_data = np.expand_dims(stitched_data, 0)
        return stitched_data
    
    
    def process_stitched(self, czi_data):
        """A function to process a czi czi_array 
        
        Parameters:
        -----------------------------
            : czi_data (np.array): a stitched czi image: 
        Returns:
        -----------------------------
            : processed_data (np.array): a preprocessed image
        """
        scene = czi_data[0]
        
        scene = np.moveaxis(scene, 1, 0)
        scene = np.squeeze(scene, 2)
    
        processed_data = np.zeros(scene.shape)
        
        for c in range(scene.shape[0]):
            
            T = list(scene[c])
            func_list = self.stitch_processing
            pool = mp.Pool(int(self.parallel_procs))
            new_T = pool.map(partial(self._process_image, func_list=func_list), T)
            new_T = np.asarray(new_T)
            processed_data[c] = new_T
            
        processed_data = np.moveaxis(processed_data, 0, 1)
        processed_data = np.expand_dims(processed_data, 0)
        processed_data = np.expand_dims(processed_data, 3)
        return processed_data
    
            
        
        
    
    
        
        

    
    
