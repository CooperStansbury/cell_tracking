import sys
import numpy as np
import multiprocessing as mp
from numba import jit
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
    
    __slots__ = ['adaptive_hist_clip',
                 'adaptive_hist_kernel_size',
                 'chain',
                 'channels',
                 "process_channels",
                 'contrast_correction_gain',
                 'data_directory',
                 'dilation_box_size',
                 'files',
                 'gamma_correction',
                 'gaussian_blur_sigma',
                 'grid_shape',
                 'input_type',
                 'metadata',
                 'ops',
                 'output_directory',
                 'parameter_input_path',
                 'params',
                 'process_chain',
                 'rescale_stitch',
                 'local_eq_radius',
                 'rolling_ball_radius',
                 'static_dilation_h',
                 'resize_factor']
    
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
            'resize' : self._resize
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


    def log(self, image):
        """ contrast operations 

        Parameters:
        -----------------------------
            : image (np.array): image 

        Returns:
        -----------------------------
            : image (np.array): image post processing 
        """
        gain = self.contrast_correction_gain
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
        rf = self.resize_factor
        
        output_shape = (image.shape[0] // rf, image.shape[1] // rf)
        image = transform.resize(image, output_shape)
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
        M_new = np.asarray([self._process_image(i) for i in M])
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
        
        if 'resize' in self.process_chain:
            rf = self.resize_factor

            new_shape = (scene.shape[0],
                         scene.shape[1],
                         scene.shape[2],
                         (scene.shape[3] // rf),
                         (scene.shape[4] // rf))
        else:
            new_shape = scene.shape
        
        processed_data = np.zeros(new_shape)
        print(processed_data.shape)

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
        rf = self.params['resize_factor']
        
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
                
                if self.params['rescale_stitch']:
                    stitched = exposure.rescale_intensity(stitched, out_range=(0, 1))
                
                stitched_data[t, c, 0, :, :] = stitched
        
        stitched_data = np.expand_dims(stitched_data, 0)
        return stitched_data
    
    
        
        

    
    
